import json

from adapters.service import ProcessorService
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.batch import (
    BatchProcessor,
    EventType,
    batch_processor,
)
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
processor = BatchProcessor(event_type=EventType.SQS)
service: ProcessorService = ProcessorService()


def record_handler(record: SQSRecord):
    payload: str = record.body
    if payload:
        event: dict = json.loads(payload)
        message_id = event.get("message_id")
        content = event.get("body")
        service.store_event(message_id, content)


@logger.inject_lambda_context(log_event=True)
@batch_processor(record_handler=record_handler, processor=processor)
def lambda_handler(event, context: LambdaContext):
    return processor.response()
