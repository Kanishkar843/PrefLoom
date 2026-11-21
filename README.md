# PrefLoom

A career workspace with SQL-backed preference memory and human-approved typed actions.

**Status: native and PostgreSQL workflows verified; Docker startup/restart verified; live-provider credentials are unavailable.** This repository is original first-party code authored for this assignment. It is not a clone or reskin. No live job data, production-readiness or successful GitHub publishing is claimed.

## React frontend setup

```powershell
npm ci --prefix frontend
npm run build --prefix frontend
```

The API serves the compiled React frontend. The preserved original interface is at `/legacy`. For development, run `npm run dev --prefix frontend` after starting the API.

## Run on Windows

A project-local Python 3.12 virtual environment was created. From PowerShell 7:

```powershell
cd K:\Projects\PrefLoom
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. OpenAPI is at `/docs`. Run one application at a time. Stop it with Ctrl+C before starting the next.

Fresh install (dependency resolution and app runs tested; fresh-machine bootstrap not tested):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pytest -q tests
```

## Implemented

- LangGraph intent, retrieval, execution and Pydantic validation nodes
- Hashed bearer demo sessions and per-user query scoping
- Preference proposal, approval/rejection, version increments and forgetting
- Stored conversations, tool invocation records and audit events
- Synthetic opportunity search, comparison, ranking explanation and SSE endpoint

## Screenshots

Browser-captured screenshots, if successful, are under `docs/assets/desktop.png`, `light.png` and `mobile.png`. See TEST_REPORT for the actual browser result; these are not design mockups.

## Tests and evidence

Backend: **10 native tests and one real PostgreSQL acceptance test passed**. Commands: `python -m pytest -q tests`, `npm run typecheck --prefix frontend`, `npm run lint --prefix frontend`, `npm test --prefix frontend`. Run the explicit real-service suite separately with `TEST_DATABASE_URL`: `python -m pytest -q integration`. Read [test report](docs/TEST_REPORT.md), [environment report](docs/ENVIRONMENT_REPORT.md), and [architecture](docs/ARCHITECTURE.md).

## Deployment

Native mode uses SQLite explicitly. PostgreSQL is selected with `DATABASE_URL=postgresql+psycopg://...`. Copy `.env.example` to `.env`, choose local secrets and run `docker compose up --build` when Docker Desktop is available. This path passed isolated Compose startup and restart-persistence acceptance on this host. Never use literal sample credentials for a deployment. Services bind only to loopback in Compose.

WSL and Docker Desktop are installed and the Linux engine is running. Open `/mnt/k/Projects/PrefLoom` in WSL, set local secrets, and run `docker compose up --build`. See the executed acceptance status below. Native Windows virtual environments cannot be reused inside Linux; create a Linux venv or use containers.

## Environment

| Variable | Meaning |
|---|---|
| DATABASE_URL | SQLAlchemy database URL; defaults to project-local SQLite demo file |
| POSTGRES_PASSWORD | Required by Docker Compose |
| AGENT_MODE | offline (default) or provider |
| LLM_BASE_URL / LLM_MODEL / LLM_API_KEY | Optional HTTPS provider endpoint, model and secret |

## Acceptance status

- PASSED: 10 native backend tests, 1 real PostgreSQL integration test including API restart and concurrent approvals.
- PASSED: React/TypeScript typecheck, ESLint, 4 frontend tests, Vite production build and browser workflow (including error/retry, dark/light and mobile).
- IMPLEMENTED: optional real HTTPS provider planner and semantic structured profile extraction; live-provider smoke test is BLOCKED because credentials are not configured. Mocked transport tests are identified as such.
- PASSED: Docker image build, Compose readiness, approval gating and persisted conversation/memory after API restart. No Windows restart was performed.
- NOT RUN: GitHub Actions; feature branch and pull request are published; see linked CI for current status.

[Full requested specification](docs/MASTER_PROMPT.md) · [Dependency attribution](docs/DEPENDENCIES_AND_ATTRIBUTION.md) · [Security](docs/SECURITY.md)

Target repository: https://github.com/Kanishkar843/PrefLoom. Existing remote history was detected. The verified feature branch is pushed; existing main history is preserved. There is intentionally no project LICENSE pending the owner's decision.

Browser check on this Windows host: install `requirements-browser.txt`, then run `python tests/browser_journey.py`. Uses the installed Chrome executable, a temporary synthetic demo database, and one browser context. It starts and stops its own API server.

## Optional real provider

Set `AGENT_MODE=provider`, `LLM_BASE_URL=https://api.openai.com/v1`, `LLM_MODEL` and `LLM_API_KEY` through environment variables. The provider returns a schema-validated plan of up to five calls; generated profile fields remain proposals. Keep credentials out of files and Git. HTTPS uses the system trust store. Requests have timeouts and at most three attempts. Without credentials, use the default deterministic offline mode; no live inference result is claimed for that mode.

## GitHub delivery

Published branch: `feat/verified-agent-react`. [Review pull request](https://github.com/Kanishkar843/PrefLoom/pull/1) · [Current CI results](https://github.com/Kanishkar843/PrefLoom/actions). Main was not force-pushed or overwritten. Local acceptance evidence is recorded separately from GitHub checks.
