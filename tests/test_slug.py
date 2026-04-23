"""Tests for slug generation and filename manipulation."""

import sys
from pathlib import Path

import pytest

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from refractor.lib.slug import (
    extract_timestamp,
    generate_slug,
    strip_classification_suffix,
    vault_filename,
)


class TestExtractTimestamp:
    """Test timestamp extraction from filenames."""

    def test_full_timestamp(self):
        """Extract YYYY-MM-DD_HH-MM-SS prefix."""
        ts, remainder = extract_timestamp("2026-03-24_08-12-15_wyoming-emulator-summary.md")
        assert ts == "2026-03-24_08-12-15"
        assert remainder == "wyoming-emulator-summary"

    def test_date_only_timestamp(self):
        """Extract YYYY-MM-DD prefix."""
        ts, remainder = extract_timestamp("2026-03-24_epic-8-playback-plan.md")
        assert ts == "2026-03-24"
        assert remainder == "epic-8-playback-plan"

    def test_no_timestamp(self):
        """Handle filenames without timestamp."""
        ts, remainder = extract_timestamp("EPIC2_IMPLEMENTATION_SUMMARY.md")
        assert ts is None
        assert remainder == "EPIC2_IMPLEMENTATION_SUMMARY"

    def test_timestamp_without_extension(self):
        """Handle filenames passed without .md extension."""
        ts, remainder = extract_timestamp("2026-03-24_epic-plan")
        assert ts == "2026-03-24"
        assert remainder == "epic-plan"


class TestStripClassificationSuffix:
    """Test removal of classification suffixes."""

    def test_strip_plan(self):
        """Remove -plan suffix."""
        result = strip_classification_suffix("epic-8-playback-plan")
        assert result == "epic-8-playback"

    def test_strip_summary(self):
        """Remove -summary suffix."""
        result = strip_classification_suffix("performance-analysis-summary")
        assert result == "performance-analysis"

    def test_strip_prompt(self):
        """Remove -prompt suffix."""
        result = strip_classification_suffix("api-requirements-prompt")
        assert result == "api-requirements"

    def test_strip_spec(self):
        """Remove -spec suffix."""
        result = strip_classification_suffix("endpoint-design-spec")
        assert result == "endpoint-design"

    def test_no_suffix(self):
        """Leave text without classification suffix unchanged."""
        result = strip_classification_suffix("random-note")
        assert result == "random-note"


class TestGenerateSlug:
    """Test slug generation."""

    def test_full_example(self):
        """Generate slug from full timestamped filename."""
        slug = generate_slug("2026-03-24_epic-8-receiving-audio-playback-plan.md")
        assert slug == "epic-8-receiving-audio-playback"

    def test_no_timestamp(self):
        """Generate slug from filename without timestamp."""
        slug = generate_slug("EPIC2_EPIC5_IMPLEMENTATION_NOTE.md")
        assert slug == "epic2-epic5-implementation-note"

    def test_spaces_to_hyphens(self):
        """Convert spaces to hyphens."""
        slug = generate_slug("My Random Plan.md")
        assert slug == "my-random-plan"

    def test_underscores_to_hyphens(self):
        """Convert underscores to hyphens."""
        slug = generate_slug("epic_planning_doc.md")
        assert slug == "epic-planning-doc"

    def test_special_chars_removed(self):
        """Remove special characters."""
        slug = generate_slug("plan (v2) [draft].md")
        assert slug == "plan-v2-draft"

    def test_max_length_capped(self):
        """Cap slug at max_length."""
        long_name = "a-very-long-description-that-exceeds-the-maximum-slug-length-by-quite-a-bit.md"
        slug = generate_slug(long_name, max_length=30)
        assert len(slug) <= 30

    def test_empty_slug_fallback(self):
        """Return 'note' if slug becomes empty."""
        slug = generate_slug("@#$%.md")
        assert slug == "note"


class TestVaultFilename:
    """Test vault filename construction."""

    def test_with_timestamp(self):
        """Construct filename with timestamp."""
        result = vault_filename("2026-03-24", "epic-8-playback")
        assert result == "2026-03-24_epic-8-playback.md"

    def test_without_timestamp(self):
        """Construct filename without timestamp."""
        result = vault_filename(None, "epic2-implementation")
        assert result == "epic2-implementation.md"

    def test_full_timestamp_with_seconds(self):
        """Construct filename with full timestamp including seconds."""
        result = vault_filename("2026-03-24_08-12-15", "note")
        assert result == "2026-03-24_08-12-15_note.md"
