"""ASGI application entrypoint."""

from agentic_project_starter.runtime.bootstrap import create_app

app = create_app()
