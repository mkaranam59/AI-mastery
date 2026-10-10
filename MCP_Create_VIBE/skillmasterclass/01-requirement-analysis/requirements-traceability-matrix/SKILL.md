---
name: requirements-traceability-matrix
description: >-
  Build and maintain a requirements traceability matrix (RTM) linking requirements, acceptance criteria, scenarios, test cases, automation and defects. Use when a tester says "create an RTM", "trace requirements to tests", "which requirements have no tests", or before sign-off needs proof of coverage. Produces a matrix plus a gap list, then stops for review.
license: MIT
metadata:
  author: Muralidhar Karanam
  stlc-phase: Requirement Analysis
  version: 1.0.0
---

# Requirements Traceability Matrix

## When to use
- A release needs evidence that every requirement is covered by tests.
- Requirements changed and the impact on existing tests must be found.
- An audit asks which tests verify a given requirement.

## Workflow
1. **Collect sources.** Gather requirement IDs/acceptance criteria, scenario and test-case IDs, automation IDs, and linked defects. Ask for any source that is missing instead of guessing links.
2. **Link forward and backward.** Map requirement -> AC -> scenario -> test case -> automation -> defect. Every link must cite a real ID from the sources.
3. **Find gaps.** List requirements with no test (uncovered), tests with no requirement (orphans), and ACs covered only by negative or only by positive cases.
4. **Rate coverage.** Mark each requirement Full, Partial or None with a one-line reason.
5. **HUMAN REVIEW GATE.** Present the matrix and gap list as a draft; do not declare coverage complete until a reviewer confirms.

## Output shape
A table with columns: Requirement ID | AC | Scenario IDs | Test case IDs | Automated? | Open defects | Coverage (Full/Partial/None). Followed by `Uncovered requirements`, `Orphan tests`, and `Assumptions`.

## Quality checks
- Every ID in the matrix exists in the supplied sources.
- No requirement is marked Full without at least one positive and one negative case.
- Gap lists add up to the totals stated.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
