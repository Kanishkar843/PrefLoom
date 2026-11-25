import hashlib, json, secrets, time, logging, os
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import select, text, update, delete
from .db import (
    Base,
    engine,
    Session,
    User,
    Profile,
    Fact,
    Thread,
    Message,
    Invocation,
    Approval,
    Audit,
    SessionLease,
    MemoryRevision,
)
from .agent import graph


@asynccontextmanager
async def lifespan(app):
    # PostgreSQL schema is managed by Alembic; native SQLite is an explicit test/demo fallback.
    if engine.dialect.name == "sqlite":
        Base.metadata.create_all(engine)
    yield


app = FastAPI(title="PrefLoom", version="0.1.0", lifespan=lifespan)
limits = defaultdict(deque)


@app.middleware("http")
async def bounds(request: Request, call_next):
    rid = str(uuid4())
    key = hashlib.sha256(
        request.headers.get(
            "authorization", request.client.host if request.client else "local"
        ).encode()
    ).hexdigest()
    q = limits[key]
    now = time.monotonic()
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= 120:
        from fastapi.responses import JSONResponse

        return JSONResponse(
            {"detail": "Rate limit exceeded"},
            status_code=429,
            headers={"Retry-After": "60"},
        )
    q.append(now)
    if len(limits) > 10000:
        limits.clear()
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    logging.getLogger("prefloom").info(
        "request_id=%s method=%s status=%s", rid, request.method, response.status_code
    )
    return response


def db():
    with Session() as session:
        yield session


def user(request: Request, s=Depends(db)):
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    u = s.scalar(
        select(User).where(
            User.token_hash == hashlib.sha256(token.encode()).hexdigest()
        )
    )
    if not u:
        raise HTTPException(401, "Create a local demo session first")
    lease = s.get(SessionLease, u.id)
    if lease and (
        lease.revoked
        or datetime.fromisoformat(lease.expires_at) <= datetime.now(timezone.utc)
    ):
        raise HTTPException(401, "Session expired or revoked")
    return u.id


class Chat(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, max_length=2000)
    thread_id: str | None = None


class Memory(BaseModel):
    key: str = Field(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_ -]+$")
    value: str = Field(min_length=1, max_length=500)


class Decision(BaseModel):
    approved: bool


@app.get("/health")
def health():
    return {
        "status": "ok",
        "mode": (
            "provider-backed"
            if os.getenv("AGENT_MODE") == "provider"
            else "deterministic-offline"
        ),
        "database": engine.dialect.name,
    }


@app.get("/ready")
def ready(s=Depends(db)):
    s.execute(text("SELECT 1"))
    return {"ready": True}


@app.post("/sessions")
def session(s=Depends(db)):
    token = secrets.token_urlsafe(32)
    u = User(token_hash=hashlib.sha256(token.encode()).hexdigest())
    s.add(u)
    s.commit()
    s.add_all(
        [
            Profile(user_id=u.id, data={}),
            SessionLease(
                user_id=u.id,
                expires_at=(datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
                revoked=False,
            ),
        ]
    )
    s.commit()
    return {"token": token, "user_id": u.id, "mode": "local-demo"}


@app.get("/memory")
def memory(u=Depends(user), s=Depends(db)):
    return [
        {"id": f.id, "key": f.key, "value": f.value, "version": f.version}
        for f in s.scalars(select(Fact).where(Fact.user_id == u))
    ]


@app.post("/memory")
def propose(data: Memory, u=Depends(user), s=Depends(db)):
    a = Approval(user_id=u, action="save_preference", payload=data.model_dump())
    s.add(a)
    s.commit()
    return {"approval_id": a.id}


@app.delete("/memory/{fact_id}")
def forget(fact_id: str, u=Depends(user), s=Depends(db)):
    f = s.scalar(select(Fact).where(Fact.id == fact_id, Fact.user_id == u))
    if not f:
        raise HTTPException(404, "Memory not found")
    s.execute(
        delete(MemoryRevision).where(
            MemoryRevision.fact_id == f.id, MemoryRevision.user_id == u
        )
    )
    s.add(Audit(user_id=u, event="forget", detail={"fact_id": f.id}))
    s.delete(f)
    s.commit()
    return {"deleted": True}


@app.get("/profile")
def profile(u=Depends(user), s=Depends(db)):
    return s.get(Profile, u).data


@app.get("/approvals")
def approvals(u=Depends(user), s=Depends(db)):
    return [
        {"id": a.id, "action": a.action, "payload": a.payload, "status": a.status}
        for a in s.scalars(
            select(Approval).where(Approval.user_id == u, Approval.status == "pending")
        )
    ]


@app.post("/approvals/{approval_id}")
def decide(approval_id: str, data: Decision, u=Depends(user), s=Depends(db)):
    a = s.scalar(
        select(Approval)
        .where(Approval.id == approval_id, Approval.user_id == u)
        .with_for_update()
    )
    if not a:
        raise HTTPException(404, "Approval not found")
    if a.status != "pending":
        raise HTTPException(409, "Already resolved")
    claimed = s.execute(
        update(Approval)
        .where(
            Approval.id == approval_id,
            Approval.user_id == u,
            Approval.status == "pending",
        )
        .values(status="processing")
    )
    if claimed.rowcount != 1:
        raise HTTPException(409, "Already resolved")
    s.execute(select(User).where(User.id == u).with_for_update())
    if data.approved:
        if a.action == "save_preference":
            p = Memory.model_validate(a.payload)
            f = s.scalar(select(Fact).where(Fact.user_id == u, Fact.key == p.key))
            if f:
                f.value = p.value
                f.version += 1
            else:
                f = Fact(user_id=u, key=p.key, value=p.value)
                s.add(f)
                s.flush()
            s.add(
                MemoryRevision(
                    user_id=u, fact_id=f.id, version=f.version, value=f.value
                )
            )
        elif a.action == "update_profile":
            s.get(Profile, u).data = a.payload
        else:
            raise HTTPException(400, "Unsupported action")
    a.status = "approved" if data.approved else "rejected"
    s.add(
        Audit(
            user_id=u, event=a.status, detail={"approval_id": a.id, "action": a.action}
        )
    )
    s.commit()
    return {"status": a.status}


@app.get("/threads")
def threads(u=Depends(user), s=Depends(db)):
    return [{"id": t.id} for t in s.scalars(select(Thread).where(Thread.user_id == u))]


@app.get("/threads/{thread_id}/messages")
def messages(thread_id: str, u=Depends(user), s=Depends(db)):
    if not s.scalar(select(Thread).where(Thread.id == thread_id, Thread.user_id == u)):
        raise HTTPException(404, "Thread not found")
    return [
        {"role": m.role, "text": m.text}
        for m in s.scalars(
            select(Message)
            .where(Message.thread_id == thread_id)
            .order_by(Message.created_at)
        )
    ]


def run_chat(data, u, s):
    if data.thread_id:
        t = s.scalar(
            select(Thread).where(Thread.id == data.thread_id, Thread.user_id == u)
        )
        if not t:
            raise HTTPException(404, "Thread not found")
    else:
        t = Thread(user_id=u)
        s.add(t)
        s.flush()
    facts = {f.key: f.value for f in s.scalars(select(Fact).where(Fact.user_id == u))}
    try:
        state = graph.invoke({"text": data.text, "memory": facts})
    except ValueError:
        raise HTTPException(422, "Invalid tool arguments; use /remember key=value")
    except RuntimeError:
        raise HTTPException(
            503, "Planner unavailable; retry later or select offline mode"
        )
    result = state["result"]
    proposal = result["proposal"]
    if proposal:
        if proposal["action"] == "save_preference":
            try:
                Memory.model_validate(proposal["payload"])
            except ValueError:
                raise HTTPException(422, "Invalid preference key/value")
        a = Approval(user_id=u, action=proposal["action"], payload=proposal["payload"])
        s.add(a)
        s.flush()
        result["approval_id"] = a.id
    s.add_all(
        [
            Message(thread_id=t.id, role="user", text=data.text),
            Message(thread_id=t.id, role="assistant", text=result["message"]),
            *[
                Invocation(
                    user_id=u,
                    thread_id=t.id,
                    tool=step["call"]["name"],
                    arguments=step["call"],
                    output=step["output"],
                )
                for step in state["results"]
            ],
        ]
    )
    s.commit()
    return {**result, "thread_id": t.id}


@app.post("/chat")
def chat(data: Chat, u=Depends(user), s=Depends(db)):
    return run_chat(data, u, s)


@app.post("/chat/stream")
def stream(data: Chat, u=Depends(user), s=Depends(db)):
    result = run_chat(data, u, s)

    def events():
        for step in result["trace"]:
            yield "event: trace\ndata: " + json.dumps({"step": step}) + "\n\n"
        yield "event: result\ndata: " + json.dumps(result) + "\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


@app.get("/traces")
def traces(u=Depends(user), s=Depends(db)):
    return [
        {
            "id": i.id,
            "tool": i.tool,
            "arguments": i.arguments,
            "output": i.output,
            "created_at": i.created_at,
        }
        for i in s.scalars(
            select(Invocation)
            .where(Invocation.user_id == u)
            .order_by(Invocation.created_at.desc())
            .limit(100)
        )
    ]


@app.delete("/sessions/current")
def logout(u=Depends(user), s=Depends(db)):
    lease = s.get(SessionLease, u)
    if lease:
        lease.revoked = True
    else:
        s.add(
            SessionLease(
                user_id=u,
                expires_at=datetime.now(timezone.utc).isoformat(),
                revoked=True,
            )
        )
    s.commit()
    return {"revoked": True}


@app.get("/memory/{fact_id}/versions")
def versions(fact_id: str, u=Depends(user), s=Depends(db)):
    if not s.scalar(select(Fact).where(Fact.id == fact_id, Fact.user_id == u)):
        raise HTTPException(404, "Memory not found")
    return [
        {"version": r.version, "value": r.value, "created_at": r.created_at}
        for r in s.scalars(
            select(MemoryRevision)
            .where(MemoryRevision.fact_id == fact_id, MemoryRevision.user_id == u)
            .order_by(MemoryRevision.version)
        )
    ]


STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")
FRONTEND = Path(__file__).parent.parent / "frontend" / "dist"
if (FRONTEND / "assets").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND / "assets"), name="assets")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(
        FRONTEND / "index.html"
        if (FRONTEND / "index.html").exists()
        else STATIC / "index.html"
    )


@app.get("/legacy", include_in_schema=False)
def legacy():
    return FileResponse(STATIC / "index.html")
