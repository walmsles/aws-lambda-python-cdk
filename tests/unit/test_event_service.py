import json

from services.event_api.runtime.adapters.service import EventService
from tests.unit.adapters.file_port import FakeStorage
from tests.unit.adapters.message_port import FakeMessagePort


def test_event_service():
    # Given
    transaction_id = "xxx-111"
    event_detail = {"event": "test-event", "data": {"key1": "value1"}}
    fake_storage = FakeStorage()
    fake_message = FakeMessagePort(resource_id="sqs_queue")
    event_service = EventService(
        file_storage=fake_storage, message_provider=fake_message
    )

    # When
    result = event_service.process_event(
        transaction_id=transaction_id, event_detail=event_detail
    )

    # Then
    assert result is True
    assert fake_storage.save_filename == f"{transaction_id}.json"
    assert fake_storage.save_content == json.dumps(
        {"event": "test-event", "data": {"key1": "value1"}}
    )
    assert fake_message.message_id == transaction_id
    assert fake_message.body == event_detail
