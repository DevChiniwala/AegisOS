"""AegisOS MCP Server — Exposes fraud intelligence tools to AI assistants."""
import asyncio
import json
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

from packages.mcp_server.tools import TOOLS, execute_tool


def create_server() -> "Server":
    if not HAS_MCP:
        raise ImportError("MCP package not installed. Run: pip install mcp")

    server = Server("aegisos")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=t["name"],
                description=t["description"],
                inputSchema=t["input_schema"],
            )
            for t in TOOLS
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        result = await execute_tool(name, arguments)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    return server


async def main():
    if not HAS_MCP:
        print("ERROR: MCP package not installed. Run: pip install mcp")
        return

    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    asyncio.run(main())
