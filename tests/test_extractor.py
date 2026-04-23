"""Tests for metadata extraction from files."""

import sys
from pathlib import Path

import pytest

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from refractor.lib.extractor import (
    extract_body_metadata,
    extract_created_date,
    extract_mtime,
    parse_frontmatter,
)


class TestParseFrontmatter:
    """Test YAML frontmatter parsing."""

    def test_valid_frontmatter(self):
        """Parse valid YAML frontmatter."""
        content = "---\ntype: plan\nstatus: draft\n---\n# Body\n"
        fm, body = parse_frontmatter(content)
        assert fm == {"type": "plan", "status": "draft"}
        assert body == "# Body\n"

    def test_empty_frontmatter(self):
        """Parse empty frontmatter block."""
        content = "---\n---\n# Body\n"
        fm, body = parse_frontmatter(content)
        assert fm == {}
        assert body == "# Body\n"

    def test_no_frontmatter(self):
        """Return empty dict when no frontmatter."""
        content = "# No frontmatter\nJust content.\n"
        fm, body = parse_frontmatter(content)
        assert fm == {}
        assert body == content

    def test_unclosed_frontmatter(self):
        """Return empty dict if frontmatter is not closed."""
        content = "---\ntype: plan\n# No closing\n"
        fm, body = parse_frontmatter(content)
        assert fm == {}
        assert body == content

    def test_frontmatter_with_complex_yaml(self):
        """Parse frontmatter with nested structures."""
        content = "---\ntype: plan\ntags:\n  - urgent\n  - draft\n---\nBody\n"
        fm, body = parse_frontmatter(content)
        assert fm["type"] == "plan"
        assert fm["tags"] == ["urgent", "draft"]
        assert body == "Body\n"


class TestExtractBodyMetadata:
    """Test extraction of metadata from body headers."""

    def test_bold_colon_pattern(self):
        """Extract **Key:** Value pattern."""
        content = "**Status:** Planned\n**Target Completion:** 2026-06-23\n## Section\n"
        metadata = extract_body_metadata(content, allowed_keys={"status", "target_completion"})
        assert metadata["status"] == "Planned"
        assert metadata["target_completion"] == "2026-06-23"

    def test_list_bold_colon_pattern(self):
        """Extract - **Key:** Value pattern."""
        content = "- **Status:** In Progress\n- **Owner:** Alice\n## Body\n"
        metadata = extract_body_metadata(content, allowed_keys={"status", "owner"})
        assert metadata["status"] == "In Progress"
        assert metadata["owner"] == "Alice"

    def test_bare_pattern(self):
        """Extract Key: Value pattern."""
        content = "Status: Draft\nAuthor: Bob\n## Section\n"
        metadata = extract_body_metadata(content, allowed_keys={"status", "author"})
        assert metadata["status"] == "Draft"
        assert metadata["author"] == "Bob"

    def test_mixed_patterns(self):
        """Extract with mixed metadata patterns."""
        content = """**Status:** Planned
- **Target:** 2026-06-23
Owner: Charlie
## Content
"""
        metadata = extract_body_metadata(content, allowed_keys={"status", "target", "owner"})
        assert metadata["status"] == "Planned"
        assert metadata["target"] == "2026-06-23"
        assert metadata["owner"] == "Charlie"

    def test_stops_at_heading(self):
        """Only extract from preamble before first ## heading."""
        content = """**Status:** Planned

## Main Section

**Embedded:** False

## Another Section
"""
        metadata = extract_body_metadata(content)
        assert metadata["status"] == "Planned"
        assert "embedded" not in metadata

    def test_multiline_value(self):
        """Extract only single-line values (multiline stops at newline)."""
        content = "**Description:** This is a\nmultiline value\n## Section\n"
        metadata = extract_body_metadata(content, allowed_keys={"description"})
        # Should capture only the first line after the colon.
        assert metadata["description"] == "This is a"

    def test_empty_body(self):
        """Handle empty body."""
        content = ""
        metadata = extract_body_metadata(content)
        assert metadata == {}

    def test_no_metadata(self):
        """Return empty dict when no metadata patterns found."""
        content = "Just some random text\nwith no metadata\n## Heading\n"
        metadata = extract_body_metadata(content)
        assert metadata == {}

    def test_key_normalization(self):
        """Normalize key names to lowercase with underscores."""
        content = "**Target Completion:** 2026-06-23\n## Body\n"
        metadata = extract_body_metadata(content, allowed_keys={"target_completion"})
        assert "target_completion" in metadata
        assert "Target Completion" not in metadata


class TestExtractCreatedDate:
    """Test creation date extraction."""

    def test_date_from_filename(self):
        """Extract date from filename with YYYY-MM-DD prefix."""
        date = extract_created_date("2026-03-24_epic-plan.md", Path("/tmp/dummy.md"))
        assert date == "2026-03-24"

    def test_full_timestamp_from_filename(self):
        """Extract date from filename with full timestamp."""
        date = extract_created_date(
            "2026-03-24_08-12-15_epic-plan.md",
            Path("/tmp/dummy.md")
        )
        assert date == "2026-03-24"

    def test_no_date_in_filename(self):
        """Fall back to mtime when filename has no date."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            temp_path = Path(f.name)
            date = extract_created_date("no-date-plan.md", temp_path)
            # Should return a valid date string in YYYY-MM-DD format.
            assert len(date) == 10
            assert date[4] == "-" and date[7] == "-"
            temp_path.unlink()


class TestExtractMtime:
    """Test file modification time extraction."""

    def test_extract_mtime(self):
        """Extract mtime as ISO date."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            temp_path = Path(f.name)
            mtime = extract_mtime(temp_path)
            # Should be a valid date string.
            assert len(mtime) == 10
            assert mtime[4] == "-" and mtime[7] == "-"
            temp_path.unlink()
