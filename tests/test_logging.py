import logging

from app.core.logging import get_logger


def test_get_logger_returns_configured_logger():
    logger = get_logger("projectrag.test")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "projectrag.test"
