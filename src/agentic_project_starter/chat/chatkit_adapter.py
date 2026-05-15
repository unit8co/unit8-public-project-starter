"""ChatKit HTTP adapter layered over the generic starter chat service."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.types import ThreadMetadata, ThreadStreamEvent, UserMessageItem
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse

from agentic_project_starter.chat.models import ChatTurnRequest
from agentic_project_starter.chat.service import ChatService
from agentic_project_starter.chat.storage import FileChatStore


class StarterChatKitServer(ChatKitServer[dict[str, str]]):
    """Adapt starter chat turns into ChatKit thread events."""

    def __init__(self, *, store: FileChatStore, chat_service: ChatService) -> None:
        super().__init__(store=store)
        self._chat_service = chat_service

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: dict[str, str],
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Stream one user turn via the generic starter chat service."""

        items_page = await self.store.load_thread_items(
            thread.id,
            after=None,
            limit=50,
            order="asc",
            context=context,
        )
        input_items = await simple_to_agent_input(items_page.data)
        request = ChatTurnRequest(
            thread_id=thread.id,
            user_id=context["user_id"],
            input_items=cast_agent_input(input_items),
            latest_user_message=extract_latest_user_text(input_user_message),
        )
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )
        result = await self._chat_service.run_turn(request)
        async for event in stream_agent_response(agent_context, result):
            yield event


def build_chatkit_router(
    *,
    chat_service: ChatService,
    chat_store: FileChatStore,
    openai_api_key_available: bool,
) -> APIRouter:
    """Create the ChatKit router mounted by the starter FastAPI app."""

    router = APIRouter(tags=["chat"])
    server = StarterChatKitServer(store=chat_store, chat_service=chat_service)

    @router.post("")
    async def chatkit_endpoint(request: Request) -> Response:
        if not openai_api_key_available:
            return JSONResponse(
                {
                    "detail": "OPENAI_API_KEY is required for the starter ChatKit chat route. "
                    "Set it in `.env` before sending live chat requests."
                },
                status_code=503,
            )
        context = {"user_id": resolve_request_user_id(request)}
        result = await server.process(await request.body(), context=context)
        if isinstance(result, StreamingResult):
            return StreamingResponse(result, media_type="text/event-stream")
        return Response(content=result.json, media_type="application/json")

    return router


def resolve_request_user_id(request: Request) -> str:
    """Resolve a stable anonymous starter user identifier from request headers."""

    candidate = request.headers.get("x-starter-user-id", "").strip()
    return candidate or "starter-anonymous-user"


def extract_latest_user_text(message: UserMessageItem | None) -> str | None:
    """Extract plain text from the latest ChatKit user message when available."""

    if message is None:
        return None
    parts: list[str] = []
    for block in message.content:
        block_payload = block.model_dump(mode="json")
        if block_payload.get("type") == "input_text":
            text = block_payload.get("text")
            if isinstance(text, str):
                parts.append(text)
    return "\n".join(parts) if parts else None


def cast_agent_input(input_items: list[Any]) -> list[dict[str, Any]]:
    """Cast ChatKit-converted input items into the generic service payload."""

    return [item for item in input_items if isinstance(item, dict)]
