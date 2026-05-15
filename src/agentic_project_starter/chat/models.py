"""Generic chat models that keep the starter transport-agnostic."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ChatTurnRequest:
    """Normalized chat turn input passed to the starter chat service."""

    thread_id: str
    user_id: str
    input_items: list[dict[str, Any]]
    latest_user_message: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class ChatRuntimeSummary:
    """Template-safe runtime facts exposed through the starter chat tool."""

    app_name: str
    environment: str
    default_agent: str
    agents: tuple[str, ...]
    etl_jobs: tuple[str, ...]
    storage_uri: str
    chat_adapter: str = "chatkit"
    chat_storage_backend: str = "file"
