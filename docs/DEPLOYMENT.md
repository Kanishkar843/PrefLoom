# Deployment status

Native startup: see README. Port: 8000. Python used for tests: 3.12.12. `docker compose up --build` is supplied but NOT RUN because Docker/WSL are unavailable. `docker compose down` stops services; omit `-v` to retain data.

Required integration sequence: build images; start DB; run `alembic upgrade head`; call `/health` and `/docs`; execute the product workflow; stop/restart API; assert data survived; run database-specific tests. Do not publish until these checks pass.

Existing GitHub destination: Kanishkar843/PrefLoom. Remote HEAD was detected; no push occurred. To preserve existing history, review the remote, fetch it and prepare an integration branch/PR after acceptance checks. Do not force-push this new local history over the existing repository.

No privileged system changes were made. WSL installation would use `wsl --install` in an authorized Administrator PowerShell followed by the required reboot; Docker Desktop setup and WSL integration must then be completed by an authorized user. These steps were not executed.
