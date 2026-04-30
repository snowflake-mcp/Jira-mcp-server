# Jira MCP Server

An MCP (Model Context Protocol) server that lets AI assistants read Jira tickets.


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

You need three environment variables:

| Variable | Example |
|---|---|
| `JIRA_BASE_URL` | `https://yourcompany.atlassian.net` |
| `JIRA_EMAIL` | `you@company.com` |
| `JIRA_API_TOKEN` | `your-api-token` |

### 4. Add to Cursor

Add the following to your Cursor MCP config (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "jira": {
      "command": "/full/path/to/jira-mcp-server/venv/bin/python",
      "args": ["/full/path/to/jira-mcp-server/jira_mcp/main.py"],
      "env": {
        "JIRA_BASE_URL": "https://yourcompany.atlassian.net",
        "JIRA_EMAIL": "you@company.com",
        "JIRA_API_TOKEN": "your-api-token"
      }
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
