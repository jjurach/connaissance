---
fileClass: project
type: project
created: 2026-04-13
---

# Project File Class

A `project` note represents a major initiative, module, or work area. Each project has a hub note in `10-Projects/<project-name>/` that serves as the entry point and index for all related specs, plans, and summaries.

## Required Fields

All project notes must have:

- **`type`**: Always `"project"`
- **`project`**: Wikilink to the project name (typically `[[self]]` for hub notes), e.g., `[[chatterbox]]`
- **`created`**: Date the project was established in `YYYY-MM-DD` or `YYYY-MM-DD_HH-MM-SS` format

## Optional Fields

Project notes may have:

- **`owner`**: Human or agent responsible for the project
- **`modules`**: Array of related module names
- **`priority`**: One of `high`, `medium`, `low`
- **`links`**: Array of wikilinks to related resources or memory notes
- **`status`**: Current project status (one of: `approved`, `awaiting-approval`, `design-phase`, `design-specification`, `full-plan`, `test-plan`, `completed`)

## Field Descriptions

### owner
The person or agent who owns or leads this project. Helps with responsibility tracking and cross-project coordination.

### modules
List of module names that this project spans or depends on (e.g., `["mellona", "second_voice"]`).

### priority
Relative priority level. Used for filtering and prioritization in dashboards.

### links
Array of related note wikilinks for navigation and context. Automatically indexed by Dataview.

### status
The current lifecycle state of the project. Used by Dataview queries to filter for active, pending, or completed work.

## Template Example

```yaml
---
type: project
project: [[chatterbox]]
created: 2026-03-15
owner: Agent Name
priority: high
status: in-progress
modules:
  - chatterbox
  - mellona
links:
  - "[[chatterbox-epic-1]]"
  - "[[memory/chatterbox-patterns]]"
---

# Chatterbox

Project hub and overview for the Chatterbox voice interaction system.

## Overview

[Project summary]

## Active Work

[Dataview query showing active plans and prompts]

## Resources

[Related specs, memories, external links]
```

## See Also

- [[spec]] — Specification file class
- [[plan]] — Plan file class
- [[summary]] — Summary file class
