"""Generic chat service seam used by the optional ChatKit accelerator."""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any, Protocol, cast

from agents import Agent, RunConfig, Runner, function_tool
from agents.result import RunResultStreaming

from agentic_project_starter.chat.models import ChatRuntimeSummary, ChatTurnRequest

if TYPE_CHECKING:
    from agentic_project_starter.runtime.models import RuntimeContext


class ChatService(Protocol):
    """Transport-agnostic chat service contract for starter integrations."""

    async def run_turn(self, request: ChatTurnRequest) -> RunResultStreaming:
        """Run one streamed chat turn and return the streaming result handle."""


class StarterChatService:
    """Starter-safe chat implementation backed by the Agents SDK."""

    def __init__(self, runtime_context: RuntimeContext) -> None:
        self._runtime_context = runtime_context
        self._runtime_summary = ChatRuntimeSummary(
            app_name=runtime_context.settings.app_name,
            environment=runtime_context.settings.app_environment,
            default_agent=runtime_context.settings.openai_default_agent,
            agents=tuple(sorted(runtime_context.agent_specs)),
            etl_jobs=tuple(sorted(runtime_context.etl_job_specs)),
            storage_uri=runtime_context.settings.storage_uri,
        )
        self._responder = Agent(
            name="starter_responder",
            model=runtime_context.settings.openai_model,
            instructions=(
                "You are the final responder for a reusable starter template. "
                "Give direct answers, mention when a capability is still scaffold-only, "
                "and stay concise."
            ),
        )
        self._coordinator = Agent(
            name="starter_coordinator",
            model=runtime_context.settings.openai_model,
            instructions=(
                "You coordinate a reusable starter-template chat experience. "
                "At the start of every turn, call inspect_runtime_summary exactly once. "
                "After you have the summary, hand off to starter_responder "
                "to write the final reply. Do not answer directly."
            ),
            tools=[self._build_runtime_summary_tool()],
            handoffs=[self._responder],
        )
        self._run_config = RunConfig(
            model=runtime_context.settings.openai_model,
            tracing_disabled=not runtime_context.settings.openai_enable_tracing,
            workflow_name="Starter Chat Workflow",
            trace_metadata={
                "app_name": runtime_context.settings.app_name,
                "environment": runtime_context.settings.app_environment,
            },
        )

    async def run_turn(self, request: ChatTurnRequest) -> RunResultStreaming:
        """Stream a chat turn through the starter coordinator agent."""

        input_items = cast(list[Any], request.input_items)
        return Runner.run_streamed(
            self._coordinator,
            input_items,
            context={
                "thread_id": request.thread_id,
                "user_id": request.user_id,
                "latest_user_message": request.latest_user_message or "",
            },
            run_config=self._run_config,
        )

    def _build_runtime_summary_tool(self) -> Any:
        @function_tool
        def inspect_runtime_summary() -> dict[str, object]:
            """Inspect the starter runtime summary and capabilities."""

            payload = asdict(self._runtime_summary)
            payload["capabilities"] = {
                "chat_ui": "ChatKit optional accelerator",
                "agent_registry": "placeholder-only",
                "etl_registry": "placeholder-only",
            }
            return payload

        return inspect_runtime_summary


def build_chat_service(runtime_context: RuntimeContext) -> ChatService:
    """Build the default starter chat service."""

    return StarterChatService(runtime_context)
