"""Data models for ETL job definitions and run results."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class ETLJobSpec:
    """A starter-friendly ETL job definition."""

    name: str
    description: str
    stages: tuple[str, ...]


@dataclass(slots=True)
class ETLRunRequest:
    """Parameters for running an ETL job."""

    job_name: str
    dataset: str
    dry_run: bool = True
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class ETLRunResult:
    """Starter output from an ETL execution."""

    job_name: str
    dataset: str
    mode: str
    completed_stages: tuple[str, ...]
