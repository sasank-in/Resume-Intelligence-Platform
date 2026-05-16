"""Optional Sentry integration. Active only when SENTRY_DSN is set."""
import os

from .logging_config import get_logger

log = get_logger(__name__)


def init_sentry(release: str, environment: str) -> None:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        log.info("sentry_disabled (no SENTRY_DSN)")
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration
    except ImportError:
        log.warning("sentry_sdk not installed; skipping Sentry init")
        return

    traces = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.05"))
    profiles = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.0"))

    sentry_sdk.init(
        dsn=dsn,
        release=release,
        environment=environment,
        traces_sample_rate=traces,
        profiles_sample_rate=profiles,
        send_default_pii=False,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            StarletteIntegration(transaction_style="endpoint"),
        ],
    )
    log.info("sentry_enabled", extra={"env": environment, "release": release})
