---
name: database-test-designer
description: >-
  Design database and SQL validation tests: schema, constraints, migrations, data integrity, stored procedures, transactions, ETL reconciliation and query correctness. Use when a tester says "database testing", "validate this SQL", "check data after migration", or "reconcile source and target".
license: MIT
metadata:
  author: skillmasterclass-local
  stlc-phase: Test Design
  version: 1.0.0
---

# Database Test Designer

## When to use
- A migration or schema change needs verification.
- Application writes must be checked against stored data.
- A data pipeline needs source-to-target reconciliation.

## Workflow
1. **Understand the schema.** Get tables, keys, constraints, indexes and the feature under test. Ask if the schema is not provided.
2. **Design integrity checks.** Primary/foreign keys, NOT NULL, unique, check constraints, orphan rows and duplicate detection.
3. **Design behavior checks.** CRUD effects, transaction commit/rollback, isolation concerns, stored-procedure results and trigger side effects.
4. **Write validation queries** (read-only by default) for row counts, checksums, null rates and value-range checks, with expected results.
5. **Handle data safely.** Use test data only; never propose destructive statements against shared environments. **HUMAN REVIEW GATE** before any query is run.

## Output shape
Test cases grouped by integrity, behavior and reconciliation, each with the SQL to run, the expected result and the data it needs.

## Quality checks
- Queries are read-only unless the case is explicitly about writes in a test database.
- Each constraint in scope has a positive and a violating case.
- Reconciliation checks compare counts and at least one content measure.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
