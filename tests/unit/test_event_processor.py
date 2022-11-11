from services.event_processor.runtime.adapters.service import ProcessorService
from tests.unit.adapters.event_store import FakeEventStore


def test_event_processor():
    # GIVEN
    message_id = "xxx-111"
    content = {"event": "test-event", "data": {"key1": "value1"}}
    fake_event_store = FakeEventStore()
    service: ProcessorService = ProcessorService(storage_service=fake_event_store)

    # WHEN
    service.store_event(message_id, content)

    # THEN
    assert message_id == fake_event_store.message_id
    assert content == fake_event_store.content
