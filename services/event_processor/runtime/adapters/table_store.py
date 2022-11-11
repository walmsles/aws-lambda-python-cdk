import os
from typing import Any, Dict

import boto3
from mypy_boto3_dynamodb import DynamoDBClient

from .ports.event_store import EventStoragePort


class TableStore(EventStoragePort):
    def __init__(self) -> None:
        self._client: DynamoDBClient = boto3.resource("dynamodb")
        self._table = self._client.Table(os.environ.get("EVENT_STORE", "EventStore"))

    def store_event(self, message_id: str, content: Dict[str, Any]):
        self._table.put_item(
            Item={
                "message_id": message_id,
                "body": content,
            },
        )
