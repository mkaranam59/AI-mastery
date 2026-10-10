---
name: ci-cd-test-integrator
description: >-
  Integrate automated tests into CI/CD pipelines: stages, parallelization, environments, secrets, artifacts, reports, quality gates and failure triage on GitHub Actions, GitLab CI, Jenkins or Azure DevOps. Use when a tester says "run tests in the pipeline", "CI/CD for automation", "quality gate", or "parallelize tests".
license: MIT
metadata:
  author: skillmasterclass-local
  stlc-phase: Test Execution
  version: 1.0.0
---

# CI/CD Test Integrator

## When to use
- Automated tests currently run only on a laptop.
- Pipeline runs are slow or flaky.
- A release needs automated quality gates.

## Workflow
1. **Identify the platform and suites.** Ask which CI system and which suites (smoke, regression, API, UI) exist.
2. **Design stages.** Fast checks first (lint, unit, smoke), then API, then UI; run heavier suites on schedule or merge.
3. **Handle environments and secrets.** Use the CI secret store; never commit credentials; define data setup and teardown.
4. **Speed and stability.** Sharding or parallel jobs, dependency caching, bounded retries for known flaky cases with reporting.
5. **Publish results.** Test reports, traces, screenshots and logs as artifacts, and gate merges on defined thresholds.
6. **HUMAN REVIEW GATE** before enabling gates that block merges.

## Output shape
A pipeline outline (stage table) with a sample configuration for the user's CI platform, the artifact list and the quality-gate rules.

## Quality checks
- No secret appears in the configuration.
- Every stage has a failure policy.
- Retries are bounded and visible in reports.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
