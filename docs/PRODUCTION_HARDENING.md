# Production hardening audit â€” 2026-11-25

Scope: existing application; dedicated branch `feat/production-hardening`. Historical CI and screenshots are not current security acceptance evidence.

## Findings

Anonymous demo bearer sessions previously reached provider inference. Missing leases were accepted. Approval resolution has transactional ownership checks, but expiry/cancellation and full managed identity are missing.

| Area | Audit classification | Evidence / outstanding work |
|---|---|---|
| Existing React pages and exports | partially implemented | Existing distinct designs preserved; account/settings/error experiences missing |
| Managed account lifecycle | missing | No managed auth configuration found during environment-name inspection |
| Personal authorization | partially implemented | PrefLoom scopes local sessions; DeltaIndex/EvalTrace use a shared operator boundary |
| PostgreSQL persistence | partially implemented | Schema and prior integration reports exist; this hardening branch needs isolated migration and tenancy validation |
| External integrations | partially implemented | Real provider/search implementations exist; quotas and ownership need verification |
| Production readiness | blocked | Managed auth, preview isolation and two-user deployed acceptance not established |

## Trust boundaries and architecture

Browser input and model output are untrusted. API identity must come from a managed provider, never client ownership claims. Database and provider credentials stay server-side. Each application retains a separate database and account realm. Managed Neon Better Auth is the proposed provider matching existing infrastructure; provisioning and SDK integration remain pending. A configured Auth URL alone is not authentication verification.

Preview databases and provider configuration must be separate from production. Do not deploy this branch to production while acceptance gaps remain. No production data migration or deletion is authorized by this report.

## Implementation order

1. Close anonymous costly access; enforce request bounds and private cache controls.
2. Integrate managed sessions and lifecycle screens, validate revocation and callbacks.
3. Add additive ownership migrations and server-side authorization to all resources, caches and jobs.
4. Implement project-specific approval/ingestion/evaluation state guarantees and distributed quotas.
5. Validate isolated PostgreSQL, two-user browser journeys, preview environment and recovery.
6. Record dependency/security checks, operational evidence, rollout and rollback instructions; open reviewable PR.

## Permission target (not yet fully implemented)

Public visitors: landing only. Authenticated owners: own records, exports and operations within quotas. Operators: explicitly granted maintenance actions, without implicit access to private user data. Deny unknown roles and resources. No collaboration roles are needed for the present personal-user product.

## Deployment hold

Current live deployment is unchanged. No new security claim is made for it. Production rollout requires the managed-provider lifecycle, cross-user isolation, quota controls and deployed acceptance tests to pass. Backup availability, restore exercises and alerts are unverified.

## Verified first implementation slice

PrefLoom only: anonymous sessions now fail closed on Vercel and whenever provider mode is enabled, including already-issued demo tokens. Missing session leases are rejected. User/profile/session creation commits atomically. Approval decisions reject extra parameters and coerced boolean strings; profile actions are schema-validated at execution. HTTP middleware caps received bodies at 64 KiB, including chunked requests, and adds no-store, CSP, framing and MIME protections. CSP presently allows same-origin connections only; managed auth must be integrated and browser-tested before rollout. Vercel static CDN headers still need separate configuration.

Commands run on 2026-11-25:

- `.venv/Scripts/python.exe -m pytest tests -q`: 18 passed (SQLite and controlled provider fixture; not real provider verification).
- `.venv/Scripts/python.exe -m ruff check app tests --select E9,F63,F7,F82`: passed.
- `npm run typecheck --prefix frontend`: passed.
- `npm run lint --prefix frontend`: passed.
- `npm run test --prefix frontend`: 4 passed.
- `npm run build --prefix frontend`: passed.
- `.venv/Scripts/python.exe tests/browser_journey.py`: passed, local isolated SQLite with real Chromium; screenshots regenerated.

This branch intentionally cannot serve deployed private workflows until managed auth is implemented. Do not publish it as a completed release. Existing live deployment remains unchanged. Distributed quotas, approval lifecycle expansion, retention and managed identity remain outstanding.

Neon console SSO was reached through the signed-in Vercel account. Console access is blocked by Neon account email activation, which the account holder must complete. No auth resources or production data were changed.

## 2026-11-27 incremental verification

Added a 15-second total request-body deadline (HTTP 408) alongside the existing 64 KiB cap. Response correlation IDs now match server request logs. Slow-upload rejection and log correlation are covered by automated tests.

Validation: `python -m pytest tests -q` — 20 passed; `python -m ruff check app tests --select E9,F63,F7,F82` — passed; `git diff --check` — passed. These are local tests, not deployed or real-provider acceptance.

GitHub CLI CI lookup failed certificate verification (unknown certificate authority). Certificate validation was not disabled. Neon setup remains pending browser access; no production changes were made.
