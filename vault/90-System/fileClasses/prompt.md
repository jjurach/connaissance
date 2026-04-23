---
fileClass: prompt
type: prompt
created: 2026-04-13
---

# Prompt File Class

A `prompt` note captures a request, question, or instruction sent to an AI agent. It may include context, background, and expected output format.

## Required Fields

All prompt notes must have:

- **`type`**: Always `"prompt"`
- **`project`**: Wikilink to the owning project, e.g., `[[mellona]]`
- **`created`**: Date the prompt was created in `YYYY-MM-DD` or `YYYY-MM-DD_HH-MM-SS` format

## Optional Fields

Prompt notes may have:

- **`status`**: One of `approved`, `awaiting-approval`, `design-phase`, `design-specification`, `full-plan`, `test-plan`, `completed`
- **`agent`**: Which agent received or is assigned to this prompt
- **`result`**: Outcome or result (free-form, can reference a summary note)
- **`original_path`**: Path to the original file if migrated

## Field Descriptions

### status
Tracks the prompt lifecycle: `pending` = waiting for execution, `completed` = executed and result captured.

### agent
Which agent (Claude, Gemini, Cline, etc.) this prompt is intended for.

### result
Summary or wikilink to the result. If a long output was captured, may link to a `summary` note.

## Template Example

```yaml
---
type: prompt
project: [[chatterbox]]
created: 2026-04-13T14:30:00
agent: Claude
status: completed
result: "[[2026-04-13_chatterbox-wyoming-integration-summary]]"
---

# Chatterbox Wyoming Integration Issues

## Context

We're integrating Wyoming protocol support into the Chatterbox server. The STT/TTS pipeline works in isolation but fails under concurrent load.

## Background

- **Spec:** [[chatterbox-wyoming-protocol-spec]]
- **Plan:** [[epic-4-wyoming-protocol-plan]]
- **Current Issue:** Home Assistant reports timeouts when multiple concurrent clients connect

## The Ask

Review the concurrent stream handling in the Wyoming event loop. Specifically:

1. Is there a mutex protecting the Whisper/Piper model resources?
2. Can those libraries handle concurrent requests, or do we need serialization?
3. Suggest a fix if needed.

## Constraints

- Must not break existing single-stream tests
- Solution should be documented in concurrency guide
- No performance degradation expected

## Expected Output

- Analysis of the concurrency issue
- Recommended fix (code + rationale)
- Test plan for verification
```

## See Also

- [[project]] — Project hub notes
- [[summary]] — Result summaries
- [[plan]] — Related execution plans
