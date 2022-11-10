from typing import Any, Dict, Optional

from services.event_api.runtime.adapters.ports.message_port import MessagePort


class FakeMessagePort(MessagePort):
    def __init__(self, resource_id: str):
        super().__init__(resource_id)

    def send_event(
        self, message_id: str, body: Dict[str, Any], group_id: Optional[str]
    ):
        self.message_id = message_id
        self.body = body
