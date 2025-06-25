import pytest
import logging
from utility.logger import get_logger

class TestLogger:
    def test_get_logger_default(self):
        logger = get_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "peerless"

    def test_get_logger_custom_name(self):
        logger = get_logger("test_logger")
        assert logger.name == "test_logger"

    def test_get_logger_prevents_duplicate_handlers(self):
        logger1 = get_logger("duplicate_test")
        initial_handler_count = len(logger1.handlers)
        
        logger2 = get_logger("duplicate_test")
        assert len(logger2.handlers) == initial_handler_count
        assert logger1 is logger2
