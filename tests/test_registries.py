"""Registry tests for starter modules."""

import pytest

from agentic_project_starter.agentic.registry import get_agent_specs
from agentic_project_starter.agentic.service import get_agent_spec
from agentic_project_starter.etl.registry import get_etl_job_specs
from agentic_project_starter.etl.service import get_etl_job


def test_agent_registry_contains_default_entries() -> None:
    specs = get_agent_specs()

    assert set(specs) >= {"coordinator", "researcher", "analyst", "executor"}


def test_etl_registry_contains_default_entries() -> None:
    specs = get_etl_job_specs()

    assert set(specs) >= {"bootstrap_pipeline", "backfill_pipeline"}


def test_unknown_agent_fails_clearly() -> None:
    with pytest.raises(ValueError, match="Unknown agent"):
        get_agent_spec("missing")


def test_unknown_etl_job_fails_clearly() -> None:
    with pytest.raises(ValueError, match="Unknown ETL job"):
        get_etl_job("missing")
