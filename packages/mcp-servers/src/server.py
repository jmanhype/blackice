"""
BLACKICE MCP Server
===================

Unified MCP server that exposes all BLACKICE capabilities.
"""

import asyncio
import json
from typing import Any

from .solver_server import (
    SOLVER_TOOLS,
    handle_solve_bfs,
    handle_validate_plan,
)
from .filesystem_server import (
    FILESYSTEM_TOOLS,
    handle_read_file,
    handle_write_file,
    handle_list_files,
    handle_git_info,
    handle_git_commit,
    handle_git_diff,
)


# Tool registry
TOOLS = SOLVER_TOOLS + FILESYSTEM_TOOLS

HANDLERS = {
    # Solver tools
    "solve_bfs": handle_solve_bfs,
    "validate_plan": handle_validate_plan,
    # Filesystem tools
    "read_file": handle_read_file,
    "write_file": handle_write_file,
    "list_files": handle_list_files,
    "git_info": handle_git_info,
    "git_commit": handle_git_commit,
    "git_diff": handle_git_diff,
}


class BlackiceMCPServer:
    """
    MCP Server that exposes BLACKICE capabilities.

    This is a simplified implementation. For production, use the mcp package
    to create a proper MCP server.
    """

    def __init__(self):
        self.tools = TOOLS
        self.handlers = HANDLERS

    def list_tools(self) -> list[dict]:
        """List available tools."""
        return self.tools

    def call_tool(self, name: str, params: dict) -> dict:
        """Call a tool by name."""
        if name not in self.handlers:
            return {"error": f"Unknown tool: {name}"}

        try:
            return self.handlers[name](params)
        except Exception as e:
            return {"error": str(e)}

    async def handle_message(self, message: dict) -> dict:
        """Handle an MCP message."""
        method = message.get("method")

        if method == "tools/list":
            return {
                "tools": self.list_tools(),
            }

        elif method == "tools/call":
            params = message.get("params", {})
            tool_name = params.get("name")
            tool_params = params.get("arguments", {})
            result = self.call_tool(tool_name, tool_params)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2),
                    }
                ],
            }

        else:
            return {"error": f"Unknown method: {method}"}


async def run_stdio_server():
    """Run the MCP server over stdio."""
    import sys

    server = BlackiceMCPServer()

    # Read JSON-RPC messages from stdin, write to stdout
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)

    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

    writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
        asyncio.streams.FlowControlMixin, sys.stdout
    )
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, reader, asyncio.get_event_loop())

    while True:
        line = await reader.readline()
        if not line:
            break

        try:
            message = json.loads(line.decode())
            response = await server.handle_message(message)
            response["jsonrpc"] = "2.0"
            response["id"] = message.get("id")

            writer.write((json.dumps(response) + "\n").encode())
            await writer.drain()
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)},
            }
            writer.write((json.dumps(error_response) + "\n").encode())
            await writer.drain()


def main():
    """Entry point for the MCP server."""
    asyncio.run(run_stdio_server())


if __name__ == "__main__":
    main()
