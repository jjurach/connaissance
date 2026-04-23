"""Pytest fixtures for refractor tests."""

import pytest
from pathlib import Path


@pytest.fixture
def tmp_hentown(tmp_path):
    """Create a temporary hentown directory structure with planning files."""
    hentown_root = tmp_path / "hentown"
    hentown_root.mkdir()

    # Create base directories.
    (hentown_root / "modules").mkdir()
    (hentown_root / "planning").mkdir()

    # Create AGENTS.md so get_hentown_root() can find it.
    (hentown_root / "AGENTS.md").touch()

    # Create module planning directories with fixtures.
    modules = ["chatterbox", "mellona", "pigeon"]
    for module in modules:
        planning_dir = hentown_root / "modules" / module / "planning"
        planning_dir.mkdir(parents=True)
        _create_module_fixtures(planning_dir, module)

    # Create root planning directory.
    _create_root_fixtures(hentown_root / "planning")

    return hentown_root


@pytest.fixture
def tmp_vault(tmp_path):
    """Create a temporary vault directory structure."""
    vault_root = tmp_path / "vault"
    vault_root.mkdir()

    # Create PARA structure.
    for dirname in ["00-Inbox", "10-Projects", "20-Memory", "30-Resources", "40-Archive", "90-System"]:
        (vault_root / dirname).mkdir()

    return vault_root


def _create_module_fixtures(planning_dir: Path, module: str) -> None:
    """Create fixture planning files for a module."""
    # Plan with timestamp and body metadata.
    plan_file = planning_dir / f"2026-03-24_epic-plan-{module}.md"
    plan_file.write_text(
        f"""**Status:** Planned
**Target Completion:** 2026-06-23
**Estimated Duration:** 1.5 weeks

## Overview

This is a plan for {module}.
"""
    )

    # Prompt without timestamp.
    prompt_file = planning_dir / f"prompt-{module}-requirements.md"
    prompt_file.write_text(
        f"""# Requirements for {module}

What should the {module} module do?
"""
    )

    # Summary with body metadata.
    summary_file = planning_dir / f"2026-04-10_epic-summary.md"
    summary_file.write_text(
        f"""---
status: completed
---

**Status:** Completed
**Outcome:** Successful

## Summary

Work is done.
"""
    )

    # Create inbox subdirectory with a note.
    inbox_dir = planning_dir / "inbox"
    inbox_dir.mkdir()
    inbox_note = inbox_dir / "2026-04-11_random-idea.md"
    inbox_note.write_text("Quick thought to organize later.\n")

    # Create specs subdirectory.
    specs_dir = planning_dir / "specs"
    specs_dir.mkdir()
    spec_file = specs_dir / f"2026-01-15_api-spec.md"
    spec_file.write_text(
        """**Status:** Draft

API specification for the module.
"""
    )

    # Create analysis subdirectory.
    analysis_dir = planning_dir / "analysis"
    analysis_dir.mkdir()
    analysis_file = analysis_dir / f"2026-04-09_performance-analysis.md"
    analysis_file.write_text("Performance measurement results.\n")


def _create_root_fixtures(planning_dir: Path) -> None:
    """Create fixture planning files in the root planning/ directory."""
    # Root plan.
    plan_file = planning_dir / f"2026-02-01_roadmap-plan.md"
    plan_file.write_text(
        """**Status:** In Progress

## Q2 Roadmap

Key initiatives for Q2 2026.
"""
    )

    # Root summary.
    summary_file = planning_dir / f"2026-04-01_monthly-summary.md"
    summary_file.write_text(
        """**Status:** Completed

## April Summary

Month review and outcomes.
"""
    )
