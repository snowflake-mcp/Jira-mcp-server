import logging
from typing import Any

logger = logging.getLogger('jira_tools')


class EditComment:
    """Mixin that provides Jira comment editing capabilities."""

    def edit_comment(self, issue_key: str, comment_id: str, comment_text: str) -> dict[str, Any]:
        """Edit an existing comment on a Jira issue."""
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
        result = self.jira_request("PUT", f"issue/{issue_key}/comment/{comment_id}", data=body)
        return {
            "status": "success",
            "issue_key": issue_key,
            "comment_id": comment_id,
            "author": result.get("updateAuthor", {}).get("displayName", "Unknown"),
            "updated": result.get("updated", ""),
            "body": comment_text,
        }
