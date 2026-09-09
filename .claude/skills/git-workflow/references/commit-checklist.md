# Commit Checklist

1. **Gather context (parallel):**
   - `git status` (never `-uall`, it can be slow on large repos)
   - `git diff` (staged + unstaged)
   - `git log --oneline -5` (match this repo's message style)

2. **Draft the message:**
   - Classify the change: feature, enhancement, fix, refactor, test, docs.
   - 1-2 sentences, focused on *why*, not a restatement of the diff.
   - Accurate: "add" = new feature, "update" = enhancement, "fix" = bug fix.

3. **Stage deliberately:**
   - Add specific files by name.
   - Never commit files that likely hold secrets (`.env`, `credentials.json`,
     etc.) — warn the user if they ask for this explicitly.
   - After a broad `git add`, run `git status` again and eyeball the list.

4. **Commit:**
   - Pass the message via heredoc/here-string, not repeated `-m` flags.
   - Append the attribution line from this session's system reminder, if any.
   - Always create a new commit — never `--amend` — unless explicitly asked.

5. **Verify:** `git status` after the commit to confirm a clean result.

6. **On hook failure:** fix the underlying issue, re-stage, create a new
   commit. Never `--no-verify` unless explicitly instructed.
