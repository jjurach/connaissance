"""Validate vault files against the schema (Phase 2)."""

import json
from pathlib import Path
from typing import Any

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False


class Validate:
    """Validate vault files against schema.json."""

    def __init__(self, vault_root: Path, schema_path: Path | None = None):
        """
        Initialize the validator.

        Args:
            vault_root: Absolute path to vault root.
            schema_path: Optional path to schema.json. If not provided,
                defaults to vault_root/90-System/fileClasses/schema.json.
        """
        self.vault_root = vault_root

        if schema_path is None:
            schema_path = vault_root / "90-System" / "fileClasses" / "schema.json"

        self.schema_path = schema_path
        self.schema = None
        self.errors = []
        self.warnings = []
        self.checked_files = 0

        # Load schema if available.
        if self.schema_path.exists():
            try:
                with open(self.schema_path, "r") as f:
                    self.schema = json.load(f)
            except Exception as e:
                self.errors.append({
                    "file": str(self.schema_path),
                    "error": f"Could not load schema: {e}",
                })

    def run(self) -> dict[str, Any]:
        """
        Run validation on vault files.

        Validates against schema.json using jsonschema if available.
        Performs schema validation and semantic checks:
        - Frontmatter is valid YAML
        - Required fields present per type
        - Enum values match schema constraints
        - Wikilinks are properly formatted
        - Referenced hub notes exist

        Returns:
            A dict containing:
            - valid: True if all checks pass
            - errors: list of validation errors
            - warnings: list of warnings
            - checked_files: count of files checked
        """
        self._validate_vault_files()

        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "checked_files": self.checked_files,
        }

    def _validate_vault_files(self) -> None:
        """Validate files under vault/10-Projects/ and vault/00-Inbox/."""
        for root_dir in ("10-Projects", "00-Inbox"):
            vault_dir = self.vault_root / root_dir
            if not vault_dir.exists():
                continue

            for file_path in vault_dir.rglob("*.md"):
                self._validate_file(file_path)

    def _validate_file(self, file_path: Path) -> None:
        """
        Validate a single vault file.

        Args:
            file_path: Absolute path to the file.
        """
        self.checked_files += 1

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            self.errors.append({
                "file": str(file_path.relative_to(self.vault_root)),
                "error": f"Could not read file: {e}",
            })
            return

        # Check for frontmatter.
        if not content.startswith("---"):
            self.errors.append({
                "file": str(file_path.relative_to(self.vault_root)),
                "field": "frontmatter",
                "error": "Missing YAML frontmatter (must start with ---)",
            })
            return

        # Extract frontmatter.
        lines = content.split("\n")
        closing_idx = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                closing_idx = i
                break

        if closing_idx is None:
            self.errors.append({
                "file": str(file_path.relative_to(self.vault_root)),
                "field": "frontmatter",
                "error": "Incomplete YAML frontmatter (missing closing ---)",
            })
            return

        # Parse YAML.
        try:
            import yaml
            fm_text = "\n".join(lines[1:closing_idx])
            fm = yaml.safe_load(fm_text) or {}
        except Exception as e:
            self.errors.append({
                "file": str(file_path.relative_to(self.vault_root)),
                "field": "frontmatter",
                "error": f"Invalid YAML: {e}",
            })
            return

        # Validate against JSON Schema if available.
        if self.schema and JSONSCHEMA_AVAILABLE:
            self._validate_against_schema(file_path, fm)
        else:
            # Fall back to basic checks.
            self._validate_basic_checks(file_path, fm)

        # Check project wikilink format (if present).
        if "project" in fm:
            project_val = fm["project"]
            if not (isinstance(project_val, str) and project_val.startswith("[[") and project_val.endswith("]]")):
                self.warnings.append({
                    "file": str(file_path.relative_to(self.vault_root)),
                    "field": "project",
                    "warning": f"Project should be a wikilink like [[project-name]], got: {project_val}",
                })
            else:
                # Check that the referenced hub note exists.
                self._check_hub_exists(file_path, project_val)

    def _validate_against_schema(self, file_path: Path, fm: dict[str, Any]) -> None:
        """
        Validate frontmatter against JSON Schema.

        Args:
            file_path: Path to the file being validated.
            fm: Frontmatter dict to validate.
        """
        try:
            jsonschema.validate(instance=fm, schema=self.schema)
        except jsonschema.ValidationError as e:
            rel_path = str(file_path.relative_to(self.vault_root))
            # Extract the field name from the error message if possible.
            field = "frontmatter"
            if e.path:
                field = ".".join(str(p) for p in e.path)

            self.errors.append({
                "file": rel_path,
                "field": field,
                "error": e.message,
            })
        except jsonschema.SchemaError as e:
            self.errors.append({
                "file": str(file_path.relative_to(self.vault_root)),
                "error": f"Schema error: {e.message}",
            })

    def _validate_basic_checks(self, file_path: Path, fm: dict[str, Any]) -> None:
        """
        Perform basic validation checks when schema validation is unavailable.

        Args:
            file_path: Path to the file being validated.
            fm: Frontmatter dict to validate.
        """
        # Check required fields.
        required_fields = ("type", "created")
        for field in required_fields:
            if field not in fm:
                self.errors.append({
                    "file": str(file_path.relative_to(self.vault_root)),
                    "field": field,
                    "error": f"Missing required field: {field}",
                })

        # Check type enum.
        if "type" in fm:
            valid_types = ["project", "spec", "plan", "prompt", "summary", "memory", "inbox", "note"]
            if fm["type"] not in valid_types:
                self.errors.append({
                    "file": str(file_path.relative_to(self.vault_root)),
                    "field": "type",
                    "error": f"Invalid type: {fm['type']}. Must be one of: {', '.join(valid_types)}",
                })

    def _check_hub_exists(self, file_path: Path, project_val: str) -> None:
        """
        Check that a referenced project hub note exists.

        Args:
            file_path: Path to the file being validated.
            project_val: Wikilink value, e.g., [[chatterbox]].
        """
        # Extract project name from wikilink.
        project_name = project_val[2:-2]  # Remove [[ and ]]

        # Check for hub note in 10-Projects/<project-name>/<project-name>.md
        hub_path = self.vault_root / "10-Projects" / project_name / f"{project_name}.md"

        if not hub_path.exists():
            self.warnings.append({
                "file": str(file_path.relative_to(self.vault_root)),
                "field": "project",
                "warning": f"Project hub note not found: {hub_path}",
            })

    def report_json(self) -> str:
        """
        Generate a JSON validation report.

        Returns:
            JSON-formatted validation report.
        """
        data = self.run()
        return json.dumps(data, indent=2)
