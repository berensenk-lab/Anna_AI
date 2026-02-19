"""
MCP (Model Context Protocol) Client for Anna AI
================================================
Provides connectivity to MCP servers for external tool integrations.

MCP is an open protocol that allows AI models to connect to external
tools and services. This client enables Anna AI to:
- Connect to MCP servers
- Discover available tools on servers
- Execute remote tools
- Stream responses

Inspired by Claude Code's MCP support.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)


class MCPConnectionState(Enum):
    """MCP connection states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class MCPTool:
    """Represents a tool available on an MCP server"""
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    server_name: str = ""


@dataclass
class MCPMessage:
    """MCP protocol message"""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class MCPClient:
    """
    MCP Client for connecting to Model Context Protocol servers

    Supports:
    - Server discovery and connection
    - Tool listing and execution
    - Bidirectional communication
    - Server lifecycle management
    """

    def __init__(
        self,
        server_name: str,
        server_url: str,
        timeout: float = 30.0,
        auth_token: Optional[str] = None
    ):
        """
        Initialize MCP client

        Args:
            server_name: Name identifier for this server connection
            server_url: URL of MCP server (http/https or stdio command)
            timeout: Request timeout in seconds
            auth_token: Optional authentication token
        """
        self.server_name = server_name
        self.server_url = server_url
        self.timeout = timeout
        self.auth_token = auth_token

        self._state = MCPConnectionState.DISCONNECTED
        self._tools: Dict[str, MCPTool] = {}
        self._request_id = 0
        self._connection = None
        self._callbacks: Dict[str, List[Callable]] = {
            'notification': [],
            'tools_changed': [],
            'error': []
        }

    @property
    def state(self) -> MCPConnectionState:
        """Get current connection state"""
        return self._state

    @property
    def tools(self) -> List[MCPTool]:
        """Get list of available tools"""
        return list(self._tools.values())

    @property
    def is_connected(self) -> bool:
        """Check if connected to server"""
        return self._state == MCPConnectionState.CONNECTED

    # =========================================================================
    # Connection Management
    # =========================================================================

    async def connect(self) -> bool:
        """
        Connect to MCP server

        Returns:
            True if connection successful
        """
        try:
            self._state = MCPConnectionState.CONNECTING
            logger.info(f"[MCP] Connecting to {self.server_name} at {self.server_url}")

            # Determine connection type
            if self.server_url.startswith(('http://', 'https://')):
                success = await self._connect_http()
            else:
                success = await self._connect_stdio()

            if success:
                self._state = MCPConnectionState.CONNECTED
                # Initialize by listing tools
                await self.list_tools()
                logger.info(f"[MCP] Connected to {self.server_name}, {len(self._tools)} tools available")
                return True
            else:
                self._state = MCPConnectionState.ERROR
                return False

        except Exception as e:
            logger.error(f"[MCP] Connection failed: {e}")
            self._state = MCPConnectionState.ERROR
            return False

    async def _connect_http(self) -> bool:
        """Connect via HTTP/WebSocket"""
        # Initialize connection - in a full implementation,
        # this would establish WebSocket or SSE connection
        try:
            # Test connection with initialize request
            response = await self._send_request(
                'initialize',
                {
                    'protocolVersion': '2024-11-05',
                    'capabilities': {},
                    'clientInfo': {
                        'name': 'anna-ai',
                        'version': '1.0.0'
                    }
                }
            )
            return response is not None
        except Exception as e:
            logger.error(f"[MCP] HTTP connection error: {e}")
            return False

    async def _connect_stdio(self) -> bool:
        """Connect via stdio (local command)"""
        # For stdio connections, would spawn subprocess
        # This is a simplified implementation
        logger.info(f"[MCP] Stdio connection not fully implemented")
        return False

    async def disconnect(self):
        """Disconnect from MCP server"""
        if self._state == MCPConnectionState.CONNECTED:
            try:
                await self._send_notification('shutdown')
            except:
                pass

        self._state = MCPConnectionState.DISCONNECTED
        self._tools.clear()
        logger.info(f"[MCP] Disconnected from {self.server_name}")

    # =========================================================================
    # Tool Operations
    # =========================================================================

    async def list_tools(self) -> List[MCPTool]:
        """
        List available tools on the server

        Returns:
            List of MCPTool objects
        """
        try:
            response = await self._send_request('tools/list')

            if response and 'result' in response:
                tools = response['result'].get('tools', [])
                self._tools.clear()

                for tool_data in tools:
                    tool = MCPTool(
                        name=tool_data['name'],
                        description=tool_data.get('description', ''),
                        input_schema=tool_data.get('inputSchema', {}),
                        server_name=self.server_name
                    )
                    self._tools[tool.name] = tool

                logger.info(f"[MCP] Listed {len(self._tools)} tools from {self.server_name}")
                return list(self._tools.values())

            return []

        except Exception as e:
            logger.error(f"[MCP] Failed to list tools: {e}")
            return []

    async def call_tool(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call a tool on the MCP server

        Args:
            tool_name: Name of tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        if not self.is_connected:
            return {
                'success': False,
                'error': 'Not connected to MCP server'
            }

        if tool_name not in self._tools:
            return {
                'success': False,
                'error': f'Tool not found: {tool_name}'
            }

        try:
            response = await self._send_request(
                'tools/call',
                {
                    'name': tool_name,
                    'arguments': arguments or {}
                }
            )

            if response and 'result' in response:
                return {
                    'success': True,
                    'result': response['result']
                }
            else:
                return {
                    'success': False,
                    'error': 'Invalid response from server'
                }

        except Exception as e:
            logger.error(f"[MCP] Tool call failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get a specific tool by name"""
        return self._tools.get(tool_name)

    # =========================================================================
    # Protocol Operations
    # =========================================================================

    async def _send_request(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send JSON-RPC request to server

        Args:
            method: RPC method name
            params: Method parameters

        Returns:
            Response dict or None on error
        """
        self._request_id += 1
        request_id = str(self._request_id)

        message = {
            'jsonrpc': '2.0',
            'id': request_id,
            'method': method,
        }

        if params:
            message['params'] = params

        # For HTTP connection
        if self.server_url.startswith(('http://', 'https://')):
            return await self._send_http_request(message)

        return None

    async def _send_http_request(self, message: Dict) -> Optional[Dict[str, Any]]:
        """Send HTTP request to MCP server"""
        try:
            headers = {
                'Content-Type': 'application/json'
            }

            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'

            # Prepare request
            data = json.dumps(message).encode('utf-8')

            req = urllib.request.Request(
                self.server_url,
                data=data,
                headers=headers,
                method='POST'
            )

            # Execute with timeout
            loop = asyncio.get_event_loop()

            def _execute():
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    return json.loads(response.read().decode('utf-8'))

            result = await loop.run_in_executor(None, _execute)
            return result

        except urllib.error.URLError as e:
            logger.error(f"[MCP] HTTP request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"[MCP] Invalid JSON response: {e}")
            return None
        except Exception as e:
            logger.error(f"[MCP] Request error: {e}")
            return None

    async def _send_notification(self, method: str, params: Optional[Dict] = None):
        """Send notification (no response expected)"""
        # Notifications don't get responses
        # Would be implemented similarly to _send_request but without ID
        pass

    # =========================================================================
    # Event Handling
    # =========================================================================

    def on(self, event: str, callback: Callable):
        """Register event callback"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def off(self, event: str, callback: Callable):
        """Unregister event callback"""
        if event in self._callbacks:
            self._callbacks[event].remove(callback)

    def _emit(self, event: str, *args):
        """Emit event to registered callbacks"""
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                try:
                    callback(*args)
                except Exception as e:
                    logger.error(f"[MCP] Callback error: {e}")


class MCPClientManager:
    """
    Manager for multiple MCP server connections
    """

    def __init__(self):
        self._clients: Dict[str, MCPClient] = {}

    def add_server(
        self,
        name: str,
        url: str,
        auth_token: Optional[str] = None
    ) -> MCPClient:
        """
        Add and connect to an MCP server

        Args:
            name: Server identifier
            url: Server URL
            auth_token: Optional auth token

        Returns:
            MCPClient instance
        """
        client = MCPClient(
            server_name=name,
            server_url=url,
            auth_token=auth_token
        )
        self._clients[name] = client
        return client

    def remove_server(self, name: str):
        """Remove MCP server connection"""
        if name in self._clients:
            client = self._clients[name]
            if client.is_connected:
                asyncio.create_task(client.disconnect())
            del self._clients[name]

    def get_client(self, name: str) -> Optional[MCPClient]:
        """Get MCP client by name"""
        return self._clients.get(name)

    def get_all_tools(self) -> List[MCPTool]:
        """Get all tools from all connected servers"""
        tools = []
        for client in self._clients.values():
            if client.is_connected:
                tools.extend(client.tools)
        return tools

    def get_all_connected(self) -> List[str]:
        """Get list of connected server names"""
        return [
            name for name, client in self._clients.items()
            if client.is_connected
        ]

    async def connect_all(self) -> Dict[str, bool]:
        """Connect to all registered servers"""
        results = {}
        for name, client in self._clients.items():
            results[name] = await client.connect()
        return results

    async def disconnect_all(self):
        """Disconnect from all servers"""
        for client in self._clients.values():
            await client.disconnect()

    @property
    def client_count(self) -> int:
        """Get number of registered clients"""
        return len(self._clients)

    @property
    def connected_count(self) -> int:
        """Get number of connected clients"""
        return len(self.get_all_connected())


# Global MCP manager instance
_mcp_manager: Optional[MCPClientManager] = None


def get_mcp_manager() -> MCPClientManager:
    """Get global MCP manager instance"""
    global _mcp_manager
    if _mcp_manager is None:
        _mcp_manager = MCPClientManager()
    return _mcp_manager
