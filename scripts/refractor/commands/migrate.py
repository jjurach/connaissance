"""Phase 1.3: Migrate command — copy files to vault with frontmatter."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from ..config import MODULES
from ..lib.classifier import classify_file, extract_project
from ..lib.extractor import extract_body_metadata, extract_created_date, parse_frontmatter
from ..lib.slug import extract_timestamp, generate_slug, vault_filename
from ..lib.validators import is_markdown


class Migrate:
    """Copy planning files to the vault with injected frontmatter."""

    def __init__(self, hentown_root: Path, vault_root: Path, overwrite: bool = False):
        """
        Initialize the migrate operation.

        Args:
            hentown_root: Absolute path to hentown root.
            vault_root: Absolute path to vault root.
            overwrite: If True, overwrite existing vault files.
        """
        self.hentown_root = hentown_root
        self.vault_root = vault_root
        self.overwrite = overwrite
        self.files_migrated = []
        self.files_skipped = []
        self.errors = []

    def run(self) -> dict[str, Any]:
        """
        Run the migration across all whitelisted modules.

        Returns:
            A dict containing:
            - timestamp: when the migration ran
            - files_migrated: list of migrated files
            - files_skipped: list of skipped files (collisions)
            - errors: list of errors encountered
        """
        self._migrate_planning_directories()

        return {
            "timestamp": datetime.now().isoformat(),
            "files_migrated": len(self.files_migrated),
            "files_skipped": len(self.files_skipped),
            "errors": len(self.errors),
            "files_migrated_detail": self.files_migrated,
            "files_skipped_detail": self.files_skipped,
            "errors_detail": self.errors,
        }

    def _migrate_planning_directories(self) -> None:
        """Walk all whitelisted modules and migrate files."""
        for module in MODULES:
            if module == "_root":
                planning_dir = self.hentown_root / "planning"
            else:
                planning_dir = self.hentown_root / "modules" / module / "planning"

            if not planning_dir.exists():
                continue

            for file_path in planning_dir.rglob("*"):
                if file_path.is_dir() or not is_markdown(file_path):
                    continue

                self._migrate_file(file_path)

    def _migrate_file(self, file_path: Path) -> None:
        """
        Migrate a single file to the vault.

        Args:
            file_path: Absolute path to the source file.
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            self.errors.append({
                "file": str(file_path.relative_to(self.hentown_root)),
                "error": f"Could not read file: {e}",
            })
            return

        # Parse existing frontmatter and body.
        fm_existing, body = parse_frontmatter(content)

        # Classify and extract metadata.
        file_type = classify_file(file_path)
        project = extract_project(file_path, self.hentown_root)
        project_link = "[[hentown]]" if project == "_root" else f"[[{project}]]"
        created = extract_created_date(file_path.name, file_path)
        body_meta = extract_body_metadata(body)

        # Generate vault filename.
        filename = file_path.name
        timestamp, _ = extract_timestamp(filename)
        slug = generate_slug(filename)
        vault_fname = vault_filename(timestamp, slug)

        # Compute target directory.
        from ..config import VAULT_PATHS

        if file_type == "note":
            target_subdir = "."
        else:
            target_subdir = VAULT_PATHS.get(file_type, ".")

        if target_subdir == ".":
            target_dir = self.vault_root / "10-Projects" / project
            target_path = target_dir / vault_fname
        else:
            target_dir = self.vault_root / "10-Projects" / project / target_subdir
            target_path = target_dir / vault_fname

        # Check for collision.
        if target_path.exists() and not self.overwrite:
            self.files_skipped.append({
                "source": str(file_path.relative_to(self.hentown_root)),
                "target": str(target_path.relative_to(self.vault_root)),
                "reason": "File exists (use --overwrite to overwrite)",
            })
            return

        # Construct final frontmatter.
        final_fm = {
            "type": file_type,
            "project": project_link,
            "created": created,
            "original_path": f"modules/{project}/planning/{filename}" if project != "_root" else f"planning/{filename}",
        }

        # Add extracted body metadata.
        for key, value in body_meta.items():
            if key not in final_fm:
                final_fm[key] = value

        # Merge with existing frontmatter (preserve existing unless overwriting).
        if not self.overwrite:
            for key, value in fm_existing.items():
                if key not in final_fm:
                    final_fm[key] = value
        else:
            # When overwriting, keep other keys from existing frontmatter.
            for key, value in fm_existing.items():
                if key not in final_fm and key not in ("type", "project", "created", "original_path"):
                    final_fm[key] = value

        # Create target directory if needed.
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.errors.append({
                "file": str(file_path.relative_to(self.hentown_root)),
                "error": f"Could not create target directory {target_dir}: {e}",
            })
            return

        # Create hub note for project if it doesn't exist.
        self._create_project_hub(project)

        # Write the vault file with frontmatter.
        try:
            # Serialize frontmatter to YAML.
            fm_yaml = yaml.dump(final_fm, default_flow_style=False, sort_keys=False)
            output_content = f"---\n{fm_yaml}---\n{body}"

            target_path.write_text(output_content, encoding="utf-8")

            self.files_migrated.append({
                "source": str(file_path.relative_to(self.hentown_root)),
                "target": str(target_path.relative_to(self.vault_root)),
                "type": file_type,
                "project": project,
            })
        except Exception as e:
            self.errors.append({
                "file": str(file_path.relative_to(self.hentown_root)),
                "error": f"Could not write vault file: {e}",
            })

    def _create_project_hub(self, project: str) -> None:
        """
        Create a project hub note if it doesn't exist.

        Args:
            project: Project name (e.g., "chatterbox").
        """
        if project == "_root":
            hub_project = "hentown"
        else:
            hub_project = project

        hub_path = self.vault_root / "10-Projects" / hub_project / f"{hub_project}.md"

        if hub_path.exists():
            return

        # Create the hub note.
        hub_path.parent.mkdir(parents=True, exist_ok=True)

        hub_fm = {
            "type": "project",
            "project": f"[[{hub_project}]]",
        }

        fm_yaml = yaml.dump(hub_fm, default_flow_style=False, sort_keys=False)
        hub_content = f"---\n{fm_yaml}---\n# {hub_project.title()}\n\n" \
                      f"Project hub for {hub_project}.\n\n" \
                      f"## Files in this project\n"

        try:
            hub_path.write_text(hub_content, encoding="utf-8")
        except Exception:
            # Ignore errors creating hub notes (non-critical).
            pass

    def report_json(self) -> str:
        """
        Generate a JSON migration report.

        Returns:
            JSON-formatted migration report.
        """
        data = self.run()
        return json.dumps(data, indent=2)

    def delete_originals(self) -> dict[str, Any]:
        """
        Delete source files after successful migration.

        This should only be called after validation passes.
        Returns a dict with deletion results.
        """
        deleted = []
        failed = []

        for migrated in self.files_migrated:
            source_path = self.hentown_root / migrated["source"]
            try:
                source_path.unlink()
                deleted.append(str(migrated["source"]))
            except Exception as e:
                failed.append({
                    "file": str(migrated["source"]),
                    "error": str(e),
                })

        return {
            "deleted": deleted,
            "failed": failed,
        }
