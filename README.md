# PrefLoom

A career workspace with SQL-backed preference memory and human-approved typed actions.

**Status: functional native demo, incomplete against the full master prompt.** This repository is original first-party code authored for this assignment. It is not a clone or reskin. No live data, production-readiness, PostgreSQL verification or successful GitHub publishing is claimed.

## Run on Windows

A project-local Python 3.12 virtual environment was created. From PowerShell 7:

```powershell
cd K:\Projects\PrefLoom
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. OpenAPI is at `/docs`. For DeltaIndex/EvalTrace, enter the same local token in the UI. Run one application at a time. Stop it with Ctrl+C before starting the next.

Fresh install (dependency resolution and app runs tested; fresh-machine bootstrap not tested):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pytest -q
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

Backend: **5 passed in 12.49s**. Commands: `python -m pytest -q`, `node --check app/static/app.js`. Read [test report](docs/TEST_REPORT.md), [environment report](docs/ENVIRONMENT_REPORT.md), and [architecture](docs/ARCHITECTURE.md).

## Deployment

Native mode uses SQLite explicitly. PostgreSQL is selected with `DATABASE_URL=postgresql+psycopg://...`. Copy `.env.example` to `.env`, choose local secrets and run `docker compose up --build` when Docker Desktop is available. This path is **NOT RUN** on this host. Never use literal sample credentials for a deployment. Services bind only to loopback in Compose.

WSL 2 instructions (NOT RUN; WSL is not installed): install WSL 2 and Docker Desktop with the user's approval, enable Linux containers, open `/mnt/k/Projects/PrefLoom`, and run `docker compose up --build`. Native Windows virtual environments cannot be reused inside Linux; create a Linux venv or use containers.

## Environment

| Variable | Meaning |
|---|---|
| DATABASE_URL | SQLAlchemy database URL; defaults to project-local SQLite demo file |
| ADMIN_TOKEN | Required for protected DeltaIndex/EvalTrace routes; never committed |
| POSTGRES_PASSWORD | Required by Docker Compose |
| EMBEDDING_MODE | DeltaIndex: fixture (default) or sentence-transformers |
| REDIS_URL | DeltaIndex: enable actual Redis cache |
| LOCAL_TARGET_URL | EvalTrace: loopback HTTP endpoint; no remote redirects |

## Limits and remaining acceptance work

- PostgreSQL integration, Docker builds and restart tests are blocked by missing infrastructure.
- The UI consumes SSE trace/result events; this deterministic mode does not stream generated LLM tokens.
- No provider-backed language model is implemented; parsing is deterministic and command-based.
- No React/TypeScript build; the original frontend is plain accessible HTML/CSS/JavaScript.
- Alembic initial migration imports current model metadata; freeze explicit operations before subsequent schema evolution.
- Concurrency race handling and production session lifecycle require additional work.

[Full requested specification](docs/MASTER_PROMPT.md) · [Dependency attribution](docs/DEPENDENCIES_AND_ATTRIBUTION.md) · [Security](docs/SECURITY.md)

Target repository: https://github.com/Kanishkar843/PrefLoom. Existing remote history was detected. Nothing has been pushed or overwritten. Mandatory offline infrastructure checks must pass before publishing a feature branch. There is intentionally no project LICENSE pending the owner's decision.

Browser check on this Windows host: install `requirements-browser.txt`, then run `python tests/browser_journey.py`. Uses the installed Chrome executable, a temporary synthetic demo database, and one browser context. It starts and stops its own API server.
