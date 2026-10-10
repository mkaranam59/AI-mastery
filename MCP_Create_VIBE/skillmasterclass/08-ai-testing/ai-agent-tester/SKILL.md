---
name: ai-agent-tester
description: >-
  Test tool-using AI agents: task success, tool selection and arguments, multi-step planning, error recovery, guardrails, permission boundaries, loops, cost and determinism. Use when a tester says "test an AI agent", "agent evaluation", "MCP tool testing", or an agent calls tools autonomously.
license: MIT
metadata:
  author: skillmasterclass-local
  stlc-phase: AI Testing
  version: 1.0.0
---

# AI Agent Tester

## When to use
- An agent can call tools that change real state.
- Agent behavior varies between runs.
- Guardrails or permissions must be verified.

## Workflow
1. **Define tasks and tools.** List the agent's tools, permissions and the end states that count as success.
2. **Scenario tests.** Happy path, ambiguous requests, missing information, tool failures, and conflicting instructions.
3. **Safety tests.** Prompt injection through tool outputs, requests beyond permission, destructive actions without confirmation, data exfiltration attempts.
4. **Trajectory checks.** Correct tool choice and arguments, no unnecessary calls, bounded loops and cost.
5. **Run repeatedly** to measure consistency, and use a sandbox or mocks for side effects.
6. **HUMAN REVIEW GATE** before any test touches real systems.

## Output shape
A scenario table (task, setup, expected end state, forbidden actions, pass criteria) and a repeat-run protocol.

## Quality checks
- Destructive tools run only against sandboxes.
- Each scenario defines forbidden actions as well as goals.
- Results are reported over multiple runs.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
