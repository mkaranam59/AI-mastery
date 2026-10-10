---
name: performance-test-designer
description: >-
  Design performance tests: load, stress, spike, soak and scalability scenarios with workload models, SLAs, metrics and tooling (k6, JMeter, Gatling, Locust). Use when a tester says "performance testing", "load test plan", "how many users can it handle", or needs response-time targets verified.
license: MIT
metadata:
  author: Muralidhar Karanam
  stlc-phase: Test Design
  version: 1.0.0
---

# Performance Test Designer

## When to use
- A release needs response-time or throughput evidence.
- Capacity must be sized before a launch or campaign.
- A regression in latency or resource use must be investigated.

## Workflow
1. **Define goals.** Get SLAs or ask for them: p95/p99 latency, throughput, error rate, resource ceilings. Do not invent targets.
2. **Model the workload.** Identify key user journeys, their mix, think times, data volumes and concurrency; base them on production analytics when available.
3. **Pick test types.** Baseline, load, stress, spike, soak; state the purpose and ramp profile of each.
4. **Specify measurements.** Client metrics, server metrics (CPU, memory, DB), and the pass/fail thresholds.
5. **Plan environment and data,** note how it differs from production, then **HUMAN REVIEW GATE.**

## Output shape
A performance test plan: goals, workload model, scenarios (type, load profile, duration), metrics and thresholds, environment notes, risks.

## Quality checks
- Every scenario has a measurable pass criterion.
- The environment gap to production is stated.
- No load figure is given without a stated source or marked assumption.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
