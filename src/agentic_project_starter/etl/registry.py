"""Registry of starter ETL jobs."""

from agentic_project_starter.etl.models import ETLJobSpec


def get_etl_job_specs() -> dict[str, ETLJobSpec]:
    """Return the default ETL job registry."""

    return {
        "bootstrap_pipeline": ETLJobSpec(
            name="bootstrap_pipeline",
            description="Example end-to-end ETL flow for new projects.",
            stages=("extract", "transform", "load"),
        ),
        "backfill_pipeline": ETLJobSpec(
            name="backfill_pipeline",
            description="Historical replay flow with the same starter interfaces.",
            stages=("extract", "validate", "transform", "load"),
        ),
    }
