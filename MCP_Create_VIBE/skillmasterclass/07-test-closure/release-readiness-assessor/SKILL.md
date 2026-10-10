---
name: release-readiness-assessor
description: >-
  Assess whether a release is ready: exit criteria, coverage, open defects by severity, test results, risks, non-functional status and a go/no-go recommendation with conditions. Use when a lead says "are we ready to release", "go/no-go", "release sign-off", or "readiness report".
license: MIT
metadata:
  author: Muralidhar Karanam
  stlc-phase: Test Closure
  version: 1.0.0
---

# Release Readiness Assessor

## When to use
- A release candidate is approaching and a decision is needed.
- Stakeholders need a one-page quality summary.
- Conditions for a conditional release must be written down.

## Workflow
1. **Collect inputs.** Exit criteria, execution results, coverage, open defects with severity, non-functional results and known risks. Ask for missing inputs; do not assume pass.
2. **Check each exit criterion.** Mark Met, Not met or Unknown with evidence.
3. **Weigh open defects.** List blockers and accepted risks with owners.
4. **Recommend.** Go, Go with conditions, or No-go, with the reasoning and conditions.
5. **HUMAN REVIEW GATE.** The decision belongs to the accountable person; present the recommendation, not a verdict.

## Output shape
A readiness summary: criteria table, defect summary, risks, recommendation with conditions, and unknowns.

## Quality checks
- Unknown is never reported as Met.
- Every blocker has an owner or resolution path.
- The recommendation follows from the criteria table.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
