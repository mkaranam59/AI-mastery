#!/usr/bin/env bash

# ==============================================================================
# Jira Ticket Fetcher Tool for AI Agents / CLI
# Requires: curl, jq, base64
# ==============================================================================

set -euo pipefail

# 1. Load configuration from environment or .env file
if [[ -f ".env" ]]; then
  # Export variables from w.env ignoring comments
  export $(grep -v '^#' .env | xargs)
fi

JIRA_DOMAIN="${JIRA_DOMAIN:-}"
JIRA_EMAIL="${JIRA_EMAIL:-}"
JIRA_API_TOKEN="${JIRA_API_TOKEN:-}"

# Clean domain prefix/trailing slashes
JIRA_DOMAIN=$(echo "$JIRA_DOMAIN" | sed -e 's|^https://||' -e 's|/*$||')

# 2. Validate prerequisites and inputs
if [[ -z "$JIRA_DOMAIN" || -z "$JIRA_EMAIL" || -z "$JIRA_API_TOKEN" ]]; then
  echo '{"error": "Missing credentials. Ensure JIRA_DOMAIN, JIRA_EMAIL, and JIRA_API_TOKEN are set."}' >&2
  exit 1
fi

if ! command -v jq &> /dev/null; then
  echo '{"error": "Dependency missing: jq is required for JSON processing."}' >&2
  exit 1
fi

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <TICKET_KEY> [optional: --raw]" >&2
  echo "Example: $0 PROJ-123" >&2
  exit 1
fi

TICKET_KEY="$1"
OUTPUT_MODE="${2:-summary}"

# 3. Base64 Encode Auth Credentials
AUTH_HEADER=$(echo -n "${JIRA_EMAIL}:${JIRA_API_TOKEN}" | base64)

# 4. Fetch ticket via Jira REST API v3
API_URL="https://${JIRA_DOMAIN}/rest/api/3/issue/${TICKET_KEY}?fields=summary,status,issuetype,priority,assignee,reporter,created,updated,labels,description,comment"

RESPONSE=$(curl -s -w "\n%{http_code}" \
  --request GET \
  --url "$API_URL" \
  --header "Authorization: Basic ${AUTH_HEADER}" \
  --header "Accept: application/json")

# Split response body and HTTP status code
HTTP_BODY=$(echo "$RESPONSE" | sed '$d')
HTTP_STATUS=$(echo "$RESPONSE" | tail -n1)

# 5. Handle HTTP Errors
if [[ "$HTTP_STATUS" -eq 404 ]]; then
  echo "{\"error\": \"Ticket '${TICKET_KEY}' not found.\"}"
  exit 1
elif [[ "$HTTP_STATUS" -ne 200 ]]; then
  ERROR_MSG=$(echo "$HTTP_BODY" | jq -r '.errorMessages // [.errors] | join(", ")' 2>/dev/null || echo "HTTP $HTTP_STATUS")
  echo "{\"error\": \"Jira API error ($HTTP_STATUS): $ERROR_MSG\"}"
  exit 1
fi

# 6. If --raw flag is passed, return full unmodified Jira JSON
if [[ "$OUTPUT_MODE" == "--raw" ]]; then
  echo "$HTTP_BODY" | jq .
  exit 0
fi

# 7. Extract & Clean High-Signal Fields for AI Agent Context
echo "$HTTP_BODY" | jq \
  --arg domain "$JIRA_DOMAIN" \
  '{
    key: .key,
    url: ("https://" + $domain + "/browse/" + .key),
    summary: .fields.summary,
    status: .fields.status.name,
    issue_type: .fields.issuetype.name,
    priority: .fields.priority.name,
    assignee: (.fields.assignee.displayName // "Unassigned"),
    reporter: (.fields.reporter.displayName // "Unknown"),
    created: .fields.created,
    updated: .fields.updated,
    labels: .fields.labels,
    # Recursively extract text from Atlassian Document Format (ADF) description
    description: (
      if .fields.description == null then 
        ""
      elif (.fields.description | type) == "string" then 
        .fields.description
      else 
        [.fields.description | .. | objects | select(.type? == "text") | .text] | join(" ")
      end
    ),
    comments: [
      .fields.comment.comments[]? | {
        author: .author.displayName,
        created: .created,
        body: (
          if (.body | type) == "string" then 
            .body
          else 
            [.body | .. | objects | select(.type? == "text") | .text] | join(" ")
          end
        )
      }
    ]
  }'