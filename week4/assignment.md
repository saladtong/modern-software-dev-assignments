# Week 4 Assignment: The Autonomous Coding Agent IRL

Build at least two automations in the context of this repo using any combination of:
- Claude Code custom slash commands (checked into `.claude/commands/*.md`)
- `CLAUDE.md` files for repository/context guidance
- Claude SubAgents (role-specialized agents working together)

Use the app in `week4/` as your playground. Your automations should meaningfully improve a developer workflow (tests, docs, refactors, data tasks, etc.).

## References
- Claude Code best practices: [anthropic.com/engineering/claude-code-best-practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- SubAgents overview: [docs.anthropic.com/en/docs/claude-code/sub-agents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)

## What to build (choose at least two)
You may mix-and-match across categories.

### A) Claude custom commands (slash commands)
Create Markdown files in `.claude/commands/` that define reusable workflows. Claude exposes these via `/`.

- Example 1: Test runner with coverage
  - Name: `tests.md`
  - Intent: Run `pytest -q backend/tests --maxfail=1 -x` and, if green, run coverage.
  - Inputs: Optional marker or path.
  - Output: Summarize failures and suggest next steps.
- Example 2: Docs sync
  - Name: `docs-sync.md`
  - Intent: Read `/openapi.json`, update `docs/API.md`, and list route deltas.
  - Output: Diff-like summary and TODOs.
- Example 3: Refactor harness
  - Name: `refactor-module.md`
  - Intent: Rename a module (e.g., `services/extract.py` → `services/parser.py`), update imports, run lint/tests.
  - Output: A checklist of modified files and verification steps.

Tips (from best practices): keep commands focused, use `$ARGUMENTS`, and prefer idempotent steps. Consider allowlisting safe tools and using headless mode for repeatability.

### B) `CLAUDE.md` guidance files
Create `CLAUDE.md` in the repo root (and optionally in `week4/` subfolders) to guide Claude’s behavior.

- Example 1: Code navigation and entry points
  - Include: How to run the app, where routers live (`backend/app/routers`), where tests live, how the DB is seeded.
- Example 2: Style and safety guardrails
  - Include: Tooling expectations (black/ruff), safe commands to run, commands to avoid, and lint/test gates.
- Example 3: Workflow snippets
  - Include: “When asked to add an endpoint, first write a failing test, then implement, then run pre-commit.”

Tips (from best practices): iterate on `CLAUDE.md` like a prompt, keep it concise and actionable, and document custom tools/scripts you expect Claude to use.

### C) SubAgents (role-specialized)
Design two or more cooperating agents that each own a step in a workflow.

- Example 1: TestAgent + CodeAgent
  - Flow: TestAgent writes/updates tests for a change → CodeAgent implements code to pass tests → TestAgent verifies.
- Example 2: DocsAgent + CodeAgent
  - Flow: CodeAgent adds a new API route → DocsAgent updates `API.md` and `TASKS.md` and checks drift against `/openapi.json`.
- Example 3: DBAgent + RefactorAgent
  - Flow: DBAgent proposes a schema change (adjust `data/seed.sql`) → RefactorAgent updates models/schemas/routers and fixes lints.

Tips (from best practices): use checklists/scratchpads, reset context (`/clear`) between roles, and run agents in parallel for independent tasks.

## Deliverables
1) The automations themselves:
   - Slash commands in `.claude/commands/*.md`, and/or
   - `CLAUDE.md` files, and/or
   - SubAgent prompts/configuration (documented clearly, files/scripts if any)
2) A write-up: `week4_automations.md` under `week4/` that includes:
   - The design of each automation (goals, inputs/outputs, steps)
   - What inspired the design (cite the best-practices and/or sub-agents docs)
   - Before/after: what the workflow looked like manually vs. with automation
   - How to run it (exact commands), expected outputs, and rollback/safety notes

Use the best-practices guidance to iterate: keep prompts small, use headless mode for repeatability, and maintain checklists so agents can track progress ([best practices](https://www.anthropic.com/engineering/claude-code-best-practices), [SubAgents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)).
