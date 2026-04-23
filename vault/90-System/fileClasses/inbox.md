---
fileClass: inbox
type: inbox
created: 2026-04-13
---

# Inbox File Class

An `inbox` note is a transient capture of raw content: voice transcripts from STT, Drive pickups from Pigeon, or quick notes waiting for classification. Inbox notes progress from `triage` to classification and eventual movement to a project folder.

## Required Fields

All inbox notes must have:

- **`type`**: Always `"inbox"`
- **`created`**: Date the item was captured in `YYYY-MM-DD` or `YYYY-MM-DD_HH-MM-SS` format

## Optional Fields

Inbox notes may have:

- **`status`**: Processing status (e.g., `triage`, `to-process`, `ready`)
- **`source`**: Where this came from (e.g., `gdrive`, `voice`, `manual`)
- **`project`**: Wikilink if already classified to a project

## Field Descriptions

### status
Processing state: `triage` = new/unsorted, `to-process` = reviewed/scheduled, `ready` = ready to move to project folder.

### source
Origin: `gdrive` = Pigeon pickup, `voice` = STT transcript, `manual` = human capture, etc.

### project
If already classified, wikilink to destination project.

## Template Example

Inbox notes capture raw content for later processing.

## See Also

- [[project]] — Project hub notes
- [[00-Inbox]] — Inbox folder
