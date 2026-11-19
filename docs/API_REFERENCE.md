# API reference

Open `/docs` for generated parameter and response contracts.

- `/health`
- `POST /sessions`
- `POST /chat`
- `POST /chat/stream`
- `GET /threads`
- `GET /threads/{id}/messages`
- `GET/POST /memory`
- `DELETE /memory/{id}`
- `GET /profile`
- `GET /approvals`
- `POST /approvals/{id}`
- `GET /traces`

Protected routes use `Authorization: Bearer <local-token>`. PrefLoom creates opaque demo session tokens at POST /sessions and scopes data by the authenticated user. DeltaIndex/EvalTrace are single-operator local tools using ADMIN_TOKEN, not multi-tenant services. Never put credentials in query parameters.
