"""Dependency probes for the /health endpoint."""
import asyncio
import time
from typing import Any, Dict

from .config import APP_TITLE, APP_VERSION, REDIS_URL, SESSION_BACKEND
from .logging_config import get_logger

log = get_logger(__name__)

# Cache last result for HEALTH_CACHE_TTL seconds to avoid hammering deps from
# orchestrators that probe every second.
_HEALTH_CACHE_TTL = 5.0
_cache: Dict[str, Any] = {"at": 0.0, "result": None}


async def _check_redis() -> Dict[str, Any]:
    if SESSION_BACKEND != "redis":
        return {"status": "skipped", "reason": "SESSION_BACKEND != redis"}
    try:
        import redis

        r = redis.from_url(REDIS_URL, socket_connect_timeout=1.0, decode_responses=True)
        # PING is the standard Redis liveness probe.
        ok = r.ping()
        return {"status": "ok" if ok else "fail"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "fail", "error": str(exc)[:120]}


async def _check_groq() -> Dict[str, Any]:
    # We don't call the LLM — too expensive. Just check that the SDK client
    # holds a usable key. A real liveness call would consume tokens on every probe.
    try:
        from .services import client  # already-initialized Groq client
        if not client.api_key:
            return {"status": "fail", "error": "no api key"}
        return {"status": "ok"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "fail", "error": str(exc)[:120]}


async def run_checks(_state) -> Dict[str, Any]:
    """Aggregate dep probes with a short TTL cache."""
    now = time.monotonic()
    if _cache["result"] is not None and now - _cache["at"] < _HEALTH_CACHE_TTL:
        return _cache["result"]

    redis_res, groq_res = await asyncio.gather(_check_redis(), _check_groq())

    overall_ok = all(
        c["status"] in ("ok", "skipped") for c in (redis_res, groq_res)
    )

    result = {
        "status": "healthy" if overall_ok else "degraded",
        "service": APP_TITLE,
        "version": APP_VERSION,
        "checks": {
            "redis": redis_res,
            "groq": groq_res,
        },
    }
    _cache["result"] = result
    _cache["at"] = now
    return result
