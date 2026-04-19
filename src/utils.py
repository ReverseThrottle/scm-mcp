"""Shared utilities: serialization and error handling."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel


def serialize(obj: Any) -> Any:
    """Recursively convert Pydantic models and UUIDs to JSON-safe types."""
    if isinstance(obj, BaseModel):
        return serialize(obj.model_dump())
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize(i) for i in obj]
    if isinstance(obj, uuid.UUID):
        return str(obj)
    return obj


def handle_error(exc: Exception) -> dict:
    """Convert an SCM SDK exception to a structured error dict."""
    return {
        "error": type(exc).__name__,
        "message": str(exc),
    }
