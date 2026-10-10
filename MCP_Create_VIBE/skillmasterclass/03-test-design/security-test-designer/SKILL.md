---
name: security-test-designer
description: >-
  Design application security tests aligned to OWASP: authentication, authorization, injection, session management, input validation, sensitive data exposure and API security. Use when a tester says "security testing", "OWASP test cases", "check authorization", or a feature handles credentials or personal data. Only for systems the user is authorised to test.
license: MIT
metadata:
  author: Muralidhar Karanam
  stlc-phase: Test Design
  version: 1.0.0
---

# Security Test Designer

## When to use
- A feature handles authentication, payments or personal data.
- An API exposes resources by ID and access control must be verified.
- A security review needs test cases before a release.

## Workflow
1. **Confirm authorisation and scope.** Test only systems the user owns or has written permission to test; ask if this is unclear.
2. **Map the attack surface.** Entry points, roles, data classification and trust boundaries.
3. **Design cases per category.** Broken access control (IDOR, privilege escalation), authentication and session (lockout, token expiry, fixation), injection (SQL, XSS, command), input validation, data exposure (logs, errors, transport), and rate limiting.
4. **State expected secure behavior** for each case and the evidence that proves it.
5. **HUMAN REVIEW GATE.** Flag any case that could be destructive and require explicit approval first.

## Output shape
Test cases by OWASP category with role, precondition, input, expected secure behavior and severity if it fails.

## Quality checks
- Every role pair has an authorization check.
- No case relies on exploiting third-party systems.
- Destructive cases are flagged for approval.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
