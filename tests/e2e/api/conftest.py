import pytest

from tests.e2e.api.infrastructure import EndToEndApiStack


@pytest.fixture(autouse=True, scope="module")
def infrastructure():
    """Setup and teardown logic for E2E test infrastructure

    Yields
    ------
    Dict[str, str]
        CloudFormation Outputs from deployed infrastructure
    """
    stack = EndToEndApiStack()
    try:
        yield stack.deploy()
    finally:
        stack.delete()
