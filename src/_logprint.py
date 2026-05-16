"""Redirect `print(...)` to the module's logger.

Domain modules in src/ historically use `print()` for operational status
(scraper progress, parser milestones). Rather than rewrite ~70 call sites,
each module replaces its `print` with `log_print` at import time so the
output flows into the configured logging pipeline (and Sentry breadcrumbs).
"""
import logging


def make_log_print(name: str):
    log = logging.getLogger(name)

    def log_print(*args, **kwargs):
        # Strip kwargs that don't apply (end, sep, file, flush)
        sep = kwargs.get("sep", " ")
        msg = sep.join(str(a) for a in args)
        log.info(msg)

    return log_print
