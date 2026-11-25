import pytest
from datetime import datetime, timedelta, timezone
from app.db import Session, SessionLease
from test_hardening import c


def test_anonymous_provider_access_is_disabled(c, monkeypatch):
    token = c.post("/sessions").json()["token"]
    monkeypatch.setenv("AGENT_MODE", "provider")
    assert c.post("/sessions").status_code == 503
    assert (
        c.post(
            "/chat",
            headers={"Authorization": "Bearer " + token},
            json={"text": "hello"},
        ).status_code
        == 503
    )


def test_deployed_demo_is_disabled(c, monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    assert c.post("/sessions").status_code == 503
    assert c.get("/").status_code == 200


@pytest.mark.parametrize("state", ["missing", "expired", "revoked"])
def test_invalid_lease_rejected(c, state):
    account = c.post("/sessions").json()
    with Session() as s:
        lease = s.get(SessionLease, account["user_id"])
        if state == "missing":
            s.delete(lease)
        elif state == "expired":
            lease.expires_at = (
                datetime.now(timezone.utc) - timedelta(seconds=1)
            ).isoformat()
        else:
            lease.revoked = True
        s.commit()
    assert (
        c.get(
            "/memory", headers={"Authorization": "Bearer " + account["token"]}
        ).status_code
        == 401
    )


def test_approval_cannot_replace_parameters(c):
    h = {"Authorization": "Bearer " + c.post("/sessions").json()["token"]}
    aid = c.post(
        "/memory", headers=h, json={"key": "location", "value": "Remote"}
    ).json()["approval_id"]
    for body in [
        {"approved": True, "payload": {"value": "altered"}},
        {"approved": "true"},
    ]:
        assert c.post("/approvals/" + aid, headers=h, json=body).status_code == 422
    assert c.get("/memory", headers=h).json() == []
    assert (
        c.post("/approvals/" + aid, headers=h, json={"approved": True}).status_code
        == 200
    )
    assert c.get("/memory", headers=h).json()[0]["value"] == "Remote"


def test_size_limit_and_security_headers(c):
    response = c.post("/chat", content=b"x" * 65537)
    assert response.status_code == 413
    for path in ["/memory", "/", "/does-not-exist"]:
        response = c.get(path)
        assert response.headers["cache-control"] == "no-store"
        assert response.headers["x-content-type-options"] == "nosniff"
        assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
        assert response.headers["x-request-id"]


def test_chunked_oversized_body_rejected():
    import asyncio
    from app.security import SecurityBoundary

    called = []
    sent = []
    messages = iter(
        [
            {"type": "http.request", "body": b"a" * 40000, "more_body": True},
            {"type": "http.request", "body": b"b" * 40000, "more_body": False},
        ]
    )

    async def downstream(*args):
        called.append(True)

    async def receive():
        return next(messages)

    async def send(message):
        sent.append(message)

    asyncio.run(SecurityBoundary(downstream)({"type": "http"}, receive, send))
    assert not called
    assert sent[0]["status"] == 413
