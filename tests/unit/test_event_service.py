import json

from services.event_api.runtime.event import EventService
from tests.unit.adapters.fake_storage import FakeStorage


def test_service_process_event():
    # Given
    transaction_id = "xxx-111"
    event_detail = {"event": "test-event", "data": {"key1": "value1"}}
    fake_storage = FakeStorage()

    event_service = EventService(file_storage=fake_storage)

    # When
    result = event_service.process_event(
        transaction_id=transaction_id, event_detail=event_detail
    )

    # Then
    assert result is True
    assert fake_storage.save_filename == "xxx-111.json"
    assert fake_storage.save_content == json.dumps(
        {"event": "test-event", "data": {"key1": "value1"}}
    )
