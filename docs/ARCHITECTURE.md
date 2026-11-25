# PrefLoom architecture

PrefLoom separates planning from authorized state changes. Both the deterministic planner and optional provider planner return a Pydantic `ToolPlan` of at most five calls. LangGraph executes read tools in sequence and stops as soon as a call proposes a write. The approval endpoint claims a pending request transactionally, serializes changes for the user, applies the change, and writes an audit event in the same transaction.

```mermaid
flowchart LR
    UI[React and TypeScript] --> API[FastAPI]
    API --> Graph[LangGraph bounded plan]
    Graph --> Offline[Deterministic planner]
    Graph --> Provider[Optional HTTPS LLM planner]
    Graph --> Tools[Typed read tools and write proposals]
    API --> Approval[Approval transaction]
    Approval --> SQL[(PostgreSQL)]
    API --> SQL
    Graph --> Trace[Validated tool evidence]
    Trace --> SQL
```

```mermaid
stateDiagram-v2
    [*] --> ParsePlan
    ParsePlan --> RetrieveMemory
    RetrieveMemory --> ChooseTool
    ChooseTool --> Execute
    Execute --> Validate
    Validate --> ChooseTool: more read steps
    Validate --> Respond: plan finished
    Validate --> Respond: write proposal needs approval
    Respond --> PersistConversation
    PersistConversation --> [*]
```

```mermaid
sequenceDiagram
    actor User
    participant UI
    participant API
    participant Graph
    participant DB as PostgreSQL
    User->>UI: Describe profile or preference
    UI->>API: Authenticated chat
    API->>Graph: User-scoped memory and request
    Graph-->>API: Schema-validated proposal
    API->>DB: Persist message, invocation and pending approval
    API-->>UI: SSE trace and result
    User->>UI: Approve
    UI->>API: Decision for approval ID
    API->>DB: Claim pending row, lock user, apply revision, audit
    DB-->>API: Commit
    API-->>UI: Applied once
```

## Persistence and isolation

Tables include users, career_profiles, preference_facts, conversation_threads, messages, tool_invocations, approval_requests, audit_events, memory_revisions and session_leases. Tokens are random and only their SHA-256 digests are stored. New sessions expire after seven days and can be revoked. User ownership filters are applied to threads, memories, approvals and traces. Forgetting deletes current memory and its version history; the audit retains only the fact ID.

Migrations contain frozen operations independent of runtime models. Native SQLite remains an explicitly labeled convenience mode. PostgreSQL integration evidence is reported separately and is never inferred from SQLite tests.

## Provider contract

Set AGENT_MODE=provider, LLM_BASE_URL, LLM_MODEL and LLM_API_KEY. The adapter performs actual HTTPS inference using the OpenAI-compatible chat-completions protocol with JSON Schema output. A maximum of three attempts and per-request connect/read timeouts bound failures. No provider response can grant approval. Provider-produced profile fields are validated and stored only after the user approves. Provider failures produce a sanitized 503 response. The test suite mocks provider transport; live execution requires supplied credentials and is marked separately.

## Deliberate limits

The offline planner uses explicit deterministic rules and synthetic jobs. It is not an LLM simulation presented as live inference. The demo has no external action tools. SSE carries actual trace/result events; it does not expose private model reasoning. Multi-instance rate limiting and consumer identity verification are outside this local demo's auth scope. The UI and API share one origin and no heavyweight worker infrastructure is needed.
