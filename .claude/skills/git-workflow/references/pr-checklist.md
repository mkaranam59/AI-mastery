# Pull Request Checklist

1. **Gather context (parallel):**
   - `git status`
   - `git diff` (staged + unstaged)
   - Is the current branch tracking a remote, and is it up to date?
   - `git log` and `git diff <base-branch>...HEAD` for the full commit history
     since the branch diverged.

2. **Review every commit** that will be included in the PR, not just the
   latest one, before drafting the summary.

3. **Draft:**
   - Title under 70 characters.
   - Body via heredoc: `## Summary` (1-3 bullets) + `## Test plan`
     (checklist of what should be verified).
   - End with the attribution block from this session's system reminder, if
     any.

4. **Execute (parallel where independent):**
   - Create the branch if needed.
   - Push with `-u` if not already tracked.
   - `gh pr create` with the drafted title/body.

5. **Report back:** return the PR URL to the user.

Use `gh` for all GitHub-related lookups too (issues, checks, releases,
reading a PR given its URL).
