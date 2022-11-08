from typing import Any, Dict

from .file_storage import FileStorage
from .message import MessageProvider


class EventService:
    def __init__(self, file_storage=None, message_provider=None):
        self._file_storage = file_storage
        self._message_provider = message_provider
        self._create_file_storage()
        self._create_message_provider()

    def _create_file_storage(self):
        if self._file_storage is None:
            self._file_storage = FileStorage()

    def _create_message_provider(self):
        if self._message_provider is None:
            self._message_provider = MessageProvider()

    def process_event(self, transaction_id: str, event_detail: Dict[str, Any]):
        self._file_storage.save_file(transaction_id, event_detail)
        return True
