import os
from typing import Any, Dict
from uuid import UUID

import sentry_sdk
from loguru import logger

from vocode.meta import ensure_punkt_installed

environment = {}
logger.disable("vocode")

ensure_punkt_installed()

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN")
)

def set_context(key: str, value: Any) -> None:
    """Set a context variable using Sentry's scope."""
    with sentry_sdk.configure_scope() as scope:
        scope.set_context(key, value)
        if isinstance(value, str):
            scope.set_tag(key, value)
        elif isinstance(value, UUID):
            scope.set_tag(key, str(value))

def get_context(key: str, default: Any = None) -> Any:
    """Get a context variable from Sentry's scope."""
    with sentry_sdk.configure_scope() as scope:
        contexts = scope._contexts
        return contexts.get(key, default)

def reset_context(key: str) -> None:
    """Reset a context variable in Sentry's scope."""
    with sentry_sdk.configure_scope() as scope:
        scope.set_context(key, None)

def serialize_context() -> Dict[str, Any]:
    hub = sentry_sdk.Hub.current
    if hub.client is None:
        return {}
    with hub:
        scope = hub.scope
        contexts = scope._contexts
        return {k: v for k, v in contexts.items() if isinstance(v, (str, UUID))}

def setenv(**kwargs):
    for key, value in kwargs.items():
        environment[key] = value

def getenv(key, default=None):
    return environment.get(key) or os.getenv(key, default)

api_key = getenv("VOCODE_API_KEY")
base_url = getenv("VOCODE_BASE_URL", "api.vocode.dev")

set_context("conversation_id", None)
set_context("sentry_span_tags", None)
set_context("sentry_transaction", None)
get_serialized_ctx_wrappers = serialize_context