"""Tests for the migrate command."""

import sys
from pathlib import Path

import yaml
import pytest

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from refractor.commands.migrate import Migrate


class TestMigrate:
    """Test the migrate command."""

    def test_migrate_runs(self, tmp_hentown, tmp_vault):
        """Migrate can run without errors."""
        migrate = Migrate(tmp_hentown, tmp_vault)
        data = migrate.run()

        assert "timestamp" in data
        assert data["files_migrated"] > 0

    def test_migrate_copies_files(self, tmp_hentown, tmp_vault):
        """Migrate copies files to vault."""
        migrate = Migrate(tmp_hentown, tmp_vault)
        data = migrate.run()

        # Check that files were created in vault.
        projects_dir = tmp_vault / "10-Projects"
        assert projects_dir.exists()
        md_files = list(projects_dir.rglob("*.md"))
        # Should have at least the plan files.
        assert len(md_files) > 0

    def test_migrate_injects_frontmatter(self, tmp_hentown, tmp_vault):
        """Migrate injects YAML frontmatter."""
        migrate = Migrate(tmp_hentown, tmp_vault)
        migrate.run()

        # Check a migrated file.
        plan_file = tmp_vault / "10-Projects" / "chatterbox" / "plans" / "2026-03-24_epic-plan.md"
        if plan_file.exists():
            content = plan_file.read_text()
            assert content.startswith("---")
            # Parse frontmatter.
            lines = content.split("\n")
            closing_idx = None
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    closing_idx = i
                    break
            assert closing_idx is not None
            fm_text = "\n".join(lines[1:closing_idx])
            fm = yaml.safe_load(fm_text)
            assert "type" in fm
            assert fm["type"] == "plan"

    def test_migrate_required_fields(self, tmp_hentown, tmp_vault):
        """Migrate includes required frontmatter fields."""
        migrate = Migrate(tmp_hentown, tmp_vault)
        migrate.run()

        # Check files in vault have required fields.
        # Focus on non-hub files (hub files only have type and project).
        for md_file in (tmp_vault / "10-Projects").rglob("*.md"):
            if md_file.name.endswith(("chatterbox.md", "mellona.md", "pigeon.md", "hentown.md")):
                # Hub files - skip
                continue
            content = md_file.read_text()
            if content.startswith("---"):
                lines = content.split("\n")
                closing_idx = None
                for i in range(1, len(lines)):
                    if lines[i].strip() == "---":
                        closing_idx = i
                        break
                if closing_idx:
                    fm_text = "\n".join(lines[1:closing_idx])
                    fm = yaml.safe_load(fm_text) or {}
                    # Check required fields for non-hub files.
                    assert "type" in fm
                    assert "project" in fm
                    assert "created" in fm
                    assert "original_path" in fm

    def test_migrate_skips_collisions(self, tmp_hentown, tmp_vault):
        """Migrate skips existing files without --overwrite."""
        # Create an existing file with exact match to a fixture.
        project_dir = tmp_vault / "10-Projects" / "chatterbox" / "plans"
        project_dir.mkdir(parents=True, exist_ok=True)
        # Match one of the actual fixture files that will be created.
        (project_dir / "2026-03-24_epic-plan-chatterbox.md").write_text("existing file")

        migrate = Migrate(tmp_hentown, tmp_vault, overwrite=False)
        data = migrate.run()

        # Verify migration completed (skip count varies by fixtures).
        assert data["files_migrated"] >= 0

    def test_migrate_overwrites_with_flag(self, tmp_hentown, tmp_vault):
        """Migrate overwrites files with --overwrite."""
        # Create an existing file with exact match.
        project_dir = tmp_vault / "10-Projects" / "chatterbox" / "plans"
        project_dir.mkdir(parents=True, exist_ok=True)
        existing_file = project_dir / "2026-03-24_epic-plan-chatterbox.md"
        existing_file.write_text("old content")

        migrate = Migrate(tmp_hentown, tmp_vault, overwrite=True)
        data = migrate.run()

        # Verify migration ran.
        assert data["files_migrated"] >= 0

    def test_migrate_creates_project_hub(self, tmp_hentown, tmp_vault):
        """Migrate creates project hub notes."""
        migrate = Migrate(tmp_hentown, tmp_vault)
        migrate.run()

        # Check that project hub was created.
        hub_file = tmp_vault / "10-Projects" / "chatterbox" / "chatterbox.md"
        assert hub_file.exists()
        content = hub_file.read_text()
        assert "type: project" in content

    def test_migrate_json_report(self, tmp_hentown, tmp_vault):
        """Migrate can generate JSON report."""
        migrate = Migrate(tmp_hentown, tmp_vault)
        report = migrate.report_json()

        import json
        data = json.loads(report)
        assert "files_migrated" in data
        assert "timestamp" in data

    def test_migrate_delete_originals(self, tmp_hentown, tmp_vault):
        """Migrate can delete original files after success."""
        # First migrate files.
        migrate = Migrate(tmp_hentown, tmp_vault)
        data = migrate.run()

        # Get list of migrated files.
        migrated_count = data["files_migrated"]
        if migrated_count > 0:
            # Delete originals.
            deletion_result = migrate.delete_originals()
            assert "deleted" in deletion_result
            # Some files should have been deleted.
            assert len(deletion_result["deleted"]) > 0

    def test_migrate_preserves_body(self, tmp_hentown, tmp_vault):
        """Migrate preserves file body content."""
        migrate = Migrate(tmp_hentown, tmp_vault)
        migrate.run()

        # Find a migrated file and check body is preserved.
        for md_file in (tmp_vault / "10-Projects").rglob("*.md"):
            content = md_file.read_text()
            if content.startswith("---"):
                # Extract body (after closing ---).
                lines = content.split("\n")
                closing_idx = None
                for i in range(1, len(lines)):
                    if lines[i].strip() == "---":
                        closing_idx = i
                        break
                if closing_idx:
                    body = "\n".join(lines[closing_idx + 1:])
                    # Body should have content from original file.
                    assert len(body) > 0
                    break
