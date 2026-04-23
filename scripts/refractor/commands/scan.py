"""Phase 1.2: Scan command — classify and preview extraction for each file."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ..config import MODULES, VAULT_PATHS
from ..lib.classifier import classify_file, extract_project
from ..lib.extractor import extract_body_metadata, extract_created_date, parse_frontmatter
from ..lib.slug import extract_timestamp, generate_slug, vault_filename
from ..lib.validators import is_markdown


class Scan:
    """Classify files and preview migration extraction."""

    def __init__(self, hentown_root: Path, vault_root: Path):
        """
        Initialize the scan.

        Args:
            hentown_root: Absolute path to hentown root.
            vault_root: Absolute path to vault root.
        """
        self.hentown_root = hentown_root
        self.vault_root = vault_root
        self.files_scanned = []
        self.warnings = []

    def run(self) -> dict[str, Any]:
        """
        Run the scan across all whitelisted modules.

        Returns:
            A dict containing:
            - timestamp: when the scan was run
            - files_count: total files scanned
            - files: list of dicts with derived metadata
            - warnings: list of extraction/collision warnings
        """
        self._scan_planning_directories()

        return {
            "timestamp": datetime.now().isoformat(),
            "files_count": len(self.files_scanned),
            "files": self.files_scanned,
            "warnings": self.warnings,
        }

    def _scan_planning_directories(self) -> None:
        """Walk all whitelisted modules and scan files."""
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

                self._scan_file(file_path)

    def _scan_file(self, file_path: Path) -> None:
        """
        Scan a single file and derive its migration metadata.

        Args:
            file_path: Absolute path to the file.
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            self.warnings.append({
                "file": str(file_path.relative_to(self.hentown_root)),
                "warning": f"Could not read file: {e}",
            })
            return

        # Parse existing frontmatter.
        fm_existing, body = parse_frontmatter(content)

        # Classify type.
        file_type = classify_file(file_path)

        # Extract project.
        project = extract_project(file_path, self.hentown_root)
        project_link = "[[hentown]]" if project == "_root" else f"[[{project}]]"

        # Extract created date.
        created = extract_created_date(file_path.name, file_path)

        # Extract body metadata.
        body_meta = extract_body_metadata(body)

        # Generate slug and timestamp.
        filename = file_path.name
        timestamp, _ = extract_timestamp(filename)
        slug = generate_slug(filename)
        vault_fname = vault_filename(timestamp, slug)

        # Compute target path.
        if file_type == "note":
            # Fallback: root of project folder.
            target_subdir = "."
        else:
            target_subdir = VAULT_PATHS.get(file_type, ".")

        if target_subdir == ".":
            target_path = f"10-Projects/{project}/{vault_fname}"
        else:
            target_path = f"10-Projects/{project}/{target_subdir}/{vault_fname}"

        # Construct final frontmatter (always-required fields + extracted).
        final_fm = {
            "type": file_type,
            "project": project_link,
            "created": created,
            "original_path": f"modules/{project}/planning/{filename}" if project != "_root" else f"planning/{filename}",
        }

        # Add extracted body metadata only if present.
        for key, value in body_meta.items():
            if key not in final_fm:
                final_fm[key] = value

        # Merge with existing frontmatter (existing values are preserved).
        for key, value in fm_existing.items():
            if key not in final_fm:
                final_fm[key] = value

        # Check for target collision.
        target_full_path = self.vault_root / target_path
        collision = target_full_path.exists()

        self.files_scanned.append({
            "source_path": str(file_path.relative_to(self.hentown_root)),
            "source_filename": filename,
            "project": project,
            "type": file_type,
            "created": created,
            "slug": slug,
            "timestamp": timestamp,
            "target_path": target_path,
            "target_filename": vault_fname,
            "frontmatter": final_fm,
            "body_metadata_keys": list(body_meta.keys()),
            "has_existing_frontmatter": bool(fm_existing),
            "collision": collision,
        })

        if collision:
            self.warnings.append({
                "file": str(file_path.relative_to(self.hentown_root)),
                "warning": f"Target collision: {target_path} already exists",
            })

    def report_json(self) -> str:
        """
        Generate a JSON report suitable for the next phase.

        Returns:
            JSON-formatted scan report.
        """
        data = self.run()
        return json.dumps(data, indent=2)
