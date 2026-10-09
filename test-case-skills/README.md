# Test Case Skills

Two Claude Code skills that turn requirements into a Jira-import CSV of test cases.

| Skill | Input | Output |
|---|---|---|
| `test-cases-from-requirements` | A requirements document in Google Drive (PDF, Doc, Word) | `TestCases_<document name>.csv` in the same Drive folder |
| `test-cases-from-jira` | A Jira ticket key or link, including every child story of an epic | `TestCases_<ticket key>.csv` in a fixed Drive folder |

The CSV has the header `Title,Type,Preconditions,Steps,Expected Result`. Type is one of Happy Path, Negative, Performance, Security, UI, API. Steps are numbered, one per line, inside double quotes.

## How it works

A skill is a text file of instructions. Claude Code reads only each skill's name and description until a request matches, then loads the full file. The model decides what to do next, and tools do the exact work:

| Piece | Role |
|---|---|
| Claude (the LLM) | Matches the request to a skill, reads the requirements, designs the test cases, decides the next step, asks when something is unclear |
| Skills | The rules: what to ask, what to cover, the exact CSV format, where to save |
| Google Drive connector | Finds and reads the requirements, saves the CSV |
| `jira_get_issue.py` | Reads a Jira ticket (and an epic's children) with GET requests only |
| Python | Builds the CSV and checks header, field counts and Types |

No custom sub-agent is used. The running Claude Code session is the agent.

## Requirements

- Claude Code
- The Google Drive connector enabled in your Claude account
- Python 3 (standard library only)
- For the Jira skill: a Jira Cloud API token, preferably a **scoped, read-only** token

## Install

Copy the two skill folders into your Claude skills folder:

```
Windows:  C:\Users\<you>\.claude\skills\
macOS/Linux:  ~/.claude/skills/
```

```
skills/test-cases-from-requirements  ->  <skills folder>/test-cases-from-requirements
skills/test-cases-from-jira          ->  <skills folder>/test-cases-from-jira
```

Start a new Claude Code session so the skills are picked up.

## Set up Jira access (Jira skill only)

Create an API token at https://id.atlassian.com/manage-profile/security/api-tokens, then set three environment variables. Do this in your own terminal. Never paste the token into a chat or a file in this repo.

Windows (PowerShell):

```
setx JIRA_BASE_URL "https://YOURSITE.atlassian.net"
setx JIRA_EMAIL "you@example.com"
setx JIRA_API_TOKEN "your-token"
```

macOS/Linux: add the same three `export` lines to your shell profile.

Restart Claude Code afterwards. To test the script on its own:

```
python -I skills/test-cases-from-jira/scripts/jira_get_issue.py PROJ-123
```

## Use

Open Claude Code in any folder and ask:

- Drive document: `Generate test cases from "<exact file name>" in my Drive`
- Jira: `Generate test cases for PROJ-123` (or paste the ticket link)
- To force a skill: `/test-cases-from-jira PROJ-123` or `/test-cases-from-requirements`

Answer any question it asks. The skills stop and ask when:

- more than one file or ticket matches
- acceptance criteria are missing (looked for in a dedicated field first, then in an "Acceptance Criteria" section of the description)
- a test case fits none of the six Types
- the output file already exists (it never overwrites silently)

Then read the reply. It lists every Type it skipped and every assumption it made, so you can challenge them. Open the CSV in Drive and import it into Jira, and check that the columns map correctly.

## Rules built into the skills

- Jira is read-only. The script has no code path that writes, and the skill refuses write requests.
- Credentials are read from environment variables and are never printed.
- For an epic, the epic and its children are the scope together. Children with no acceptance criteria are collected and the user is asked once. Criteria are never invented.
- Every Title starts with the key of the issue the case traces to.

## Customise

- **Output folder (Jira skill).** Step 4 of `skills/test-cases-from-jira/SKILL.md` contains a Google Drive folder link. Replace it with your own.
- **CSV columns.** The header must match your Jira import exactly. If your import uses different names, change step 3 in both skills.
- **Coverage.** Step 2 lists the test types. Add or remove types there and in the Type rule.

## Known limits

- The Jira script reads Jira Cloud only (REST API v3) and reads at most 100 children of an epic.
- Test cases are written to the requirements as stated. Where a ticket is vague the skill lists its assumptions in the reply, and they need a human check.
- The skills have been tested on one requirements PDF and one epic with four stories. An issue with no acceptance criteria was skipped by decision, not covered.

## Examples

`examples/` has two generated CSVs: one from a Drive requirements PDF and one from a Jira epic.
