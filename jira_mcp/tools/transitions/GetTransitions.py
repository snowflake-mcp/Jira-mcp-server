import logging
from typing import Any

logger = logging.getLogger('jira_tools')


class GetTransitions:
    """Mixin that provides Jira issue transition listing capabilities."""

    def get_transitions(self, issue_key: str) -> list[dict[str, Any]]:
        """Fetch available transitions for a Jira issue."""
        result = self.jira_request("GET", f"issue/{issue_key}/transitions")
        return [
            {"id": t["id"], "name": t["name"]}
            for t in result.get("transitions", [])
        ]
