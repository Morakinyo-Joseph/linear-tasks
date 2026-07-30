"""Initialize Insider once for WSGI/ASGI entrypoints.

Call before get_wsgi_application() / get_asgi_application().
Release is left unset unless INSIDER_RELEASE or GIT_SHA is provided so the
SDK can fall back to `git rev-parse HEAD` when a .git directory exists.
"""

from __future__ import annotations

import os
from pathlib import Path

import environ


def init_insider():
    # Load .env before Django settings so INSIDER_DSN is available at process start.
    environ.Env.read_env(Path(__file__).resolve().parent.parent / ".env")

    dsn = os.environ.get("INSIDER_DSN") or None
    if not dsn:
        return None

    import insider
    from insider.integrations.django import DjangoIntegration
    from insider.integrations.logging import LoggingIntegration

    release = os.environ.get("INSIDER_RELEASE") or os.environ.get("GIT_SHA") or None
    debug = os.environ.get("INSIDER_DEBUG", "").lower() in ("1", "true", "yes")
    environment = os.environ.get("INSIDER_ENVIRONMENT", "development")

    return insider.init(
        dsn=dsn,
        environment=environment,
        release=release,
        enable_logs=True,
        ignore_paths=["/health/", "/admin/"],
        integrations=[DjangoIntegration(), LoggingIntegration()],
        debug=debug,
        send_default_pii=True
    )
