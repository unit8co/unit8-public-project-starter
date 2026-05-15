"""CLI for local starter workflows."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

import uvicorn

from agentic_project_starter.agentic.models import AgentRunRequest
from agentic_project_starter.agentic.service import run_agent_request
from agentic_project_starter.etl.models import ETLRunRequest
from agentic_project_starter.etl.service import run_etl_request
from agentic_project_starter.quality.change_quiz import (
    DEFAULT_ARTIFACT_PATH,
    QuizError,
    collect_change_set,
    run_interactive_quiz,
    validate_quiz_artifact,
)
from agentic_project_starter.runtime.bootstrap import build_runtime_context
from agentic_project_starter.shared.config import get_settings


def build_parser() -> argparse.ArgumentParser:
    """Build the starter CLI parser."""

    parser = argparse.ArgumentParser(
        prog="agentic-starter",
        description="Starter CLI for local runtime, agent, and ETL workflows.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    serve = subcommands.add_parser("serve", help="Run the FastAPI service locally.")
    serve.add_argument("--host", default=None, help="Bind host override.")
    serve.add_argument("--port", type=int, default=None, help="Bind port override.")
    serve.add_argument("--reload", action="store_true", help="Enable local autoreload.")

    subcommands.add_parser("doctor", help="Print runtime summary information.")

    run_agent = subcommands.add_parser("run-agent", help="Execute a placeholder agent workflow.")
    run_agent.add_argument("--agent-name", required=True, help="Agent registry name.")
    run_agent.add_argument("--prompt", required=True, help="Prompt for the starter agent.")
    run_agent.add_argument(
        "--live",
        action="store_true",
        help="Require OPENAI_API_KEY and mark the run as live-preview.",
    )

    run_etl = subcommands.add_parser("run-etl", help="Execute a placeholder ETL workflow.")
    run_etl.add_argument("--job-name", required=True, help="ETL job registry name.")
    run_etl.add_argument("--dataset", default=None, help="Dataset name override.")
    run_etl.add_argument(
        "--live",
        action="store_true",
        help="Mark the ETL run as live-preview instead of dry-run.",
    )

    quiz = subcommands.add_parser(
        "quiz-changes",
        help="Run or verify the AI-assisted change-understanding quiz.",
    )
    quiz.add_argument("--base", default="origin/main", help="Base git ref for the quiz diff.")
    quiz.add_argument("--head", default="HEAD", help="Head git ref for the quiz diff.")
    quiz.add_argument(
        "--artifact",
        default=str(DEFAULT_ARTIFACT_PATH),
        help="Quiz result artifact path.",
    )
    quiz.add_argument(
        "--verify",
        action="store_true",
        help="Validate an existing quiz artifact without calling an LLM.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Dispatch starter CLI commands."""

    parser = build_parser()
    args = parser.parse_args(argv)
    settings = get_settings()

    if args.command == "serve":
        uvicorn.run(
            "agentic_project_starter.api.app:app",
            host=args.host or settings.app_host,
            port=args.port or settings.app_port,
            reload=args.reload,
        )
        return

    if args.command == "doctor":
        context = build_runtime_context(settings)
        print(
            json.dumps(
                {
                    "app_name": context.settings.app_name,
                    "environment": context.settings.app_environment,
                    "agents": sorted(context.agent_specs),
                    "etl_jobs": sorted(context.etl_job_specs),
                    "storage_uri": context.settings.storage_uri,
                    "chat_adapter": "chatkit",
                    "chat_storage_backend": "file",
                    "chat_storage_root": (
                        str(context.chat_store.root_dir) if context.chat_store is not None else None
                    ),
                    "chat_domain_key": context.settings.chatkit_domain_key,
                }
            )
        )
        return

    if args.command == "run-agent":
        agent_result = asyncio.run(
            run_agent_request(
                AgentRunRequest(
                    agent_name=args.agent_name,
                    prompt=args.prompt,
                    live=args.live,
                ),
                settings,
            )
        )
        print(json.dumps(asdict(agent_result)))
        return

    if args.command == "run-etl":
        etl_result = run_etl_request(
            ETLRunRequest(
                job_name=args.job_name,
                dataset=args.dataset or settings.etl_default_dataset,
                dry_run=not args.live,
            )
        )
        print(json.dumps(asdict(etl_result)))
        return

    if args.command == "quiz-changes":
        try:
            artifact_path = Path(args.artifact)
            if args.verify:
                validation = validate_quiz_artifact(
                    artifact_path=artifact_path,
                    base_ref=args.base,
                    head_ref=args.head,
                )
                print(validation.message)
                if not validation.valid:
                    raise SystemExit(1)
                return

            change_set = collect_change_set(base_ref=args.base, head_ref=args.head)
            exit_code = run_interactive_quiz(
                change_set=change_set,
                settings=settings,
                artifact_path=artifact_path,
            )
            if exit_code:
                raise SystemExit(exit_code)
            return
        except QuizError as exc:
            print(f"quiz-changes failed: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc

    parser.error(f"Unsupported command: {args.command}")
