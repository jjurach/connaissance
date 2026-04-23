---
fileClass: spec
type: spec
created: 2026-04-13
---

# Spec File Class

A `spec` note defines requirements, goals, or acceptance criteria for a feature or task. Specs are the foundation for planning and serve as the reference point for validation.

## Required Fields

All spec notes must have:

- **`type`**: Always `"spec"`
- **`project`**: Wikilink to the owning project, e.g., `[[mellona]]`
- **`created`**: Date the spec was created in `YYYY-MM-DD` or `YYYY-MM-DD_HH-MM-SS` format

## Optional Fields

Spec notes may have:

- **`status`**: One of `approved`, `awaiting-approval`, `design-phase`, `design-specification`, `full-plan`, `test-plan`, `completed`
- **`source`**: How this spec was sourced (e.g., `conversation`, `planning-session`, `research`)
- **`agent`**: Agent or human who created or owns this spec
- **`original_path`**: Path to the original file if migrated
- **`supersedes`**: Wikilink to a prior spec this one replaces
- **`updated`**: Last update date in `YYYY-MM-DD` format

## Field Descriptions

### status
Tracks the lifecycle of the spec. `approved` means it's ready for planning; `awaiting-approval` means it's under review.

### source
Documents where the spec came from, helping with traceability and future research.

### agent
The person or agent who created or is responsible for this spec. Useful for follow-up questions.

### supersedes
If this spec replaces an earlier one, link to it for historical reference.

### updated
When the spec was last revised. Helps identify stale specs that may need review.

## Template Example

```yaml
---
type: spec
project: [[mellona]]
created: 2026-04-01
status: approved
source: planning-session
agent: Claude
updated: 2026-04-10
---

# Mellona: Async Provider Integration

## Goals

- Integrate async/await support for Ollama provider
- Support concurrent requests
- Maintain backward compatibility with sync interface

## Acceptance Criteria

- [ ] All sync-only providers now support async context manager
- [ ] Concurrent requests work without race conditions
- [ ] Existing sync code continues to work unchanged

## Key Assumptions

- Ollama API remains stable
- aiohttp library available and compatible

## Out of Scope

- Migrate all consumers to async (follow-up)
- GPU memory management beyond Ollama API
```

## See Also

- [[project]] — Project hub notes
- [[plan]] — Plans derived from specs
- [[memory/spec-patterns]] — Common specification patterns
