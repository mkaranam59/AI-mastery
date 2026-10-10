---
name: ai-test-case-evaluator
description: >-
  Review test cases written by an AI for correctness and usefulness: traceability, hallucinated features, duplicate or vague steps, missing negative and boundary coverage, and testability. Use when a tester says "review these generated test cases", "are these AI test cases good", or before accepting generated cases into a suite.
license: MIT
metadata:
  author: Muralidhar Karanam
  stlc-phase: AI Testing
  version: 1.0.0
---

# AI-Generated Test Case Evaluator

## When to use
- A batch of test cases came from an AI tool.
- Generated cases must be checked before entering the suite.
- A team wants a quality bar for AI-assisted test design.

## Workflow
1. **Get the source.** Obtain the requirement or ticket the cases were generated from; without it, only internal quality can be checked.
2. **Check grounding.** Flag steps or expected results that mention features, fields or behaviors not in the source.
3. **Check quality.** Atomic steps, specific expected results, correct preconditions and data, unique IDs, no duplicates.
4. **Check coverage.** Missing negative, boundary, security, accessibility or state cases relative to the source.
5. **Score and decide.** Accept, fix or reject each case with a reason.
6. **HUMAN REVIEW GATE.** A tester confirms before cases are merged.

## Output shape
A per-case verdict table (case ID, verdict, issues, suggested fix) and a coverage-gap list.

## Quality checks
- Every flagged hallucination quotes the offending text.
- Verdicts have reasons.
- Coverage gaps are tied to the source requirement.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
