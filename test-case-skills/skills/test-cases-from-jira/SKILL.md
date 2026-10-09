---
name: test-cases-from-jira
description: Reads a Jira ticket (by key or link) and generates functional (happy path, negative) and non-functional (performance, security, UI, API) test cases with steps and expected results. Use when the user gives a Jira ticket key such as PROJ-123 and asks for test cases, test steps, or QA coverage. Reads Jira only, never writes to it. Produces a CSV file for Jira import, not automation code.
---

# Test Cases from a Jira Ticket

## 1. Get the requirements (read-only)
- Read the ticket by running `python -I <this skill's base directory>/scripts/jira_get_issue.py <ticket key or link>` (the base directory is shown when the skill loads). It reads the credentials from the environment variables JIRA_BASE_URL, JIRA_EMAIL and JIRA_API_TOKEN, and prints the summary, description, acceptance criteria, subtasks and linked issues.
- If the script fails (missing variables, bad credentials, issue not found), stop and tell the user what it said. Never print, log or ask for the token.
- Only read from Jira. Never create, edit, comment on or transition an issue, even if asked mid-task; tell the user it is out of scope.
- If the key is invalid or several tickets match, ask. Never guess.
- Look for acceptance criteria in a dedicated field first, and otherwise in a section of the description labelled "Acceptance Criteria". Ask before generating only if neither exists.
- If the ticket is an Epic, the script also prints every child issue. Treat the epic and its children together as the scope, and apply the acceptance-criteria rule to each child separately. Collect the children that have none and ask the user once what to do with them. Never invent criteria for them.
- Put the ticket key and the last-updated time of each issue you used in your reply.

## 2. Generate the test cases
For each requirement, cover the types that apply: happy path, negative, performance, security, UI, API.
Skip a type only when it clearly does not apply. In your reply (not in the CSV), list each skipped type with a one-line reason, so the user can challenge it.
Where the ticket is vague, list the assumptions you made in your reply.

## 3. Write the CSV
Header row, exactly: `Title,Type,Preconditions,Steps,Expected Result`

- One test case per row.
- Start every Title with the key of the issue the case traces to, for example `PROJ-123: Reject a malformed email`. For an epic, use the child's key for cases from that child and the epic's key for cases from the epic itself.
- Steps: one step per line inside the cell, numbered "1.", "2.", and so on.
- Always wrap the Steps field in double quotes, or the line breaks will split the row and corrupt the import.
- Type is one of: Happy Path, Negative, Performance, Security, UI, API.
- If a test case fits none of the six types, don't invent a type. Collect all such cases and ask the user once, listing them, which type fits each.

## 4. Check, then save
- Re-read the CSV: header correct, every row has 5 fields.
- Save it to the Google Drive folder https://drive.google.com/drive/folders/1YdC9gQWxaPBakzJqfrBSLCvO0C1QMtiD, named `TestCases_<ticket key>.csv`.
- If the folder can't be found or written to, stop and ask the user.
- If a file with that name already exists in the folder, stop and ask the user before overwriting. Never overwrite silently.
- Tell the user the file name and where it is.
