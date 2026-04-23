---
fileClass: summary
type: summary
created: 2026-04-13
---

# Summary File Class

A `summary` note captures the result or outcome of executing a plan, prompt, or investigation. Summaries are the record of what was done, what was learned, and what comes next.

## Required Fields

All summary notes must have:

- **`type`**: Always `"summary"`
- **`project`**: Wikilink to the owning project, e.g., `[[second_voice]]`
- **`created`**: Date the summary was created in `YYYY-MM-DD` or `YYYY-MM-DD_HH-MM-SS` format

## Optional Fields

Summary notes may have:

- **`status`**: One of `approved`, `awaiting-approval`, `design-phase`, `design-specification`, `full-plan`, `test-plan`, `completed`
- **`plan`**: Wikilink to the plan that was executed
- **`commit`**: Git commit hash or reference if code changes were made
- **`agent`**: Agent or human who produced this summary
- **`outcome`**: Key outcome or result
- **`original_path`**: Path to the original file if migrated

## Field Descriptions

### status
Completion status: `completed` = finished, `needs-review` = awaiting approval.

### plan
Cross-reference to the plan being executed.

### commit
Git commit hash(es) if this summary includes code changes.

### agent
Who executed the work and produced the summary.

### outcome
High-level result: success, partial-success, blocked, analysis-only, etc.

## See Also

- [[project]] — Project hub notes
- [[plan]] — Execution plans
- [[prompt]] — Related prompts/requests
