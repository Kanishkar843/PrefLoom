# Resume verification checklist

| Claim | Code | Evidence status |
|---|---|---|
| Context-aware agent and persistent preference memory | app/agent.py, app/db.py | Native tests pass; PostgreSQL evidence recorded in TEST_REPORT |
| Typed tools and schema-validated multi-step discovery | ToolPlan, ToolCall, ToolResult, LangGraph conditional loop | Three-step discovery test passes; maximum plan length is five |
| Profile extraction | deterministic extractor and optional provider ProfileFields | Offline and mocked-provider approval tests pass; live provider requires credentials |
| SQL conversation state and preference revisions | messages, threads, preference_facts, memory_revisions | Native persistence/ownership tests pass; isolated process restart test uses PostgreSQL only |
| Human-approved actions and auditable traces | transactional pending-claim, user lock, audit and tool_invocations | Concurrent approval test proves one success and one conflict |

Do not describe a mocked provider test as live inference or a SQLite test as PostgreSQL validation. The current test report is the authority for executed acceptance commands.
