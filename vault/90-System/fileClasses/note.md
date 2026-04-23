---
fileClass: note
type: note
created: 2026-04-13
---

# Note File Class

A `note` is a fallback type for miscellaneous content that doesn't fit the other categories. Notes might be research snippets, analysis explorations, or documentation that doesn't belong in a formal spec or plan.

## Required Fields

All note files must have:

- **`type`**: Always `"note"`
- **`created`**: Date the note was created in `YYYY-MM-DD` or `YYYY-MM-DD_HH-MM-SS` format

## Optional Fields

Notes may have:

- **`project`**: Wikilink to the project it relates to
- **`topic`**: Subject or category
- **`links`**: Related note wikilinks

## Field Descriptions

### project
If this note is part of a project, link to the project hub.

### topic
What this note is about (free-form category).

### links
Related notes for context and navigation.

## Template Example

General notes for miscellaneous content.

## See Also

- [[project]] — Project hub notes
- [[memory]] — For cross-project learned facts
