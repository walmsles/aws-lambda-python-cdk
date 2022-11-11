from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class MessagePort(ABC):
    """
    Message Provider
    ----------------
    Message provider abstract class to provide a port for sending messages to cloud infrastructure.
    Messages will have a message_id and a body and an optional group_id to enable grouping of messages.
    """

    def __init__(self, resource_id: str):
        self._resource_id = resource_id

    @abstractmethod
    def send_event(
        self, message_id: str, body: Dict[str, Any], group_id: Optional[str]
    ):
        pass
