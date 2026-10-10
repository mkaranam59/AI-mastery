---
name: api-contract-tester
description: >-
  Design contract tests for REST APIs from OpenAPI/Swagger specs or consumer expectations: schema, status codes, headers, required fields, backward compatibility and versioning. Use when a tester says "contract testing", "validate the API against the spec", "did this change break consumers", or Pact is mentioned.
license: MIT
metadata:
  author: Muralidhar Karanam
  stlc-phase: Test Design
  version: 1.0.0
---

# API Contract Tester

## When to use
- A provider API changes and consumers must not break.
- An OpenAPI spec exists and responses must be verified against it.
- Teams want consumer-driven contracts between services.

## Workflow
1. **Get the contract.** Obtain the OpenAPI document or consumer expectations. If neither exists, ask; do not invent endpoints.
2. **Derive checks per operation.** Status codes, response schema (types, required, enums, formats), headers, and error body shape.
3. **Add compatibility checks.** For a changed spec, list removed or renamed fields, tightened validations and changed types as breaking; additive optional fields as non-breaking.
4. **Choose tooling.** Suggest schema validation in the existing test framework or consumer-driven contracts (for example Pact) depending on team setup.
5. **HUMAN REVIEW GATE.** Present the checks and the breaking-change list for review.

## Output shape
A contract-check table (operation, check, expected, breaking-if-changed) and a breaking-change report when two spec versions are supplied.

## Quality checks
- Every operation in scope has at least a success and an error check.
- Breaking vs non-breaking classification is justified.
- No endpoint appears that is not in the supplied contract.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
