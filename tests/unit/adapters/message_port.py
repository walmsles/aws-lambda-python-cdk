from typing import Any, Dict, Optional

from services.event_api.runtime.adapters.ports.message_port import MessagePort


class FakeMessagePort(MessagePort):
    def send_event(
        self, message_id: str, body: Dict[str, Any], group_id: Optional[str]
    ):
        self.message_id = message_id
        self.body = body
        self.group_id = group_id
