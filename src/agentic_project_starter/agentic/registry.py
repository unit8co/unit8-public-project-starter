"""Starter agent registry definitions."""

from agentic_project_starter.agentic.models import AgentSpec


def get_agent_specs() -> dict[str, AgentSpec]:
    """Return the default starter agent registry."""

    return {
        "coordinator": AgentSpec(
            name="coordinator",
            model="gpt-5",
            instructions=(
                "Coordinate the workflow, decide which specialist agent should act next, "
                "and keep outputs implementation-ready."
            ),
            handoff_targets=("researcher", "analyst", "executor"),
            toolsets=("registry", "handoffs"),
            tags=("default", "orchestration"),
        ),
        "researcher": AgentSpec(
            name="researcher",
            model="gpt-5",
            instructions=(
                "Gather structured context and summarize findings that a downstream agent can use."
            ),
            handoff_targets=("coordinator", "analyst"),
            toolsets=("documents", "web"),
            tags=("discovery",),
        ),
        "analyst": AgentSpec(
            name="analyst",
            model="gpt-5",
            instructions=(
                "Turn gathered context into explicit decisions, tradeoffs, and recommended actions."
            ),
            handoff_targets=("coordinator", "executor"),
            toolsets=("reasoning", "handoffs"),
            tags=("decision-support",),
        ),
        "executor": AgentSpec(
            name="executor",
            model="gpt-5",
            instructions=(
                "Apply the chosen workflow with narrow scope and report concrete outcomes or gaps."
            ),
            handoff_targets=("coordinator",),
            toolsets=("tools", "artifacts"),
            tags=("delivery",),
        ),
    }
