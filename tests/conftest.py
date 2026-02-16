"""
Pytest configuration and shared fixtures.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def project_root():
    """Provide the project root path."""
    return PROJECT_ROOT


@pytest.fixture
def mock_config():
    """Provide a mock Config object."""
    config = MagicMock()
    config.MODEL = "mistral"
    config.THINKING_MODEL = "mistral"
    config.EMBEDDING_MODEL = "nomic-embed-text"
    config.OLLAMA_ENDPOINT = "http://localhost:11434"
    config.OLLAMA_TIMEOUT = 600
    config.LOG_LEVEL = "INFO"
    config.DEBUG = False
    return config


@pytest.fixture
def mock_logger():
    """Provide a mock Logger object."""
    logger = MagicMock()
    logger.log = MagicMock()
    return logger


@pytest.fixture
def mock_ai_core(mock_config, mock_logger):
    """Provide a mock AI core object."""
    core = MagicMock()
    core.config = mock_config
    core.logger = mock_logger
    core.process_user_message = MagicMock()
    core.get_response = MagicMock(return_value="Test response")
    return core
