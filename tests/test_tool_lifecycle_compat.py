"""
Compatibility tests for ToolLifecycleManager startup/shutdown APIs.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from BASE.handlers.tool_lifecycle import ToolLifecycleManager


class LegacyTool:
    def __init__(self, config, controls, logger=None):
        self._running = False

    async def initialize(self):
        self._running = True
        return True

    async def cleanup(self):
        self._running = False

    def is_available(self):
        return self._running


class StartEndTool:
    def __init__(self, config, controls, logger=None):
        self.started = False
        self.stopped = False

    async def start(self, thought_buffer=None, event_loop=None):
        self.started = True

    async def end(self):
        self.stopped = True

    def is_available(self):
        return self.started and not self.stopped


@pytest.mark.asyncio
async def test_lifecycle_supports_legacy_initialize_cleanup():
    manager = ToolLifecycleManager(project_root=Path("."), logger=MagicMock())
    manager._tool_metadata = {
        "legacy_tool": {"tool_file": Path("dummy.py")}
    }
    with patch.object(ToolLifecycleManager, "load_tool_class", return_value=LegacyTool):
        ok = await manager.start_tool("legacy_tool", config=MagicMock(), controls=MagicMock())
    assert ok is True
    assert "legacy_tool" in manager._active_tools
    assert manager._active_tools["legacy_tool"].is_available() is True

    stopped = await manager.stop_tool("legacy_tool")
    assert stopped is True
    assert "legacy_tool" not in manager._active_tools


@pytest.mark.asyncio
async def test_lifecycle_supports_start_end_with_tool_name_injection():
    manager = ToolLifecycleManager(project_root=Path("."), logger=MagicMock())
    manager._tool_metadata = {
        "modern_tool": {"tool_file": Path("dummy.py")}
    }
    with patch.object(ToolLifecycleManager, "load_tool_class", return_value=StartEndTool):
        ok = await manager.start_tool("modern_tool", config=MagicMock(), controls=MagicMock())
    assert ok is True
    tool = manager._active_tools["modern_tool"]
    assert tool.started is True
    assert getattr(tool, "tool_name", None) == "modern_tool"

    stopped = await manager.stop_tool("modern_tool")
    assert stopped is True
