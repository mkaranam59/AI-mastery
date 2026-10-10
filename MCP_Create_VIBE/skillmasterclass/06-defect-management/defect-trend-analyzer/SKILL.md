---
name: defect-trend-analyzer
description: >-
  Analyze defect data over time: arrival and closure rates, severity mix, aging, escape rate, hot spots by module or cause, and trends across releases. Use when a lead says "defect trends", "where are the bugs", "defect leakage", or a retrospective needs evidence.
license: MIT
metadata:
  author: Muralidhar Karanam
  stlc-phase: Defect Management
  version: 1.0.0
---

# Defect Trend Analyzer

## When to use
- A release retrospective needs defect evidence.
- Quality seems to be dropping and the cause is unknown.
- A report on leakage to production is requested.

## Workflow
1. **Get the data.** Obtain an export (key, created, resolved, severity, component, found-in, cause). State what the data does and does not cover.
2. **Compute metrics.** Open vs closed over time, mean age, severity distribution, defects per component, reopen rate, and escape rate (found in production / total).
3. **Find patterns.** Hot spots, recurring causes, phases where defects are introduced vs found.
4. **Interpret carefully.** Separate observations from hypotheses; note small-sample limits.
5. **HUMAN REVIEW GATE.** Present findings with recommended actions for confirmation.

## Output shape
A summary of metrics with tables, the top three patterns, supported hypotheses, and recommended actions.

## Quality checks
- Every number is traceable to the supplied export.
- Hypotheses are labelled as hypotheses.
- Sample size is stated for each trend.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
