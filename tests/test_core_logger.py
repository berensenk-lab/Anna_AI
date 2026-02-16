"""
Unit tests for logger system.
"""

import pytest
from unittest.mock import MagicMock, patch
from BASE.core.logger import MessageType


class TestMessageTypes:
    """Test message type enumeration."""

    def test_message_types_defined(self):
        """Test that all expected message types are defined."""
        expected_types = [
            "SYSTEM",
            "USER",
            "AGENT",
            "TOOL",
            "ERROR",
            "THINKING",
            "MEMORY",
        ]

        for msg_type in expected_types:
            assert hasattr(MessageType, msg_type), f"Missing message type: {msg_type}"


class TestLoggerInitialization:
    """Test Logger initialization."""

    def test_logger_creation(self, mock_config):
        """Test that Logger can be instantiated."""
        from BASE.core.logger import Logger

        logger = Logger(mock_config)
        assert logger is not None
        assert logger.config == mock_config

    def test_logger_logging_method(self, mock_config):
        """Test that Logger has log method."""
        from BASE.core.logger import Logger

        logger = Logger(mock_config)
        assert hasattr(logger, "log")
        assert callable(logger.log)


class TestLoggerLogging:
    """Test logging functionality."""

    def test_log_message_stored(self, mock_config):
        """Test that logged messages are stored."""
        from BASE.core.logger import Logger

        logger = Logger(mock_config)

        # Should not raise
        logger.log(
            "Test message",
            MessageType.SYSTEM,
            extra_info={"test": "value"}
        )

    def test_log_different_message_types(self, mock_config):
        """Test logging different message types."""
        from BASE.core.logger import Logger

        logger = Logger(mock_config)

        message_types = [
            MessageType.SYSTEM,
            MessageType.USER,
            MessageType.AGENT,
            MessageType.ERROR,
        ]

        for msg_type in message_types:
            # Should not raise
            logger.log("Test message", msg_type)
