# Security scope

Local demo only; bind to 127.0.0.1. Tokens and database URLs belong in process environment or ignored .env files. No credentials or resumes were used as fixtures. Browser rendering uses textContent rather than HTML injection. SQL parameters are bound, not concatenated from input.

PrefLoom sessions store token hashes. Preference/profile writes from the agent create approval records; an authenticated approval endpoint applies them. User IDs are not accepted as authority from request bodies. Direct forgetting is an explicit authenticated user action.

DeltaIndex/EvalTrace use a single operator token; they are not multi-tenant systems. No internet-facing auth, TLS termination, account recovery or key rotation is supplied. EvalTrace HTTP target URLs are restricted to loopback and redirects are disabled. Dataset content may contain sensitive text: use only synthetic fixtures until access/retention policies are implemented.

Do not deploy publicly without authentication review, resource/request limits, concurrency tests, backups, dependency scanning and required PostgreSQL integration checks. No production security certification is claimed.
