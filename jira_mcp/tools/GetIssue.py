import json
import logging
from typing import Any

logger = logging.getLogger('jira_tools')


def _extract_text_from_adf(node: dict | str | None) -> str:
    """Recursively extract plain text from Atlassian Document Format (ADF)."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        if node.get("type") == "text":
            return node.get("text", "")
        content = node.get("content", [])
        parts = [_extract_text_from_adf(child) for child in content]
        block_types = (
            "doc", "paragraph", "bulletList", "orderedList",
            "listItem", "blockquote", "codeBlock", "heading",
        )
        separator = "\n" if node.get("type") in block_types else ""
        return separator.join(parts)
    if isinstance(node, list):
        return "\n".join(_extract_text_from_adf(item) for item in node)
    return ""


class GetIssue:
    """Mixin that provides Jira issue retrieval capabilities."""

    def get_issue(self, issue_key: str) -> dict[str, Any]:
        """Fetch and format a Jira issue by key."""
        issue = self.jira_request("GET", f"issue/{issue_key}")
        return self._format_issue(issue)

    def _format_issue(self, issue: dict) -> dict[str, Any]:
        """Format a Jira issue response into a clean, readable structure."""
        fields = issue.get("fields", {})

        description_adf = fields.get("description")
        description = _extract_text_from_adf(description_adf) if description_adf else "No description"

        assignee = fields.get("assignee")
        reporter = fields.get("reporter")
        priority = fields.get("priority")
        parent = fields.get("parent")

        labels = fields.get("labels", [])
        components = [c.get("name", "") for c in fields.get("components", [])]

        comments_data = fields.get("comment", {}).get("comments", [])
        comments = []
        for c in comments_data:
            comment_body = _extract_text_from_adf(c.get("body"))
            comments.append({
                "id": c.get("id", ""),
                "author": c.get("author", {}).get("displayName", "Unknown"),
                "created": c.get("created", ""),
                "body": comment_body,
            })

        return {
            "key": issue.get("key", ""),
            "summary": fields.get("summary", ""),
            "status": fields.get("status", {}).get("name", "Unknown"),
            "issue_type": fields.get("issuetype", {}).get("name", "Unknown"),
            "priority": priority.get("name", "Unknown") if priority else "None",
            "assignee": assignee.get("displayName", "Unassigned") if assignee else "Unassigned",
            "reporter": reporter.get("displayName", "Unknown") if reporter else "Unknown",
            "labels": labels,
            "components": components,
            "parent": parent.get("key", "") if parent else None,
            "created": fields.get("created", ""),
            "updated": fields.get("updated", ""),
            "description": description,
            "comments": comments,
        }
