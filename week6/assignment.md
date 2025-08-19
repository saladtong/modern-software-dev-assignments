## Week 6 Assignment

### Overview
In this assignment, you will practice agent-driven development and AI-assisted code review on a more advanced codebase. You will implement a subset of the advanced tasks in `week6/docs/TASKS.md`, validate your work with tests and manual review, and compare your own review notes with AI-generated code reviews.

### What to do
1) Choose 5 tasks from `week6/docs/TASKS.md` and complete them using an AI coding tool of your choice (Cursor, Copilot, Claude, etc.). You may pick any mix of difficulty.
2) For each task:
   - Create a separate branch.
   - Implement the task with your AI tool using a 1-shot prompt. 
   - Manually review the changes line-by-line. Fix issues you notice and add explanatory commit messages where helpful.
   - Open a Pull Request (PR) for the task.
   - Use Graphite Diamond to generate an AI-assisted code review on the PR.

3) Ensure your PRs include:
   - Description of the problem and your approach.
   - Summary of testing performed (include commands and results) and any added/updated tests.
   - Notable tradeoffs, limitations, or follow-ups.

### Deliverables
- 5 PRs, one per completed task, each with:
  - Clear PR description and links to relevant commits/issues.
  - Graphite Diamond AI review comments visible on the PR.

- A short write-up (add to this `assignment.md` below or as a separate `REPORT.md`) covering:
  - The types of comments you typically made in your manual reviews (e.g., correctness, performance, security, naming, test gaps, API shape, UX, docs).
  - How your comments compared to Graphite’s AI-generated comments for each PR.
  - When the AI reviews were better/worse than yours, with concrete examples.
  - Your comfort level trusting AI reviews going forward and any heuristics for when to rely on them.

### Evaluation criteria
- Technical correctness and completeness of each task.
- Code quality: readability, naming, structure, error handling, and tests.
- Thoughtfulness and depth of manual review notes.
- Insightful comparison between your review and Graphite’s AI review.
- Clear documentation of setup, testing, and tradeoffs in PR descriptions and the write-up.

