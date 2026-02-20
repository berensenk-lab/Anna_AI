"""
Regression tests for CoreInitializer startup behavior.
"""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from BASE.core.core_initializer import CoreInitializer


def test_inject_tool_manager_does_not_restart_tools():
    """_inject_tool_manager should not call _start_tool/run_coroutine_threadsafe."""
    logger = MagicMock()
    ai_core = SimpleNamespace(gui_logger=None)

    initializer = CoreInitializer(
        ai_core=ai_core,
        config=MagicMock(),
        controls=MagicMock(),
        project_root=Path("."),
        logger=logger,
        main_loop=object(),
    )

    thought_processor = SimpleNamespace(
        thought_buffer=MagicMock(),
        tool_manager=None,
        verify_tool_injection=MagicMock(return_value=True),
    )

    processing_delegator = MagicMock()
    processing_delegator.thought_processor = thought_processor

    tool_manager = MagicMock()
    tool_manager.get_enabled_tool_names.return_value = ["group_chat"]
    tool_manager._tool_metadata = {"group_chat": {}}

    def _set_tool_manager(manager):
        thought_processor.tool_manager = manager

    processing_delegator.set_tool_manager.side_effect = _set_tool_manager

    initializer.processing_delegator = processing_delegator
    initializer.tool_manager = tool_manager

    with patch("BASE.core.core_initializer.asyncio.run_coroutine_threadsafe") as run_threadsafe:
        initializer._inject_tool_manager()
        run_threadsafe.assert_not_called()

    tool_manager.set_event_loop.assert_called_once_with(initializer.main_loop)
    tool_manager.set_thought_buffer.assert_called_once_with(thought_processor.thought_buffer)
    assert thought_processor.tool_manager is tool_manager
