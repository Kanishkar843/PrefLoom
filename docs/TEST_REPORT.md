# PrefLoom executed acceptance report

Updated: 2026-11-22, Asia/Kolkata. These results supersede the initial native-demo report.

| Command / check | Actual result |
|---|---|
| `.venv/Scripts/python.exe -m pytest -q tests` | PASSED: 10 tests, 5.31 seconds |
| `pytest -q integration` with isolated TEST_DATABASE_URL | PASSED: 1 test, 10.99 seconds, PostgreSQL 17.12 |
| `npm run typecheck` | PASSED |
| `npm run lint` | PASSED, upgraded to supported ESLint |
| `npm run test` | PASSED: 4 tests |
| `npm run build` | PASSED: Vite 8.3.8 production bundle |
| `ruff check app tests integration --select E9,F63,F7,F82` | PASSED |
| `python tests/browser_journey.py` | PASSED: actual React UI in Chrome |
| Docker Compose runtime | PASSED: cached image build, healthy Compose startup, approval and conversation/memory persistence after API restart |
| Live provider | BLOCKED: no configured credentials; mock-provider checks are not live inference |
| GitHub CI | NOT RUN; no completed release published |

PostgreSQL acceptance applies frozen migrations, creates isolated demo sessions, rejects cross-user approval/history access, races two approvals and asserts [200,409], restarts only the test-owned API process, recovers memory/messages, executes a three-step graph and forgets the memory. It does not use SQLite.

Browser coverage: new session, memory proposal/approval, profile extraction/approval, multi-step search, reload persistence, injected 503 and retry, role comparison, memory version history, dark/light and 390px layout. No page errors or horizontal overflow. Screenshots: docs/assets/desktop.png, light.png, mobile.png.

A Windows HTTPX/certifi initialization failure (`OPENSSL_Applink`) was reproduced and corrected by using the operating system trust store. TLS verification was not disabled. Early failing attempts were not counted as passing integration tests. The provider adapter uses the same system trust context.

Docker acceptance output is recorded in docker-test-output.txt. Earlier image builds failed on network download timeouts; a complete cached dependency layer allowed a successful final build without further downloads. The host acceptance HTTP client needed the same truststore fix as the provider. Docker runs the full pinned dependency set, including test tools; requirements-runtime.lock is an optional minimal dependency inventory, not the current Docker build input.

No RAM/CPU benchmark or live LLM latency is claimed for PrefLoom. Test servers are isolated from existing user instances.
