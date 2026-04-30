import logging
from typing import Any

logger = logging.getLogger('jira_tools')


class AddComment:
    """Mixin that provides Jira comment adding capabilities."""

    def add_comment(self, issue_key: str, comment_text: str) -> dict[str, Any]:
        """Add a comment to a Jira issue."""
        body = {
            "body": {
                "version": 1,
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment_text
                            }
                        ]
                    }
                ]
            }
        }
        result = self.jira_request("POST", f"issue/{issue_key}/comment", data=body)
        return {
            "status": "success",
            "issue_key": issue_key,
            "comment_id": result.get("id", ""),
            "author": result.get("author", {}).get("displayName", "Unknown"),
            "created": result.get("created", ""),
            "body": comment_text,
        }
