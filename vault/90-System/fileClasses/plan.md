---
fileClass: plan
type: plan
created: 2026-04-13
---

# Plan File Class

A `plan` note outlines how to execute a spec or initiative. It breaks down work into phases, assigns owners, and tracks progress. Plans are the primary coordination document between agents and humans.

## Required Fields

All plan notes must have:

- **`type`**: Always `"plan"`
- **`project`**: Wikilink to the owning project, e.g., `[[pigeon]]`
- **`created`**: Date the plan was created in `YYYY-MM-DD` or `YYYY-MM-DD_HH-MM-SS` format

## Optional Fields

Plan notes may have:

- **`status`**: One of `approved`, `awaiting-approval`, `design-phase`, `design-specification`, `full-plan`, `test-plan`, `completed`
- **`spec`**: Wikilink to the spec this plan implements, e.g., `[[spec-name]]`
- **`target_completion`**: Target completion date in `YYYY-MM-DD` format
- **`estimated_duration`**: Estimated time to complete (free-form, e.g., `"2 weeks (~40 hours)"`)
- **`doc_id`**: Internal tracking ID (e.g., `EPIC-1-OTA`)
- **`updated`**: Last update date in `YYYY-MM-DD` format
- **`agent`**: Agent or human assigned to execute the plan
- **`original_path`**: Path to the original file if migrated

## Field Descriptions

### status
Tracks plan lifecycle: `approved` = ready to execute, `in-progress` = currently being worked, `completed` = done.

### spec
Cross-reference to the spec this plan satisfies. Helps validation and traceability.

### target_completion
When this work should be done. Used by Dataview for timeline views.

### estimated_duration
Time estimate in any reasonable format. Updated as work progresses.

### doc_id
Unique ID for tracking across systems (e.g., Jira, beads, GitHub). Useful for cross-tool searching.

### agent
Who is assigned to execute. Can change during execution if reassigned.

### updated
When the plan was last revised. Helps identify stale plans needing review.

## Template Example

```yaml
---
type: plan
project: [[chatterbox]]
spec: [[chatterbox-wyoming-protocol-spec]]
created: 2026-04-01
status: approved
target_completion: 2026-06-15
estimated_duration: "6 weeks (~240 hours)"
doc_id: EPIC-4-WYOMING
agent: Claude
updated: 2026-04-13
---

# Epic 4: Wyoming Protocol Validation

## Overview

Validate Wyoming protocol implementation and PCM streaming on both input (STT) and output (TTS) sides.

## Phases

### Phase 1: Simulator Setup (Week 1)
- Set up Wyoming protocol simulator tools
- Document both client and server simulator behavior
- **Owner:** Agent A
- **Duration:** 1 week

### Phase 2: Integration Testing (Weeks 2-3)
- Wire Whisper integration (STT input)
- Wire Piper integration (TTS output)
- Test concurrent streams
- **Owner:** Agent B
- **Duration:** 2 weeks

### Phase 3: Verification & Hardening (Weeks 4-6)
- Load testing with concurrent connections
- Error handling and recovery
- Documentation and examples
- **Owner:** Agent C
- **Duration:** 3 weeks

## Success Criteria

- [x] Simulators run without errors
- [ ] All integration tests pass
- [ ] Concurrent 10+ streams without race conditions
- [ ] Full test coverage >90%

## Dependencies

- Spec [[chatterbox-wyoming-protocol-spec]] (in progress)
- Whisper library installed
- Piper library installed
- Home Assistant test environment running

## Risks

- PCM streaming synchronization across concurrent streams
- Ollama model availability in multi-request scenarios

## See Also

- [[chatterbox]] — Project hub
- [[chatterbox-epic-3-connectivity-plan]] — Prior epic
```

## See Also

- [[spec]] — Specification file class
- [[project]] — Project hub notes
- [[summary]] — Completion summaries
