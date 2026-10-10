# Project: SkillMasterclass — Dynamic Skill Discovery and MCP Server

## 1. Role and Objective

Act as a **Senior MCP Engineer, AI Agent Architect, Software Test Automation Expert, and Python/TypeScript Software Architect**.

Your task is to inspect the existing repository and build a production-ready **Model Context Protocol (MCP) server** that enables compatible LLMs and AI agents to discover, search, retrieve, and leverage skills from the existing `/skillmasterclass/` directory.

The MCP server must allow an LLM to find the appropriate skill based on a keyword, natural-language query, task description, or testing requirement.

For example:

- Searching for `Playwright` should return relevant Playwright skills.
- Searching for `Playwright API testing` should return relevant API testing skills.
- Searching for `test case creator` should find skills for generating test cases.
- Searching for `test plan creator` should find skills for creating test plans.
- Searching for `test strategy` should identify applicable testing strategy skills.
- Searching for `analyze production defect` should identify relevant defect analysis and root cause analysis skills.
- Searching for `create an end-to-end automation framework` should identify relevant automation architecture, framework development, and CI/CD skills.

The server must expose a reusable set of MCP tools, prompts, and resources that allow an LLM to discover the right skill and retrieve the corresponding instructions and supporting resources.

**Primary objective:** Build a maintainable, extensible skill discovery platform that dynamically uses the existing skill library without hardcoding individual skill names or duplicating their complete contents.

Do not stop at proposing an architecture. Implement, test, document, and validate the solution in the existing repository.

---

## 2. Source of Truth: `/skillmasterclass/`

The `/skillmasterclass/` directory is the **single source of truth for all skills**.

Each skill has its own directory containing a `SKILL.md` file. A skill may also include supporting resources, examples, scripts, templates, or reference documents.

Illustrative directory structure:

```text
project-root/
├── skillmasterclass/
│   ├── playwright/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── playwright-api-testing/
│   │   └── SKILL.md
│   ├── selenium-automation/
│   │   └── SKILL.md
│   ├── test-case-creator/
│   │   └── SKILL.md
│   ├── test-plan-creator/
│   │   └── SKILL.md
│   ├── test-strategy/
│   │   └── SKILL.md
│   └── ... additional skills
├── src/
│   └── ... MCP server implementation
├── tests/
├── README.md
└── ... existing project files
```

This structure is illustrative only. Inspect the actual repository before making assumptions about paths, naming conventions, or technology choices.

### Mandatory source-discovery rules

1. Identify the actual path of `/skillmasterclass/` relative to the repository root.
2. Recursively discover valid skills by locating their `SKILL.md` files.
3. Treat each skill's `SKILL.md` as its authoritative definition.
4. Parse the existing metadata and frontmatter conventions rather than imposing an incompatible format.
5. Extract fields such as skill name, description, tags, category, and other metadata when available.
6. Discover supporting resources relative to the corresponding skill directory.
7. Build the search index dynamically from the discovered skills.
8. Do not hardcode individual skill names in the MCP implementation.
9. Do not maintain a manually synchronized catalog that duplicates the full contents of `SKILL.md`.
10. Preserve existing skills and their supporting resources.
11. Support future additions, modifications, and removals of skills without modifying the core MCP implementation.
12. If the configured source directory is missing or invalid, report a clear configuration error. Do not silently switch to another directory.

Make the skill directory configurable through an environment variable or equivalent project configuration, while defaulting to the actual `/skillmasterclass/` location in the repository.

---

## 3. Repository Inspection and Initial Audit

Before writing code, inspect the existing project.

Determine:

- Programming language and framework
- Existing project architecture
- Package manager and dependency management approach
- Current MCP SDK or related dependencies
- Existing skill directory location
- Number of discovered `SKILL.md` files
- Skill metadata and frontmatter conventions
- Existing tools, prompts, resources, and integrations
- Existing tests and testing framework
- Current configuration and logging practices

Produce an initial audit containing:

1. Repository structure summary
2. Current valid skill count
3. Skill metadata conventions
4. Missing or malformed skill definitions
5. Duplicate skill identifiers, if any
6. Recommended MCP architecture
7. Implementation plan

Reuse the existing technology stack wherever practical.

If no stack has been established, choose a suitable implementation based on maintainability, MCP SDK support, testing, and ease of client integration. Document the decision and its rationale.

Do not replace working components unnecessarily.

---

## 4. Minimum Skill Inventory: At Least 50 Valid Skills

The repository must contain **at least 50 distinct, valid, usable skills**, each represented by its own `SKILL.md` file under `/skillmasterclass/`.

First, audit the existing inventory. Reuse existing skills wherever possible.

If fewer than 50 valid skills exist, create additional skills to meet the target.

### Skill creation requirements

Each new skill must:

- Have its own appropriately named directory.
- Contain a `SKILL.md` file.
- Follow the repository's established skill format.
- Include meaningful, actionable instructions.
- Clearly describe its purpose and applicable use cases.
- Define the workflow for applying the skill.
- Specify expected inputs and outputs where appropriate.
- Include examples and validation criteria when useful.
- Reference supporting resources through valid paths.
- Avoid duplication of existing skills.
- Avoid empty placeholders or superficial variations of existing skills.

Do not rewrite or overwrite existing skills unless there is a clear reason and the change is justified.

Create a validation report showing the total discovered skills, valid skills, invalid skills, and duplicate identifiers.

### Suggested skill categories

Prioritize software testing, quality engineering, test automation, and AI-assisted development.

#### A. Test analysis and planning

1. Requirements analysis
2. Test scenario identification
3. Test case creation
4. Test plan creation
5. Test strategy development
6. Risk-based testing
7. Test estimation
8. Requirements traceability matrix generation
9. Test coverage analysis
10. Test data design

#### B. Test automation

11. Playwright automation
12. Playwright API testing
13. Selenium automation
14. WebdriverIO automation
15. Pytest framework development
16. Page Object Model design
17. Test automation framework architecture
18. Cross-browser testing
19. Mobile application testing
20. CI/CD test integration

#### C. API, database, and integration testing

21. REST API testing
22. API contract testing
23. API authentication and authorization testing
24. Database testing
25. SQL validation
26. Data pipeline testing
27. Integration testing
28. Microservices testing
29. Message queue testing
30. Test data generation

#### D. Defect and quality management

31. Bug report creation
32. Defect triage
33. Root cause analysis
34. Regression testing
35. Smoke and sanity testing
36. Exploratory testing
37. Test execution reporting
38. Quality metrics and dashboards
39. Release readiness assessment
40. Defect trend analysis

#### E. Specialized and AI testing

41. Performance testing
42. Security testing
43. Accessibility testing
44. Compatibility testing
45. AI/ML application testing
46. LLM prompt evaluation
47. RAG application testing
48. AI agent testing
49. AI-generated test case evaluation
50. Test automation code review

These are suggested capabilities, not mandatory filenames. Map them to existing skills where possible. Add other useful skills when the existing library supports them or when there is a clear capability gap.

---

## 5. MCP Server Architecture

Implement a modular MCP server with a clean separation of responsibilities.

Recommended logical components:

1. **Skill Discovery Service** — discovers skill directories and their `SKILL.md` files.
2. **Skill Parser** — extracts metadata and content while preserving the original instructions.
3. **Skill Index** — maintains searchable metadata and relevant content.
4. **Search Engine** — matches and ranks skills against user queries.
5. **Skill Retrieval Service** — retrieves the complete selected skill instructions.
6. **Resource Service** — discovers and retrieves supporting files safely.
7. **MCP Tool Registry** — exposes skill discovery and retrieval capabilities as tools.
8. **MCP Prompt Registry** — exposes reusable task-oriented prompt templates.
9. **MCP Resource Registry** — exposes skill catalogs and individual skill resources.
10. **Transport Layer** — supports local stdio and Streamable HTTP.
11. **Validation Service** — checks skill structure, metadata, and resource references.
12. **Configuration and Logging** — manages paths, transport settings, errors, and diagnostics.

Keep business logic independent of the transport layer so the same discovery and retrieval implementation can serve both local and HTTP clients.

Follow the current official MCP specification and the selected SDK's supported APIs.

Do not implement deprecated transport patterns when a supported alternative is available.

---

## 6. MCP Tools

Expose a manageable set of generic MCP tools that operate dynamically on the discovered skill inventory.

Do not create one hardcoded MCP tool for every skill. The server must support a growing skill library without requiring changes to its core implementation.

### Tool 1: `list_skills`

**Purpose:** List available skills.

Inputs:

- `category` — optional category filter
- `keyword` — optional keyword filter
- `limit` — optional maximum number of results
- `offset` or equivalent pagination parameter — optional

Expected output:

- Skill name
- Description
- Category, if available
- Tags, if available
- Stable skill identifier
- Relative skill path

Requirements:

- Return only discovered skills.
- Support pagination.
- Handle an empty inventory gracefully.
- Avoid returning full skill instructions unnecessarily.

### Tool 2: `search_skills`

**Purpose:** Search skills by keyword, phrase, or natural-language task description.

Inputs:

- `query` — required search query
- `category` — optional category
- `limit` — optional result limit
- `search_mode` — optional search strategy, such as keyword or semantic

Expected behavior:

- Case-insensitive matching
- Partial keyword matching
- Phrase matching
- Multiple keyword matching
- Search across names, descriptions, tags, and relevant content
- Relevance-based ranking
- Configurable result limits
- Useful explanations of why a skill matches

Example:

```text
Query: Playwright API testing

Results:
1. Playwright API Testing
   Reason: Matches Playwright, API testing, and related instructions.

2. API Test Automation
   Reason: Matches API testing and automation concepts.

3. Test Automation Framework Design
   Reason: Provides related framework design guidance.
```

The example results above are illustrative. Return actual skills from the repository, and do not invent nonexistent skills.

Search must remain useful when semantic search or external embedding services are unavailable.

### Tool 3: `get_skill`

**Purpose:** Retrieve the complete `SKILL.md` content for a selected skill.

Inputs:

- `skill_id` or a unique skill name

Expected output:

- Skill metadata
- Complete `SKILL.md` content
- Skill identifier and relative path
- References to associated resources, when available

Requirements:

- Resolve identifiers against the discovered inventory.
- Reject ambiguous identifiers or provide a clear selection mechanism.
- Validate paths before reading files.
- Prevent path traversal.
- Never read files outside the configured skill directory through user-controlled identifiers.
- Report missing or unreadable files clearly.

The returned instructions must preserve the original skill's content and meaning.

### Tool 4: `get_skill_details`

**Purpose:** Retrieve structured metadata without returning the entire skill instructions.

Inputs:

- Skill identifier or unique name

Expected output:

- Name
- Description
- Tags
- Category
- Relative path
- Supported use cases
- Associated resources
- Other available metadata

Do not fabricate metadata that does not exist. Derive additional fields only when appropriate and identify inferred fields when necessary.

### Tool 5: `get_skill_resources`

**Purpose:** Discover or retrieve supporting resources associated with a skill.

Inputs:

- Skill identifier
- Optional relative resource path

Possible resources:

- Reference documentation
- Templates
- Examples
- Scripts
- Configuration files
- Other supporting documents

Requirements:

- List available resources when no specific resource is provided.
- Retrieve the selected resource when requested.
- Restrict file access to the selected skill's permitted directory and any explicitly configured shared-resource directory.
- Reject path traversal and unsafe file access.
- Handle missing resources gracefully.

### Tool 6: `recommend_skills`

**Purpose:** Recommend relevant skills for a task.

Inputs:

- Natural-language task description
- Optional maximum result count

Example request:

```text
Build an end-to-end Playwright API automation framework
with authentication, reusable fixtures, reporting, and CI/CD integration.
```

The tool should identify relevant available skills for API automation, Playwright fixtures, authentication, framework architecture, reporting, and CI/CD, where those skills exist.

Expected output:

- Recommended skill identifiers
- Skill descriptions
- Relevance scores or rankings
- Reasons for each recommendation
- Suggested order of use, where useful

Recommendations must be based on the actual inventory. Do not claim that a skill exists when it does not.

### Tool 7: `validate_skills`

**Purpose:** Validate the complete skill inventory.

Check for:

- Missing `SKILL.md` files
- Invalid metadata or frontmatter
- Missing required fields
- Empty or incomplete instructions
- Duplicate identifiers
- Duplicate or highly overlapping skills
- Broken resource references
- Unreadable files
- Invalid resource paths
- Skills that cannot be indexed

Return a structured report with errors, warnings, affected skill identifiers, and actionable suggestions.

Validation must not silently modify existing skills.

### Tool 8: `get_skill_catalog`

**Purpose:** Retrieve a compact overview of the available skill library.

Return:

- Total discovered skills
- Number of valid skills
- Categories and counts, when available
- Skill names and short descriptions
- Inventory validation status

Support pagination or category filtering so the complete inventory does not need to be returned in a single response.

### Tool 9: `refresh_skill_index`

**Purpose:** Refresh the skill inventory and search index after file changes.

Requirements:

- Rediscover `SKILL.md` files.
- Reparse updated metadata.
- Add newly created skills.
- Remove deleted skills from the active index.
- Update changed skill contents.
- Report the refresh outcome.
- Handle partial failures without silently corrupting the existing usable index.

Protect the refresh operation against concurrent requests where necessary.

If appropriate, provide a read-only deployment mode in which index refresh is disabled for untrusted clients.

### Additional tools

Add other tools only when they provide meaningful value, such as:

- `list_skill_categories`
- `find_related_skills`
- `get_skill_statistics`
- `check_skill_dependencies`

Document every registered tool, its input schema, expected output, and error behavior.

---

## 7. MCP Prompts

Expose reusable MCP prompts that guide LLMs through common workflows using the actual skill library.

Suggested prompts:

- `find_skill_for_task`
- `generate_test_cases`
- `create_test_plan`
- `create_test_strategy`
- `design_playwright_tests`
- `design_playwright_api_tests`
- `review_test_automation_framework`
- `analyze_defect`
- `perform_root_cause_analysis`
- `analyze_test_coverage`
- `evaluate_llm_application`
- `review_test_results`

Each prompt should:

1. Accept relevant user inputs.
2. Identify the user's objective and constraints.
3. Guide the LLM to discover relevant skills.
4. Guide the LLM to retrieve the selected skill instructions.
5. Use supporting resources when needed.
6. Apply the retrieved instructions to the task.
7. Produce an output appropriate to the requested workflow.
8. Identify missing information and state assumptions.
9. Avoid inventing unavailable skills or resources.

Where possible, prompts should reference the discovery tools and resources exposed by the server rather than embedding copies of individual skill instructions.

Prompts must be discoverable and invocable through MCP clients that support MCP prompts.

---

## 8. MCP Resources

Expose discoverable MCP resources for the skill inventory and individual skills.

At a minimum, support:

### A. Skill catalog resource

Provide a resource representing the available skill catalog.

It should contain a compact inventory of discovered skills, including identifiers, descriptions, and metadata when available.

### B. Individual skill resources

Expose each skill's content using a stable resource URI or equivalent identifier.

For example, a URI pattern could resemble:

```text
skillmasterclass://skills/playwright
skillmasterclass://skills/playwright-api-testing
skillmasterclass://skills/test-case-creator
```

These are illustrative identifiers. Select a valid, documented resource URI scheme consistent with the chosen MCP SDK and implementation.

### C. Skill metadata resources

Where useful, expose structured metadata for individual skills.

### D. Supporting resources

Expose references to associated resources when appropriate and permitted.

Requirements:

- Resource identifiers must resolve deterministically.
- Resource discovery must reflect the actual inventory.
- Individual resources must be retrievable without loading the entire library.
- Deleted or unavailable resources must return meaningful errors.
- Resource access must respect the configured filesystem boundary.
- Document how clients discover and retrieve resources.

Do not assume every MCP client supports dynamic resource listing, resource templates, prompts, and tools identically. Test the capabilities supported by the selected SDK and document any client-specific limitations.

---

## 9. Search and Indexing Strategy

Implement a search engine that works without requiring an external AI service.

### Phase 1: Keyword search

Index:

- Skill names
- Descriptions
- Tags
- Categories
- Relevant `SKILL.md` content

Implement:

- Case-insensitive matching
- Partial matching
- Phrase matching
- Multiple keyword matching
- Relevance ranking
- Optional category filtering
- Result limits and pagination

Use a suitable local search implementation for the selected programming language.

### Phase 2: Optional semantic search

Provide semantic search as an optional enhancement.

Possible approaches include:

- A configurable embedding provider
- A local embedding model
- A pluggable vector search implementation

Requirements:

- Do not make semantic search mandatory.
- Do not require an external AI API for basic operation.
- Handle missing credentials, model failures, and unavailable embedding services gracefully.
- Allow semantic search to be disabled through configuration.
- Document additional dependencies and resource requirements.

### Search result format

Return structured results containing:

- Skill identifier
- Skill name
- Description
- Relative path
- Match score or ranking
- Short match explanation

Do not expose complete skill contents in ordinary search results unless explicitly requested.

### Index refresh

Build the index at startup and support explicit refresh through the relevant MCP tool.

If automatic filesystem watching is implemented, make it configurable and ensure it does not introduce unnecessary CPU usage or concurrency problems.

A refreshed index should become available atomically so clients do not observe a partially rebuilt catalog.

---

## 10. Skill Parsing and File Safety

Follow the existing `SKILL.md` conventions.

Do not assume that every file contains identical metadata or that every metadata field is mandatory.

Requirements:

- Parse supported frontmatter and structured metadata.
- Preserve the original Markdown instructions.
- Handle malformed frontmatter without crashing the entire server.
- Distinguish fatal errors from recoverable validation warnings.
- Normalize skill identifiers consistently.
- Detect duplicate identifiers and ambiguous skill names.
- Validate all paths before reading resources.
- Resolve symbolic links safely or reject them according to the security policy.
- Prevent traversal outside permitted directories.
- Apply sensible file-size limits.
- Avoid executing scripts found in skill directories merely because they exist.
- Do not interpret skill instructions as trusted system-level instructions for the MCP server itself.

Treat skill contents as data supplied to the consuming LLM. Retrieved instructions must not be allowed to override server security policies or authorize unrestricted filesystem access.

---

## 11. Transport and Client Compatibility

Support two transport modes through the same underlying skill services.

### A. Local MCP mode

Use a supported local transport, typically stdio.

Requirements:

- Provide straightforward startup instructions.
- Provide configuration examples for compatible MCP clients and coding agents.
- Use the correct SDK initialization and lifecycle procedures.
- Keep stdout free of diagnostic logs and other non-protocol output when required by the selected transport.
- Send diagnostics to stderr or an appropriate logging destination.
- Support configurable paths and environment variables.
- Shut down cleanly when the client disconnects.

Provide a representative client configuration, adapted to the actual project structure and runtime.

### B. Streamable HTTP mode

Implement Streamable HTTP using the supported MCP SDK and current protocol specification.

Requirements:

- Configurable host, port, and endpoint.
- Correct MCP session and request handling as required by the selected SDK.
- Appropriate connection lifecycle management.
- Input validation and request size limits.
- Authentication and authorization when exposed beyond a trusted local environment.
- Safe network binding defaults.
- Appropriate CORS and origin validation where applicable.
- Protection against DNS rebinding and unauthorized cross-origin access where relevant to the deployment.
- Clear startup and client connection instructions.

Do not expose an unauthenticated filesystem-backed MCP service to an untrusted network.

### C. Shared implementation

Both transports must expose the same core discovery, retrieval, search, validation, prompts, and resource capabilities, subject to SDK and transport support.

Do not maintain separate copies of the skill search logic for different transports.

### D. Client compatibility

Verify protocol interactions using an MCP client or SDK test harness.

Document compatibility based on actual tests rather than claiming support for every LLM client.

---

## 12. Configuration

Provide a clear configuration mechanism using environment variables, configuration files, or the repository's existing approach.

Support relevant settings such as:

```text
SKILLMASTERCLASS_ROOT=<absolute-or-resolved-skillmasterclass-path>
MCP_TRANSPORT=stdio
MCP_HOST=127.0.0.1
MCP_PORT=<configured-port>
MCP_LOG_LEVEL=INFO
SKILL_SEARCH_MODE=keyword
SKILL_INDEX_REFRESH_ENABLED=true
```

These are illustrative variable names. Align the final names with the existing project and document them consistently.

Requirements:

- Validate configuration at startup.
- Resolve relative paths deterministically.
- Avoid relying on the process's current working directory without a documented reason.
- Use safe defaults.
- Do not hardcode credentials.
- Keep secrets out of logs and source control.
- Clearly distinguish development settings from production settings.

---

## 13. Testing Requirements

Create automated tests using the repository's existing testing framework or a suitable framework for the chosen stack.

### A. Discovery tests

Test:

- Discovery of valid `SKILL.md` files
- Nested skill directories
- Empty directories
- Missing source directory
- Malformed metadata
- Unreadable files
- Duplicate skill identifiers
- Supporting-resource discovery

### B. Inventory tests

Test:

- The minimum 50-valid-skill acceptance requirement
- Correct skill counts
- No placeholder skills
- No duplicate skill identifiers
- Correct association between skill directories and their `SKILL.md` files

### C. Search tests

Test:

- Exact skill name
- Partial keyword
- Case-insensitive query
- Multi-keyword query
- Natural-language query
- Description matching
- Content matching
- Category filtering
- Result ranking
- Pagination
- Empty search results

Include test cases for:

```text
Playwright
Playwright API testing
test case creator
test plan creator
test strategy
generate login test cases
analyze production defects
create an automation framework
```

Use real skills in the repository and verify expected matches.

### D. Retrieval tests

Test:

- Complete skill retrieval
- Metadata retrieval
- Missing skill identifier
- Ambiguous skill name
- Deleted skill
- Missing `SKILL.md`
- Unicode and Markdown content
- Supporting-resource retrieval

### E. Security tests

Test:

- Path traversal attempts
- Absolute paths supplied as identifiers
- Malicious relative paths
- Unsafe symbolic links
- Access attempts outside permitted directories
- Oversized resource files
- Malformed requests
- Unauthorized HTTP access where authentication is configured

### F. MCP protocol tests

Verify that the server correctly exposes and handles:

- Tool listing
- Tool invocation
- Prompt listing and invocation
- Resource discovery and retrieval
- Tool input validation
- Protocol errors
- Session lifecycle where applicable
- Transport initialization and shutdown

Use real MCP protocol interactions rather than relying exclusively on direct function calls.

### G. Index refresh tests

Test:

- Adding a new skill
- Modifying a skill
- Removing a skill
- Refreshing after a metadata change
- Handling a partially invalid inventory
- Preserving the last usable index if a refresh fails

### H. Transport tests

Test:

- Local stdio startup and communication
- Streamable HTTP initialization and communication
- Correct error handling
- Logging behavior
- Configuration validation

### I. Regression tests

Ensure that existing repository functionality remains intact.

Run the complete test suite and resolve failures caused by the implementation. Report any remaining unrelated or environment-dependent failures honestly.

---

## 14. Performance and Reliability

The server must be suitable for a skill library that grows beyond 50 skills.

Requirements:

- Avoid reading every skill file for every search request when a valid index is available.
- Cache parsed metadata and indexed content appropriately.
- Refresh changed data deterministically.
- Use bounded result sizes.
- Avoid loading all skill resources into every response.
- Prevent duplicate concurrent index rebuilds.
- Handle file changes and partial failures gracefully.
- Provide structured logging and actionable errors.
- Avoid unnecessary external service dependencies.
- Keep startup time and memory usage reasonable.

Do not introduce a database or vector store unless the implementation benefits justify the additional complexity.

---

## 15. Documentation and Deliverables

Provide the following deliverables in the existing repository.

### A. MCP server implementation

- Complete source code
- Skill discovery and parsing
- Search and indexing implementation
- Skill retrieval
- Resource retrieval
- MCP tools
- MCP prompts
- MCP resources
- Local stdio transport
- Streamable HTTP transport
- Configuration and logging

### B. Skill inventory

- At least 50 valid, usable skills
- One `SKILL.md` per skill
- Existing supporting resources preserved
- Newly created skills validated
- No duplicate identifiers introduced

### C. Automated tests

- Unit tests
- Integration tests
- MCP protocol tests
- Security tests
- Transport tests
- Search and indexing tests

### D. Documentation

Create or update the README with:

1. Project overview
2. Architecture diagram or architecture description
3. Repository structure
4. Skill directory conventions
5. Skill discovery and indexing flow
6. MCP tool catalog
7. MCP prompt catalog
8. MCP resource catalog
9. Installation instructions
10. Configuration settings
11. Local MCP client configuration
12. Streamable HTTP setup and connection examples
13. Security guidance
14. Commands to run the server
15. Commands to execute tests
16. Example search requests and expected responses
17. Instructions for adding a new skill
18. Troubleshooting guidance
19. Known limitations
20. Future enhancement opportunities

### E. Final implementation report

Include:

- Original skill count
- Final valid skill count
- Number of newly created skills
- Tools implemented
- Prompts implemented
- Resources implemented
- Supported transports
- Tests executed
- Test results
- Security validation results
- Any known limitations

---

## 16. Acceptance Criteria

The project is considered complete only when all applicable criteria below have been verified.

### Skill inventory

- [ ] `/skillmasterclass/` is the authoritative source directory.
- [ ] Each valid skill is discovered from its own `SKILL.md`.
- [ ] At least 50 distinct, valid, usable skills exist.
- [ ] Existing skills and supporting resources are preserved.
- [ ] Newly created skills follow the repository's established format.
- [ ] No duplicate skill identifiers are introduced.

### Search and retrieval

- [ ] Searching for `Playwright` returns relevant available skills.
- [ ] Searching for `Playwright API testing` returns relevant API testing skills.
- [ ] Searching for `test case creator` finds the relevant test case skill.
- [ ] Searching for `test plan creator` finds the relevant planning skill.
- [ ] Searching for `test strategy` finds relevant strategy skills.
- [ ] Natural-language task queries return relevant results.
- [ ] The LLM can retrieve the complete `SKILL.md` for a selected skill.
- [ ] Associated resources can be discovered and retrieved safely.
- [ ] Results reflect new, modified, and removed skills after index refresh.

### MCP capabilities

- [ ] The MCP server exposes the required tools.
- [ ] Reusable prompts are registered and usable.
- [ ] Skill catalog and individual skill resources are available.
- [ ] Tools, prompts, and resources work through supported MCP protocol interactions.
- [ ] Local stdio transport works.
- [ ] Streamable HTTP transport works.
- [ ] Both transports use the same underlying skill services.

### Security and quality

- [ ] Path traversal attempts are rejected.
- [ ] Unauthorized file access is prevented.
- [ ] HTTP deployment follows appropriate security controls.
- [ ] Invalid skill files produce clear validation errors.
- [ ] Automated tests execute successfully, with any remaining failures documented.
- [ ] Documentation matches the actual implementation.
- [ ] The final implementation report is provided.

Do not mark a criterion complete without verification.

---

## 17. Execution Workflow

Execute the project in the following sequence.

### Phase 1: Inspect

- Examine the repository.
- Identify the actual `/skillmasterclass/` path.
- Count valid skills.
- Review representative `SKILL.md` files.
- Identify the existing technology stack and dependencies.
- Document the initial state.

### Phase 2: Design

- Propose the architecture.
- Define skill discovery and metadata parsing.
- Define the search and indexing approach.
- Define the MCP tools, prompts, and resources.
- Define transport configuration and security controls.
- Identify required dependencies.

### Phase 3: Implement discovery and search

- Build the recursive skill discovery service.
- Parse metadata and instructions.
- Build the index.
- Implement keyword search and ranking.
- Implement skill retrieval and resource access.
- Implement index refresh.

### Phase 4: Implement MCP capabilities

- Register MCP tools.
- Register reusable prompts.
- Register skill catalog and individual resources.
- Validate tool input and output schemas.
- Verify protocol interactions.

### Phase 5: Complete the skill inventory

- Audit the current inventory.
- Reuse existing skills.
- Add distinct skills until the minimum target is met.
- Validate each new `SKILL.md`.
- Confirm that all valid skills are discoverable.

### Phase 6: Implement transports

- Implement local stdio mode.
- Implement Streamable HTTP mode.
- Add configuration and safe defaults.
- Verify both modes through MCP client interactions.

### Phase 7: Test and harden

- Run automated tests.
- Validate search accuracy.
- Test resource access boundaries.
- Test index refresh.
- Test protocol interactions and transport lifecycle.
- Resolve defects and regressions.

### Phase 8: Document and report

- Update the README.
- Provide client configuration examples.
- Document installation, execution, and testing.
- Report the actual skill count and implementation status.
- List verified acceptance criteria.
- Document known limitations and future improvements.

---

## 18. Implementation Rules

Follow these rules throughout development:

1. Work directly in the existing repository.
2. Inspect before modifying.
3. Reuse existing code and dependencies when appropriate.
4. Do not overwrite existing skill content unnecessarily.
5. Do not hardcode skill names into the core MCP server.
6. Do not create placeholder skills to satisfy the minimum count.
7. Do not expose unrestricted filesystem access through MCP.
8. Do not execute scripts merely because they exist in a skill directory.
9. Do not require external AI services for basic keyword search.
10. Do not claim tests passed unless they were actually executed.
11. Do not claim compatibility with clients or transports that were not verified.
12. Keep documentation aligned with the implementation.
13. Make reasonable, documented decisions instead of stopping for nonessential questions.
14. If blocked by a missing dependency, unavailable environment, or permission issue, explain the limitation and complete all independent work possible.
15. Preserve backward compatibility with existing repository functionality wherever feasible.

## Final Objective

Build **SkillMasterclass MCP Server**, a reusable skill discovery and retrieval platform that allows compatible LLMs and AI agents to search a library of at least 50 skills, retrieve their authoritative `SKILL.md` instructions, access associated resources, and apply the skills through standardized MCP tools, prompts, and resources.

The implementation must be dynamic, secure, testable, documented, and extensible. Adding a new skill to `/skillmasterclass/` must not require changes to the MCP server's core code.