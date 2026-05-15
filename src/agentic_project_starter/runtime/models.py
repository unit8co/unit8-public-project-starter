"""Runtime context models used by API and CLI entrypoints."""

from __future__ import annotations

from dataclasses import dataclass

from agentic_project_starter.agentic.models import AgentSpec
from agentic_project_starter.chat.service import ChatService
from agentic_project_starter.chat.storage import FileChatStore
from agentic_project_starter.etl.models import ETLJobSpec
from agentic_project_starter.shared.config import Settings


@dataclass(slots=True)
class RuntimeContext:
    """Resolved runtime wiring for starter services."""

    settings: Settings
    agent_specs: dict[str, AgentSpec]
    etl_job_specs: dict[str, ETLJobSpec]
    chat_service: ChatService | None = None
    chat_store: FileChatStore | None = None
