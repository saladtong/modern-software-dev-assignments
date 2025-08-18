# Week 5 Assignment: Agentic Development with Warp

Use the app in `week5/` as your playground. This week mirrors the prior assignment but emphasizes the Warp agentic development environment and multi‑agent workflows.

## References
- Warp Agentic Development Environment: [warp.dev](https://www.warp.dev/)
- [Warp University](https://www.warp.dev/university?slug=university)

## What to build 
Pick from `week5/docs/TASKS.md` and automate parts of those flows with Warp. You may mix‑and‑match across categories. Keep changes focused on backend/frontend/logic/tests inside `week5/`.

### A) Warp Drive saved prompts, rules, MCP servers (required: at least one)
Create one or more shareable Warp Drive prompts, rules, or MCP server integrations tailored to this repo. Examples:
- Test runner with coverage and flaky‑test re‑run
- Docs sync: generate/update `docs/API.md` from `/openapi.json`, list route deltas
- Refactor harness: rename a module, update imports, run lint/tests
- Release helper: bump versions, run checks, prepare a changelog snippet
- Integrate the Git MCP server to have Warp interact with Git autonomously (creating branches, commits, PR notes, etc)

Tips: keep workflows focused, pass arguments, make them idempotent, and prefer headless/non‑interactive steps where possible.

### B) Multi‑agent workflows in Warp (required: at least one)
Run a multi‑agent session where separate agents in different Warp tabs handle independent tasks concurrently. 
- Perform multiple self-contained tasks from `TASKS.md` in separate Warp tabs using concurrent agents. Challenge: how many agents can you have working simultaneously?

Tips: [git worktree](https://git-scm.com/docs/git-worktree) may be helpful here to keep agents from clobbering over each other.

## Constraints and scope
- Work strictly in `week5/` (backend, frontend, logic, tests). Avoid changing other weeks unless the automation explicitly requires it and you document why.

## Deliverables
1) The automations themselves:
   - Warp Drive workflows/rules (share links and/or exported definitions) and any helper scripts
   - Any supplemental prompts/playbooks used to coordinate multiple agents
2) A write‑up: `week5_automations.md` under `week5/` that includes:
   - The design of each automation (goals, inputs/outputs, steps)
   - Why you built it (what pain it resolves or accelerates)
   - Before/after: manual workflow vs. automated
   - Autonomy levels used for each completed task (what level, why, and how you supervised)
   - Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures
