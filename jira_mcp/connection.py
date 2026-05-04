import os
import base64
import logging
import json
from typing import Optional, Any

import requests
from dotenv import load_dotenv, find_dotenv
from tools.GetIssue import GetIssue
from tools.ListUserIssues import ListUserIssues
from tools.comments.AddComment import AddComment
from tools.comments.EditComment import EditComment
from tools.comments.DeleteComment import DeleteComment
from tools.transitions.GetTransitions import GetTransitions
from tools.transitions.TransitionIssue import TransitionIssue

logger = logging.getLogger('jira_connection')

load_dotenv(find_dotenv())


class JiraConnection(GetIssue, ListUserIssues, AddComment, EditComment, DeleteComment, GetTransitions, TransitionIssue):
    """Manages Jira API connections and request execution."""

    def __init__(self) -> None:
        self.config = {
            "base_url": os.getenv("JIRA_BASE_URL", ""),
            "email": os.getenv("JIRA_EMAIL", ""),
            "api_token": os.getenv("JIRA_API_TOKEN", ""),
        }
        self.session: Optional[requests.Session] = None

        safe_config = {k: v for k, v in self.config.items() if k != "api_token"}
        logger.info(f"Initialized with config: {json.dumps(safe_config)}")

    def _get_auth_headers(self) -> dict[str, str]:
        if not all(self.config.values()):
            raise ValueError(
                "Missing Jira configuration. Set JIRA_BASE_URL, JIRA_EMAIL, "
                "and JIRA_API_TOKEN environment variables."
            )
        credentials = base64.b64encode(
            f"{self.config['email']}:{self.config['api_token']}".encode()
        ).decode()
        return {
            "Authorization": f"Basic {credentials}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def verify_link(self) -> requests.Session:
        """Ensure the HTTP session is available and configured."""
        try:
            if self.session is None:
                logger.info("Creating new Jira session...")
                self.session = requests.Session()
                self.session.headers.update(self._get_auth_headers())
                logger.info("New session established")

            return self.session

        except Exception as e:
            logger.error(f"Session error: {str(e)}")
            raise

    def jira_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict:
        """Execute a Jira REST API request."""
        session = self.verify_link()
        url = f"{self.config['base_url'].rstrip('/')}/rest/api/3/{endpoint.lstrip('/')}"

        response = session.request(method, url, params=params, json=data)
        if not response.ok:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text[:500]
            raise requests.exceptions.HTTPError(
                f"HTTP {response.status_code}: {error_body}",
                response=response,
            )
        if not response.content:
            return {}
        return response.json()

    def cleanup(self) -> None:
        """Safely close the HTTP session."""
        if self.session:
            try:
                self.session.close()
                logger.info("Session closed")
            except Exception as e:
                logger.error(f"Error closing session: {str(e)}")
            finally:
                self.session = None
