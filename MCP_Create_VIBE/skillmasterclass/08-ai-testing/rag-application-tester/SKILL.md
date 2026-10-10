---
name: rag-application-tester
description: >-
  Test retrieval-augmented generation systems: retrieval quality, chunking, grounding and citation accuracy, hallucination, freshness, access control and end-to-end answer quality. Use when a tester says "test RAG", "retrieval testing", "is the answer grounded", or a chatbot answers from documents.
license: MIT
metadata:
  author: skillmasterclass-local
  stlc-phase: AI Testing
  version: 1.0.0
---

# RAG Application Tester

## When to use
- A document-grounded assistant is being released or changed.
- Answers cite wrong or missing sources.
- The index or embedding model changed.

## Workflow
1. **Separate the stages.** Test retrieval and generation independently, then end to end.
2. **Retrieval tests.** For labelled questions check recall@k and precision@k, ranking of the right chunk, and behavior when no document answers.
3. **Generation tests.** Faithfulness to retrieved context, correct citations, refusal when context is insufficient, and handling of conflicting sources.
4. **System tests.** Access control per user, data freshness after updates, prompt injection inside documents, latency and cost.
5. **HUMAN REVIEW GATE** on the labelled question set and thresholds.

## Output shape
A test matrix by stage (retrieval, generation, system) with dataset needs, metrics and pass thresholds.

## Quality checks
- Questions with no answer in the corpus are included.
- Citations are verified against the source text.
- Per-user access control is tested.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
