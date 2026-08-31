# Test Plan — KAN-7: Feature requirements for VWO app

**Ticket:** [KAN-7](https://mkaranam59.atlassian.net/browse/KAN-7)
**Status:** To Do | **Type:** Story | **Priority:** Medium | **Assignee:** Unassigned
**Draft status:** DRAFT — requires human review before use (see Human Review Gate at the end)

---

## 1. Scope & Objectives

The ticket contains a full Product Requirements Document (PRD) for the **VWO Login Dashboard**, not a scoped set of acceptance criteria. It covers authentication, password management, UX/accessibility, security, performance, integrations, and future enhancements for a login experience used by VWO customers (digital marketers, enterprise teams, etc.).

**Objective of this test plan:** validate the login/authentication experience described in the PRD — primarily the "Phase 1: Core Authentication" slice (secure login form, validation/error handling, password reset), since that is the only phase the PRD marks as immediate scope. Phases 2 (UX/accessibility polish) and 3 (SSO/enterprise/analytics) are treated as stretch/likely-future scope pending confirmation (see Gaps section).

**In scope (as inferred):**
- Email/password login and validation
- Remember-me / session handling
- Forgot-password / password-reset flow
- Error handling and messaging
- Basic responsive/accessible rendering of the login form

**Not yet confirmed in scope (flagged in Gaps):**
- MFA / 2FA
- SSO (SAML/OAuth) and social login (Google/Microsoft)
- Full WCAG 2.1 AA audit
- i18n/localization
- Analytics/tracking integration
- Performance/load testing at the stated scale (thousands of concurrent logins, 99.9% uptime)

---

## 2. Gaps & Questions for the Author

The ticket is a PRD, not a groomed story — there are no explicit, testable acceptance criteria. Below is the requirement gap analysis (✅ present · ⚠️ ambiguous · ❌ missing):

| Area | Status | Note / Question |
|---|---|---|
| User story ("As a … I want … so that …") | ❌ Missing | The PRD describes a product vision, not a scoped story. **Which phase/slice does this specific ticket cover — Phase 1 only, or the whole PRD?** |
| Testable acceptance criteria | ❌ Missing | No pass/fail criteria are stated anywhere. Needs to be broken into discrete, testable stories before sign-off is possible. |
| Happy path | ✅ Present | Email + password login → dashboard transition is described. |
| Negative / error paths | ⚠️ Ambiguous | "Clear, actionable error messages" is stated but not enumerated. **What specific error states exist (wrong password, unknown email, locked account, expired session, network failure)? What is the exact copy/behavior for each?** |
| Boundary & empty states | ❌ Missing | No password length/complexity rules, no lockout threshold, no rate-limit numbers given. **What are the exact password policy and lockout/rate-limit thresholds?** |
| State transitions / workflow | ⚠️ Ambiguous | Login→dashboard and forgot-password flows are named but not diagrammed step-by-step. |
| Test data | ❌ Missing | No sample accounts, roles, or edge-case data sets provided. |
| Environment / feature flags | ❌ Missing | No staging URL, environment list, or flag names given. Dark/Light mode is referenced as "recently launched" — **is that in scope for this ticket, or already shipped?** |
| External dependencies | ⚠️ Ambiguous | SSO (SAML/OAuth) and social login (Google/Microsoft) are named as capabilities but with no provider/config detail. **Is SSO in scope for this ticket or a later one?** |
| Preconditions / setup | ❌ Missing | No mention of required accounts, seeded data, or environment setup. |
| Performance | ✅ Present (numbers given) | <2s load, 99.9% uptime, "thousands of simultaneous logins." **Are these targets in scope for this ticket's test cycle, or validated separately by a performance/SRE workstream?** |
| Security / authorization | ⚠️ Ambiguous | Encryption, HTTPS, rate limiting, and "optional 2FA" are mentioned, but role/permission boundaries after login (who can access what in the dashboard) are not defined. |
| Accessibility | ✅ Present (WCAG 2.1 AA target stated) | No specific components/flows called out for a11y testing yet. |
| Internationalization | ❌ Missing | Not mentioned at all — is the login page single-language only? |
| Audit / logging | ⚠️ Ambiguous | "Login success/failure tracking" is mentioned but no detail on what's logged, retention, or where it surfaces. |
| Regression impact | ❌ Missing | The PRD implies an *existing* login page is being replaced/enhanced ("Current State Analysis" section). **Is this a redesign of production login? If so, what's the migration/rollback plan and what existing behavior must not regress?** |
| Backward compatibility | ❌ Missing | Not addressed — will existing sessions/cookies remain valid? |
| Browser / device matrix | ⚠️ Ambiguous | "Responsive," "mobile-optimized" stated, no explicit browser/OS/device list. |
| Rollback / feature flag behavior | ❌ Missing | Not mentioned. |
| Ambiguous wording | ⚠️ Ambiguous | Terms like "seamless," "streamlined," "clear feedback," "enterprise-grade" appear throughout without measurable definitions. |
| Mockups / designs | ❌ Missing | No design/Figma links attached to the ticket. |

**Top blocking questions for the ticket author before this plan can be finalized:**
1. Which phase of the PRD does KAN-7 actually deliver — Phase 1 (core auth) only, or the full document?
2. Is this a redesign of an existing production login page, or new? If a redesign, what must not regress?
3. What are the concrete password policy, lockout, and rate-limit values?
4. Is SSO / social login / MFA in scope for this ticket, or tracked separately?
5. Are there design mockups this implementation should match?
6. What environments/URLs and test accounts should QA use?

---

## 3. Test Scenarios

### P0 — Critical / must pass before release
| # | Scenario | Maps to |
|---|---|---|
| P0-1 | Valid email + correct password logs the user into the dashboard | Happy path |
| P0-2 | Invalid password shows a clear, non-revealing error (does not confirm whether the email exists) | Error handling / Security |
| P0-3 | Unknown/unregistered email shows a clear error without leaking account existence | Error handling / Security |
| P0-4 | Empty email and/or empty password fields are blocked with inline validation before submit | Boundary / empty state (gap) |
| P0-5 | Password field masks input by default | Security |
| P0-6 | All login traffic is served over HTTPS/TLS; no credentials sent in plaintext or query strings | Data protection |
| P0-7 | Repeated failed login attempts trigger rate limiting / lockout per policy (**policy value pending author answer**) | Security / gap |
| P0-8 | "Forgot password" generates a secure, single-use, time-limited reset token and emails it to the account owner | Password management |
| P0-9 | Password reset link expires after its stated window and a new one must be requested | Password management / boundary |
| P0-10 | Session persists correctly when "Remember me" is checked, and does not when unchecked | Session management |
| P0-11 | Session times out after the configured inactivity period and re-prompts login | Session management |

### P1 — High priority
| # | Scenario | Maps to |
|---|---|---|
| P1-1 | Real-time field validation fires on blur (email format check) | UX requirement |
| P1-2 | Malformed email format is rejected with a specific inline message | Negative path |
| P1-3 | Password strength indicator reflects policy in real time while typing | UX requirement |
| P1-4 | First input field receives auto-focus on page load | UX requirement |
| P1-5 | Clicking form labels focuses the associated input (label/input association) | Accessibility |
| P1-6 | Login form is fully operable via keyboard only (tab order, enter-to-submit) | Accessibility |
| P1-7 | Screen reader announces field labels, errors, and loading state (ARIA) | Accessibility |
| P1-8 | Login page renders and functions correctly on mobile viewport widths | Responsive design |
| P1-9 | Loading state is shown while authentication request is in flight, with the submit control disabled to prevent duplicate submits | UX requirement |
| P1-10 | Successful login is recorded in login analytics/audit trail; failed attempts are recorded with reason code | Audit / observability (gap) |
| P1-11 | "Sign up" / free-trial link on the login page navigates correctly and does not break the login form state | Registration link |
| P1-12 | Light/Dark mode toggle (if in scope for this ticket) renders the login form correctly in both themes | UX / gap — confirm scope |

### P2 — Lower priority / exploratory
| # | Scenario | Maps to |
|---|---|---|
| P2-1 | Login page loads within 2 seconds on a standard connection (measured, not just asserted) | Performance target |
| P2-2 | Copy/paste into email and password fields works correctly (no blocked paste) | UX |
| P2-3 | Autofill via browser/password manager populates fields correctly | UX / compatibility |
| P2-4 | Login page behaves correctly across the supported browser/device matrix (**matrix pending author answer**) | Cross-browser / gap |
| P2-5 | High-contrast mode renders the form legibly | Accessibility |
| P2-6 | Concurrent login attempts from the same account on multiple devices behave per session policy | Session edge case |
| P2-7 | SSO / social login entry points (if present) route correctly to the relevant identity provider | Integration / gap — confirm scope |
| P2-8 | 2FA challenge (if enabled for the account) is correctly required and validated | Security / gap — confirm scope |

---

## 4. Test Data & Environment

**Not specified in the ticket — the following is proposed and needs author/QA-lead confirmation:**
- Test environment URL(s) (staging/QA instance of the VWO login page)
- A set of test accounts: valid active user, locked-out user, unverified/new user, account with 2FA enabled (if in scope)
- No credentials are recorded in this document; provisioning and storage of test credentials should follow the team's existing secrets-handling process.
- Browser/device matrix to be confirmed (proposed default: latest Chrome, Firefox, Safari, Edge; iOS Safari and Android Chrome for mobile)

---

## 5. Risks & Assumptions

**Assumptions made while drafting this plan:**
- Assumed KAN-7 covers at minimum "Phase 1: Core Authentication" as named in the PRD's Implementation Considerations section.
- Assumed this is a redesign/enhancement of an existing production login page (based on the "Current State Analysis" section), not a greenfield build — pending confirmation.
- Assumed SSO, social login, and MFA are stretch/later-phase scope, not required for this ticket's initial release — pending confirmation.
- Assumed standard web security practice (no plaintext credentials, hashed storage, HTTPS-only) applies even though not explicitly re-stated as an AC.

**Risks:**
- Because there are no explicit acceptance criteria, testers may validate the wrong scope or miss criteria the author intended but didn't write down.
- Undefined password/lockout policy could ship with either weak security or user-hostile lockout behavior.
- No design mockups means visual/UX QA has nothing authoritative to compare against.
- Ambiguity about whether this is a redesign of production login raises regression risk if the existing behavior isn't documented.

---

## 6. Entry / Exit Criteria

**Entry criteria:**
- Ticket author has answered the blocking questions in Section 2 (scope, policy values, redesign vs. greenfield, SSO/MFA scope).
- A build is deployed to a testable environment with the agreed test accounts provisioned.
- Design mockups (if any) are linked to the ticket.

**Exit criteria:**
- All P0 scenarios pass with zero open Critical/Blocker defects.
- P1 scenarios pass or have triaged, accepted-risk exceptions signed off by the product owner.
- Any regression against existing production login behavior (if this is a redesign) is explicitly reviewed and accepted.
- Open questions from Section 2 are resolved and reflected back into the ticket's acceptance criteria.

---

## --- HUMAN REVIEW GATE ---

This is a **draft**, not an approved test plan. Before it is used for execution:

**Assumptions made (needs confirmation):**
- Scope = Phase 1 core authentication only
- This is a redesign of an existing login page
- SSO / MFA / social login are out of scope for this cycle

**Open questions that block sign-off** (full list in Section 2):
1. Which phase/scope does KAN-7 actually cover?
2. Is this a redesign of production login — what must not regress?
3. Concrete password policy / lockout / rate-limit values?
4. Is SSO/MFA/social login in scope now or later?
5. Are there design mockups to test against?
6. What environment(s) and test accounts should QA use?

**Please review, edit, and confirm/answer the above before this plan is treated as approved.**
