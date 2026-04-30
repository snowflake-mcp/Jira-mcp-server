import logging
from typing import Any

import requests

logger = logging.getLogger('jira_tools')


class DeleteComment:
    """Mixin that provides Jira comment deletion capabilities."""

    def delete_comment(self, issue_key: str, comment_id: str) -> dict[str, Any]:
        """Delete a comment from a Jira issue."""
        session = self.verify_link()
        url = (
            f"{self.config['base_url'].rstrip('/')}"
            f"/rest/api/3/issue/{issue_key}/comment/{comment_id}"
        )
        response = session.delete(url)
        if not response.ok:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text[:500]
            raise requests.exceptions.HTTPError(
                f"HTTP {response.status_code}: {error_body}",
                response=response,
            )
        return {
            "status": "success",
            "issue_key": issue_key,
            "comment_id": comment_id,
            "message": f"Comment {comment_id} deleted from {issue_key}",
        }
