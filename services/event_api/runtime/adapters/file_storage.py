import json
import os
from typing import TYPE_CHECKING, Any, Dict

import boto3

from .ports.file_port import FileStorageProvider

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


class FileStorage(FileStorageProvider):
    def __init__(self):
        super().__init__()

        self.s3_client: "S3Client" = boto3.client("s3")

        # read bucket name from envionrment variable
        self.bucket_name = os.environ.get("EVENT_BUCKET", "bucket")

    def read_file(self, filename: str) -> str:
        file_object = self.s3_client.get_object(Bucket=self.bucket_name, Key=filename)
        data: str = json.loads(file_object["Body"].read())
        return data

    def save_file(self, filename: str, content: Dict[str, Any]) -> None:
        self.s3_client.put_object(
            Body=json.dumps(content),
            Bucket=self.bucket_name,
            Key=f"{filename}.json",
        )
