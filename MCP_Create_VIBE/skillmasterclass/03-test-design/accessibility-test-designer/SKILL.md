---
name: accessibility-test-designer
description: >-
  Design accessibility tests against WCAG 2.2: keyboard operation, screen-reader semantics, contrast, focus management, forms, media and responsive behavior, using axe and manual checks. Use when a tester says "accessibility testing", "WCAG", "a11y", "screen reader", or a UI release needs compliance evidence.
license: MIT
metadata:
  author: skillmasterclass-local
  stlc-phase: Test Design
  version: 1.0.0
---

# Accessibility Test Designer

## When to use
- A new UI or component needs accessibility verification.
- A compliance deadline requires WCAG evidence.
- Users report problems with keyboard or screen-reader use.

## Workflow
1. **Fix the target.** Confirm the WCAG level (A/AA) and the pages or components in scope.
2. **Automated pass.** Plan axe or Lighthouse scans for each page state; note that automation finds only a fraction of issues.
3. **Manual keyboard checks.** Tab order, visible focus, no traps, operable custom widgets, skip links.
4. **Screen-reader checks.** Names, roles, states, landmarks, form labels, error announcements, dynamic updates.
5. **Visual checks.** Contrast, zoom to 200%, reflow, motion and time limits.
6. **HUMAN REVIEW GATE.** Map findings to WCAG success criteria and ask for confirmation of severity.

## Output shape
A checklist-style test set mapped to WCAG success criteria with the method (auto/keyboard/screen reader), expected result and severity.

## Quality checks
- Every case cites a WCAG success criterion.
- Both automated and manual methods are covered.
- Custom controls have explicit keyboard and ARIA cases.

## Boundaries
- Work only from supplied or confirmed information; state assumptions and never fabricate data, IDs or results.
- Stop at the human review gate; do not treat the output as final until a person approves it.
