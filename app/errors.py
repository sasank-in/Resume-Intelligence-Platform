"""HTTP error helpers that don't leak internals."""
import uuid
from fastapi import HTTPException

from .logging_config import get_logger

log = get_logger(__name__)


def server_error(public_message: str, exc: Exception, **context) -> HTTPException:
    """Log full exception with a request id; return a generic message to client."""
    incident_id = uuid.uuid4().hex[:12]
    log.exception(
        public_message,
        extra={"incident_id": incident_id, **context, "error": str(exc)},
    )
    return HTTPException(
        status_code=500,
        detail=f"{public_message} (incident {incident_id})",
    )


def bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=400, detail=message)


def not_found(message: str) -> HTTPException:
    return HTTPException(status_code=404, detail=message)
