import ssl, truststore

"""Explicit real PostgreSQL/process-restart acceptance test. Never substitutes SQLite."""

import os, sys, socket, time, subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import httpx
from sqlalchemy import create_engine, text


def test_postgres_restart_isolation_and_concurrency():
    url = os.environ.get("TEST_DATABASE_URL")
    assert url and url.startswith("postgresql"), (
        "TEST_DATABASE_URL must identify an isolated PostgreSQL test database"
    )
    root = Path(__file__).resolve().parents[1]
    (root / ".cache").mkdir(exist_ok=True)
    env = {**os.environ, "DATABASE_URL": url, "AGENT_MODE": "offline"}
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=root,
        env=env,
        check=True,
        capture_output=True,
    )
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    log = (root / ".cache/postgres-api.log").open("w")
    proc = None

    def start():
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=root,
            env=env,
            stdout=log,
            stderr=log,
        )
        for _ in range(100):
            try:
                if client.get("/ready").status_code == 200:
                    return process
            except httpx.HTTPError:
                pass
            if process.poll() is not None:
                raise AssertionError("API exited; inspect .cache/postgres-api.log")
            time.sleep(0.1)
        process.terminate()
        process.wait()
        raise AssertionError("API startup timed out")

    with httpx.Client(
        verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT),
        base_url=f"http://127.0.0.1:{port}",
        trust_env=False,
        timeout=10,
    ) as client:
        try:
            proc = start()
            assert client.get("/health").json()["database"] == "postgresql"
            assert client.get("/docs").status_code == 200
            h = {"Authorization": "Bearer " + client.post("/sessions").json()["token"]}
            other = {
                "Authorization": "Bearer " + client.post("/sessions").json()["token"]
            }
            result = client.post(
                "/chat", headers=h, json={"text": "/remember location=Remote"}
            ).json()
            aid = result["approval_id"]
            assert client.get("/memory", headers=h).json() == []
            assert (
                client.post(
                    "/approvals/" + aid, headers=other, json={"approved": True}
                ).status_code
                == 404
            )
            with ThreadPoolExecutor(2) as pool:
                statuses = list(
                    pool.map(
                        lambda _: (
                            client.post(
                                "/approvals/" + aid, headers=h, json={"approved": True}
                            ).status_code
                        ),
                        range(2),
                    )
                )
            assert sorted(statuses) == [200, 409]
            proc.terminate()
            proc.wait(timeout=15)
            proc = start()
            facts = client.get("/memory", headers=h).json()
            assert facts[0]["value"] == "Remote" and facts[0]["version"] == 1
            assert client.get("/memory", headers=other).json() == []
            assert (
                len(
                    client.get(
                        "/threads/" + result["thread_id"] + "/messages", headers=h
                    ).json()
                )
                == 2
            )
            assert (
                client.get(
                    "/threads/" + result["thread_id"] + "/messages", headers=other
                ).status_code
                == 404
            )
            discovery = client.post(
                "/chat", headers=h, json={"text": "discover and compare python roles"}
            ).json()
            assert len(discovery["steps"]) == 3
            client.delete("/memory/" + facts[0]["id"], headers=h)
            assert client.get("/memory", headers=h).json() == []
            engine = create_engine(url)
            with engine.connect() as c:
                assert (
                    c.execute(text("SELECT count(*) FROM tool_invocations")).scalar()
                    >= 4
                )
            engine.dispose()
        finally:
            if proc and proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=15)
            log.close()
