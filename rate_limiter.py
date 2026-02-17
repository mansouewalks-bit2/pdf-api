"""Rate limiting using SQLite usage tracking."""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from database import get_usage_count, log_usage
from models import PLAN_LIMITS
from datetime import datetime, timezone
import calendar


def get_reset_date() -> str:
    """Get the first day of next month (UTC) as ISO string."""
    now = datetime.now(timezone.utc)
    _, last_day = calendar.monthrange(now.year, now.month)
    if now.month == 12:
        reset = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        reset = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
    return reset.isoformat()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Check and enforce rate limits per API key or IP."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Only rate-limit API conversion endpoints
        if not path.startswith("/api/v1/") or path in ("/api/v1/usage", "/api/v1/generate-key"):
            response = await call_next(request)
            return response

        # Get plan info from auth middleware
        plan = getattr(request.state, "plan", "free")
        key_hash = getattr(request.state, "key_hash", None)
        plan_config = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
        limit = plan_config["monthly_limit"]

        client_ip = request.client.host if request.client else "unknown"

        # Get current usage
        used = await get_usage_count(key_hash, client_ip)
        remaining = max(0, limit - used)

        if used >= limit:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Monthly rate limit exceeded",
                    "used": used,
                    "limit": limit,
                    "plan": plan,
                    "reset_date": get_reset_date(),
                    "upgrade_url": "https://www.editpdfree.com/api#pricing",
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": get_reset_date(),
                    "Retry-After": "3600",
                },
            )

        # Log usage BEFORE processing (count the attempt)
        await log_usage(key_hash, client_ip, path)

        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining - 1)
        response.headers["X-RateLimit-Reset"] = get_reset_date()

        return response
