"""Tests for the starter file-backed chat storage seam."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from chatkit.types import ThreadMetadata, UserMessageItem

from agentic_project_starter.chat.storage import FileChatStore, resolve_chat_storage_root


def test_resolve_chat_storage_root_handles_relative_file_uri() -> None:
    root = resolve_chat_storage_root("file://./var/data")

    assert root.name == "chatkit"
    assert "var/data" in root.as_posix()


def test_file_chat_store_persists_thread_and_items(tmp_path) -> None:
    store = FileChatStore(tmp_path / "chat")
    context = {"user_id": "starter-user"}
    thread = ThreadMetadata(
        id="thr_demo",
        created_at=datetime.now(UTC),
        metadata={"starter_user_id": context["user_id"]},
    )

    async def exercise_store() -> tuple[ThreadMetadata, list[str]]:
        await store.save_thread(thread, context)
        await store.add_thread_item(
            thread.id,
            UserMessageItem.model_validate(
                {
                    "id": "msg_1",
                    "thread_id": thread.id,
                    "created_at": datetime.now(UTC),
                    "type": "user_message",
                    "content": [{"type": "input_text", "text": "hello"}],
                    "attachments": [],
                    "quoted_text": None,
                    "inference_options": {},
                }
            ),
            context,
        )
        loaded_thread = await store.load_thread(thread.id, context)
        items_page = await store.load_thread_items(
            thread.id,
            after=None,
            limit=10,
            order="asc",
            context=context,
        )
        return loaded_thread, [item.id for item in items_page.data]

    loaded_thread, item_ids = asyncio.run(exercise_store())

    assert loaded_thread.id == thread.id
    assert item_ids == ["msg_1"]
