from typing import Any, Dict, Optional

from .ports.event_store import EventStoragePort
from .table_store import TableStore


class ProcessorService:
    def __init__(self, storage_service: Optional[EventStoragePort] = None) -> None:
        self._storage: EventStoragePort = storage_service
        self._create_storage()

    def _create_storage(self) -> None:
        if self._storage is None:
            self._storage = TableStore()

    def store_event(self, message_id: str, content: Dict[str, Any]) -> None:
        self._storage.store_event(message_id, content)
