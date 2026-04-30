"""
Jira Model Context Protocol (MCP) Server

This server enables AI assistants to interact with Jira through
the Model Context Protocol (MCP). It handles authentication,
API requests, and result formatting.
"""
import asyncio
import logging
import mcp.server.stdio
from server import JiraServer

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('jira_server')


async def start_service() -> None:
    """Start and run the MCP server."""
    try:
        server = JiraServer()
        initialization_options = server.create_initialization_options()
        logger.info("Starting server")

        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                initialization_options
            )
    except Exception as e:
        logger.critical(f"Server failed: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("Server shutting down")


if __name__ == "__main__":
    asyncio.run(start_service())
