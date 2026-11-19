# Test report

Date: 2026-11-20, Asia/Kolkata.

| Check | Status | Evidence |
|---|---|---|
| Native pytest | PASSED | 5 passed in 12.49s |
| JavaScript syntax | PASSED | node --check app/static/app.js |
| PostgreSQL integration | BLOCKED | No running PostgreSQL service provisioned |
| Docker/Compose build and workflow | BLOCKED | Docker not available; WSL not installed |
| Provider model checks | NOT RUN | No live provider mode executed |
| CI execution | NOT RUN | No push |
| GitHub publication | BLOCKED | Full mandatory offline checks have not passed |
| RAM/CPU benchmark | NOT RUN | No resource-performance claims |

Native pytest checks are reproducible from README. Browser results are appended after execution. This report distinguishes software tests from the expected failure of EvalTrace's regressed release gate.

## Browser and migration evidence

- PASSED: one sequential Playwright journey in installed Chrome, 1440px desktop and 390px mobile, dark/light screenshots, no uncaught page errors, no horizontal mobile overflow.
- Screenshots: docs/assets/desktop.png, docs/assets/light.png, docs/assets/mobile.png.
- PASSED: native SQLite `python -m alembic upgrade head`; this does not verify PostgreSQL.
- Browser verified proposal/approval, stored memory after reload, synthetic search and streamed trace/result response.
- PASSED: source scan for private-key and common provider/GitHub-token prefixes found no matches. This is a limited pattern scan, not a full security audit.
