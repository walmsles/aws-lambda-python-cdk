from abc import ABC, abstractmethod
from typing import Any, Dict


class FileStoragePort(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def save_file(self, filename: str, content: Dict[str, Any]):
        pass

    @abstractmethod
    def read_file(self, filename: str) -> str:
        pass
