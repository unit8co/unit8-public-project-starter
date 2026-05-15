"""Starter ETL execution helpers."""

from agentic_project_starter.etl.models import ETLRunRequest, ETLRunResult
from agentic_project_starter.etl.registry import get_etl_job_specs


def get_etl_job(job_name: str) -> tuple[str, ...]:
    """Return ETL stages for a named starter job."""

    specs = get_etl_job_specs()
    if job_name not in specs:
        available = ", ".join(sorted(specs))
        raise ValueError(f"Unknown ETL job '{job_name}'. Available jobs: {available}")
    return specs[job_name].stages


def run_etl_request(request: ETLRunRequest) -> ETLRunResult:
    """Return a placeholder ETL result for local testing and bootstrapping."""

    stages = get_etl_job(request.job_name)
    mode = "dry-run" if request.dry_run else "live-preview"
    return ETLRunResult(
        job_name=request.job_name,
        dataset=request.dataset,
        mode=mode,
        completed_stages=stages,
    )
