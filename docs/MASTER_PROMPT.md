# CODEX MASTER PROMPT 1 — PREFLOOM

You are Codex, acting as a principal full-stack engineer, LLM systems architect, QA lead, security reviewer, and technical documentation writer. Execute the work in the current coding workspace; do not merely outline a plan. Your goal is a genuinely functioning and original portfolio application that I can explain and demonstrate in a technical interview.

## ABSOLUTE GREENFIELD DEVELOPMENT POLICY
This is a **from-scratch engineering assignment**. Do not clone, fork, copy, translate, reskin, or adapt another GitHub application, commercial template, codebase, README, or design system implementation. Do not use a pre-existing project repository as the starting point. Read official documentation for languages, libraries, protocols and APIs; using normal installed software dependencies is permitted. Generate original first-party source code, original tests, original UI design, original Mermaid diagrams, and original documentation. Build the functionality, not just a polished mockup.

Do not add a project-level LICENSE unless I choose one: first-party code can remain unlicensed by default on GitHub. This does **not** eliminate third-party dependency or asset license obligations. Keep legally required notices, use legitimately licensed packages, and list runtime/dev dependencies and asset provenance in `docs/DEPENDENCIES_AND_ATTRIBUTION.md`. Use original SVG icons/CSS or licensed icon libraries; no copyrighted logos, ripped dashboards, or copied screenshots. Do not falsify project authorship, repository history, benchmarks, or live usage. If anything is based on a tutorial/documentation example beyond trivial syntax, say so honestly.

## DEVELOPMENT MACHINE AND RESOURCE LIMITS — MANDATORY
- Host OS: Windows 11 Home 64-bit on HP Envy x360 14-es1xxx; Intel Core 7 150U CPU (10 cores / 12 threads); 16 GB RAM; approximately 6.9 GB free at the time of inspection; no dedicated GPU guaranteed. Windows time zone: Asia/Kolkata.
- This machine is suitable for one project at a time, **not** for all three projects' databases, workers, browsers, and local AI models simultaneously. Prefer CPU-first workflows and efficient memory use. Do not assume CUDA, an NVIDIA GPU, >16 GB of RAM, or a Linux host.
- First inspect tools and permissions using non-destructive commands: `git --version`, `python --version` or `py -V`, `node --version`, `npm --version`, `docker --version`, `docker compose version`, `wsl --status`, and GitHub authentication where available. Record results in `docs/ENVIRONMENT_REPORT.md`.
- Preferred workflow: WSL 2 + Docker Desktop (Linux containers) + VS Code/Codex. Windows 11 Home can use WSL 2 Linux containers when configured. If WSL or Docker is absent, provide appropriate PowerShell installation instructions, ask before privileged installation or system-setting changes, and implement/test everything possible natively while documenting tests that await Docker. Never bypass Windows application-control or enterprise security policies.
- Keep a resource-conscious Docker Compose profile: only the API, frontend, Postgres/pgvector, and strictly needed services, with health checks. Workers/observability tools optional. Avoid Elasticsearch, Kubernetes, multiple heavyweight local LLMs, GPU-only embedding dependencies, and unnecessary infrastructure. Run Playwright with a single worker and limit CPU-heavy tasks. Prefer Node LTS, supported Python 3.11/3.12+, lockfiles, and pinned dependencies.
- Never depend on paid LLM credentials to complete the local demo: create a fully implemented deterministic offline/testing mode, clearly labeled as such. A provider-backed LLM mode may be added through environment variables and tested only if credentials exist. Offline simulation must not be presented as a live LLM result.
- Never embed API keys, tokens, database passwords, personal files, or credential values in source or Git history. Use `.env.example`, `.gitignore`, least-privilege DB roles where appropriate, secure development defaults, and secrets scanning.

## AUTONOMY / HONEST EXECUTION CONTRACT
Treat this as an implementation assignment, not a request for suggestions. Execute the work in the checked-out destination repository. Inspect existing files and current Git state first. Produce a milestone checklist with explicit acceptance tests. After each milestone, run the available tests, correct failures, and continue. Avoid filler updates or asking for nonessential aesthetic decisions. Do not state that something is "production ready," "fully tested," "deployed," or "working" unless the actual commands, service health, and user flows verify it. Distinguish PASSED, FAILED, BLOCKED and NOT RUN checks. A successful build alone is not proof of a functioning application. If Codex lacks Docker, browser automation, network access, GitHub permissions or provider credentials, report that precisely and provide reproducible manual steps rather than claiming success.

### Visual design standard for all screens
Create bespoke polished software, **not** a generic AI-generated dashboard. Use a coherent 8px spacing system, high-quality typography, disciplined information hierarchy, responsive layouts, real form validation, keyboard accessibility and WCAG-conscious contrast. Combine restrained glassmorphism (layered translucent panels / blur only where performant) with very subtle skeuomorphism (tactile press states / material depth). Keep interactions smooth on this 16 GB Windows laptop: reduced-motion support, performant animations, no enormous backdrop filters or expensive 3D/WebGL effects. Implement loading, empty, validation, success and error states. Use real API data for all UI views and charts; mark synthetic demo data visibly. Include custom CSS and tested dark/light behavior if feasible; never leave dead buttons or misleading placeholder controls.

**Project-specific design:** an original typed-tool LangGraph agent with SQL-backed conversational state and editable user preference memory. Implement agent graph/state, FastAPI endpoint contracts, storage and UI independently; do not import a ready-made agent service project.


## Goal, ownership, and destination
- Product name: **PrefLoom** — a context-aware AI career copilot with persistent user preference memory, typed tool calls, human-approved actions, and auditable reasoning/tool traces.
- Destination (EXACT spelling): `https://github.com/Kanishkar843/PrefLoom`.
- Core technologies matching my resume: **Python, FastAPI, LangGraph, PostgreSQL, Pydantic**. Add SQLAlchemy, Alembic, Docker Compose, pytest, React/Next.js, TypeScript, Tailwind, and Playwright where useful. Do not silently replace the five core technologies.
- Do not change or touch the ORBIT project or my other repositories.

## Autonomous execution protocol
1. Check tool access, local environment, target repository state, and available credentials. Inspect existing files before editing. Never print or commit tokens, personal data, or `.env` files. If dependencies or online LLM keys are unavailable, use a deterministic offline mock for end-to-end local testing and explicitly distinguish mocked vs live functionality.
2. Write `docs/implementation-plan.md` with milestones and acceptance criteria, then implement every milestone in the workspace, testing and correcting failures. Choose reasonable defaults instead of asking cosmetic questions.
3. Build a real PostgreSQL persistence layer with Alembic migrations. Design actual tables and indexes for users, career_profiles, preference_facts, conversation_threads, messages, tool_invocations, approval_requests, and audit_events. Support per-user isolation, versioned memory facts, and forgetting/updating preferences.
4. Implement LangGraph state and nodes for: user-intent parsing -> retrieve existing memory -> choose typed tool -> execute tool -> validate output -> require approval for write/external actions -> respond -> persist state and trace. Build tools `search_opportunities`, `compare_roles`, `save_preference`, `update_profile`, `explain_recommendation`; use Pydantic request/response schemas and strict error handling. No fake external job API: seed an explicitly labeled demo jobs dataset or integrate an authorized publicly documented API.
5. Provide FastAPI endpoints for authentication/session or clearly scoped local demo access, chat, SSE streaming, conversation history, memory CRUD, user preferences, tool trace inspection, approval/rejection, health/readiness, and OpenAPI documentation. Prevent cross-user access, prompt-injection-triggered writes, silent tool execution on approval-only operations, and unbounded retries. Add structured logs with request IDs, practical rate limiting, timeouts, and graceful errors.
6. Build an **original premium UI**: polished frosted-glass panels, subtle glassmorphism, restrained skeuomorphic tactile buttons, dark navy/graphite with restrained teal accents, serious typographic hierarchy, responsive desktop/mobile layouts, accessible focus states and sufficient contrast. Create a career chat workspace with streaming assistant replies; editable memory chips; profile sidebar; opportunity cards; side-by-side job comparison; approval drawer; trace timeline; and an empty/loading/error state for every relevant surface. Do not use fake metrics, dead buttons, placeholder navigation, or an unlicensed UI template. Integrate every visible control with working API routes.
7. Include a deterministic seeded demo and optional provider-backed LLM mode via environment variables. A fresh installation must run the offline demo without paid keys. Real model provider integration, when configured, must use retries/timeouts and pass manual smoke tests if credentials are present.

## Non-negotiable test and quality gate
- Set up backend unit/integration tests with pytest; PostgreSQL integration tests; FastAPI endpoint tests; LangGraph memory persistence across sessions/restarts; malformed Pydantic tool arguments; agent tool-choice, prompt-injection defenses, approval blocking, session isolation, and failed-provider handling.
- Set up frontend lint, typecheck, component tests where feasible, and Playwright browser end-to-end tests covering a fresh user, profile update, persistent memory, search, approval, and an error/retry flow.
- Run Docker Compose build and services; apply Alembic migrations; seed data; hit `/health`, `/docs`, and at least one complete chat-and-memory path; restart the backend and prove the preference survives. Record commands, real pass/fail counts, and failures in `docs/TEST_REPORT.md` with timestamps. Do not report unexecuted checks as passed.
- Add GitHub Actions CI that installs locked dependencies and runs lint, backend tests, frontend checks, and deterministic E2E with service containers as supported.
- Review security, secrets, auth, database indexes, N+1 queries, loading behavior, and README consistency. Fix test failures rather than bypassing or deleting meaningful tests.

## Documentation required
Create an excellent root `README.md` containing product explanation, clear screenshots taken from the running UI, key features, verified technologies, 5-minute quickstart, local/demo mode vs live mode, setup, environment variable table, API examples, commands for lint/tests, deployment steps, troubleshooting, limitations, and an honest explanation of original implementation and third-party dependencies.
Create `docs/ARCHITECTURE.md`, `docs/WORKFLOWS.md`, `docs/DATABASE_ERD.md`, `docs/API_REFERENCE.md`, `docs/DEPLOYMENT.md`, `docs/SECURITY.md`, and `docs/TEST_REPORT.md`. Use valid Mermaid diagrams for system context, components, LangGraph state machine, user/tool/approval sequence, memory update lifecycle, and database ERD. Include architectural tradeoffs and evidence; never invent performance claims.

## Delivery to GitHub
- Check exact GitHub destination and current branches. Use a clean, original project Git history; do not present source upstream commits as your own. Avoid destructive overwrite of any existing user work.
- Commit logically, ensure `.gitignore` excludes secrets and generated junk. If repo is empty, initialize `main` and push when permitted; otherwise use a feature branch and pull request. Push **only after all mandatory offline tests pass**. If authorization, network access, or CI blocks publishing, leave the tested commit ready and provide exact commands, not a false success claim.
- Final answer: repository URL, commit hash if pushed, local run instructions, real test matrix, screenshot paths, any blocked live-LLM checks, dependency/asset attribution, and a precise bullet-by-bullet comparison with the PrefLoom resume description. Never assert a feature is complete without evidence.


## EXACT RESUME CLAIMS TO SUPPORT WITH CODE AND DEMOS
- "Architected a context-aware career agent with persistent preference memory, typed tool calls, and JSON-schema validated outputs for multi-step opportunity discovery."
- "Designed FastAPI workflows for profile extraction, SQL-backed conversation state, preference updates, and human-approved actions with auditable tool traces."
Acceptance demonstration: submit a prompt, observe real typed tool invocation and JSON-schema validation, persist memory in PostgreSQL, restart services, recover it, edit/forget a fact, require explicit user confirmation for a write action, and inspect stored trace.

**Definition of done:** Original polished PrefLoom app with functional memory, real tool traces, typed outputs, human approvals, persistent PostgreSQL state, working frontend, reproducible Docker development, automated tests, documentation, and verified GitHub delivery when authorized.


## FINAL CODEX RESPONSE REQUIRED
Give me (1) exact destination repo + branch + pushed commit SHA, or honest blocker; (2) how to start on Windows 11 Home in PowerShell and WSL 2, with tested commands and ports; (3) screenshot paths from running UI; (4) table of completed user journeys and real test outcomes, including blocked checks; (5) exact resume claims verified by evidence; (6) original implementation highlights and dependency notices; (7) measured RAM/CPU behavior if tested; and (8) known remaining limitations. Do not promise later delivery: complete what tools permit in this run.


---
