from abc import ABC, abstractmethod
from typing import Dict


class InfrastructureProvider(ABC):
    @abstractmethod
    def deploy(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def create_resources(self):
        pass
