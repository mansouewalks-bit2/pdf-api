"""API Key authentication middleware."""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from database import get_key_info, hash_key
from models import PLAN_LIMITS


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Extract and validate API key from X-API-Key header."""

    EXEMPT_PATHS = {"/", "/docs", "/openapi.json", "/redoc", "/health", "/api/v1/generate-key", "/stripe/webhook"}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip auth for non-API routes and static files
        if path in self.EXEMPT_PATHS or path.startswith("/static") or not path.startswith("/api/"):
            response = await call_next(request)
            return response

        api_key = request.headers.get("X-API-Key")

        if api_key:
            key_info = await get_key_info(api_key)
            if not key_info:
                raise HTTPException(status_code=401, detail="Invalid API key")
            request.state.api_key = api_key
            request.state.key_hash = hash_key(api_key)
            request.state.plan = key_info["plan"]
            request.state.plan_config = PLAN_LIMITS[key_info["plan"]]
        else:
            # Free tier - no key required, limited by IP
            request.state.api_key = None
            request.state.key_hash = None
            request.state.plan = "free"
            request.state.plan_config = PLAN_LIMITS["free"]

        response = await call_next(request)
        return response
