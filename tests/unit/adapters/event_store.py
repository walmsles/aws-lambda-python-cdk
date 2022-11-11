from typing import Any, Dict

from services.event_processor.runtime.adapters.ports.event_store import EventStoragePort


class FakeEventStore(EventStoragePort):
    def __init__(self) -> None:
        self.message_id = None
        self.content = None

    def store_event(self, message_id: str, content: Dict[str, Any]):
        self.message_id = message_id
        self.content = content
