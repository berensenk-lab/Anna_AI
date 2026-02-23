"""
Regression tests for browser_tool lazy launch behavior.
"""

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from BASE.tools.installed.browser_tool.tool import BrowserTool


@pytest.mark.asyncio
async def test_browser_tool_start_does_not_create_page():
    config = MagicMock()
    config.browser_headless = True
    tool = BrowserTool(config=config, controls=MagicMock(), logger=MagicMock())

    await tool.start(thought_buffer=None, event_loop=None)

    assert tool.is_available() is True
    assert tool._page is None

    await tool.end()


@pytest.mark.asyncio
async def test_browser_tool_execute_lazily_initializes_page():
    config = MagicMock()
    config.browser_headless = True
    tool = BrowserTool(config=config, controls=MagicMock(), logger=MagicMock())

    await tool.start(thought_buffer=None, event_loop=None)

    class FakePage:
        url = "https://example.com"

        async def title(self):
            return "Example Domain"

    async def fake_ensure_ready(self):
        self._page = FakePage()
        return True

    with patch.object(BrowserTool, "_ensure_browser_ready", new=fake_ensure_ready):
        result = await tool.execute("get_page_info", [])
    assert result["success"] is True
    assert "Example Domain" in result["content"]

    await tool.end()
