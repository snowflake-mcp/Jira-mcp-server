# Jira MCP Server

An MCP (Model Context Protocol) server that lets AI assistants read Jira tickets. This MCP server uses API token based authentication. 

-----

## Setup

### 1. Install dependencies

```bash
cd jira-mcp-server
pip install -r requirements.txt
```

### 2. Get your Jira API token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **Create API token**
3. Give it a label and copy the token

### 3. Configure environment variables

Create a `.env` file in the root of the repo:

```env
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=you@company.com
JIRA_API_TOKEN=your-api-token
```

### 4. Add to Cursor

Add the following to your Cursor MCP config (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "jira": {
      "command": "/full/path/to/jira-mcp-server/venv/bin/python",
      "args": ["/full/path/to/jira-mcp-server/jira_mcp/main.py"],
    }
  }
}
```

## Available Tools

### `get_issue`

Read the full content of a Jira issue by key.

**Parameters:**
- `issue_key` (string) — The Jira issue key, e.g. `PROJ-123`

**Returns:** JSON with summary, description, status, assignee, reporter, priority, labels, components, and comments.

---

### `list_user_issues`

List all Jira issues assigned to a user, with optional status filtering.

**Parameters:**
- `username` (string, optional) — Jira display name or email. Defaults to the authenticated user.
- `status` (string, optional) — Filter by status, e.g. `Open`, `In Progress`, `Done`
- `max_results` (integer, optional) — Maximum number of issues to return (default: `50`)

**Returns:** JSON array of issues with key, summary, status, priority, and assignee.

---

### `add_comment`

Add a comment to a Jira issue.

**Parameters:**
- `issue_key` (string) — The Jira issue key, e.g. `PROJ-123`
- `comment_text` (string) — The text of the comment to add

**Returns:** JSON with the new comment's ID, author, creation time, and body.

---

### `edit_comment`

Edit an existing comment on a Jira issue.

**Parameters:**
- `issue_key` (string) — The Jira issue key, e.g. `PROJ-123`
- `comment_id` (string) — The ID of the comment to edit (use `get_issue` to find comment IDs)
- `comment_text` (string) — The updated comment text

**Returns:** JSON confirming the update with the comment's ID and new body.

---

### `delete_comment`

Delete a comment from a Jira issue.

**Parameters:**
- `issue_key` (string) — The Jira issue key, e.g. `PROJ-123`
- `comment_id` (string) — The ID of the comment to delete (use `get_issue` to find comment IDs)

**Returns:** JSON confirming the deletion.

---

### `get_transitions`

Get the available status transitions for a Jira issue.

**Parameters:**
- `issue_key` (string) — The Jira issue key, e.g. `PROJ-123`

**Returns:** List of available transitions with their IDs and names (e.g. `In Progress`, `Done`, `Closed`).

---

### `transition_issue`

Change the status of a Jira issue (e.g. move from `Backlog` to `In Progress`).

**Parameters:**
- `issue_key` (string) — The Jira issue key, e.g. `PROJ-123`
- `transition_name` (string) — The target status name, e.g. `In Progress`, `Done`, `Closed`

**Returns:** JSON confirming the transition, or an error with the list of valid transition names if the provided name is not found.
