# AI-mastery
AI Projects

## Contents

- `.claude/skills/testplan-create/` — a Claude Code skill that turns a JIRA ticket into a review-ready QA test plan: fetches the ticket, runs a requirement gap analysis, drafts scenarios by risk (P0/P1/P2), and stops for human review before anything is treated as final.
- `output/` — generated test plans produced by the skill.

## Setup

The `testplan-create` skill fetches tickets via the JIRA REST API. Create `.claude/skills/.env` (git-ignored, never commit it) with:

```
JIRA_DOMAIN=https://<your-domain>.atlassian.net/
JIRA_EMAIL=<your-email>
JIRA_API_TOKEN=<your-jira-api-token>
```
