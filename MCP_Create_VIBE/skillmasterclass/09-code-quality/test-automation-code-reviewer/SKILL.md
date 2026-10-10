---
name: test-automation-code-reviewer
description: >-
  Review test automation code: locator strategy, waits, independence, assertions, page-object design, data handling, readability, duplication, flakiness and reporting, for any framework. Use when a tester says "review my automation code", "why is this flaky", "code review of tests", or before merging test code.
license: MIT
metadata:
  author: skillmasterclass-local
  stlc-phase: Code Quality
  version: 1.0.0
---

# Test Automation Code Reviewer

## When to use
- A pull request adds or changes automated tests.
- A suite is slow, flaky or hard to maintain.
- A team wants consistent automation standards.

## Workflow
1. **Read for intent.** Confirm what each test verifies and whether it fits the right layer (unit, API, UI).
2. **Check reliability.** Hard sleeps, brittle locators, shared state, order dependence, unbounded retries, time and data assumptions.
3. **Check assertions.** Presence of meaningful assertions, assertions on the right thing, no assertion-free tests, clear failure messages.
4. **Check design.** Page objects or fixtures used well, duplication, naming, configuration and secrets handling.
5. **Report by severity.** Blocker, major, minor, with file/line references and a concrete fix for each.
6. **HUMAN REVIEW GATE.** Suggestions are advisory; the author decides.

## Output shape
Findings grouped by severity with location, problem, why it matters and a suggested change; plus a short overall assessment.

## Quality checks
- Each finding cites a specific location.
- Suggestions are concrete, not generic advice.
- Flakiness risks are called out separately.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
