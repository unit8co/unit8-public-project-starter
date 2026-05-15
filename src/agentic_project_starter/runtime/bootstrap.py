"""Runtime bootstrap helpers for API and CLI entrypoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.responses import FileResponse, JSONResponse

from agentic_project_starter.agentic.registry import get_agent_specs
from agentic_project_starter.api.routes import router as api_router
from agentic_project_starter.chat.chatkit_adapter import build_chatkit_router
from agentic_project_starter.chat.service import build_chat_service
from agentic_project_starter.chat.storage import FileChatStore
from agentic_project_starter.etl.registry import get_etl_job_specs
from agentic_project_starter.runtime.models import RuntimeContext
from agentic_project_starter.shared.config import Settings, get_settings
from agentic_project_starter.shared.logging import configure_logging


def build_runtime_context(settings: Settings | None = None) -> RuntimeContext:
    """Create the runtime context used by API and CLI workflows."""

    resolved_settings = settings or get_settings()
    context = RuntimeContext(
        settings=resolved_settings,
        agent_specs=get_agent_specs(),
        etl_job_specs=get_etl_job_specs(),
    )
    context.chat_store = FileChatStore.from_storage_uri(resolved_settings.storage_uri)
    context.chat_service = build_chat_service(context)
    return context


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the FastAPI application for local and container runtime."""

    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings.log_level)
    context = build_runtime_context(resolved_settings)

    app = FastAPI(
        title=resolved_settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.state.runtime_context = context
    app.include_router(api_router, prefix=resolved_settings.api_base_path)
    if context.chat_service is not None and context.chat_store is not None:
        app.include_router(
            build_chatkit_router(
                chat_service=context.chat_service,
                chat_store=context.chat_store,
                openai_api_key_available=bool(resolved_settings.openai_api_key),
            ),
            prefix="/chatkit",
        )

    @app.get("/healthz", tags=["platform"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok", "environment": resolved_settings.app_environment}

    register_frontend_routes(app)

    return app


def register_frontend_routes(app: FastAPI) -> None:
    """Serve the built frontend bundle when it exists."""

    frontend_dist = get_frontend_dist_dir()
    index_file = frontend_dist / "index.html"

    @app.get("/", include_in_schema=False, response_model=None)
    def frontend_root() -> Response:
        if index_file.exists():
            return FileResponse(index_file)
        return JSONResponse(
            {
                "message": "Frontend build not found. Run `npm --prefix frontend run build` "
                "or use `npm --prefix frontend run dev` for local UI development."
            }
        )

    @app.get("/{asset_path:path}", include_in_schema=False, response_model=None)
    def frontend_assets(asset_path: str) -> Response:
        candidate = frontend_dist / asset_path
        if asset_path and candidate.exists() and candidate.is_file():
            return FileResponse(candidate)
        if index_file.exists() and should_fallback_to_frontend(asset_path):
            return FileResponse(index_file)
        return JSONResponse({"detail": "Not Found"}, status_code=404)


def get_frontend_dist_dir() -> Path:
    """Resolve the built frontend output directory."""

    return Path(__file__).resolve().parents[3] / "frontend" / "dist"


def should_fallback_to_frontend(asset_path: str) -> bool:
    """Skip SPA fallback for API-like paths and obvious file requests."""

    if not asset_path:
        return False
    if asset_path.startswith(("healthz", "docs", "redoc", "openapi.json", "chatkit", "v1/")):
        return False
    return "." not in Path(asset_path).name
