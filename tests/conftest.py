import pytest
import logging


@pytest.fixture(autouse=True)
def disable_logging():
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)

