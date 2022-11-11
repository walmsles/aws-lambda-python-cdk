import os
from typing import Any, Dict

from .file_storage import FileStorage
from .message import MessageProvider
from .ports.file_port import FileStoragePort
from .ports.message_port import MessagePort


class EventService:
    def __init__(
        self,
        file_storage: FileStoragePort = None,
        message_provider: MessagePort = None,
    ):
        self._file_storage = file_storage
        self._message_provider = message_provider
        self._create_file_storage()
        self._create_message_provider()

    def _create_file_storage(self):
        if self._file_storage is None:
            self._file_storage = FileStorage()

    def _create_message_provider(self):
        if self._message_provider is None:
            sqs_queue_url = os.environ.get("EVENT_QUEUE", "queue_url")
            self._message_provider = MessageProvider(resource_id=sqs_queue_url)

    def process_event(self, transaction_id: str, event_detail: Dict[str, Any]):
        self._file_storage.save_file(transaction_id, event_detail)
        self._message_provider.send_event(
            message_id=transaction_id, body=event_detail, group_id=None
        )
        return True
