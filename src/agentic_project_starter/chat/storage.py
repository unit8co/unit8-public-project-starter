"""File-backed ChatKit store for local starter development.

The implementation is intentionally simple and heavily documented because this
is a starter seam, not a final persistence choice. Downstream repositories can
replace this module with a real storage service while keeping the higher-level
chat service and transport adapters stable.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

from chatkit.store import NotFoundError, Store
from chatkit.types import Attachment, Page, ThreadItem, ThreadMetadata
from pydantic import TypeAdapter

THREAD_ITEMS_ADAPTER = TypeAdapter(list[ThreadItem])


class FileChatStore(Store[dict[str, str]]):
    """Persist chat threads and items under the starter storage root."""

    def __init__(self, root_dir: Path) -> None:
        self._root_dir = root_dir
        self._threads_dir = root_dir / "threads"
        self._items_dir = root_dir / "items"
        self._threads_dir.mkdir(parents=True, exist_ok=True)
        self._items_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_storage_uri(cls, storage_uri: str) -> FileChatStore:
        """Build the file-backed store from the starter storage URI."""

        return cls(resolve_chat_storage_root(storage_uri))

    @property
    def root_dir(self) -> Path:
        """Expose the resolved storage root for diagnostics and docs."""

        return self._root_dir

    def generate_thread_id(self, context: dict[str, str]) -> str:
        """Generate deterministic-looking starter thread identifiers."""

        return f"thr_{uuid.uuid4().hex[:16]}"

    def generate_item_id(
        self,
        item_type: Literal[
            "thread",
            "message",
            "tool_call",
            "task",
            "workflow",
            "attachment",
            "sdk_hidden_context",
        ],
        thread: ThreadMetadata,
        context: dict[str, str],
    ) -> str:
        """Generate starter item identifiers scoped by item type."""

        prefix = item_type[:3]
        return f"{prefix}_{uuid.uuid4().hex[:16]}"

    async def load_thread(
        self,
        thread_id: str,
        context: dict[str, str],
    ) -> ThreadMetadata:
        """Load one thread or fail with the ChatKit store contract error."""

        path = self._thread_path(thread_id)
        if not path.exists():
            raise NotFoundError(f"Thread {thread_id} not found")
        return ThreadMetadata.model_validate(json.loads(path.read_text()))

    async def save_thread(
        self,
        thread: ThreadMetadata,
        context: dict[str, str],
    ) -> None:
        """Persist thread metadata as JSON."""

        self._thread_path(thread.id).write_text(
            json.dumps(thread.model_dump(mode="json"), indent=2, sort_keys=True)
        )

    async def load_threads(
        self,
        limit: int,
        after: str | None,
        order: str,
        context: dict[str, str],
    ) -> Page[ThreadMetadata]:
        """Return paginated thread metadata for one user."""

        thread_rows: list[ThreadMetadata] = []
        for path in sorted(self._threads_dir.glob("*.json")):
            payload = json.loads(path.read_text())
            metadata = ThreadMetadata.model_validate(payload)
            if self._belongs_to_user(metadata.metadata, context):
                thread_rows.append(metadata)

        return self._paginate(
            thread_rows,
            after=after,
            limit=limit,
            order=order,
            sort_key=lambda row: row.created_at,
            cursor_key=lambda row: row.id,
        )

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: dict[str, str],
    ) -> Page[ThreadItem]:
        """Return paginated items for a thread."""

        if not self._thread_path(thread_id).exists():
            raise NotFoundError(f"Thread {thread_id} not found")

        items = self._read_items(thread_id)
        return self._paginate(
            items,
            after=after,
            limit=limit,
            order=order,
            sort_key=lambda row: row.created_at,
            cursor_key=lambda row: row.id,
        )

    async def add_thread_item(
        self,
        thread_id: str,
        item: ThreadItem,
        context: dict[str, str],
    ) -> None:
        """Append one new item to a thread."""

        items = self._read_items(thread_id)
        items.append(item)
        self._write_items(thread_id, items)

    async def save_item(
        self,
        thread_id: str,
        item: ThreadItem,
        context: dict[str, str],
    ) -> None:
        """Upsert one item within a thread."""

        items = self._read_items(thread_id)
        for index, existing in enumerate(items):
            if existing.id == item.id:
                items[index] = item
                self._write_items(thread_id, items)
                return
        items.append(item)
        self._write_items(thread_id, items)

    async def load_item(
        self,
        thread_id: str,
        item_id: str,
        context: dict[str, str],
    ) -> ThreadItem:
        """Load one item or fail clearly."""

        for item in self._read_items(thread_id):
            if item.id == item_id:
                return item
        raise NotFoundError(f"Item {item_id} not found in thread {thread_id}")

    async def delete_thread(self, thread_id: str, context: dict[str, str]) -> None:
        """Delete a thread and all of its items."""

        self._thread_path(thread_id).unlink(missing_ok=True)
        self._items_path(thread_id).unlink(missing_ok=True)

    async def delete_thread_item(
        self,
        thread_id: str,
        item_id: str,
        context: dict[str, str],
    ) -> None:
        """Delete one item from a thread."""

        items = [item for item in self._read_items(thread_id) if item.id != item_id]
        self._write_items(thread_id, items)

    async def save_attachment(
        self,
        attachment: Attachment,
        context: dict[str, str],
    ) -> None:
        """Attachments are intentionally unsupported in the starter store."""

        raise NotImplementedError("Starter file chat storage does not persist attachments yet.")

    async def load_attachment(
        self,
        attachment_id: str,
        context: dict[str, str],
    ) -> Attachment:
        """Attachments are intentionally unsupported in the starter store."""

        raise NotFoundError(f"Attachment {attachment_id} not found")

    async def delete_attachment(
        self,
        attachment_id: str,
        context: dict[str, str],
    ) -> None:
        """Attachments are intentionally unsupported in the starter store."""

        return None

    def _thread_path(self, thread_id: str) -> Path:
        return self._threads_dir / f"{thread_id}.json"

    def _items_path(self, thread_id: str) -> Path:
        return self._items_dir / f"{thread_id}.json"

    def _read_items(self, thread_id: str) -> list[ThreadItem]:
        path = self._items_path(thread_id)
        if not path.exists():
            return []
        return THREAD_ITEMS_ADAPTER.validate_python(json.loads(path.read_text()))

    def _write_items(self, thread_id: str, items: list[ThreadItem]) -> None:
        payload = [item.model_dump(mode="json") for item in items]
        self._items_path(thread_id).write_text(json.dumps(payload, indent=2, sort_keys=True))

    def _paginate(
        self,
        rows: list[Any],
        *,
        after: str | None,
        limit: int,
        order: str,
        sort_key: Callable[[Any], Any],
        cursor_key: Callable[[Any], str],
    ) -> Page[Any]:
        """Apply the simple pagination contract used by the starter store."""

        sorted_rows = sorted(rows, key=sort_key, reverse=order == "desc")
        start_index = 0
        if after:
            for index, row in enumerate(sorted_rows):
                if cursor_key(row) == after:
                    start_index = index + 1
                    break
        data = sorted_rows[start_index : start_index + limit]
        has_more = start_index + limit < len(sorted_rows)
        next_after = cursor_key(data[-1]) if has_more and data else None
        return Page(data=data, has_more=has_more, after=next_after)

    def _belongs_to_user(
        self,
        metadata: dict[str, Any] | None,
        context: dict[str, str],
    ) -> bool:
        if metadata is None:
            return False
        return metadata.get("starter_user_id") == context.get("user_id")


def resolve_chat_storage_root(storage_uri: str) -> Path:
    """Resolve the starter chat storage root from the configured storage URI."""

    parsed = urlparse(storage_uri)
    if parsed.scheme in {"", "file"}:
        if parsed.scheme == "file":
            if parsed.netloc in {"", "."}:
                base_path = Path(f"{parsed.netloc}{parsed.path}")
            else:
                base_path = Path(f"/{parsed.netloc}{parsed.path}")
        else:
            base_path = Path(parsed.path or storage_uri)
    else:
        base_path = Path("./var/data")
    return base_path.expanduser().resolve() / "chatkit"
