from abc import ABC, abstractmethod
from typing import Any, Dict


class EventStoragePort(ABC):
    @abstractmethod
    def store_event(self, id: str, content: Dict[str, Any]):
        pass
