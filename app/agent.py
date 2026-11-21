import os, re
from typing import TypedDict, Literal
from pydantic import BaseModel, ConfigDict, Field
from langgraph.graph import StateGraph, START, END

JOBS = [
    {
        "id": str(i),
        "title": title,
        "company": f"Synthetic Studio {i}",
        "location": location,
        "skills": skills,
        "synthetic": True,
    }
    for i, (title, location, skills) in enumerate(
        [
            ("Python Backend Engineer", "Remote", ["python", "sql", "fastapi"]),
            ("Data Engineer", "Bengaluru", ["python", "sql", "pipelines"]),
            ("Frontend Engineer", "Remote", ["typescript", "react"]),
            ("ML Platform Engineer", "Hyderabad", ["python", "docker", "ml"]),
            ("API Engineer", "Remote", ["python", "fastapi", "postgresql"]),
        ],
        1,
    )
]


class ProfileFields(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str = Field(max_length=500)
    skills: list[str] = Field(default_factory=list, max_length=30)
    experience_years: int | None = Field(default=None, ge=0, le=70)
    remote: bool = False


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Literal[
        "search_opportunities",
        "compare_roles",
        "save_preference",
        "update_profile",
        "explain_recommendation",
    ]
    query: str = Field(default="", max_length=2000)
    key: str = Field(default="", max_length=64)
    value: str = Field(default="", max_length=500)
    profile: ProfileFields | None = None


class ToolPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    steps: list[ToolCall] = Field(min_length=1, max_length=5)


class ToolResult(BaseModel):
    mode: Literal["deterministic-offline", "provider-backed"] = "deterministic-offline"
    tool: str
    message: str
    jobs: list[dict] = Field(default_factory=list)
    proposal: dict | None = None
    trace: list[str]


class State(TypedDict, total=False):
    text: str
    memory: dict
    call: dict
    result: dict
    trace: list[str]
    calls: list[dict]
    cursor: int
    results: list[dict]


def parse(s):
    text = s["text"].strip()
    lower = text.lower()
    # Strict commands are data, never executable instructions or arbitrary tool names.
    if lower.startswith("/remember ") and "=" in text:
        key, value = text[10:].split("=", 1)
        call = ToolCall(name="save_preference", key=key.strip(), value=value.strip())
    elif lower.startswith("/profile "):
        call = ToolCall(name="update_profile", value=text[9:])
    elif lower.startswith("/compare"):
        call = ToolCall(name="compare_roles", query=text[8:].strip())
    elif lower.startswith("/explain"):
        call = ToolCall(name="explain_recommendation", query=text[8:].strip())
    elif os.getenv("AGENT_MODE", "offline") == "provider":
        from .provider import plan

        planned = ToolPlan.model_validate(
            plan(text, s.get("memory", {}), ToolPlan.model_json_schema())
        )
        return {
            "calls": [c.model_dump() for c in planned.steps],
            "cursor": 0,
            "results": [],
            "trace": ["parse_intent: provider structured plan"],
            "call": planned.steps[0].model_dump(),
        }
    else:
        call = ToolCall(name="search_opportunities", query=text)
    calls = [call]
    if call.name == "search_opportunities" and any(
        word in lower for word in ["compare", "explain", "discover"]
    ):
        calls += [
            ToolCall(name="compare_roles", query=text),
            ToolCall(name="explain_recommendation", query=text),
        ]
    return {
        "call": call.model_dump(),
        "calls": [c.model_dump() for c in calls],
        "cursor": 0,
        "results": [],
        "trace": ["parse_intent: deterministic bounded plan"],
    }


def retrieve(s):
    return {"trace": s["trace"] + ["retrieve_memory: SQL scoped to authenticated user"]}


def choose(s):
    return {"call": s["calls"][s["cursor"]]}


def execute(s):
    c = ToolCall.model_validate(s["call"])
    proposal = None
    words = set(c.query.lower().split())
    preferences = set(" ".join(s["memory"].values()).lower().split())
    ranked = sorted(
        JOBS,
        key=lambda j: (
            -len(
                (words | preferences)
                & set(
                    (" ".join(j["skills"]) + " " + j["location"] + " " + j["title"])
                    .lower()
                    .split()
                )
            ),
            j["id"],
        ),
    )
    message = "Synthetic opportunities ranked by explicit keyword and saved-preference overlap."
    if c.name == "save_preference":
        if not c.key or not c.value:
            raise ValueError("Use /remember key=value with nonempty values")
        proposal = {"action": c.name, "payload": {"key": c.key, "value": c.value}}
        message = "Preference change needs your approval."
        ranked = []
    elif c.name == "update_profile":
        skills = [
            skill
            for skill in [
                "python",
                "sql",
                "fastapi",
                "react",
                "typescript",
                "docker",
                "postgresql",
                "ml",
                "langgraph",
            ]
            if re.search(r"\b" + skill + r"\b", c.value, re.I)
        ]
        years = re.search(r"(\d{1,2})\s*(?:years?|yrs?)", c.value, re.I)
        proposal = {
            "action": c.name,
            "payload": c.profile.model_dump()
            if c.profile
            else {
                "summary": c.value,
                "skills": skills,
                "experience_years": int(years.group(1)) if years else None,
                "remote": bool(re.search(r"\bremote\b", c.value, re.I)),
            },
        }
        message = "Extracted profile fields need your approval."
        ranked = []
    elif c.name == "compare_roles":
        ranked = ranked[:2]
        message = "Compare the skills and locations of these two synthetic roles."
    elif c.name == "explain_recommendation":
        message = "Ranking uses exact token overlap with your query and stored preferences; ties use job ID. This is not an LLM judgement."
    return {
        "result": {
            "mode": "provider-backed"
            if os.getenv("AGENT_MODE") == "provider" and not s["text"].startswith("/")
            else "deterministic-offline",
            "tool": c.name,
            "message": message,
            "jobs": ranked,
            "proposal": proposal,
            "trace": s["trace"]
            + ["choose_typed_tool", "execute_read_or_propose_write"],
        }
    }


def validate(s):
    result = ToolResult.model_validate(s["result"])
    result.trace += [
        "validate_output: Pydantic",
        "approval_boundary: writes deferred",
        "respond",
    ]
    entry = {"call": s["call"], "output": result.model_dump()}
    return {
        "result": result.model_dump(),
        "results": s.get("results", []) + [entry],
        "cursor": s["cursor"] + 1,
    }


def route(s):
    return (
        "respond"
        if s["result"]["proposal"] or s["cursor"] >= len(s["calls"])
        else "choose"
    )


def respond(s):
    result = s["result"].copy()
    result["steps"] = s["results"]
    result["trace"] = [
        step for entry in s["results"] for step in entry["output"]["trace"]
    ]
    return {"result": result}


builder = StateGraph(State)
for name, fn in [
    ("parse", parse),
    ("retrieve", retrieve),
    ("choose", choose),
    ("execute", execute),
    ("validate", validate),
    ("respond", respond),
]:
    builder.add_node(name, fn)
builder.add_edge(START, "parse")
builder.add_edge("parse", "retrieve")
builder.add_edge("retrieve", "choose")
builder.add_edge("choose", "execute")
builder.add_edge("execute", "validate")
builder.add_conditional_edges(
    "validate", route, {"respond": "respond", "choose": "choose"}
)
builder.add_edge("respond", END)
graph = builder.compile()
