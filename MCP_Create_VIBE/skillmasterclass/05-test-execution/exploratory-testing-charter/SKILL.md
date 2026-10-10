---
name: exploratory-testing-charter
description: >-
  Plan and structure exploratory testing: write time-boxed session charters, heuristics, notes and debriefs. Use when a tester says "exploratory testing", "session-based testing", "charter", or wants to look for unknown issues beyond scripted cases.
license: MIT
metadata:
  author: Muralidhar Karanam
  stlc-phase: Test Execution
  version: 1.0.0
---

# Exploratory Testing Charter

## When to use
- A new or changed feature has weak scripted coverage.
- A release needs a bug-hunting pass.
- A team wants structured, reportable exploratory testing.

## Workflow
1. **Define missions.** Write charters in the form `Explore <area> with <resources> to discover <information>`, one per time-boxed session (60-90 minutes).
2. **Choose heuristics.** Use tours and mnemonics (for example SFDIPOT, CRUD, boundaries, interruptions) suited to the area.
3. **Run and note.** Record what was tested, bugs found, questions and risks, and time split between setup, testing and investigation.
4. **Debrief.** Summarize coverage, issues, new test ideas and what to automate.
5. **HUMAN REVIEW GATE.** Charters and findings are reviewed with the tester or lead.

## Output shape
A charter list, plus a session report template: charter, tester, duration, areas covered, bugs, issues, new ideas, follow-ups.

## Quality checks
- Each charter has a clear mission and a time box.
- Findings link to bug reports.
- Follow-up scripted cases are suggested for repeated risks.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
