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

Protected routes use `Authorization: Bearer <session-token>`. `POST /sessions` returns a random bearer credential once. Only its hash is stored. Session leases expire after seven days; `DELETE /sessions/current` revokes the current session. Ownership is checked for memory, threads, messages, approvals, and traces. `GET /memory/{id}/versions` returns the current user's revision history. `/ready` checks database readiness.

Example request bodies:

```json
{"text":"discover and compare python roles"}
```

```json
{"approved":true}
```

`POST /chat` returns the response, thread ID, typed plan and executed steps, with an approval ID for a proposed write. `POST /chat/stream` emits structured server-sent events. An approval from a different user returns 404; a duplicate completed approval returns 409. Invalid inputs return 422. Provider failures return a sanitized 503. `/docs` and `/openapi.json` expose parameter schemas. Tokens belong in headers, never URL parameters.
