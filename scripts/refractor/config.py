"""Configuration for refractor: module whitelist, paths, and constants."""

# Whitelisted modules to scan for planning files.
# Includes all Cackle/hentown submodules plus _root for hentown/planning/ itself.
MODULES = [
    "cackle",
    "cackle-satellite",
    "chatterbox",
    "chatvault",
    "google-personal-mcp",
    "hatchery",
    "hentown-obsidian",
    "home-assistant",
    "local-models",
    "logist",
    "mellona",
    "oneshot",
    "pigeon",
    "pitchjudge",
    "second_voice",
    "slack-agent-mcp",
    "truevote-code-signing",
    "whisper",
    "_root",  # hentown/planning/ itself
]

# Recognized subdirectories within planning/ folders that have semantic meaning.
PLANNING_SUBDIRS = {
    "inbox",
    "inbox-archive",
    "analysis",
    "specs",
    "requests",
}

# File classification patterns (filename suffixes and directory cues).
# Order matters: earlier patterns take precedence.
FILE_PATTERNS = {
    "-prompt.md": "prompt",
    "-plan.md": "plan",
    "-summary.md": "summary",
    "-spec": "spec",  # matches -spec.md, -spec-*.md, etc.
}

# Normalized body-header metadata patterns recognized during extraction.
# Used by the extractor to find keys in the format:
#   **Key:** Value
#   - **Key:** Value
#   Key: Value (at line start)
BODY_METADATA_PATTERNS = [
    "bold-colon",      # **Key:** Value
    "list-bold-colon", # - **Key:** Value
    "bare",            # Key: Value (at line start)
    "heading",         # # Key\nValue (rare)
]

# Initial type list (from §3.4 of the plan).
INITIAL_TYPES = [
    "project",
    "spec",
    "plan",
    "prompt",
    "summary",
    "memory",
    "inbox",
    "note",  # fallback
]

# Timestamp format patterns to try when parsing filenames.
TIMESTAMP_PATTERNS = [
    r"^(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})",  # YYYY-MM-DD_HH-MM-SS
    r"^(\d{4}-\d{2}-\d{2})",                     # YYYY-MM-DD
]

# Output directory for reports (default).
DEFAULT_REPORT_DIR = "refractor-out"

# Character limit for slug generation.
SLUG_MAX_LENGTH = 60

# Vault layout mapping: type → target directory relative to 10-Projects/<project>/
VAULT_PATHS = {
    "prompt": "logs/prompts",
    "plan": "plans",
    "spec": "specs",
    "summary": "logs/summaries",
    "inbox": "logs/inbox",
    "note": ".",  # root of project folder
}

# Maximum number of value examples to record per key in the survey.
SURVEY_MAX_VALUE_EXAMPLES = 5
