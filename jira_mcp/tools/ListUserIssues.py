import logging
from typing import Any

logger = logging.getLogger('jira_tools')


class ListUserIssues:
    """Mixin that provides listing issues assigned to a user."""

    def list_user_issues(
        self,
        username: str | None = None,
        status: str | None = None,
        max_results: int = 50,
    ) -> dict[str, Any]:
        """List all issues assigned to a user via JQL search.

        If username is not provided, defaults to the current authenticated user.
        Optionally filter by status (e.g. 'Open', 'In Progress', 'Done').
        """
        if username:
            jql = f'assignee = "{username}"'
        else:
            jql = "assignee = currentUser()"

        if status:
            jql += f' AND status = "{status}"'

        jql += " ORDER BY updated DESC"

        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": "summary,status,priority,issuetype,assignee,updated,created,parent,labels",
        }

        result = self.jira_request("GET", "search/jql", params=params)

        issues = []
        for issue in result.get("issues", []):
            fields = issue.get("fields", {})
            priority = fields.get("priority")
            assignee = fields.get("assignee")
            parent = fields.get("parent")
            issues.append({
                "key": issue.get("key", ""),
                "summary": fields.get("summary", ""),
                "status": fields.get("status", {}).get("name", "Unknown"),
                "issue_type": fields.get("issuetype", {}).get("name", "Unknown"),
                "priority": priority.get("name", "Unknown") if priority else "None",
                "assignee": assignee.get("displayName", "Unassigned") if assignee else "Unassigned",
                "parent": parent.get("key", "") if parent else None,
                "labels": fields.get("labels", []),
                "created": fields.get("created", ""),
                "updated": fields.get("updated", ""),
            })

        return {
            "total": result.get("total", 0),
            "showing": len(issues),
            "issues": issues,
        }
