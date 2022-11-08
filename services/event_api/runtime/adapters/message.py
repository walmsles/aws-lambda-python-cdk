import json
from typing import TYPE_CHECKING, Any, Dict, Optional

import boto3

from .ports.message_port import MessagePort

if TYPE_CHECKING:
    from mypy_boto3_sqs import SQSClient


class MessageProvider(MessagePort):
    def __init__(self, resource_id: str):
        super().__init(resource_id)

        self._client: "SQSClient" = boto3.client("sqs")

    def send_event(
        self, message_id: str, body: Dict[str, Any], group_id: Optional[str] = None
    ):

        message_body = {"message_id": message_id, "body": body}

        # Submit Message to SQS Queue
        self._client.send_message(
            QueueUrl=self._resource_id, MessageBody=json.dumps(message_body)
        )
