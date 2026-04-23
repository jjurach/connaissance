# Hentown Obsidian Vault

This is the canonical Obsidian vault for Cackle and hentown agentic planning, documentation, and knowledge management.

## Vault Structure (PARA Layout)

The vault is organized using the **PARA method** with numeric prefixes for stability and semantic folder names (hyphen-separated):

### 00-Inbox
Entry point for new, unsorted content:
- Transient notes from voice STT (faster-whisper, Cackle voice recorder)
- Quick captures from Pigeon (Drive pickups)
- Raw inbox items waiting for classification and processing
- Status: `triage` → to-process → moved to appropriate project

### 10-Projects
The working hub for all modules and major initiatives:
- One subfolder per hentown submodule (e.g., `chatterbox/`, `mellona/`, `second_voice/`)
- Each project folder contains:
  - **`<module>.md`** — project hub note (type: `project`) with overview and links
  - **`specs/`** — requirements, prompts, and specifications
  - **`plans/`** — execution plans and roadmaps
  - **`logs/`** — organized results and outputs
    - `logs/prompts/` — prompt/request records
    - `logs/summaries/` — completion summaries and outcomes
    - `logs/inbox/` — per-project captured items
  - **`analysis/`** — investigation notes, research, free-form exploration

### 20-Memory
Cross-project learned facts and reference knowledge:
- **`by-project/`** — facts and insights organized by source project
- **`by-topic/`** — facts and insights organized by subject (architecture, patterns, decisions)
- Canonical facts go here; referenced by project notes via wikilinks

### 30-Resources
Reference materials and external documentation:
- Third-party documentation, research papers, external links
- Guides and reference material for tools used across projects
- Not owned by any single project; shared utility

### 40-Archive
Retired and historical content:
- Completed projects moved here for reference
- Superseded plans and specs
- Historical context preserved for future reference

### 90-System
Vault tooling, automation, and configuration:
- **`fileClasses/`** — Metadata Menu schema definitions
  - `schema.json` — authoritative JSON Schema (Phase 2)
  - `*.md` — human-readable fileClass notes (generated from schema, Phase 2)
- **`templates/`** — Templater template notes for each content type
- **`dashboards/`** — Dataview index and query notes
- **`ci/`** — pre-commit hook and GitHub Action stubs for validation

### .obsidian
Obsidian application configuration:
- `community-plugins.json` — list of community plugins used
- Workspace and app settings (managed by Obsidian UI)

## Schema (Phase 2)

The authoritative schema is defined in **`90-System/fileClasses/schema.json`** and enforced by the validator.

### File Class Types

Every note must have a `type` field. The eight file classes are:

| Type | Purpose | Location | Required Fields |
|------|---------|----------|-----------------|
| `project` | Project hub and overview | `10-Projects/<project>/` | `type`, `project`, `created` |
| `spec` | Requirements and acceptance criteria | `10-Projects/<project>/specs/` | `type`, `project`, `created` |
| `plan` | Execution roadmap and phases | `10-Projects/<project>/plans/` | `type`, `project`, `created` |
| `prompt` | Request/question sent to agent | `10-Projects/<project>/logs/prompts/` | `type`, `project`, `created` |
| `summary` | Result or outcome of execution | `10-Projects/<project>/logs/summaries/` | `type`, `project`, `created` |
| `memory` | Learned facts for cross-project reference | `20-Memory/` | `type`, `created` |
| `inbox` | Transient capture awaiting classification | `00-Inbox/` | `type`, `created` |
| `note` | Miscellaneous content | `10-Projects/<project>/` | `type`, `created` |

### Frontmatter Fields

**Always required:**
- `type` — One of the 8 types above (enum)
- `created` — Date in `YYYY-MM-DD` or `YYYY-MM-DD_HH-MM-SS` format

**Required by location:**
- `project` — Wikilink like `[[chatterbox]]` (required for files under `10-Projects/`)

**Optional fields:**
- `status` — One of: `approved`, `awaiting-approval`, `design-phase`, `design-specification`, `full-plan`, `test-plan`, `completed`
- `agent` — Name of agent or human responsible
- `source` — Origin (e.g., `gdrive`, `voice`, `inbox`)
- `spec` — Wikilink to related specification
- `plan` — Wikilink to related plan
- `target_completion` — Date in `YYYY-MM-DD` format
- `estimated_duration` — Free-form time estimate (e.g., `"2 weeks (~40 hours)"`)
- `doc_id` — Internal tracking ID (e.g., `EPIC-1`)
- `updated` — Last update date in `YYYY-MM-DD` format
- `outcome` — Outcome or result (e.g., `success`, `analysis`)
- `topic` — Category for memory/analysis notes
- `source_session` — Reference to originating session
- `links` — Array of related wikilinks
- `supersedes` — Wikilink to spec this replaces
- `result` — Result of executing a prompt
- `modules` — Array of related module names
- `owner` — Project owner
- `priority` — One of: `high`, `medium`, `low`
- `commit` — Git commit hash

### Example Frontmatter

**Project hub note:**
```yaml
---
type: project
project: [[chatterbox]]
created: 2026-03-15
owner: Agent Name
priority: high
status: in-progress
links:
  - "[[chatterbox-epic-1]]"
  - "[[memory/wyoming-protocol]]"
---
```

**Plan note:**
```yaml
---
type: plan
project: [[chatterbox]]
spec: [[chatterbox-wyoming-spec]]
created: 2026-04-01
status: approved
target_completion: 2026-06-15
estimated_duration: "6 weeks (~240 hours)"
doc_id: EPIC-4-WYOMING
agent: Claude
---
```

**Inbox note:**
```yaml
---
type: inbox
created: 2026-04-13T14:30:00
source: voice
status: triage
project: [[chatterbox]]
---
```

### Validation

Run the validator to check the entire vault:

```bash
python -m modules.hentown_obsidian.scripts.refractor validate \
  --vault-root modules/hentown-obsidian/vault \
  --report validate-report/
```

The validator checks:
- Frontmatter is valid YAML
- Required fields are present
- Enum values match schema
- Wikilinks are properly formatted (`[[...]]`)
- Referenced hub notes exist

### File Class Notes

Human-readable schema documentation is in `90-System/fileClasses/`:
- `project.md` — Project hub notes
- `spec.md` — Specification notes
- `plan.md` — Plan notes
- `prompt.md` — Prompt/request notes
- `summary.md` — Summary/outcome notes
- `memory.md` — Memory/learned facts
- `inbox.md` — Inbox/transient items
- `note.md` — General notes

These are readable by the Metadata Menu plugin and serve as templates for creating new notes.

## Plugins

The following community plugins are enabled to support the vault's structure and automation:

- **dataview** — Dynamic queries and dashboards from frontmatter metadata
- **metadata-menu** — Schema-aware metadata UI; reads from fileClasses
- **templater-obsidian** — Dynamic template generation with JavaScript execution
- **obsidian-linter** — Enforces consistent formatting and YAML structure on save
- **obsidian-git** — Version control integration; auto-commits and pushes
- **quickadd** — Rapid capture and note creation with templates
- **obsidian-tasks-plugin** — Task tracking with status and due dates in frontmatter

**Installation:** These plugins are not auto-installed. After opening this vault in Obsidian:
1. Community Plugins → Browse
2. Search for each plugin name and install
3. Enable them in the Community Plugins settings tab

The plugin list is committed here (`community-plugins.json`) so Syncthing propagates the manifest across devices; each device must run the actual plugin installation.

## Sync Architecture

- **Live editing path:** Desktop `hentown/vault/` (Syncthing mirror of Docker container)
- **Canonical source:** `modules/hentown-obsidian/vault/` (committed to hentown submodule)
- Changes flow: local write → Syncthing → container → git commit/push → submodule pull
- `hentown/vault/` is added to `.gitignore` to prevent accidental commits to the main repo

## Getting Started

1. Open this vault (`modules/hentown-obsidian/vault/`) in Obsidian
2. Install the listed plugins (see [Plugins](#plugins) above)
3. Start capturing notes in `00-Inbox/`
4. The structure will guide classification into appropriate project folders

## Resources

- Project plan: `planning/2026-04-13_22-26-55_obsidian-vault-setup-and-migration-plan.md`
- System workflow doc: `modules/hentown-obsidian/docs/doc-system-workflow.md`
- Architectural notes: `planning/2026-04-13_obsidian-gemini-convo.md`
