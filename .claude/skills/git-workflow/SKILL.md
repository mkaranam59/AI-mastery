---
name: git-workflow
description: >-
  Standard workflow for all git activities in this project — status checks,
  branching, staging, committing, pushing, and opening pull requests. Use
  whenever the user asks to commit, branch, push, open/update a PR, resolve
  conflicts, or otherwise touch git/GitHub state in this repo.
license: MIT
metadata:
  author: Muralidhar Karanam
  version: 1.0.0
---

# Git Workflow

You perform git/GitHub actions **carefully and transparently** — these change
shared, hard-to-reverse state. Confirm scope with the user before anything
destructive or externally visible; never expand beyond what was asked.

## When to use
- The user asks to commit, branch, push, merge, rebase, resolve conflicts,
  or open/update/review a pull request in this repo.
- Any step in another skill or task requires touching git state.

## Before any action that could discard work
Run `git status` first. If there is uncommitted or untracked work that a
command would discard (`checkout`/`restore`/`reset`/`clean`, `rm -rf` in the
repo), stash it (`git stash -u`) or commit it before proceeding — never
silently discard.

## Branching
- Create feature branches off `main` with a short, descriptive name
  (`feature/x`, `fix/y`).
- Never force-push to `main`/`master`. Warn the user if they explicitly ask
  for it and get confirmation first.

## Committing
Follow `references/commit-checklist.md`. In short:
1. Run `git status`, `git diff` (staged + unstaged), and `git log --oneline -5`
   in parallel to see full context and match this repo's message style.
2. Stage specific files by name — never `git add -A` / `git add .` — and
   re-check `git status` after staging broad changes for secrets or
   unintended files.
3. Write a concise commit message (1-2 sentences) explaining **why**, not
   just what.
4. Create a **new** commit — never `--amend` — unless the user explicitly
   asks to amend, and never if a pre-commit hook just failed (that commit
   didn't happen, so amend would target the wrong one).
5. Never skip hooks (`--no-verify`) or bypass signing unless explicitly
   instructed.
6. Only commit when the user explicitly asks. Doing the underlying task does
   not imply a commit is wanted.
7. End every commit message with the attribution line supplied in this
   session's system reminder, when one is present.

## Pushing
- Only push when explicitly asked.
- Never force-push to a shared/main branch without explicit confirmation;
  prefer a non-destructive alternative (merge, rebase onto latest, new
  commit) first.

## Pull requests
Follow `references/pr-checklist.md`. In short:
1. Check branch state vs. the base branch (status, diff, whether the remote
   tracking branch is current) before drafting anything.
2. Review **all** commits that will be included, not just the latest one.
3. Push with `-u` if the branch isn't tracked yet, then `gh pr create` with a
   short title (<70 chars) and a heredoc body covering Summary and Test plan.
4. End the PR body with the attribution block from this session's system
   reminder, when one is present.
5. Return the PR URL to the user.

## Conflicts and destructive recovery
- Resolve merge conflicts in place rather than discarding either side.
- If a lock file blocks an operation, investigate what holds it rather than
  deleting it.
- Treat unfamiliar branches/files/stashes as someone's in-progress work:
  investigate before deleting or overwriting.

## Guardrails
- Never update git config.
- Never run `push --force` (without explicit instruction + confirmation),
  `reset --hard`, `checkout .` / `restore .`, `clean -f`, or `branch -D`
  unless the user explicitly requests exactly that action.
- Never skip hooks or bypass commit signing unless explicitly instructed.
- Match scope to what was asked — a request to commit is not a request to
  also push, and a request to push is not a request to also open a PR.

## References
- `references/commit-checklist.md` — step-by-step commit flow
- `references/pr-checklist.md` — step-by-step PR flow
