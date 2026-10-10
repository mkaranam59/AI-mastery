---
name: test-estimation-planner
description: >-
  Estimate testing effort and schedule from scope: test design, execution, regression, automation, defect retesting and contingency. Use when a lead says "estimate testing effort", "how long will QA take", or planning needs numbers with stated assumptions. Gives a range, not a single false-precision figure, then stops for review.
license: MIT
metadata:
  author: Muralidhar Karanam
  stlc-phase: Test Planning
  version: 1.0.0
---

# Test Estimation Planner

## When to use
- Sprint or release planning needs a QA effort figure.
- Scope changed and the estimate must be revised.
- A proposal needs a justified testing cost.

## Workflow
1. **Confirm scope.** List features, test types, platforms and environments in scope. Ask for any missing size indicator (stories, screens, endpoints, past velocity).
2. **Break down the work.** Estimate test design, data setup, execution cycles, defect retest, regression, automation and reporting separately.
3. **Use a method and say which.** Use historical data, three-point (best/likely/worst) or a count-based rate; show the arithmetic.
4. **Add contingency** for blocked environments and defect churn, stated as a percentage with a reason.
5. **Present a range** with assumptions and the risks that would move it, then **HUMAN REVIEW GATE.**

## Output shape
A table of work items with best/likely/worst effort, a total range, the contingency used, a list of assumptions, and the factors that would change the estimate.

## Quality checks
- Totals equal the sum of the parts.
- Every number cites its basis (history, rate or judgement).
- Assumptions are listed explicitly.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
