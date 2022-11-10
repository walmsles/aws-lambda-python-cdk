from typing import Dict, Optional

from .ports.event_store import EventStoragePort
from .table_store import TableStore


class ProcessorService:
    def __init__(self, storage_service: Optional[EventStoragePort] = None) -> None:
        self._storage = storage_service
        self._create_storage()

    def create_storage(self) -> None:
        if self._storage is None:
            self._storage = TableStore()

    def store_event(event: Dict) -> None:
        pass
