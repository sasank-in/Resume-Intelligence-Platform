"""Session management with pluggable backends (memory or Redis)."""
import asyncio
import json
import re
import threading
import time
from typing import Dict, Optional

from .config import (
    REDIS_URL,
    SESSION_BACKEND,
    SESSION_CLEANUP_INTERVAL,
    SESSION_TIMEOUT,
)
from .logging_config import get_logger

log = get_logger(__name__)

# session ids accepted from clients: alphanumeric, hyphen, underscore, 8-128 chars.
_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_\-]{8,128}$")


def is_valid_session_id(session_id: str) -> bool:
    return bool(session_id) and bool(_SESSION_ID_RE.match(session_id))


class SessionManager:
    """In-memory, thread-safe session store."""

    def __init__(self, timeout: int = SESSION_TIMEOUT):
        self._sessions: Dict[str, Dict] = {}
        self._timestamps: Dict[str, float] = {}
        self._lock = threading.RLock()
        self.timeout = timeout

    def create_session(self, session_id: str, data: Dict) -> None:
        with self._lock:
            self._sessions[session_id] = dict(data)
            self._timestamps[session_id] = time.time()

    def get_session(self, session_id: str) -> Optional[Dict]:
        with self._lock:
            if session_id not in self._sessions:
                return None
            if time.time() - self._timestamps[session_id] > self.timeout:
                self._sessions.pop(session_id, None)
                self._timestamps.pop(session_id, None)
                return None
            self._timestamps[session_id] = time.time()
            return self._sessions[session_id]

    def update_session(self, session_id: str, data: Dict) -> None:
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].update(data)
                self._timestamps[session_id] = time.time()

    def cleanup_old_sessions(self) -> int:
        now = time.time()
        with self._lock:
            expired = [
                sid for sid, ts in self._timestamps.items()
                if now - ts > self.timeout
            ]
            for sid in expired:
                self._sessions.pop(sid, None)
                self._timestamps.pop(sid, None)
        if expired:
            log.info("cleaned_expired_sessions", extra={"count": len(expired)})
        return len(expired)

    def session_exists(self, session_id: str) -> bool:
        with self._lock:
            return session_id in self._sessions


class RedisSessionManager:
    """Redis-backed session store. Opt in by setting SESSION_BACKEND=redis."""

    def __init__(self, redis_url: str = REDIS_URL, timeout: int = SESSION_TIMEOUT):
        import redis  # imported lazily

        self._r = redis.from_url(redis_url, decode_responses=True)
        self.timeout = timeout
        self._prefix = "session:"

    def _key(self, session_id: str) -> str:
        return f"{self._prefix}{session_id}"

    def create_session(self, session_id: str, data: Dict) -> None:
        self._r.set(self._key(session_id), json.dumps(data), ex=self.timeout)

    def get_session(self, session_id: str) -> Optional[Dict]:
        raw = self._r.get(self._key(session_id))
        if raw is None:
            return None
        # touch TTL on access
        self._r.expire(self._key(session_id), self.timeout)
        return json.loads(raw)

    def update_session(self, session_id: str, data: Dict) -> None:
        existing = self.get_session(session_id)
        if existing is None:
            return
        existing.update(data)
        self._r.set(self._key(session_id), json.dumps(existing), ex=self.timeout)

    def cleanup_old_sessions(self) -> int:
        # Redis handles expiry itself.
        return 0

    def session_exists(self, session_id: str) -> bool:
        return self._r.exists(self._key(session_id)) == 1


def build_session_manager():
    if SESSION_BACKEND == "redis":
        try:
            mgr = RedisSessionManager()
            log.info("session_backend_redis", extra={"url": REDIS_URL})
            return mgr
        except Exception as exc:  # noqa: BLE001
            log.error(
                "redis_session_init_failed_falling_back_to_memory",
                extra={"error": str(exc)},
            )
    log.info("session_backend_memory")
    return SessionManager()


async def session_cleanup_loop(manager) -> None:
    """Background task: periodically purge expired sessions (memory backend)."""
    while True:
        await asyncio.sleep(SESSION_CLEANUP_INTERVAL)
        try:
            manager.cleanup_old_sessions()
        except Exception:  # noqa: BLE001
            log.exception("session_cleanup_failed")


def validate_file_upload(filename: Optional[str], allowed_types: list) -> bool:
    if not filename:
        return False
    return any(filename.lower().endswith(ext) for ext in allowed_types)
