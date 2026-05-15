"""API routes exposing starter metadata and placeholder runtime state."""

from fastapi import APIRouter, Request

from agentic_project_starter.runtime.models import RuntimeContext

router = APIRouter(tags=["runtime"])


def get_context(request: Request) -> RuntimeContext:
    """Return the runtime context stored on the FastAPI app."""

    return request.app.state.runtime_context  # type: ignore[no-any-return]


@router.get("/runtime/summary")
def runtime_summary(request: Request) -> dict[str, object]:
    """Return starter metadata for smoke tests and local introspection."""

    context = get_context(request)
    return {
        "app_name": context.settings.app_name,
        "environment": context.settings.app_environment,
        "agents": sorted(context.agent_specs.keys()),
        "etl_jobs": sorted(context.etl_job_specs.keys()),
        "storage_uri": context.settings.storage_uri,
        "chat_adapter": "chatkit",
        "chat_storage_backend": "file",
        "chat_storage_root": (
            str(context.chat_store.root_dir) if context.chat_store is not None else None
        ),
        "chat_domain_key": context.settings.chatkit_domain_key,
    }
