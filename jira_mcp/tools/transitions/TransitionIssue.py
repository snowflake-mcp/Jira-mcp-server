import logging
from typing import Any

logger = logging.getLogger('jira_tools')


class TransitionIssue:
    """Mixin that provides Jira issue status transition capabilities."""

    def transition_issue(self, issue_key: str, transition_name: str) -> dict[str, Any]:
        """Transition a Jira issue to a new status by transition name."""
        transitions = self.get_transitions(issue_key)

        match = next(
            (t for t in transitions if t["name"].lower() == transition_name.lower()),
            None,
        )

        if match is None:
            available = [t["name"] for t in transitions]
            return {
                "error": f"Transition '{transition_name}' not found for {issue_key}.",
                "available_transitions": available,
            }

        self.jira_request(
            "POST",
            f"issue/{issue_key}/transitions",
            data={"transition": {"id": match["id"]}},
        )

        return {
            "success": True,
            "issue_key": issue_key,
            "transitioned_to": match["name"],
        }
