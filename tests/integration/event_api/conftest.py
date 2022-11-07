import pytest

from tests.integration.event_api.infrastructure import EventApiIntegrationStack


@pytest.fixture(autouse=True, scope="module")
def infrastructure():
    """Setup and teardown logic for E2E test infrastructure

    Yields
    ------
    Dict[str, str]
        CloudFormation Outputs from deployed infrastructure
    """
    stack = EventApiIntegrationStack()
    try:
        yield stack.deploy()
    finally:
        stack.delete()
