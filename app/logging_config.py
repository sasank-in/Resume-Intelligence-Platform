"""Centralized logging setup."""
import logging
import sys

from .config import LOG_LEVEL, LOG_JSON


def setup_logging() -> None:
    root = logging.getLogger()
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)

    if LOG_JSON:
        try:
            from pythonjsonlogger import jsonlogger

            fmt = jsonlogger.JsonFormatter(
                "%(asctime)s %(levelname)s %(name)s %(message)s"
            )
        except ImportError:
            fmt = logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s %(message)s"
            )
    else:
        fmt = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)s - %(message)s"
        )

    handler.setFormatter(fmt)
    root.addHandler(handler)
    root.setLevel(LOG_LEVEL)

    # Quiet noisy libraries.
    for noisy in ("selenium", "urllib3", "httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
