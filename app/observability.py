"""Optional observability: Sentry + Prometheus.

Both are off by default. They're activated independently by env vars:
- SENTRY_DSN unset             → Sentry disabled
- METRICS_ENABLED != "true"    → no /metrics route registered

Activating /metrics requires the `prometheus-fastapi-instrumentator` dep.
If basic auth is desired, set METRICS_BASIC_AUTH="user:pass" and the
instrumentator's exposition route will be guarded.
"""
import base64
import os

from .config import METRICS_BASIC_AUTH, METRICS_ENABLED
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


def init_metrics(app) -> None:
    """Wire Prometheus /metrics if METRICS_ENABLED=true. Optional basic-auth guard."""
    if not METRICS_ENABLED:
        log.info("metrics_disabled (METRICS_ENABLED != true)")
        return
    try:
        from prometheus_fastapi_instrumentator import Instrumentator
    except ImportError:
        log.warning("prometheus_fastapi_instrumentator not installed; skipping /metrics")
        return

    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=False,
        excluded_handlers=["/health", "/metrics"],
        env_var_name="ENABLE_METRICS",
    ).instrument(app)

    # Wrap exposition with basic-auth if configured.
    if METRICS_BASIC_AUTH and ":" in METRICS_BASIC_AUTH:
        expected = "Basic " + base64.b64encode(METRICS_BASIC_AUTH.encode()).decode()

        from fastapi import Request, Response
        from prometheus_client import (
            CONTENT_TYPE_LATEST,
            REGISTRY,
            generate_latest,
        )

        @app.get("/metrics", include_in_schema=False, tags=["system"])
        async def metrics(request: Request) -> Response:
            auth = request.headers.get("authorization", "")
            if auth != expected:
                return Response(
                    status_code=401,
                    headers={"WWW-Authenticate": 'Basic realm="metrics"'},
                )
            return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
    else:
        # No auth — instrumentator's default exposition route at /metrics.
        instrumentator.expose(app, endpoint="/metrics", include_in_schema=False, tags=["system"])

    log.info("metrics_enabled", extra={"auth": bool(METRICS_BASIC_AUTH)})
