"""Streamable HTTP app: FastMCP's transport plus a request-size limit.
Auth (bearer token) is configured on the FastMCP server; Host/Origin checks
(DNS-rebinding protection) use FastMCP's built-in guard."""
from starlette.middleware import Middleware
from starlette.responses import PlainTextResponse

from .config import Config


class BodySizeLimit:
    """Reject request bodies larger than max_bytes (413)."""

    def __init__(self, app, max_bytes: int):
        self.app, self.max_bytes = app, max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        for k, v in scope.get("headers", []):
            if k == b"content-length" and v.isdigit() and int(v) > self.max_bytes:
                return await PlainTextResponse("Request body too large", 413)(scope, receive, send)
        seen = 0

        async def limited():
            nonlocal seen
            msg = await receive()
            if msg["type"] == "http.request":
                seen += len(msg.get("body", b""))
                if seen > self.max_bytes:
                    raise ValueError("Request body too large")
            return msg

        return await self.app(scope, limited, send)


def build_http_app(cfg: Config, mcp):
    return mcp.http_app(
        path=cfg.http_path,
        middleware=[Middleware(BodySizeLimit, max_bytes=cfg.max_request_bytes)],
        host_origin_protection=True,
        allowed_origins=list(cfg.allowed_origins) or None,
    )
