"""Phase 1.0: Survey command — catalog filename patterns and metadata across all files."""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from ..config import MODULES, SURVEY_MAX_VALUE_EXAMPLES
from ..lib.classifier import classify_file, extract_project
from ..lib.extractor import extract_body_metadata, extract_created_date, parse_frontmatter
from ..lib.validators import is_markdown


class Survey:
    """Catalog and analyze metadata patterns across planning files."""

    def __init__(self, hentown_root: Path):
        """
        Initialize the survey.

        Args:
            hentown_root: Absolute path to hentown root.
        """
        self.hentown_root = hentown_root
        self.files_found = []
        self.filename_patterns = defaultdict(int)
        self.files_with_existing_frontmatter = 0
        self.key_frequency = defaultdict(int)
        self.key_values = defaultdict(lambda: defaultdict(int))
        self.body_metadata_patterns = defaultdict(int)
        self.anomalies = {
            "unexpected_subdirs": [],
            "zero_byte_files": [],
            "non_markdown_files": [],
            "filename_collisions": defaultdict(list),
        }

    def run(self) -> dict[str, Any]:
        """
        Run the survey across all whitelisted modules.

        Returns:
            A dict containing:
            - files_found: list of file paths scanned
            - filename_taxonomy: pattern counts
            - existing_frontmatter_count: how many files already have YAML
            - key_frequency: every key seen, with occurrence count
            - key_values: value examples per key
            - body_metadata_patterns_found: pattern type counts
            - anomalies: dict of anomaly classes and their instances
            - timestamp: when the survey was run
        """
        self._scan_planning_directories()
        self._detect_filename_collisions()

        return {
            "timestamp": datetime.now().isoformat(),
            "files_found": len(self.files_found),
            "files_with_existing_frontmatter": self.files_with_existing_frontmatter,
            "filename_patterns": dict(self.filename_patterns),
            "key_frequency": dict(self.key_frequency),
            "key_values": {k: dict(v) for k, v in self.key_values.items()},
            "body_metadata_patterns_found": dict(self.body_metadata_patterns),
            "anomalies": dict(self.anomalies),
            "files_detail": self.files_found,
        }

    def _scan_planning_directories(self) -> None:
        """Walk all whitelisted modules' planning/ directories and catalog files."""
        for module in MODULES:
            if module == "_root":
                # hentown/planning/ at the root.
                planning_dir = self.hentown_root / "planning"
            else:
                # modules/<module>/planning/
                planning_dir = self.hentown_root / "modules" / module / "planning"

            if not planning_dir.exists():
                continue

            # Walk all files under planning/ (including subdirs).
            for file_path in planning_dir.rglob("*"):
                if file_path.is_dir():
                    continue

                self._analyze_file(file_path, planning_dir)

    def _analyze_file(self, file_path: Path, planning_dir: Path) -> None:
        """
        Analyze a single file for patterns.

        Args:
            file_path: Absolute path to the file.
            planning_dir: The planning/ directory it came from (for relative path).
        """
        # Anomaly: non-markdown files.
        if not is_markdown(file_path):
            self.anomalies["non_markdown_files"].append(str(file_path.relative_to(self.hentown_root)))
            return

        # Anomaly: zero-byte files.
        if file_path.stat().st_size == 0:
            self.anomalies["zero_byte_files"].append(str(file_path.relative_to(self.hentown_root)))
            return

        # Detect unexpected subdirs.
        rel_path = file_path.relative_to(planning_dir)
        if len(rel_path.parts) > 1:
            parent_dir = rel_path.parts[0]
            if parent_dir not in ("inbox", "inbox-archive", "analysis", "specs", "requests"):
                self.anomalies["unexpected_subdirs"].append(str(file_path.relative_to(self.hentown_root)))

        # Filename pattern analysis.
        filename = file_path.name
        self._analyze_filename_pattern(filename)

        # Read content for frontmatter and body metadata.
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            # Ignore files we can't read.
            return

        # Check for existing frontmatter.
        fm, body = parse_frontmatter(content)
        if fm:
            self.files_with_existing_frontmatter += 1
            self._analyze_frontmatter(fm)

        # Extract body metadata (only 'status' for simplified schema).
        body_meta = extract_body_metadata(body, allowed_keys={"status"})
        if body_meta:
            self._analyze_body_metadata(body_meta)

        # Record the file.
        self.files_found.append({
            "path": str(file_path.relative_to(self.hentown_root)),
            "filename": filename,
            "project": extract_project(file_path, self.hentown_root),
            "type": classify_file(file_path),
            "created": extract_created_date(filename, file_path),
            "has_frontmatter": bool(fm),
            "body_metadata_keys": list(body_meta.keys()),
        })

    def _analyze_filename_pattern(self, filename: str) -> None:
        """
        Categorize the filename by its pattern.

        Args:
            filename: The filename to categorize.
        """
        if filename.endswith("-prompt.md"):
            self.filename_patterns["-prompt.md"] += 1
        elif filename.endswith("-plan.md"):
            self.filename_patterns["-plan.md"] += 1
        elif filename.endswith("-summary.md"):
            self.filename_patterns["-summary.md"] += 1
        elif "-spec" in filename and filename.endswith(".md"):
            self.filename_patterns["-spec*.md"] += 1
        elif filename.startswith(("YYYY-MM-DD", "20")):
            # Likely has a timestamp.
            self.filename_patterns["timestamped"] += 1
        else:
            self.filename_patterns["other"] += 1

    def _analyze_frontmatter(self, fm: dict[str, Any]) -> None:
        """
        Record frontmatter key frequency and value samples.

        Args:
            fm: Parsed frontmatter dict.
        """
        for key, value in fm.items():
            self.key_frequency[f"fm:{key}"] += 1
            # Record value examples (up to SURVEY_MAX_VALUE_EXAMPLES).
            value_str = str(value)
            self.key_values[f"fm:{key}"][value_str] += 1

    def _analyze_body_metadata(self, body_meta: dict[str, str]) -> None:
        """
        Record body metadata key frequency and value samples.

        Args:
            body_meta: Dict of extracted body metadata.
        """
        self.body_metadata_patterns["found"] += 1
        for key, value in body_meta.items():
            self.key_frequency[f"body:{key}"] += 1
            # Record value examples.
            self.key_values[f"body:{key}"][value] += 1

    def _detect_filename_collisions(self) -> None:
        """Detect collisions: multiple source files that map to same target vault path."""
        from ..lib.slug import extract_timestamp, generate_slug

        target_paths = defaultdict(list)
        for file_info in self.files_found:
            source_path = file_info["path"]
            file_type = file_info["type"]
            project = file_info["project"]
            created = file_info["created"]
            filename = file_info["filename"]

            # Compute target vault path (mirrors migrate.py logic).
            slug = generate_slug(filename)

            # Build target path based on file type and project.
            if project:
                if file_type == "prompt":
                    target = f"10-Projects/{project}/logs/prompts/{created}_{slug}.md"
                elif file_type == "plan":
                    target = f"10-Projects/{project}/plans/{created}_{slug}.md"
                elif file_type == "spec":
                    target = f"10-Projects/{project}/specs/{created}_{slug}.md"
                elif file_type == "summary":
                    target = f"10-Projects/{project}/logs/summaries/{created}_{slug}.md"
                elif file_type == "inbox":
                    target = f"10-Projects/{project}/logs/inbox/{created}_{slug}.md"
                else:  # note
                    target = f"10-Projects/{project}/{created}_{slug}.md"
            else:
                # Fallback for files without a project.
                target = f"10-Projects/orphan/{created}_{slug}.md"

            target_paths[target].append(source_path)

        # Report only actual collisions: same target path, different sources.
        for target, sources in target_paths.items():
            if len(sources) > 1 and len(set(sources)) > 1:  # Different source paths
                self.anomalies["filename_collisions"][target] = sources

    def report_markdown(self) -> str:
        """
        Generate a human-readable markdown report.

        Returns:
            Markdown-formatted survey report.
        """
        data = self.run()

        lines = [
            "# Survey Report",
            "",
            f"**Generated:** {data['timestamp']}",
            "",
            "## Summary",
            "",
            f"- **Files found:** {data['files_found']}",
            f"- **Files with existing frontmatter:** {data['files_with_existing_frontmatter']}",
            "",
            "## Filename Patterns",
            "",
        ]

        # Filename taxonomy.
        lines.append("### Pattern Distribution")
        lines.append("")
        for pattern, count in sorted(data["filename_patterns"].items(), key=lambda x: -x[1]):
            lines.append(f"- `{pattern}`: **{count}** files")
        lines.append("")

        # Frontmatter & Body metadata.
        lines.append("## Metadata Keys Found")
        lines.append("")
        lines.append("### Key Frequency")
        lines.append("")
        for key, count in sorted(data["key_frequency"].items(), key=lambda x: -x[1])[:50]:
            lines.append(f"- `{key}`: **{count}** files")
        lines.append("")

        # Value distribution for key keys.
        lines.append("### Value Distribution (top keys)")
        lines.append("")
        for key in ["body:status", "body:type", "fm:status", "fm:type"]:
            if key not in data["key_values"]:
                continue
            lines.append(f"#### `{key}`")
            lines.append("")
            for value, count in sorted(data["key_values"][key].items(), key=lambda x: -x[1]):
                lines.append(f"- `{value}`: **{count}**")
            lines.append("")

        # Anomalies.
        lines.append("## Anomalies")
        lines.append("")
        if data["anomalies"]["zero_byte_files"]:
            lines.append(f"### Zero-byte files ({len(data['anomalies']['zero_byte_files'])})")
            lines.append("")
            for path in data["anomalies"]["zero_byte_files"][:10]:
                lines.append(f"- `{path}`")
            lines.append("")

        if data["anomalies"]["non_markdown_files"]:
            lines.append(f"### Non-markdown files ({len(data['anomalies']['non_markdown_files'])})")
            lines.append("")
            for path in data["anomalies"]["non_markdown_files"][:10]:
                lines.append(f"- `{path}`")
            lines.append("")

        if data["anomalies"]["unexpected_subdirs"]:
            lines.append(f"### Unexpected subdirs ({len(data['anomalies']['unexpected_subdirs'])})")
            lines.append("")
            for path in data["anomalies"]["unexpected_subdirs"][:10]:
                lines.append(f"- `{path}`")
            lines.append("")

        if data["anomalies"]["filename_collisions"]:
            lines.append(f"### Filename collisions ({len(data['anomalies']['filename_collisions'])})")
            lines.append("")
            for basename, paths in sorted(data["anomalies"]["filename_collisions"].items())[:10]:
                lines.append(f"#### `{basename}`")
                lines.append("")
                for path in paths:
                    lines.append(f"- `{path}`")
                lines.append("")

        return "\n".join(lines)
