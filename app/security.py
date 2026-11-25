"""HTTP boundary controls; no credentials, request bodies, or paths are logged."""

import json
from uuid import uuid4


class SecurityBoundary:
    def __init__(self, app, max_body=65536):
        self.app = app
        self.max_body = max_body

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        request_id = str(uuid4())
        headers = [
            (b"x-request-id", request_id.encode()),
            (b"x-content-type-options", b"nosniff"),
            (b"referrer-policy", b"no-referrer"),
            (b"x-frame-options", b"DENY"),
            (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
            (b"cache-control", b"no-store"),
            (
                b"content-security-policy",
                b"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
            ),
        ]

        async def secure_send(message):
            if message["type"] == "http.response.start":
                names = {name for name, _ in headers}
                message["headers"] = [
                    (k, v)
                    for k, v in message.get("headers", [])
                    if k.lower() not in names
                ] + headers
            await send(message)

        chunks = []
        size = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body = message.get("body", b"")
            size += len(body)
            if size > self.max_body:
                payload = json.dumps({"detail": "Request body too large"}).encode()
                await secure_send(
                    {
                        "type": "http.response.start",
                        "status": 413,
                        "headers": [(b"content-type", b"application/json")],
                    }
                )
                await secure_send({"type": "http.response.body", "body": payload})
                return
            chunks.append(body)
            if not message.get("more_body", False):
                break
        consumed = False

        async def bounded_receive():
            nonlocal consumed
            if not consumed:
                consumed = True
                return {
                    "type": "http.request",
                    "body": b"".join(chunks),
                    "more_body": False,
                }
            return await receive()

        await self.app(scope, bounded_receive, secure_send)
