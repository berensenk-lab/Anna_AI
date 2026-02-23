"""
Tests for VTube Studio tool basic behavior.
"""

from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from BASE.tools.installed.vtube_studio.tool import VTubeStudioTool


@pytest.mark.asyncio
async def test_vtube_tool_initializes_with_defaults():
    config = MagicMock()
    config.project_root = Path(".")
    config.vtube_studio_ws_url = "ws://127.0.0.1:8001"
    config.vtube_studio_plugin_name = "Anna AI"
    config.vtube_studio_plugin_developer = "beren"
    config.vtube_studio_timeout = 5.0

    tool = VTubeStudioTool(config=config, controls=MagicMock(), logger=MagicMock())
    ok = await tool.initialize()
    assert ok is True

    tool._running = True
    assert tool.is_available() is True


@pytest.mark.asyncio
async def test_vtube_emotion_returns_not_found_when_hotkey_missing():
    config = MagicMock()
    config.project_root = Path(".")
    tool = VTubeStudioTool(config=config, controls=MagicMock(), logger=MagicMock())
    await tool.initialize()
    tool._running = True
    tool._ws_client_ready = True

    with patch.object(
        VTubeStudioTool,
        "_ensure_authenticated",
        return_value=(True, "ok"),
    ), patch.object(
        VTubeStudioTool,
        "_send_request",
        return_value={"data": {"availableHotkeys": [{"name": "wave", "hotkeyID": "1"}]}},
    ):
        result = await tool.execute("emotion", ["happy"])
    assert result["success"] is False
    assert "Hotkey not found" in result["content"]
