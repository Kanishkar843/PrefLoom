import os

os.environ["DATABASE_URL"] = "sqlite:///./test-hardening.db"
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine
from app.provider import plan, ProviderUnavailable
import httpx, pytest


@pytest.fixture
def c():
    Base.metadata.drop_all(engine)
    with TestClient(app) as client:
        yield client


def test_profile_history_forget_logout(c):
    h = {"Authorization": "Bearer " + c.post("/sessions").json()["token"]}
    for value in ["Remote", "Hybrid"]:
        aid = c.post(
            "/memory", headers=h, json={"key": "location", "value": value}
        ).json()["approval_id"]
        assert (
            c.post("/approvals/" + aid, headers=h, json={"approved": True}).status_code
            == 200
        )
    fact = c.get("/memory", headers=h).json()[0]
    assert [
        r["version"]
        for r in c.get("/memory/" + fact["id"] + "/versions", headers=h).json()
    ] == [1, 2]
    a = c.post(
        "/chat",
        headers=h,
        json={"text": "/profile Python engineer with 3 years, SQL and remote work"},
    ).json()
    assert a["proposal"]["payload"]["experience_years"] == 3
    assert c.get("/profile", headers=h).json() == {}
    c.post("/approvals/" + a["approval_id"], headers=h, json={"approved": True})
    assert "python" in c.get("/profile", headers=h).json()["skills"]
    c.delete("/memory/" + fact["id"], headers=h)
    assert c.get("/memory/" + fact["id"] + "/versions", headers=h).status_code == 404
    c.delete("/sessions/current", headers=h)
    assert c.get("/memory", headers=h).status_code == 401


def test_provider_failure_redaction(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-provider-credential")
    transport = httpx.MockTransport(
        lambda request: httpx.Response(503, text="sensitive upstream content")
    )
    with pytest.raises(ProviderUnavailable, match="Provider failed") as err:
        plan("python", {}, {}, transport)
    assert "sensitive" not in str(err.value)


def test_multistep_plan_and_approval_stop(c):
    h = {"Authorization": "Bearer " + c.post("/sessions").json()["token"]}
    response = c.post(
        "/chat", headers=h, json={"text": "discover and compare python roles"}
    ).json()
    assert [r["call"]["name"] for r in response["steps"]] == [
        "search_opportunities",
        "compare_roles",
        "explain_recommendation",
    ]
    assert len(c.get("/traces", headers=h).json()) == 3


def test_concurrent_approval_exactly_once(c):
    from concurrent.futures import ThreadPoolExecutor

    h = {"Authorization": "Bearer " + c.post("/sessions").json()["token"]}
    aid = c.post("/memory", headers=h, json={"key": "remote", "value": "yes"}).json()[
        "approval_id"
    ]
    with ThreadPoolExecutor(2) as pool:
        statuses = list(
            pool.map(
                lambda _: (
                    c.post(
                        "/approvals/" + aid, headers=h, json={"approved": True}
                    ).status_code
                ),
                range(2),
            )
        )
    assert sorted(statuses) == [200, 409]
    assert c.get("/memory", headers=h).json()[0]["version"] == 1


def test_provider_structured_profile_is_only_a_proposal(c, monkeypatch):
    from app import provider

    monkeypatch.setenv("AGENT_MODE", "provider")
    monkeypatch.setattr(
        provider,
        "plan",
        lambda *args, **kwargs: {
            "steps": [
                {
                    "name": "update_profile",
                    "profile": {
                        "summary": "Backend specialist",
                        "skills": ["python", "sql"],
                        "experience_years": 5,
                        "remote": True,
                    },
                }
            ]
        },
    )
    h = {"Authorization": "Bearer " + c.post("/sessions").json()["token"]}
    r = c.post("/chat", headers=h, json={"text": "Extract my profile"}).json()
    assert r["mode"] == "provider-backed"
    assert r["proposal"]["payload"]["experience_years"] == 5
    assert c.get("/profile", headers=h).json() == {}
    c.post("/approvals/" + r["approval_id"], headers=h, json={"approved": True})
    assert c.get("/profile", headers=h).json()["skills"] == ["python", "sql"]
