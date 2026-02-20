"""
Base Tool - Simplified Architecture
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import asyncio


class BaseTool(ABC):
    """Base class for all tools in the simplified architecture."""

    __slots__ = ("_config", "_controls", "_logger", "_running", "_context_task")

    def __init__(self, config, controls, logger=None):
        self._config = config
        self._controls = controls
        self._logger = logger
        self._running = False
        self._context_task = None

    @property
    @abstractmethod
    def name(self) -> str:
        """Return tool name (must match control mapping)."""

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the tool and return success."""

    @abstractmethod
    async def cleanup(self):
        """Cleanup resources allocated by the tool."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return whether tool can execute commands."""

    @abstractmethod
    async def execute(self, command: str, args: List[Any]) -> Dict[str, Any]:
        """Execute tool command."""

    def has_context_loop(self) -> bool:
        """Whether tool needs a background context loop."""
        return False

    async def context_loop(self, thought_buffer):
        """Optional background context loop."""

    async def start(self, thought_buffer=None, event_loop=None):
        """Start tool lifecycle."""
        if self._running:
            if self._logger:
                self._logger.warning(f"[{self.name}] Already running")
            return

        success = await self.initialize()
        if not success:
            if self._logger:
                self._logger.error(f"[{self.name}] Initialization failed")
            return

        self._running = True

        if self.has_context_loop() and thought_buffer and event_loop:
            self._context_task = event_loop.create_task(
                self._safe_context_loop(thought_buffer)
            )
            if self._logger:
                self._logger.system(f"[{self.name}] Context loop started")

        if self._logger:
            self._logger.success(f"[{self.name}] Tool started successfully")

    async def end(self):
        """Stop tool lifecycle."""
        if not self._running:
            return

        self._running = False

        if self._context_task:
            self._context_task.cancel()
            try:
                await self._context_task
            except asyncio.CancelledError:
                pass
            self._context_task = None
            if self._logger:
                self._logger.system(f"[{self.name}] Context loop stopped")

        await self.cleanup()

        if self._logger:
            self._logger.system(f"[{self.name}] Tool stopped")

    async def _safe_context_loop(self, thought_buffer):
        """Run context loop with cancellation/error safety."""
        try:
            await self.context_loop(thought_buffer)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if self._logger:
                self._logger.error(f"[{self.name}] Context loop error: {e}")

    def _success_result(
        self, content: str, metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create standardized success result."""
        return {
            "success": True,
            "content": content,
            "source": self.name,
            "metadata": metadata or {},
            "guidance": f"{self.name} executed successfully",
        }

    def _error_result(
        self,
        content: str,
        metadata: Optional[Dict] = None,
        guidance: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create standardized error result."""
        return {
            "success": False,
            "content": content,
            "source": self.name,
            "metadata": metadata or {},
            "guidance": guidance or f"{self.name} execution failed",
        }
