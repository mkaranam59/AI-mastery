---
name: test-cases-from-requirements
description: Generates functional (happy path, negative) and non-functional (performance, security, UI, API) test cases, with test steps and expected results, from a user story, requirements document, or acceptance criteria. Use when the user asks for test cases, test steps, test scenarios, or QA coverage. Produces a CSV file for Jira import, not automation code.
---

# Test Cases from Requirements

## 1. Get the requirements
- Read the requirements document from Google Drive. The user gives a link or a file name.
- If more than one file matches, ask which one. Never guess.
- If acceptance criteria are missing, ask before generating.

## 2. Generate the test cases
For each requirement, cover the types that apply: happy path, negative, performance, security, UI, API.
Skip a type only when it clearly does not apply. In your reply (not in the CSV), list each skipped type with a one-line reason, so the user can challenge it.

## 3. Write the CSV
Header row, exactly: `Title,Type,Preconditions,Steps,Expected Result`

- One test case per row.
- Steps: one step per line inside the cell, numbered "1.", "2.", and so on.
- Always wrap the Steps field in double quotes, or the line breaks will split the row and corrupt the import.
- Type is one of: Happy Path, Negative, Performance, Security, UI, API.
- If a test case fits none of the six types, don't invent a type. Collect all such cases and ask the user once, listing them, which type fits each.

## 4. Check, then save
- Re-read the CSV: header correct, every row has 5 fields.
- Save it in the same Google Drive folder as the requirements document, named `TestCases_<document name>.csv`.
- If a file with that name already exists in the folder, stop and ask the user before overwriting. Never overwrite silently.
- Tell the user the file name and where it is.
