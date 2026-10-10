---
name: test-strategy-creator
description: >-
  Create an organization- or product-level test strategy: test levels, types, tooling, environments, automation approach, entry/exit criteria and quality goals. Use when a lead says "write a test strategy", "define our testing approach", or a new product needs a testing blueprint above any single release plan. Stops for human review.
license: MIT
metadata:
  author: skillmasterclass-local
  stlc-phase: Test Planning
  version: 1.0.0
---

# Test Strategy Creator

## When to use
- A new product or platform needs an agreed testing approach.
- Several teams need one consistent strategy that individual test plans follow.
- An existing strategy is outdated after an architecture or tooling change.

## Workflow
1. **Understand context.** Capture product type, architecture, release cadence, regulatory constraints, team size and current pain points. Ask for what is missing.
2. **Choose test levels and types.** Decide the split across unit, integration, API, UI, performance, security, accessibility; justify each choice against the product risks.
3. **Define the automation approach.** State what is automated, at which layer, with which tools, and what stays manual (the test pyramid you are targeting).
4. **Set environments and data.** Describe environments, data management, and who owns them.
5. **Set quality gates.** Define entry/exit criteria, defect severity policy, and metrics that will be reported.
6. **Record risks and dependencies,** then **HUMAN REVIEW GATE:** present as a draft and list assumptions.

## Output shape
Sections: Scope and objectives; Test levels and types (with rationale); Automation approach; Environments and data; Entry/exit criteria; Roles; Metrics; Risks; Assumptions and open questions.

## Quality checks
- Each test type chosen is tied to a stated risk or requirement.
- Entry and exit criteria are measurable.
- Nothing is stated about tools or environments the user did not confirm.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
