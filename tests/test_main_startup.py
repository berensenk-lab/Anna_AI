"""
Regression tests for main startup and CLI scheduling behavior.
"""

import importlib
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock


def test_main_import_has_no_runtime_side_effect():
    """Importing main should not execute undefined startup side effects."""
    sys.modules.pop("main", None)
    module = importlib.import_module("main")
    assert hasattr(module, "AnnaAIApp")
    assert hasattr(module, "main")


def test_cli_schedules_user_message_on_core_loop(monkeypatch):
    """CLI mode should schedule message processing via run_coroutine_threadsafe."""
    import main

    app = main.AnnaAIApp(gui_enabled=False)

    process_user_message = MagicMock(return_value="mock_coro")
    app.ai_core = SimpleNamespace(
        main_loop=object(),
        process_user_message=process_user_message,
    )

    future = MagicMock()
    future.result.return_value = None
    run_threadsafe = MagicMock(return_value=future)

    inputs = iter(["hello", "exit"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(inputs))
    monkeypatch.setattr(main.asyncio, "run_coroutine_threadsafe", run_threadsafe)

    assert app.run_cli() is True

    process_user_message.assert_called_once_with("hello")
    run_threadsafe.assert_called_once_with("mock_coro", app.ai_core.main_loop)
    future.result.assert_called_once_with(timeout=30)
