"""
MCP (Model Context Protocol) Integration for Anna AI
====================================================

This module provides MCP client functionality to connect Anna AI
to external tools and services via the MCP protocol.

Usage:
    from BASE.integrations.mcp_client import MCPClient, get_mcp_manager

    # Get global manager
    manager = get_mcp_manager()

    # Add a server
    client = manager.add_server('database', 'http://localhost:3000')

    # Connect and use tools
    await client.connect()
    result = await client.call_tool('query', {'sql': 'SELECT * FROM users'})
"""

from BASE.integrations.mcp_client import (
    MCPClient,
    MCPClientManager,
    MCPTool,
    MCPMessage,
    MCPConnectionState,
    get_mcp_manager
)

__all__ = [
    'MCPClient',
    'MCPClientManager',
    'MCPTool',
    'MCPMessage',
    'MCPConnectionState',
    'get_mcp_manager'
]
