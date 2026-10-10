---
name: llm-prompt-evaluator
description: >-
  Design evaluations for LLM prompts and applications: golden datasets, rubrics, LLM-as-judge, regression comparisons, safety and robustness checks, and metrics. Use when a tester says "evaluate this prompt", "LLM testing", "prompt regression", "hallucination checks", or compares prompt or model versions.
license: MIT
metadata:
  author: Muralidhar Karanam
  stlc-phase: AI Testing
  version: 1.0.0
---

# LLM Prompt Evaluator

## When to use
- A prompt or model version changes and quality must not regress.
- An LLM feature needs acceptance criteria.
- Outputs must be checked for safety, format and factuality.

## Workflow
1. **Define the task and success.** What a good answer is, with measurable criteria (correctness, format, tone, safety).
2. **Build the dataset.** Typical, edge, adversarial and out-of-scope inputs with expected properties or reference answers; keep it versioned.
3. **Choose scoring.** Exact or schema checks where possible, rubric scoring or LLM-as-judge where not; calibrate the judge against human labels.
4. **Run comparisons.** Same dataset across versions, with repeat runs to measure variance.
5. **Report.** Per-criterion scores, regressions, failure clusters and examples.
6. **HUMAN REVIEW GATE** on rubric and thresholds.

## Output shape
An evaluation plan: criteria, dataset design, scoring method, thresholds, run protocol and report format.

## Quality checks
- Non-determinism is handled by repeated runs.
- Judge prompts are validated against human labels.
- Adversarial and out-of-scope cases are included.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
