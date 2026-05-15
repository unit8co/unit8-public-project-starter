"""Data models for agent definitions and run results."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class AgentSpec:
    """A starter-friendly description of an agent role."""

    name: str
    model: str
    instructions: str
    handoff_targets: tuple[str, ...] = ()
    toolsets: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


@dataclass(slots=True)
class AgentRunRequest:
    """Parameters for a starter agent execution."""

    agent_name: str
    prompt: str
    live: bool = False
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class AgentRunResult:
    """Result of a placeholder or live agent execution."""

    agent_name: str
    mode: str
    summary: str
    handoff_targets: tuple[str, ...]
