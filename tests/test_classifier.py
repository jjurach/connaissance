"""Tests for file classification."""

import sys
from pathlib import Path

import pytest

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from refractor.lib.classifier import classify_file, extract_project


class TestClassifyFile:
    """Test file classification by type."""

    def test_inbox_directory(self):
        """Files in inbox/ are classified as inbox."""
        path = Path("/modules/chatterbox/planning/inbox/note.md")
        assert classify_file(path) == "inbox"

    def test_inbox_archive_directory(self):
        """Files in inbox-archive/ are classified as inbox."""
        path = Path("/modules/chatterbox/planning/inbox-archive/old.md")
        assert classify_file(path) == "inbox"

    def test_analysis_directory(self):
        """Files in analysis/ are classified as summary."""
        path = Path("/modules/chatterbox/planning/analysis/perf-report.md")
        assert classify_file(path) == "summary"

    def test_specs_directory(self):
        """Files in specs/ are classified as spec."""
        path = Path("/modules/chatterbox/planning/specs/api-spec.md")
        assert classify_file(path) == "spec"

    def test_spec_suffix(self):
        """Filename with -spec suffix is classified as spec."""
        path = Path("/modules/chatterbox/planning/2026-03-24_api-spec.md")
        assert classify_file(path) == "spec"

    def test_spec_variant_suffix(self):
        """Filename with -spec- variant is classified as spec."""
        path = Path("/modules/chatterbox/planning/endpoint-spec-v2.md")
        assert classify_file(path) == "spec"

    def test_plan_suffix(self):
        """Filename with -plan.md suffix is classified as plan."""
        path = Path("/modules/chatterbox/planning/2026-03-24_epic-plan.md")
        assert classify_file(path) == "plan"

    def test_prompt_suffix(self):
        """Filename with -prompt.md suffix is classified as prompt."""
        path = Path("/modules/chatterbox/planning/requirements-prompt.md")
        assert classify_file(path) == "prompt"

    def test_summary_suffix(self):
        """Filename with -summary.md suffix is classified as summary."""
        path = Path("/modules/chatterbox/planning/2026-04-10_work-summary.md")
        assert classify_file(path) == "summary"

    def test_fallback_note(self):
        """Filename with no recognized pattern is classified as note."""
        path = Path("/modules/chatterbox/planning/misc-thoughts.md")
        assert classify_file(path) == "note"

    def test_directory_precedence_over_filename(self):
        """Directory classification takes precedence over filename."""
        # File in inbox/ with -plan.md suffix → inbox wins.
        path = Path("/modules/chatterbox/planning/inbox/2026-03-24_epic-plan.md")
        assert classify_file(path) == "inbox"


class TestExtractProject:
    """Test project extraction from file paths."""

    def test_module_path(self):
        """Extract module name from modules/<module>/planning/ path."""
        path = Path("/home/phaedrus/hentown/modules/chatterbox/planning/foo.md")
        hentown_root = Path("/home/phaedrus/hentown")
        assert extract_project(path, hentown_root) == "chatterbox"

    def test_root_path(self):
        """Extract _root for planning/ at hentown root."""
        path = Path("/home/phaedrus/hentown/planning/foo.md")
        hentown_root = Path("/home/phaedrus/hentown")
        assert extract_project(path, hentown_root) == "_root"

    def test_nested_module_path(self):
        """Extract module from nested directory under modules/."""
        path = Path("/home/phaedrus/hentown/modules/chatterbox/planning/inbox/note.md")
        hentown_root = Path("/home/phaedrus/hentown")
        assert extract_project(path, hentown_root) == "chatterbox"

    def test_multiple_modules(self):
        """Extract correct module when multiple could match."""
        path = Path("/home/phaedrus/hentown/modules/mellona/planning/spec.md")
        hentown_root = Path("/home/phaedrus/hentown")
        assert extract_project(path, hentown_root) == "mellona"
