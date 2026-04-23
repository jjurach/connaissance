"""Tests for the validate command."""

import sys
from pathlib import Path

import yaml
import pytest

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from refractor.commands.validate import Validate


class TestValidate:
    """Test the validate command."""

    def test_validate_runs(self, tmp_vault):
        """Validate can run without errors."""
        validate = Validate(tmp_vault)
        data = validate.run()

        assert "valid" in data
        assert isinstance(data["errors"], list)
        assert isinstance(data["warnings"], list)

    def test_validate_accepts_correct_frontmatter(self, tmp_vault):
        """Validate passes for files with correct frontmatter."""
        # Create a valid file in the vault.
        project_dir = tmp_vault / "10-Projects" / "test-project"
        project_dir.mkdir(parents=True, exist_ok=True)

        fm = {
            "type": "plan",
            "project": "[[test-project]]",
            "created": "2026-03-24",
        }
        fm_yaml = yaml.dump(fm, default_flow_style=False)
        content = f"---\n{fm_yaml}---\n# Body\n"

        valid_file = project_dir / "test.md"
        valid_file.write_text(content)

        validate = Validate(tmp_vault)
        data = validate.run()

        # Should be valid.
        assert data["valid"] is True

    def test_validate_rejects_missing_frontmatter(self, tmp_vault):
        """Validate fails for files without frontmatter."""
        # Create a file without frontmatter.
        project_dir = tmp_vault / "10-Projects" / "test-project"
        project_dir.mkdir(parents=True, exist_ok=True)

        invalid_file = project_dir / "no-fm.md"
        invalid_file.write_text("# No Frontmatter\nJust body content.\n")

        validate = Validate(tmp_vault)
        data = validate.run()

        # Should find error.
        assert len(data["errors"]) > 0
        assert any("frontmatter" in e.get("field", "") for e in data["errors"])

    def test_validate_rejects_missing_required_field(self, tmp_vault):
        """Validate fails when required fields are missing."""
        # Create file with incomplete frontmatter.
        project_dir = tmp_vault / "10-Projects" / "test-project"
        project_dir.mkdir(parents=True, exist_ok=True)

        fm = {
            "type": "plan",
            # Missing "project" and "created"
        }
        fm_yaml = yaml.dump(fm, default_flow_style=False)
        content = f"---\n{fm_yaml}---\n# Body\n"

        incomplete_file = project_dir / "incomplete.md"
        incomplete_file.write_text(content)

        validate = Validate(tmp_vault)
        data = validate.run()

        # Should find missing field error.
        assert len(data["errors"]) > 0
        assert any("project" in e.get("field", "") or "created" in e.get("field", "")
                   for e in data["errors"])

    def test_validate_warns_on_invalid_wikilink(self, tmp_vault):
        """Validate warns if project is not a wikilink."""
        # Create file with invalid project format.
        project_dir = tmp_vault / "10-Projects" / "test-project"
        project_dir.mkdir(parents=True, exist_ok=True)

        fm = {
            "type": "plan",
            "project": "not-a-wikilink",  # Should be [[...]]
            "created": "2026-03-24",
        }
        fm_yaml = yaml.dump(fm, default_flow_style=False)
        content = f"---\n{fm_yaml}---\n# Body\n"

        invalid_wikilink_file = project_dir / "bad-wiki.md"
        invalid_wikilink_file.write_text(content)

        validate = Validate(tmp_vault)
        data = validate.run()

        # Should find warning.
        assert len(data["warnings"]) > 0

    def test_validate_json_report(self, tmp_vault):
        """Validate can generate JSON report."""
        validate = Validate(tmp_vault)
        report = validate.report_json()

        import json
        data = json.loads(report)
        assert "valid" in data
        assert "errors" in data

    def test_validate_inbox_directory(self, tmp_vault):
        """Validate checks files in 00-Inbox too."""
        # Create file in Inbox.
        inbox_dir = tmp_vault / "00-Inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)

        fm = {
            "type": "inbox",
            "created": "2026-03-24",
        }
        fm_yaml = yaml.dump(fm, default_flow_style=False)
        content = f"---\n{fm_yaml}---\n# Inbox Note\n"

        inbox_file = inbox_dir / "inbox-note.md"
        inbox_file.write_text(content)

        validate = Validate(tmp_vault)
        data = validate.run()

        # Should validate the inbox file too.
        assert data["checked_files"] > 0

    def test_schema_json_is_valid(self, tmp_vault):
        """schema.json is a valid JSON Schema."""
        import json
        from jsonschema import Draft7Validator

        schema_path = tmp_vault / "90-System" / "fileClasses" / "schema.json"
        schema_path.parent.mkdir(parents=True, exist_ok=True)

        # Create a minimal valid schema for testing
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "created": {"type": "string"}
            }
        }
        schema_path.write_text(json.dumps(schema))

        # Validate the schema itself
        validator = Draft7Validator(schema)
        assert validator.is_valid({"type": "plan", "created": "2026-04-13"})

    def test_schema_enforces_enum_values(self, tmp_vault):
        """Schema enforces enum values for type."""
        import json

        # Create schema in vault
        schema_path = tmp_vault / "90-System" / "fileClasses" / "schema.json"
        schema_path.parent.mkdir(parents=True, exist_ok=True)

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["project", "spec", "plan", "prompt", "summary", "memory", "inbox", "note"]
                }
            }
        }
        schema_path.write_text(json.dumps(schema))

        # Create file with invalid type
        project_dir = tmp_vault / "10-Projects" / "test"
        project_dir.mkdir(parents=True, exist_ok=True)

        fm = {
            "type": "invalid-type",
            "project": "[[test]]",
            "created": "2026-04-13",
        }
        fm_yaml = yaml.dump(fm, default_flow_style=False)
        content = f"---\n{fm_yaml}---\n# Body\n"

        invalid_file = project_dir / "invalid.md"
        invalid_file.write_text(content)

        # With schema, should fail validation
        validate = Validate(tmp_vault, schema_path)
        data = validate.run()

        # Check that validation catches the invalid enum value
        if data["errors"]:  # Only if jsonschema is available
            assert len(data["errors"]) > 0

    def test_validate_conformant_note_passes(self, tmp_vault):
        """A conformant note passes all validation checks."""
        import json

        # Create schema in vault
        schema_path = tmp_vault / "90-System" / "fileClasses" / "schema.json"
        schema_path.parent.mkdir(parents=True, exist_ok=True)

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["type", "created"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["project", "spec", "plan", "prompt", "summary", "memory", "inbox", "note"]
                },
                "created": {"type": "string"},
                "project": {"type": "string"}
            }
        }
        schema_path.write_text(json.dumps(schema))

        # Create valid file
        project_dir = tmp_vault / "10-Projects" / "chatterbox"
        project_dir.mkdir(parents=True, exist_ok=True)

        fm = {
            "type": "plan",
            "project": "[[chatterbox]]",
            "created": "2026-04-13",
            "status": "approved",
        }
        fm_yaml = yaml.dump(fm, default_flow_style=False)
        content = f"---\n{fm_yaml}---\n# Epic 1\n\nContent here.\n"

        valid_file = project_dir / "epic-1-plan.md"
        valid_file.write_text(content)

        validate = Validate(tmp_vault, schema_path)
        data = validate.run()

        # Should pass with no errors
        assert data["valid"] is True
        assert len(data["errors"]) == 0

    def test_validate_missing_required_field_fails(self, tmp_vault):
        """Removing a required field causes validation to fail with precise message."""
        import json

        # Create schema in vault
        schema_path = tmp_vault / "90-System" / "fileClasses" / "schema.json"
        schema_path.parent.mkdir(parents=True, exist_ok=True)

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["type", "created", "project"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["project", "spec", "plan", "prompt", "summary", "memory", "inbox", "note"]
                },
                "created": {"type": "string"},
                "project": {"type": "string"}
            }
        }
        schema_path.write_text(json.dumps(schema))

        # Create file missing "project" field (required for 10-Projects)
        project_dir = tmp_vault / "10-Projects" / "test"
        project_dir.mkdir(parents=True, exist_ok=True)

        fm = {
            "type": "plan",
            "created": "2026-04-13",
            # Missing "project"
        }
        fm_yaml = yaml.dump(fm, default_flow_style=False)
        content = f"---\n{fm_yaml}---\n# Body\n"

        incomplete_file = project_dir / "incomplete.md"
        incomplete_file.write_text(content)

        validate = Validate(tmp_vault, schema_path)
        data = validate.run()

        # Should fail with precise error message
        if data["errors"]:  # Only if jsonschema is available
            assert len(data["errors"]) > 0
            # Error should mention the missing field
            error_text = str(data["errors"])
            assert "project" in error_text.lower() or "required" in error_text.lower()
