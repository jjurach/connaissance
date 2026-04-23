"""Tests for validation utilities."""

import sys
from pathlib import Path

import pytest

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from refractor.lib.validators import (
    is_markdown,
    is_valid_slug,
    is_valid_timestamp,
    is_valid_wikilink,
    is_valid_yaml_value,
)


class TestIsMarkdown:
    """Test markdown file detection."""

    def test_markdown_file(self):
        """Recognize .md files."""
        assert is_markdown(Path("document.md")) is True

    def test_uppercase_markdown(self):
        """Recognize .MD files (case-insensitive)."""
        assert is_markdown(Path("document.MD")) is True

    def test_non_markdown_file(self):
        """Reject non-.md files."""
        assert is_markdown(Path("document.txt")) is False
        assert is_markdown(Path("document.py")) is False

    def test_no_extension(self):
        """Reject files with no extension."""
        assert is_markdown(Path("document")) is False


class TestIsValidTimestamp:
    """Test timestamp format validation."""

    def test_date_only(self):
        """Validate YYYY-MM-DD format."""
        assert is_valid_timestamp("2026-03-24") is True

    def test_full_timestamp(self):
        """Validate YYYY-MM-DD_HH-MM-SS format."""
        assert is_valid_timestamp("2026-03-24_08-12-15") is True

    def test_invalid_format(self):
        """Reject invalid timestamp formats."""
        assert is_valid_timestamp("03/24/2026") is False
        assert is_valid_timestamp("2026-3-24") is False
        assert is_valid_timestamp("2026-03-24T08:12:15") is False

    def test_empty_string(self):
        """Reject empty string."""
        assert is_valid_timestamp("") is False

    def test_partial_timestamp(self):
        """Reject partial timestamps."""
        assert is_valid_timestamp("2026") is False
        assert is_valid_timestamp("2026-03") is False


class TestIsValidSlug:
    """Test slug validation."""

    def test_valid_slug(self):
        """Recognize valid slugs."""
        assert is_valid_slug("epic-8-playback") is True
        assert is_valid_slug("simple") is True
        assert is_valid_slug("a1") is True

    def test_uppercase_rejected(self):
        """Reject uppercase characters."""
        assert is_valid_slug("Epic-8-Playback") is False

    def test_leading_hyphen_rejected(self):
        """Reject slugs starting with hyphen."""
        assert is_valid_slug("-invalid") is False

    def test_trailing_hyphen_rejected(self):
        """Reject slugs ending with hyphen."""
        assert is_valid_slug("invalid-") is False

    def test_consecutive_hyphens_rejected(self):
        """Reject consecutive hyphens."""
        assert is_valid_slug("epic--plan") is False

    def test_special_chars_rejected(self):
        """Reject special characters."""
        assert is_valid_slug("epic@plan") is False
        assert is_valid_slug("epic_plan") is False

    def test_single_char_valid(self):
        """Single lowercase letter is valid."""
        assert is_valid_slug("a") is True

    def test_empty_string_invalid(self):
        """Reject empty string."""
        assert is_valid_slug("") is False


class TestIsValidWikilink:
    """Test Obsidian wikilink validation."""

    def test_simple_wikilink(self):
        """Recognize simple wikilinks."""
        assert is_valid_wikilink("[[chatterbox]]") is True

    def test_nested_wikilink(self):
        """Recognize wikilinks with paths."""
        assert is_valid_wikilink("[[path/to/note]]") is True

    def test_wikilink_with_display_text(self):
        """Recognize wikilinks with display text (simplified check)."""
        # Note: our simple check just looks for [[ ... ]]
        assert is_valid_wikilink("[[note|display]]") is True

    def test_invalid_without_brackets(self):
        """Reject plain text without brackets."""
        assert is_valid_wikilink("chatterbox") is False

    def test_invalid_incomplete_brackets(self):
        """Reject incomplete brackets."""
        assert is_valid_wikilink("[chatterbox]]") is False
        assert is_valid_wikilink("[[chatterbox]") is False

    def test_empty_wikilink_invalid(self):
        """Reject empty wikilinks."""
        assert is_valid_wikilink("[[]]") is False

    def test_non_string_rejected(self):
        """Reject non-string values."""
        assert is_valid_wikilink(None) is False
        assert is_valid_wikilink(123) is False


class TestIsValidYamlValue:
    """Test YAML serializability of values."""

    def test_scalar_values(self):
        """Recognize YAML-serializable scalars."""
        assert is_valid_yaml_value(None) is True
        assert is_valid_yaml_value(True) is True
        assert is_valid_yaml_value(False) is True
        assert is_valid_yaml_value(42) is True
        assert is_valid_yaml_value(3.14) is True
        assert is_valid_yaml_value("text") is True

    def test_list_valid(self):
        """Recognize valid lists."""
        assert is_valid_yaml_value([1, 2, 3]) is True
        assert is_valid_yaml_value(["a", "b"]) is True

    def test_list_with_mixed_types(self):
        """Recognize lists with mixed scalar types."""
        assert is_valid_yaml_value([1, "a", None]) is True

    def test_dict_valid(self):
        """Recognize valid dicts."""
        assert is_valid_yaml_value({"key": "value"}) is True
        assert is_valid_yaml_value({"a": 1, "b": 2}) is True

    def test_nested_structures(self):
        """Recognize nested structures."""
        assert is_valid_yaml_value({"a": [1, 2], "b": {"c": "d"}}) is True

    def test_callable_invalid(self):
        """Reject callables."""
        assert is_valid_yaml_value(lambda x: x) is False

    def test_custom_object_invalid(self):
        """Reject custom objects."""
        class CustomObj:
            pass
        assert is_valid_yaml_value(CustomObj()) is False

    def test_list_with_callable_invalid(self):
        """Reject lists containing non-serializable items."""
        assert is_valid_yaml_value([1, lambda x: x]) is False
