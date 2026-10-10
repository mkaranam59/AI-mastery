---
name: smoke-sanity-suite-builder
description: >-
  Define smoke and sanity suites: a minimal build-verification set and a focused change-verification set, with criteria for when each runs and what failure means. Use when a tester says "smoke test suite", "sanity checks", "build verification", or "what must pass before we test further".
license: MIT
metadata:
  author: skillmasterclass-local
  stlc-phase: Test Execution
  version: 1.0.0
---

# Smoke and Sanity Suite Builder

## When to use
- A new build needs a fast go/no-go check before deeper testing.
- A bug fix needs quick focused verification.
- A pipeline needs a gating suite.

## Workflow
1. **List critical paths.** Identify journeys without which the product is unusable (login, core transaction, key navigation).
2. **Select smoke cases.** Choose the fewest cases that cover those paths, targeting a runtime that fits the pipeline; they must be stable and independent.
3. **Select sanity cases per change.** Pick cases around the changed area and its direct dependencies.
4. **Define rules.** Which failures block the build, who is notified, and when a case is quarantined as flaky.
5. **HUMAN REVIEW GATE** on the case list and blocking rules.

## Output shape
A smoke list and sanity template with case ID, reason it is included, expected runtime, automation status and blocking rule.

## Quality checks
- Smoke runtime meets the stated target.
- No flaky case is in the blocking set.
- Each included case maps to a critical path or change.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
