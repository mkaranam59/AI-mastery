---
name: quality-metrics-dashboard
description: >-
  Define and compute QA metrics and dashboards: pass rate, coverage, automation rate, defect density, escape rate, flakiness, cycle time and trends, with definitions that cannot be gamed. Use when a lead says "QA dashboard", "quality metrics", "KPIs for testing", or needs reporting design.
license: MIT
metadata:
  author: Muralidhar Karanam
  stlc-phase: Test Closure
  version: 1.0.0
---

# Quality Metrics Dashboard

## When to use
- A team needs a consistent QA report.
- Existing metrics are misleading or disputed.
- A dashboard is being built for stakeholders.

## Workflow
1. **Clarify the audience and decisions.** Each metric must support a decision; drop metrics that do not.
2. **Define each metric.** Name, formula, data source, refresh cadence and known ways it can mislead.
3. **Select a balanced set.** Include outcome metrics (escape rate), process metrics (cycle time) and health metrics (flaky rate), avoiding vanity counts.
4. **Design the view.** Trends over snapshots, thresholds with explicit targets, and drill-downs.
5. **HUMAN REVIEW GATE** on definitions and targets.

## Output shape
A metric catalogue table (metric, formula, source, target, caveat) and a dashboard layout description.

## Quality checks
- Every metric has a formula and a data source.
- Targets are supplied by the team, not invented.
- Each metric lists how it can be misread.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
