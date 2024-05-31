import pytest
import logging
from logging import NullHandler


@pytest.fixture(autouse=True)
def disable_logging():
    logger = logging.getLogger()
    logger.handlers = [NullHandler()]
    yield
    logger.handlers = []


@pytest.fixture(autouse=True)
def disable_logging_for_specific_loggers():
    loggers = [
        logging.getLogger('queries_logger'),
        logging.getLogger('monitoring_logger'),
        logging.getLogger('error_handler')
    ]
    for logger in loggers:
        logger.addHandler(NullHandler())
    yield
    for logger in loggers:
        logger.handlers = []
