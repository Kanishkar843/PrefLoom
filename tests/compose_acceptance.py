"""Run against an already started, isolated Compose stack; restart only its API."""

import json, os, subprocess, time, urllib.request

base = os.getenv("ACCEPTANCE_URL", "http://127.0.0.1:18080")
project = os.getenv("COMPOSE_PROJECT_NAME", "prefloom-acceptance")
docker = os.getenv("DOCKER_BIN", "docker")


def call(path, payload=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    import httpx, ssl, truststore
    with httpx.Client(verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT),trust_env=False,timeout=15) as client:
        response=client.request("POST" if payload is not None else "GET",base+path,json=payload,headers=headers)
        response.raise_for_status()
        return response.json()


assert call("/health")["database"] == "postgresql"
token = call("/sessions", {})["token"]
result = call("/chat", {"text": "/remember location=Remote"}, token)
assert call("/memory", token=token) == []
call("/approvals/" + result["approval_id"], {"approved": True}, token)
subprocess.run([docker, "compose", "-p", project, "restart", "api"], check=True)
for attempt in range(90):
    try:
        call("/ready")
        break
    except Exception:
        time.sleep(1)
else:
    raise AssertionError("Compose API did not recover")
assert call("/memory", token=token)[0]["value"] == "Remote"
assert len(call("/threads/" + result["thread_id"] + "/messages", token=token)) == 2
assert (
    len(call("/chat", {"text": "discover and compare python roles"}, token)["steps"])
    == 3
)
print(
    json.dumps(
        {
            "database": "PostgreSQL",
            "compose_restart": "passed",
            "approval": "passed",
            "memory_and_conversation_persistence": "passed",
            "multi_step": "passed",
        }
    )
)
