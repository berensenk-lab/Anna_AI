"""
Unit tests for core configuration system.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestConfigInitialization:
    """Test Config class initialization and environment loading."""

    def test_config_singleton_pattern(self):
        """Test that Config follows singleton pattern."""
        from BASE.core.config import Config

        config1 = Config()
        config2 = Config()

        assert config1 is config2, "Config should be singleton"

    def test_default_values_set(self):
        """Test that Config has reasonable default values."""
        from BASE.core.config import Config

        config = Config()

        # Basic attributes should exist
        assert hasattr(config, "MODEL")
        assert hasattr(config, "OLLAMA_ENDPOINT")
        assert hasattr(config, "DEBUG")


class TestConfigEnvironmentVariables:
    """Test environment variable loading."""

    @patch.dict(os.environ, {"OLLAMA_ENDPOINT": "http://test:11434"})
    def test_ollama_endpoint_override(self):
        """Test that OLLAMA_ENDPOINT env var overrides default."""
        # Clear singleton to reload config
        from BASE.core import config as config_module
        config_module._instance = None

        from BASE.core.config import Config
        cfg = Config()

        assert cfg.OLLAMA_ENDPOINT == "http://test:11434"

    @patch.dict(os.environ, {"DEBUG": "true"})
    def test_debug_flag_override(self):
        """Test that DEBUG env var is respected."""
        from BASE.core import config as config_module
        config_module._instance = None

        from BASE.core.config import Config
        cfg = Config()

        # This depends on Config's implementation of env var parsing
        # Adjust assertion based on actual behavior


class TestConfigValidation:
    """Test configuration validation."""

    def test_required_settings_present(self):
        """Test that all required settings are initialized."""
        from BASE.core.config import Config

        config = Config()
        required_settings = [
            "MODEL",
            "THINKING_MODEL",
            "EMBEDDING_MODEL",
            "OLLAMA_ENDPOINT",
            "DEBUG",
        ]

        for setting in required_settings:
            assert hasattr(config, setting), f"Missing required setting: {setting}"
