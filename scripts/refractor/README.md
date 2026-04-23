# Refractor: Obsidian Vault Migration Tool

A Python package that walks hentown module planning directories, catalogs metadata patterns, classifies files, and migrates them to an Obsidian vault with YAML frontmatter.

## Purpose

Refractor implements the Phase 1 survey → scan → migrate workflow from the [Obsidian Vault Setup & Cross-Module Planning Migration](../../planning/2026-04-13_22-26-55_obsidian-vault-setup-and-migration-plan.md) plan.

## Installation

The package requires:
- Python 3.11+
- `PyYAML` (for frontmatter handling)
- `jsonschema` (for Phase 2 validation)
- `pytest` (for tests, optional)

```bash
cd modules/hentown-obsidian
pip install -e .
```

Or install dependencies directly:
```bash
pip install PyYAML jsonschema pytest
```

## Usage

### Survey (Phase 1.0)

Scan all planning files and catalog metadata patterns:

```bash
python -m refractor survey [--hentown-root PATH] [--report DIR]
```

Output:
- `survey-report.json` — machine-readable data
- `survey-report.md` — human-readable analysis

The survey is **read-only** and gates the schema freeze decision.

### Scan (Phase 1.2)

Classify files and preview what migration would produce:

```bash
python -m refractor scan [--hentown-root PATH] [--vault-root PATH] [--report DIR]
```

Output:
- `scan-report.json` — file-by-file classification, frontmatter, target paths

### Migrate (Phase 1.3)

Copy files to the vault with injected YAML frontmatter:

```bash
python -m refractor migrate [--hentown-root PATH] [--vault-root PATH] [--overwrite] [--report DIR]
```

Options:
- `--overwrite` — Replace existing vault files (default: skip on collision)
- `--report` — Output directory for reports (default: `refractor-out/`)

Output:
- `migration-report.json` — list of migrated files, skipped collisions, errors

### Validate (Phase 2 stub)

Validate vault files have correct YAML frontmatter:

```bash
python -m refractor validate [--vault-root PATH] [--report DIR]
```

Output:
- `validate-report.json` — errors and warnings

In Phase 2, validation will be extended to use JSON Schema.

## Configuration

Module whitelist is defined in `config.py`:

```python
MODULES = [
    "cackle", "cackle-satellite", "chatterbox", ..., "_root"
]
```

Recognized subdirectories in planning/ folders:
- `inbox/` / `inbox-archive/` → `inbox` type
- `specs/` → `spec` type
- `analysis/` → `summary` type
- `requests/` → (unspecified, treated as note)

Filename suffixes drive classification:
- `-prompt.md` → `prompt`
- `-plan.md` → `plan`
- `-summary.md` → `summary`
- `-spec*.md` → `spec`

## Library Modules

### `lib/slug.py`

Filename and slug manipulation:
- `extract_timestamp()` — parse YYYY-MM-DD or YYYY-MM-DD_HH-MM-SS prefix
- `generate_slug()` — lowercase hyphenated slug from filename
- `vault_filename()` — construct output filename with timestamp

### `lib/classifier.py`

File type classification:
- `classify_file()` — infer type from filename and path
- `extract_project()` — find module name from path

### `lib/extractor.py`

Metadata extraction:
- `parse_frontmatter()` — parse YAML block at top of file
- `extract_body_metadata()` — find **Key:** Value patterns in body headers
- `extract_created_date()` — extract or infer creation date
- `extract_mtime()` — file modification time as ISO date

### `lib/validators.py`

Validation helpers:
- `is_markdown()` — check file extension
- `is_valid_timestamp()` — validate date format
- `is_valid_slug()` — validate slug format
- `is_valid_wikilink()` — validate Obsidian [[link]] format
- `is_valid_yaml_value()` — check YAML serializability

## Commands

### `commands/survey.py`

The `Survey` class walks all modules and generates a report on:
- Filename pattern distribution
- Existing frontmatter frequency
- Body metadata key discovery
- Anomalies (zero-byte files, collisions, unexpected subdirs)

### `commands/scan.py`

The `Scan` class classifies each file and previews:
- Type (plan, prompt, spec, summary, inbox, note)
- Extracted metadata (timestamps, body headers)
- Target vault paths
- Frontmatter that would be injected

### `commands/migrate.py`

The `Migrate` class:
- Copies files to vault with YAML frontmatter
- Creates project hub notes
- Detects and optionally overwrites collisions
- Optionally deletes originals after validation

### `commands/validate.py`

The `Validate` class (Phase 2 stub):
- Checks for YAML frontmatter
- Verifies required fields present
- Warns on malformed wikilinks
- Will validate against JSON Schema in Phase 2

## Testing

Run the test suite:

```bash
pytest tests/
```

Or with coverage:
```bash
pytest tests/ --cov=scripts/refractor
```

Test fixtures create a temporary hentown directory with sample planning files in multiple modules, plus a vault structure.

Key test classes:
- `test_slug.py` — slug generation and filename parsing
- `test_classifier.py` — file type and project extraction
- `test_extractor.py` — frontmatter and body metadata parsing
- `test_validators.py` — validation helper functions
- `test_survey.py` — survey command integration
- `test_scan.py` — scan command and path computation
- `test_migrate.py` — file migration and frontmatter injection
- `test_validate.py` — basic validation

## Frontmatter Schema

Every note migrated to the vault carries YAML frontmatter with:

**Always required** (script-supplied):
- `type` — file type (plan, prompt, spec, summary, inbox, note)
- `project` — wikilink to project hub, e.g. `[[chatterbox]]`
- `created` — ISO date YYYY-MM-DD
- `original_path` — breadcrumb path to original file

**Extracted from body** (if present):
- `status` — from `**Status:** ...` or `Status: ...`
- `target_completion` — from `**Target Completion:** ...`
- `estimated_duration` — from `**Estimated Duration:** ...`
- And any other keys recognized by the body metadata extractor

The exact field mapping is determined by the Phase 1.1 schema freeze (human review of survey output).

## Vault Layout

Files are organized in the PARA structure:

```
vault/
├── 00-Inbox/           # Unsorted, triage queue
├── 10-Projects/        # Per-module planning
│   ├── chatterbox/
│   │   ├── chatterbox.md       # hub note
│   │   ├── plans/
│   │   ├── specs/
│   │   ├── logs/
│   │   │   ├── prompts/
│   │   │   └── summaries/
│   │   └── analysis/
│   └── ...other modules...
├── 20-Memory/
├── 30-Resources/
├── 40-Archive/
└── 90-System/
    └── fileClasses/    # Phase 2: schema definitions
```

## Design Notes

- **Evidence-based schema:** Field mapping is derived from actual observed patterns in the survey, not speculation.
- **Body preservation:** The body content of files is never modified; only frontmatter is injected.
- **Idempotency:** `migrate --overwrite` re-converges frontmatter after schema updates without modifying body.
- **No migration plumbing:** No `status: migrated`, `migrated_at`, or `legacy:` fields — migration is a git event.
- **Deterministic slugs:** Same input filename always produces the same slug and vault path, enabling safe re-runs.

## Future Work

- **Phase 2:** JSON Schema validation, fileClass templates, Dataview dashboards
- **Phase 3:** Agent wiring (Pigeon, Hatchery, STT integration)
- **Phase 3.4:** Body cleanup tooling to remove promoted headers after schema is stable
