# Flaky Test Finder - session notes (2026-09-19)

## Goal
Find flaky tests by comparing two runs of the same suite: a test is flaky if its `execution_result` differs between the runs. Built as a Langflow flow (Read File -> Groq -> Chat Output), then given a web UI on Vercel with Langflow hosted on Render.

## Architecture
```
Browser (Vercel UI) -> Vercel API route (/api/analyze) -> Langflow on Render -> Groq
  2 file uploads         holds LANGFLOW_* secrets           runs the flow         LLM
  shows the table        POST /api/v1/run/flaky-finder      returns markdown
```
Vercel cannot run Langflow (long-running Python server + database), so Langflow is hosted separately.

## Files in the repo
| Path | What it is |
|---|---|
| `langflow_work/setup.md` | Original local Langflow install steps |
| `langflow_work/flaky_tests_finder/Flaky_Test_Case_Finder.json` | Original flow (Read File -> Prompt Template -> Groq -> Chat Output, with Chat Input) |
| `langflow_work/flaky_tests_finder/Flaky_Test_Case_Finder_API.json` | API copy: Read File removed, endpoint name `flaky-finder`; test data arrives via tweaks |
| `langflow_work/flaky_tests_finder/test_data/test_run_1.json`, `test_run_2.json` | 50 test cases each (`test_case_id`, `title`, `execution_result`) |
| `flaky-finder-ui/` | Next.js app: upload page + `/api/analyze` route |
| `deploy/langflow/Dockerfile`, `render.yaml` | Langflow image (with Groq bundle) and Render blueprint |

## Test data design
- Flaky (result differs between runs): TC-014, TC-023, TC-036, TC-048.
- Decoys that fail in BOTH runs (a real bug, not flaky): TC-028, TC-040.
- Expected answer: exactly the four flaky IDs, "Total flaky tests: 4".

## The flow
- Chat Input text -> Prompt Template `{user_request}`; file text -> `{test_data}`; template output -> Groq Input -> Chat Output.
- Groq model in the export: `qwen/qwen3.8-27b`, temperature 0.1, API key from the Langflow global variable `groq_key`.
- System message (as originally written; the flow JSON is authoritative): the input has two JSON arrays, the first is Run 1 and the second is Run 2; a test is flaky if the same `test_case_id` has different results; tests failing/passing in both are not flaky; output a markdown table (Test Case ID | Title | Run 1 Result | Run 2 Result) and end with "Total flaky tests: N".
- Read File "Raw Content" joins files WITHOUT file names, so upload order matters: Run 1 first.

## Run it locally
- Langflow: `cd langflow-qa` then `.\venv\Scripts\langflow.exe run` (http://127.0.0.1:7860). Requires the `lfx-bundles[groq]` package for the Groq component.
- Create a Langflow API key (avatar -> Settings -> Langflow API Keys).
- UI: `cd flaky-finder-ui`, copy `.env.example` to `.env.local`, set `LANGFLOW_API_KEY`, then `npm run dev` (http://localhost:3000).
- Env vars: `LANGFLOW_URL`, `LANGFLOW_API_KEY`, `LANGFLOW_FLOW` (default `flaky-finder`), `PROMPT_NODE` (default `Prompt Template`), `APP_PASSWORD` (optional shared password for the UI).

## Things learned the hard way
1. **Component IDs change on import.** The tweak was first keyed by ID (`Prompt Template-4NQFq`), which no longer matched after import (`Prompt Template-70510`). Langflow silently ignores unknown tweak keys, so the model received no data and invented a 3-test dataset. Fix: key the tweak by display name, `Prompt Template`. After any flow rename, re-test.
2. **Stock Langflow images lack the Groq component.** The flow uses `ext:groq:GroqModel@official` from `lfx-bundles[groq]`, so the Docker image installs it.
3. **The database is not on the persistent disk by default.** Langflow keeps `langflow.db` inside the Python package folder, so a Render redeploy would wipe flows, variables and API keys. The Dockerfile sets `LANGFLOW_DATABASE_URL=sqlite:////data/langflow.db`.
4. **`LANGFLOW_SECRET_KEY` must be a base64 32-byte value** (if 32+ chars it is used directly as a Fernet key). Never change it after data exists, or stored variables cannot be decrypted. If Render's generated value is rejected ("Fernet key must be 32 url-safe base64-encoded bytes"), set one manually.
5. **Memory:** the container used about 1.24 GiB, so Render's 512 MB plans will not work; `render.yaml` uses the 2 GB `standard` plan (paid, check current pricing).
6. Verified locally: container health in ~35 s; flow import; flow run reaches Groq (dummy key gets a 401 as expected); flow, variable and API key survive a container recreate on the same volume.

## Status
- Done: flow, test data, UI (verified in a headless browser: table shows exactly the 4 flaky tests), Docker image and Render blueprint (tested locally), committed and pushed (`dbf032e`).
- Next:
  1. Render: New -> Blueprint -> this repo; set `LANGFLOW_SUPERUSER_PASSWORD` (login `admin`).
  2. On the hosted Langflow: log in, import `Flaky_Test_Case_Finder_API.json`, create global variable `groq_key` with the real Groq key, create an API key.
  3. Test the hosted endpoint with the two test files.
  4. Deploy `flaky-finder-ui` to Vercel (root directory `flaky-finder-ui`); set `LANGFLOW_URL` (Render URL), `LANGFLOW_API_KEY`, `LANGFLOW_FLOW`, `PROMPT_NODE`, and `APP_PASSWORD`.
  5. Consider a rate limit: the public route spends your Groq quota.

## Machine changes made during the session
- Global git identity set to "M Karanam" / the account email (needed to commit).
- Docker Desktop was started; a 3.17 GB test image `flaky-langflow:test` remains (`docker image rm flaky-langflow:test` to free space).
- The local `langflow-qa/langflow.log` was overwritten when Langflow was restarted; server logs now go to `langflow.log` (stderr) and `langflow.out.log`.
