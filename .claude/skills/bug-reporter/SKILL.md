---
name: bug-reporter
description: Turns a rough bug description, plus any logs, error messages, screenshots, or context, into a clear, well-structured bug report (title, environment, steps to reproduce, expected vs actual, severity, attachments) saved as Markdown. Use this skill whenever the user says they found a bug, something is broken or not working, wants to "write up", "file", "log", or "report" a bug or defect, asks for a bug ticket or issue description, or pastes an error/stack trace and wants it documented, even if they never say "bug report".
---

# Bug Reporter

Convert messy, informal bug descriptions into reports that a developer can act on without a follow-up conversation. A good report lets someone reproduce the problem in minutes, so the goal is precision and completeness, not length.

## Workflow

1. **Gather what you have.** Read the user's description and any pasted logs, stack traces, screenshots, or files. Also check the working directory when relevant (e.g. app version, OS, git branch) instead of asking for facts you can look up.
   Determine the deployment environment (Dev, QA, Staging, Prod) from, in order:
   1. What the user says explicitly.
   2. The URL or hostname (e.g. `dev.`, `qa.`, `staging.`, `localhost` = Dev; a bare production domain = Prod).
   3. Config or branch names in the working directory.
   If it can't be determined, write "Not provided". Don't assume Prod, because a wrong guess sends the report to the wrong team. For public third-party or demo sites with a single environment, write "Prod (public site)" rather than inventing Dev/QA.
2. **Check for critical gaps.** Critical = steps to reproduce, or what the user expected to happen. If either is missing and can't be inferred, ask once, briefly, in a single message. Don't interview for anything else. For everything else, write "Not provided" rather than guessing, because invented details send developers down wrong paths.
3. **Write the report** using the template below.
4. **Deliver it.** Show the full report in chat and save it as `bug-report-<short-slug>.md` in the current working directory. Tell the user the file path.

## Report template

```markdown
# [Component/Area] Concise title describing the failure

**Severity:** Critical | High | Medium | Low  — one-line justification
**Reported:** <date>   **Reporter:** <user if known>

## Environment
- Deployment environment: Dev | QA | Staging | Prod | Not provided
- URL / host:
- App/version/build:
- OS / device:
- Browser / runtime:
- Other relevant config (account type, feature flags, data state):

## Summary
One to three sentences: what is wrong and who/what it affects.

## Steps to Reproduce
1. Numbered, specific, starting from a known state
2. Include exact inputs, URLs, and clicks
3. ...

**Reproducibility:** Always | Intermittent (~x/y) | Once | Unknown

## Expected Result
What should happen.

## Actual Result
What happens instead, including exact error text.

## Logs / Evidence
Fenced code blocks for errors and stack traces (trim noise, keep the failing lines and a few lines of context).

## Attachments
List screenshots/files with a one-line description each.

## Additional Notes
Workarounds, suspected cause (label as suspicion), regression info (last known working version), related issues, and whether it reproduces in other environments (helps separate code bugs from config or data problems).
```

## Writing guidance

- **Title:** Say what fails and where, e.g. "Checkout: Pay button unresponsive after applying coupon", not "Button broken" or "Bug in checkout".
- **Steps:** Write them so a stranger could follow them. Convert vague phrasing ("I tried logging in") into concrete actions only when the user supplied the details; otherwise ask or mark as not provided.
- **Expected vs actual:** Keep them separate and observable. Facts go here; theories go under Additional Notes.
- **Logs:** Quote verbatim. Redact secrets, tokens, passwords, and personal data (replace with `[REDACTED]`) and mention that you did.
- **Screenshots:** You may be unable to embed images in Markdown; reference them by filename in Attachments and describe what they show if you can see them.
- **Severity:** Judge by impact, and say why.
  - Critical: data loss, security issue, crash or outage with no workaround
  - High: core feature broken, workaround difficult
  - Medium: feature impaired, reasonable workaround exists
  - Low: cosmetic or minor inconvenience
  Factor in the environment: the same defect is usually more severe in Prod (real users and data affected) than in Dev or QA. A Prod issue that would be Medium elsewhere should be rated one level higher if users are impacted. For Dev/QA, note whether it is a release blocker.
  If unsure, propose a level and note it's the reporter's call.
- **One bug per report.** If the description contains several distinct problems, split them into separate reports and say so.
- Omit empty template sections only if truly irrelevant; otherwise keep them with "Not provided" so gaps are visible.
