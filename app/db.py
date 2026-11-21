import os
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import create_engine, String, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


def uid():
    return str(uuid4())


def now():
    return datetime.now(timezone.utc).isoformat()


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)


class Profile(Base):
    __tablename__ = "career_profiles"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    data: Mapped[dict] = mapped_column(JSON, default=dict)


class Fact(Base):
    __tablename__ = "preference_facts"
    __table_args__ = (UniqueConstraint("user_id", "key"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    key: Mapped[str] = mapped_column(String(64))
    value: Mapped[str] = mapped_column(String(500))
    version: Mapped[int] = mapped_column(default=1)


class Thread(Base):
    __tablename__ = "conversation_threads"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    thread_id: Mapped[str] = mapped_column(
        ForeignKey("conversation_threads.id"), index=True
    )
    role: Mapped[str] = mapped_column(String(20))
    text: Mapped[str] = mapped_column(String(8000))
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Invocation(Base):
    __tablename__ = "tool_invocations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    thread_id: Mapped[str] = mapped_column(
        ForeignKey("conversation_threads.id"), index=True
    )
    tool: Mapped[str] = mapped_column(String(64))
    arguments: Mapped[dict] = mapped_column(JSON)
    output: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Approval(Base):
    __tablename__ = "approval_requests"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="pending")


class Audit(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    event: Mapped[str] = mapped_column(String(64))
    detail: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./prefloom.db")
engine = create_engine(
    DATABASE_URL,
    **(
        {"connect_args": {"check_same_thread": False}}
        if DATABASE_URL.startswith("sqlite")
        else {"pool_pre_ping": True}
    ),
)
Session = sessionmaker(engine, expire_on_commit=False)


class SessionLease(Base):
    __tablename__ = "session_leases"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    expires_at: Mapped[str] = mapped_column(String(40))
    revoked: Mapped[bool] = mapped_column(default=False)


class MemoryRevision(Base):
    __tablename__ = "memory_revisions"
    __table_args__ = (UniqueConstraint("fact_id", "version"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    fact_id: Mapped[str] = mapped_column(String(36), index=True)
    version: Mapped[int]
    value: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[str] = mapped_column(String(40), default=now)
