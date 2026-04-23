"""Tests for the survey command."""

import sys
from pathlib import Path

import pytest

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from refractor.commands.survey import Survey


class TestSurvey:
    """Test the survey command."""

    def test_survey_runs(self, tmp_hentown):
        """Survey can run without errors."""
        survey = Survey(tmp_hentown)
        data = survey.run()

        assert "timestamp" in data
        assert data["files_found"] > 0
        assert isinstance(data["filename_patterns"], dict)
        assert isinstance(data["key_frequency"], dict)

    def test_survey_finds_files(self, tmp_hentown):
        """Survey finds planning files."""
        survey = Survey(tmp_hentown)
        data = survey.run()

        # Should find files in fixtures.
        assert data["files_found"] > 0

        # Check that files are recorded.
        file_paths = [f["path"] for f in data["files_detail"]]
        assert len(file_paths) > 0

    def test_survey_detects_patterns(self, tmp_hentown):
        """Survey detects filename patterns."""
        survey = Survey(tmp_hentown)
        data = survey.run()

        # Should detect various patterns from fixtures.
        patterns = data["filename_patterns"]
        assert any(pattern in patterns for pattern in ["-plan.md", "-summary.md", "-prompt.md"])

    def test_survey_detects_body_metadata(self, tmp_hentown):
        """Survey detects body metadata in files."""
        survey = Survey(tmp_hentown)
        data = survey.run()

        # Should detect keys from fixture body metadata.
        key_freq = data["key_frequency"]
        assert any("status" in key for key in key_freq.keys())

    def test_survey_detects_existing_frontmatter(self, tmp_hentown):
        """Survey counts files with existing frontmatter."""
        survey = Survey(tmp_hentown)
        data = survey.run()

        # Fixture includes one file with YAML frontmatter.
        assert data["files_with_existing_frontmatter"] >= 1

    def test_survey_detects_inbox_files(self, tmp_hentown):
        """Survey detects files in inbox/ subdirectory."""
        survey = Survey(tmp_hentown)
        data = survey.run()

        # Should find inbox files in fixture structure.
        files = data["files_detail"]
        inbox_files = [f for f in files if "inbox" in f["path"]]
        assert len(inbox_files) > 0

    def test_survey_markdown_report(self, tmp_hentown):
        """Survey can generate markdown report."""
        survey = Survey(tmp_hentown)
        report = survey.report_markdown()

        assert "Survey Report" in report
        assert "Filename Patterns" in report
        assert "Metadata Keys Found" in report

    def test_survey_categorizes_timestamps(self, tmp_hentown):
        """Survey categorizes files by timestamp presence."""
        survey = Survey(tmp_hentown)
        data = survey.run()

        # Some files have timestamps, some don't.
        files = data["files_detail"]
        timestamped = [f for f in files if f["created"] and "-" in f["created"]]
        assert len(timestamped) > 0
