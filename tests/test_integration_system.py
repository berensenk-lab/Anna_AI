"""
Integration tests for full system startup.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.absolute()


class TestSystemStartup:
    """Test complete system initialization."""

    @patch("BASE.core.core_initializer.CoreInitializer")
    def test_app_initialization(self, mock_initializer, project_root):
        """Test that main.py can be imported and initialized."""
        from main import AnnaAIApp

        app = AnnaAIApp(gui_enabled=False, verbose=False)
        assert app is not None
        assert not app.gui_enabled
        assert not app.verbose

    def test_environment_setup(self, project_root):
        """Test environment setup creates required directories."""
        from main import AnnaAIApp

        app = AnnaAIApp(gui_enabled=False)
        result = app.setup_environment()

        assert result is True

        # Check directories were created
        required_dirs = [
            project_root / "logs",
            project_root / "personality" / "memory",
            project_root / "personality" / "base_memory",
            project_root / "models",
        ]

        for directory in required_dirs:
            assert directory.exists(), f"Directory not created: {directory}"

    @patch("BASE.core.config.Config")
    @patch("BASE.core.logger.Logger")
    def test_health_checks(self, mock_logger, mock_config):
        """Test system health check methods."""
        from main import AnnaAIApp

        app = AnnaAIApp(gui_enabled=False)

        # These should not raise
        assert app._check_python_version() is True
        assert app._check_project_structure() is True
        assert app._check_environment_variables() is True


class TestHealthCheckSystem:
    """Test individual health check functions."""

    def test_python_version_check(self):
        """Test Python version check."""
        from main import AnnaAIApp

        result = AnnaAIApp._check_python_version()
        assert isinstance(result, bool)

    def test_project_structure_check(self):
        """Test project structure check."""
        from main import AnnaAIApp

        result = AnnaAIApp._check_project_structure()
        assert isinstance(result, bool)
        assert result is True  # Should be true since tests run from repo

    def test_dependencies_check(self):
        """Test dependencies are available."""
        from main import AnnaAIApp

        result = AnnaAIApp._check_dependencies()
        assert isinstance(result, bool)


class TestCLIMode:
    """Test CLI mode operation."""

    @patch("builtins.input", side_effect=["test message", "exit"])
    @patch("main.AnnaAIApp.run_cli")
    def test_cli_initialization(self, mock_run_cli, mock_input):
        """Test CLI mode can be initialized."""
        from main import AnnaAIApp

        app = AnnaAIApp(gui_enabled=False)
        assert app.gui_enabled is False
