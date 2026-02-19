"""
Browser Automation Tool for Anna AI
==================================
Provides browser control capabilities for automation tasks.

Features:
- Web navigation
- Element interaction (click, fill, select)
- Screenshot capture
- Form automation
- JavaScript execution
"""

import asyncio
import base64
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class BrowserType(Enum):
    """Supported browser types"""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


@dataclass
class BrowserElement:
    """Represents a DOM element"""
    selector: str
    tag_name: str
    text: str
    attributes: Dict[str, str]
    visible: bool


class BrowserTool:
    """
    Browser automation tool

    Provides headless browser control for:
    - Web scraping
    - Form automation
    - Testing
    - Screenshot capture
    """

    def __init__(
        self,
        browser_type: str = "chromium",
        headless: bool = False,
        viewport: Optional[Dict[str, int]] = None
    ):
        """
        Initialize browser tool

        Args:
            browser_type: Browser to use (chromium, firefox, webkit)
            headless: Run browser headless
            viewport: Viewport size
        """
        self.browser_type = BrowserType(browser_type)
        self.headless = headless
        self.viewport = viewport or {"width": 1280, "height": 720}

        self._browser = None
        self._context = None
        self._page = None

    # =========================================================================
    # Lifecycle
    # =========================================================================

    async def start(self) -> Dict[str, Any]:
        """
        Start browser

        Returns:
            Status dictionary
        """
        try:
            from playwright.async_api import async_playwright

            playwright = await async_playwright().start()

            if self.browser_type == BrowserType.CHROMIUM:
                self._browser = await playwright.chromium.launch(
                    headless=self.headless
                )
            elif self.browser_type == BrowserType.FIREFOX:
                self._browser = await playwright.firefox.launch(
                    headless=self.headless
                )
            else:
                self._browser = await playwright.webkit.launch(
                    headless=self.headless
                )

            self._context = await self._browser.new_context(
                viewport=self.viewport,
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            self._page = await self._context.new_page()

            return {
                "success": True,
                "message": f"Browser started: {self.browser_type.value}",
                "headless": self.headless
            }

        except ImportError:
            return {
                "success": False,
                "error": "Playwright not installed. Run: pip install playwright && playwright install"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def stop(self) -> Dict[str, Any]:
        """Stop browser"""
        try:
            if self._page:
                await self._page.close()
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()

            self._page = None
            self._context = None
            self._browser = None

            return {"success": True, "message": "Browser stopped"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # Navigation
    # =========================================================================

    async def navigate(self, url: str, wait_until: str = "load") -> Dict[str, Any]:
        """
        Navigate to URL

        Args:
            url: Target URL
            wait_until: Wait for event (load, domcontentloaded, networkidle)

        Returns:
            Status and page info
        """
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        try:
            response = await self._page.goto(url, wait_until=wait_until)

            return {
                "success": True,
                "url": self._page.url,
                "title": await self._page.title(),
                "status": response.status if response else None
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def back(self) -> Dict[str, Any]:
        """Go back in history"""
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        await self._page.go_back()
        return {"success": True, "url": self._page.url}

    async def forward(self) -> Dict[str, Any]:
        """Go forward in history"""
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        await self._page.go_forward()
        return {"success": True, "url": self._page.url}

    async def reload(self) -> Dict[str, Any]:
        """Reload current page"""
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        await self._page.reload()
        return {"success": True, "url": self._page.url}

    # =========================================================================
    # Element Interaction
    # =========================================================================

    async def click(self, selector: str) -> Dict[str, Any]:
        """Click element"""
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        try:
            await self._page.click(selector)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def fill(self, selector: str, value: str) -> Dict[str, Any]:
        """Fill input field"""
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        try:
            await self._page.fill(selector, value)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def select(self, selector: str, value: str) -> Dict[str, Any]:
        """Select option from dropdown"""
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        try:
            await self._page.select_option(selector, value)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def hover(self, selector: str) -> Dict[str, Any]:
        """Hover over element"""
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        try:
            await self._page.hover(selector)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def type_text(
        self,
        selector: str,
        text: str,
        delay: int = 0
    ) -> Dict[str, Any]:
        """
        Type text with optional delay between keystrokes

        Args:
            selector: Element selector
            text: Text to type
            delay: Delay between keystrokes (ms)
        """
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        try:
            await self._page.type(selector, text, delay=delay)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # Content Extraction
    # =========================================================================

    async def get_page_info(self) -> Dict[str, Any]:
        """Get current page information"""
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        return {
            "success": True,
            "url": self._page.url,
            "title": await self._page.title(),
        }

    async def get_text(self, selector: str) -> Dict[str, Any]:
        """Get text content of element"""
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        try:
            text = await self._page.text_content(selector)
            return {"success": True, "text": text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_html(self, selector: Optional[str] = None) -> Dict[str, Any]:
        """Get HTML content"""
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        try:
            if selector:
                html = await self._page.inner_html(selector)
            else:
                html = await self._page.content()
            return {"success": True, "html": html}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_elements(self, selector: str) -> Dict[str, Any]:
        """Get all elements matching selector"""
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        try:
            elements = await self._page.query_selector_all(selector)
            results = []

            for el in elements:
                tag = await el.evaluate("e => e.tagName")
                text = await el.text_content() or ""
                results.append({
                    "tag": tag.lower(),
                    "text": text[:100]
                })

            return {"success": True, "count": len(results), "elements": results}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # Screenshot
    # =========================================================================

    async def screenshot(
        self,
        path: Optional[str] = None,
        full_page: bool = False
    ) -> Dict[str, Any]:
        """
        Take screenshot

        Args:
            path: Save path (if None, returns base64)
            full_page: Capture full scrollable page
        """
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        try:
            if path:
                await self._page.screenshot(path=path, full_page=full_page)
                return {"success": True, "path": path}
            else:
                data = await self._page.screenshot(full_page=full_page)
                b64 = base64.b64encode(data).decode()
                return {"success": True, "base64": b64}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # JavaScript
    # =========================================================================

    async def execute_js(self, script: str) -> Dict[str, Any]:
        """Execute JavaScript"""
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        try:
            result = await self._page.evaluate(script)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # Waiting
    # =========================================================================

    async def wait_for_selector(
        self,
        selector: str,
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """Wait for element to appear"""
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        try:
            await self._page.wait_for_selector(selector, timeout=timeout)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def wait_for_navigation(
        self,
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """Wait for navigation to complete"""
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        try:
            await self._page.wait_for_load_state("networkidle", timeout=timeout)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # Cookies & Storage
    # =========================================================================

    async def get_cookies(self) -> Dict[str, Any]:
        """Get all cookies"""
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        try:
            cookies = await self._context.cookies()
            return {"success": True, "cookies": cookies}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def set_cookies(self, cookies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Set cookies"""
        if not self._page:
            return {"success": False, "error": "Browser not started"}

        try:
            await self._context.add_cookies(cookies)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Convenience functions for tool interface
async def browser_start(
    browser_type: str = "chromium",
    headless: bool = False
) -> Dict[str, Any]:
    """Start browser - tool interface"""
    tool = BrowserTool(browser_type, headless)
    return await tool.start()


async def browser_navigate(url: str) -> Dict[str, Any]:
    """Navigate to URL - tool interface"""
    tool = BrowserTool()
    await tool.start()
    result = await tool.navigate(url)
    await tool.stop()
    return result


async def browser_screenshot(
    url: str,
    path: str,
    full_page: bool = False
) -> Dict[str, Any]:
    """Take screenshot - tool interface"""
    tool = BrowserTool(headless=True)
    await tool.start()
    await tool.navigate(url)
    result = await tool.screenshot(path, full_page)
    await tool.stop()
    return result
