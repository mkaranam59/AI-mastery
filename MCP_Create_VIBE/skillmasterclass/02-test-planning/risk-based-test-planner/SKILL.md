---
name: risk-based-test-planner
description: >-
  Prioritize testing by risk: identify product and project risks, score likelihood and impact, and allocate test depth accordingly. Use when a tester says "risk-based testing", "what should we test first", "we have limited time", or needs to justify skipped coverage. Produces a risk register and a test-depth allocation, then stops for review.
license: MIT
metadata:
  author: Muralidhar Karanam
  stlc-phase: Test Planning
  version: 1.0.0
---

# Risk-Based Test Planner

## When to use
- Time or people are limited and testing must be prioritized.
- A release changes high-impact areas such as payments or authentication.
- Stakeholders need a defensible reason for what was not tested.

## Workflow
1. **List risks.** From requirements, architecture, change lists and defect history, list candidate risks as `If <cause> then <failure> affecting <user/business>`.
2. **Score.** Rate likelihood and impact (1-5 each) and compute risk = L x I. Show your reasoning for each score; mark guesses as assumptions.
3. **Allocate depth.** Map score bands to test depth: high -> thorough (positive, negative, boundary, automation); medium -> standard; low -> smoke or exploratory only.
4. **Link to tests.** Point each risk to scenarios or suites that mitigate it, and list residual risk for anything left uncovered.
5. **HUMAN REVIEW GATE.** Ask the product owner or lead to confirm scores before the allocation is used.

## Output shape
A risk register table (ID, risk, likelihood, impact, score, mitigation tests, residual risk) and a depth-allocation summary by area.

## Quality checks
- Every score has a stated reason.
- Highest-scoring risks all have mitigating tests.
- Residual risk is listed, not hidden.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
