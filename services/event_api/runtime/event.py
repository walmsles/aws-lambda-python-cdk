from typing import Any, Dict

from .adapters.file_storage import FileStorage


class EventService:
    def __init__(self, file_storage=None):
        self._file_storage = file_storage
        if self._file_storage is None:
            self._file_storage = FileStorage()

    def process_event(self, transaction_id: str, event_detail: Dict[str, Any]):
        self._file_storage.save_file(transaction_id, event_detail)
        return True
