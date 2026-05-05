import json
import logging
from typing import Any

from dotenv import load_dotenv, find_dotenv
import mcp.server.stdio
from mcp.server import Server
from mcp.types import Tool, TextContent
from connection import JiraConnection

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('jira_server')

load_dotenv(find_dotenv())


class JiraServer(Server):
    """MCP server that handles Jira operations."""

    def __init__(self) -> None:
        super().__init__(name="jira-server")
        self.db = JiraConnection()
        logger.info("JiraServer initialized")

        @self.list_tools()
        async def get_supported_operations():
            """Return list of available tools."""
            return [
                Tool(
                    name="get_issue",
                    description="Get the full content of a Jira issue/ticket by its key (e.g. PROJ-123). "
                                "Returns summary, description, status, assignee, reporter, priority, "
                                "labels, components, and comments.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The Jira issue key, e.g. PROJ-123"
                            }
                        },
                        "required": ["issue_key"]
                    }
                ),
                Tool(
                    name="list_user_issues",
                    description="List all Jira issues/tickets assigned to a user. "
                                "If no username is provided, lists issues for the current authenticated user. "
                                "Can optionally filter by status (e.g. Open, In Progress, Done).",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "username": {
                                "type": "string",
                                "description": "The Jira display name or email of the user. "
                                               "Leave empty for the current authenticated user."
                            },
                            "status": {
                                "type": "string",
                                "description": "Filter by status, e.g. 'Open', 'In Progress', 'Done' (optional)"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of issues to return (default 50)",
                                "default": 50
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="add_comment",
                    description="Add a comment to a Jira issue/ticket.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The Jira issue key, e.g. PROJ-123"
                            },
                            "comment_text": {
                                "type": "string",
                                "description": "The comment text to add to the issue"
                            }
                        },
                        "required": ["issue_key", "comment_text"]
                    }
                ),
                Tool(
                    name="edit_comment",
                    description="Edit an existing comment on a Jira issue/ticket. "
                                "Requires the comment ID (use get_issue to find comment IDs).",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The Jira issue key, e.g. PROJ-123"
                            },
                            "comment_id": {
                                "type": "string",
                                "description": "The ID of the comment to edit"
                            },
                            "comment_text": {
                                "type": "string",
                                "description": "The new comment text"
                            }
                        },
                        "required": ["issue_key", "comment_id", "comment_text"]
                    }
                ),
                Tool(
                    name="delete_comment",
                    description="Delete a comment from a Jira issue/ticket. "
                                "Requires the comment ID (use get_issue to find comment IDs).",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The Jira issue key, e.g. PROJ-123"
                            },
                            "comment_id": {
                                "type": "string",
                                "description": "The ID of the comment to delete"
                            }
                        },
                        "required": ["issue_key", "comment_id"]
                    }
                ),
                Tool(
                    name="get_transitions",
                    description="Get the available status transitions for a Jira issue. "
                                "Use this to discover which statuses the issue can be moved to "
                                "(e.g. 'In Progress', 'Done', 'Closed').",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The Jira issue key, e.g. PROJ-123"
                            }
                        },
                        "required": ["issue_key"]
                    }
                ),
                Tool(
                    name="transition_issue",
                    description="Change the status of a Jira issue by transitioning it to a new state "
                                "(e.g. from 'Backlog' to 'In Progress', or 'In Progress' to 'Done'). "
                                "Use get_transitions first to see available transition names.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The Jira issue key, e.g. PROJ-123"
                            },
                            "transition_name": {
                                "type": "string",
                                "description": "The name of the transition to apply, e.g. 'In Progress', 'Done', 'Closed'"
                            }
                        },
                        "required": ["issue_key", "transition_name"]
                    }
                ),
            ]

        @self.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Route tool calls to the appropriate handler."""
            logger.info(f"Tool called: {name} with args: {arguments}")

            try:
                if name == "get_issue":
                    issue_key = arguments.get("issue_key", "")
                    result = self.db.get_issue(issue_key)
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                elif name == "list_user_issues":
                    username = arguments.get("username") or None
                    status = arguments.get("status") or None
                    max_results = arguments.get("max_results", 50)
                    result = self.db.list_user_issues(username, status, max_results)
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                elif name == "add_comment":
                    issue_key = arguments.get("issue_key", "")
                    comment_text = arguments.get("comment_text", "")
                    result = self.db.add_comment(issue_key, comment_text)
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                elif name == "edit_comment":
                    issue_key = arguments.get("issue_key", "")
                    comment_id = arguments.get("comment_id", "")
                    comment_text = arguments.get("comment_text", "")
                    result = self.db.edit_comment(issue_key, comment_id, comment_text)
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                elif name == "delete_comment":
                    issue_key = arguments.get("issue_key", "")
                    comment_id = arguments.get("comment_id", "")
                    result = self.db.delete_comment(issue_key, comment_id)
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                elif name == "get_transitions":
                    issue_key = arguments.get("issue_key", "")
                    result = self.db.get_transitions(issue_key)
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                elif name == "transition_issue":
                    issue_key = arguments.get("issue_key", "")
                    transition_name = arguments.get("transition_name", "")
                    result = self.db.transition_issue(issue_key, transition_name)
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]

            except Exception as e:
                error_msg = f"Error executing {name}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return [TextContent(type="text", text=json.dumps({"error": error_msg}))]

    def __del__(self):
        """Clean up connection on server shutdown."""
        if hasattr(self, 'db'):
            self.db.cleanup()
