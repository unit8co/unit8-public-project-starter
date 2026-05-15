"""Starter agent execution helpers."""

from __future__ import annotations

from agentic_project_starter.agentic.models import AgentRunRequest, AgentRunResult
from agentic_project_starter.agentic.registry import get_agent_specs
from agentic_project_starter.shared.config import Settings


def get_agent_spec(agent_name: str) -> tuple[str, ...]:
    """Return the handoff targets for a named agent, or fail clearly."""

    specs = get_agent_specs()
    if agent_name not in specs:
        available = ", ".join(sorted(specs))
        raise ValueError(f"Unknown agent '{agent_name}'. Available agents: {available}")
    return specs[agent_name].handoff_targets


async def run_agent_request(
    request: AgentRunRequest,
    settings: Settings,
) -> AgentRunResult:
    """Execute a starter agent request in dry-run or live-preview mode."""

    handoff_targets = get_agent_spec(request.agent_name)

    if request.live and not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required when --live is enabled.")

    mode = "live-preview" if request.live else "dry-run"
    summary = (
        f"{request.agent_name} accepted the prompt and returned a placeholder {mode} result. "
        "Replace this stub with project-specific orchestration logic when bootstrapping a real app."
    )

    return AgentRunResult(
        agent_name=request.agent_name,
        mode=mode,
        summary=summary,
        handoff_targets=handoff_targets,
    )
