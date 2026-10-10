# Requirement Gap Review: MIN-6

**Verdict: Not ready for testing.** MIN-7, MIN-8 and MIN-9 are partly testable. MIN-10 is blocked.

## Epic MIN-6: PARTLY

- **Missing criteria:** There is no dedicated Acceptance Criteria field. The criteria are in the description, which the review rules allow.
- **No story for profile editing or data sync.** The epic title says "Profile Management", but no child story covers it.
- **No story for mobile.** The epic says "must be fully functional across web and mobile". It names no platforms, browsers or versions, and no story mentions mobile.
- **Password reset is incomplete.** MIN-9 stops at sending the email and the expired-link page. Setting the new password is not covered.
- **Vague security wording.** "Security requirements must meet OAuth2/JWT standards with encrypted passwords (e.g., bcrypt)" gives no standard version, token lifetime or hashing parameters. "e.g." leaves the hashing algorithm open.
- **"Sync" is undefined.** "User profile data must successfully sync across the database and frontend views" sets no time limit and no definition of "sync".
- **Contradiction:** The epic requires OAuth2, but its only OAuth2 story, MIN-10, is empty.

## MIN-7 (Sign-up): PARTLY

- The criteria give the password rule "minimum 8 characters, 1 number, 1 special character" but not what happens when a password breaks it.
- "They receive a verification email" has no link expiry, no behavior on click, and no rule on whether an unverified user can log in.
- Email format validation is not mentioned. Case sensitivity of "unique email" is not mentioned either.

## MIN-8 (Login and logout): PARTLY

- **Contradiction:** The error message is "Invalid username or password", but MIN-7 sign-up uses email and password, with no username.
- "A secure session (JWT) is initialized" gives no expiry, storage method or refresh behavior.
- Repeated failed logins and lockout are not covered. Whether an unverified account can log in is not covered.
- Logout says "the session token is destroyed" but not how that is verified. It does not say whether the token is invalidated on the server.

## MIN-9 (Password reset): PARTLY

- It does not say what happens when the entered email is not registered.
- The "single-use" rule has no failure case for a reused link.
- It does not say whether requesting a new link invalidates the old one.
- It does not define the success state after the password is changed.
- It does not say whether the new password follows the MIN-7 rules.

## MIN-10 (Google OAuth2 login): NO

- The description is empty and there is no acceptance criteria field.

## Suggested next steps

1. Write acceptance criteria for MIN-10.
2. Add stories for profile editing and sync, and for mobile support.
3. Add a story for setting the new password in the reset flow.
4. Fix the username/email contradiction in MIN-8.
5. Replace the vague security and sync wording with concrete values.
