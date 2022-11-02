import json

from services.event_api.runtime.adapters.ports.file_port import FileStorageProvider


class FakeStorage(FileStorageProvider):
    def __init__(self):
        super().__init__()
        self.read_filename = None
        self.save_filename = None
        self.save_content = None

    def read_file(self, filename: str) -> str:
        self.read_filename = filename

    def save_file(self, filename: str, content: str) -> None:
        self.save_filename = f"{filename}.json"
        self.save_content = json.dumps(content)
