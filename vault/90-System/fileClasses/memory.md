---
fileClass: memory
type: memory
created: 2026-04-13
---

# Memory File Class

A `memory` note captures learned facts, patterns, and insights that span projects or are useful for future reference. Memory notes are organized by topic and referenced by project notes via wikilinks.

## Required Fields

All memory notes must have:

- **`type`**: Always `"memory"`
- **`created`**: Date the memory was created in `YYYY-MM-DD` or `YYYY-MM-DD_HH-MM-SS` format

## Optional Fields

Memory notes may have:

- **`topic`**: Category or subject (e.g., `architecture`, `patterns`, `lessons`)
- **`source_session`**: Reference to the session or plan that produced this memory
- **`links`**: Array of related note wikilinks

## Field Descriptions

### topic
What category this memory belongs to. Helps organize memory notes by subject.

### source_session
Which work session or plan produced this memory. Useful for traceability.

### links
Related notes that reference or depend on this memory.

## Template Example

Memory notes document learned facts for future reference.

## See Also

- [[project]] — Project hub notes
- [[20-Memory]] — Memory folder organization
