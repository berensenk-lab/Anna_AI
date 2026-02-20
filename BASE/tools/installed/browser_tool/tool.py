# Filename: BASE/tools/installed/browser_tool/tool.py
"""
Browser Automation Tool - BaseTool wrapper for Anna AI
=======================================================
Wraps Playwright-based browser automation into the BaseTool architecture.
Requires: pip install playwright && playwright install
"""
from typing import List, Dict, Any, Optional
from BASE.handlers.base_tool import BaseTool


class BrowserTool(BaseTool):
    """
    Browser automation tool using Playwright.
    Provides headless browser control for navigation, interaction,
    screenshots, and JavaScript execution.
    """

    __slots__ = ('_browser', '_context', '_page', '_playwright')

    @property
    def name(self) -> str:
        return "browser_tool"

    async def initialize(self) -> bool:
        """Initialize Playwright browser"""
        self._browser = None
        self._context = None
        self._page = None
        self._playwright = None

        try:
            from playwright.async_api import async_playwright
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=False)
            self._context = await self._browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            self._page = await self._context.new_page()

            if self._logger:
                self._logger.success("[BrowserTool] Playwright browser ready (Chromium)")
            return True

        except ImportError:
            if self._logger:
                self._logger.error(
                    "[BrowserTool] Playwright not installed. "
                    "Run: pip install playwright && playwright install"
                )
            return False
        except Exception as e:
            if self._logger:
                self._logger.error(f"[BrowserTool] Failed to start browser: {e}")
            return False

    async def cleanup(self):
        """Close browser and release resources"""
        try:
            if self._page:
                await self._page.close()
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception as e:
            if self._logger:
                self._logger.warning(f"[BrowserTool] Cleanup error: {e}")
        finally:
            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None

        if self._logger:
            self._logger.system("[BrowserTool] Browser closed")

    def is_available(self) -> bool:
        return self._page is not None

    async def execute(self, command: str, args: List[Any]) -> Dict[str, Any]:
        """Execute browser command"""
        if not self.is_available():
            return self._error_result(
                'Browser not available',
                guidance='Browser failed to initialize. Check Playwright installation.'
            )

        if self._logger:
            self._logger.tool(f"[BrowserTool] Command: '{command}', args: {args}")

        try:
            if command == 'navigate' or command == '':
                return await self._navigate(args)
            elif command == 'screenshot':
                return await self._screenshot(args)
            elif command == 'click':
                return await self._click(args)
            elif command == 'fill':
                return await self._fill(args)
            elif command == 'get_text':
                return await self._get_text(args)
            elif command == 'get_page_info':
                return await self._get_page_info()
            elif command == 'execute_js':
                return await self._execute_js(args)
            elif command == 'back':
                await self._page.go_back()
                return self._success_result(f"Navigated back to: {self._page.url}")
            elif command == 'forward':
                await self._page.go_forward()
                return self._success_result(f"Navigated forward to: {self._page.url}")
            elif command == 'reload':
                await self._page.reload()
                return self._success_result(f"Reloaded: {self._page.url}")
            else:
                return self._error_result(
                    f'Unknown command: {command}',
                    guidance='Available: navigate, screenshot, click, fill, get_text, '
                             'get_page_info, execute_js, back, forward, reload'
                )
        except Exception as e:
            if self._logger:
                self._logger.error(f"[BrowserTool] Command error: {e}")
            return self._error_result(f'Browser error: {str(e)}')

    # =========================================================================
    # COMMAND IMPLEMENTATIONS
    # =========================================================================

    async def _navigate(self, args: List[Any]) -> Dict[str, Any]:
        if not args or not args[0]:
            return self._error_result('No URL provided', guidance='Provide a URL to navigate to')

        url = str(args[0]).strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        response = await self._page.goto(url, wait_until='load')
        title = await self._page.title()
        status = response.status if response else None

        return self._success_result(
            f"Navigated to: {self._page.url}\nTitle: {title}",
            metadata={'url': self._page.url, 'title': title, 'status': status}
        )

    async def _screenshot(self, args: List[Any]) -> Dict[str, Any]:
        import base64
        path = str(args[0]).strip() if args and args[0] else None

        if path:
            await self._page.screenshot(path=path, full_page=False)
            return self._success_result(f"Screenshot saved to: {path}", metadata={'path': path})
        else:
            data = await self._page.screenshot(full_page=False)
            b64 = base64.b64encode(data).decode()
            return self._success_result(
                "Screenshot captured",
                metadata={'base64': b64[:100] + '...', 'size_bytes': len(data)}
            )

    async def _click(self, args: List[Any]) -> Dict[str, Any]:
        if not args or not args[0]:
            return self._error_result('No selector provided', guidance='Provide a CSS selector')
        selector = str(args[0]).strip()
        await self._page.click(selector)
        return self._success_result(f"Clicked: {selector}")

    async def _fill(self, args: List[Any]) -> Dict[str, Any]:
        if len(args) < 2:
            return self._error_result(
                'Requires selector and value',
                guidance='Provide a CSS selector and the value to fill'
            )
        selector = str(args[0]).strip()
        value = str(args[1])
        await self._page.fill(selector, value)
        return self._success_result(f"Filled '{selector}' with value")

    async def _get_text(self, args: List[Any]) -> Dict[str, Any]:
        if not args or not args[0]:
            return self._error_result('No selector provided', guidance='Provide a CSS selector')
        selector = str(args[0]).strip()
        text = await self._page.text_content(selector)
        return self._success_result(text or '(empty)', metadata={'selector': selector})

    async def _get_page_info(self) -> Dict[str, Any]:
        title = await self._page.title()
        return self._success_result(
            f"URL: {self._page.url}\nTitle: {title}",
            metadata={'url': self._page.url, 'title': title}
        )

    async def _execute_js(self, args: List[Any]) -> Dict[str, Any]:
        if not args or not args[0]:
            return self._error_result('No script provided', guidance='Provide JavaScript to execute')
        script = str(args[0])
        result = await self._page.evaluate(script)
        return self._success_result(
            f"JS result: {result}",
            metadata={'result': result}
        )
