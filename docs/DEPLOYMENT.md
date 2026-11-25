# Windows and Docker setup

Use Python 3.12, Node 22, and one project stack at a time. Install dependencies using the README commands and build `frontend` before starting Uvicorn. Native default storage is SQLite; `DATABASE_URL` selects PostgreSQL and requires `alembic upgrade head` first.

WSL and Docker Desktop were installed with authorization. No automatic Windows restart or security-policy bypass occurred. WSL 3.0.5 / Linux kernel 6.18.58 and Docker Engine 29.9.3 are operational on this host. Local portable PostgreSQL 17.12 acceptance ran separately from Docker.

Set a strong `POSTGRES_PASSWORD` in an ignored `.env`, then run:

```powershell
docker compose build
docker compose up -d --wait
$env:ACCEPTANCE_URL='http://127.0.0.1:8000'
$env:COMPOSE_PROJECT_NAME='prefloom'
python tests/compose_acceptance.py
docker compose down
```

Use the same Compose project name for every command (or set `COMPOSE_PROJECT_NAME` before starting). Omit `-v` to retain data. The API is nonroot, binds on loopback externally, has a readiness check, and applies Alembic before startup. PostgreSQL has no public host port. Container limits are 512MB database / 768MB API.

On networks requiring an enterprise certificate, export only trusted public CA certificates to a PEM outside this repository, set `BUILD_CA_FILE`, and add `-f compose.yaml -f compose.trust.yaml` to build. BuildKit mounts it temporarily; TLS verification remains enabled. Do not include private keys or commit a machine trust bundle. Pip allows a 120-second download timeout and bounded retries.

The acceptance script creates a disposable demo session and restarts only the specified project's API. Never point it at a production stack. Current executed evidence is in TEST_REPORT.md. Publication uses a feature branch preserving existing remote history; never force-push main.
