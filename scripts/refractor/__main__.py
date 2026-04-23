"""
CLI entry point for refractor.

Usage:
    python -m refractor survey [--hentown-root PATH] [--report DIR]
    python -m refractor scan [--hentown-root PATH] [--vault-root PATH] [--report DIR]
    python -m refractor migrate [--hentown-root PATH] [--vault-root PATH] [--overwrite] [--report DIR]
    python -m refractor validate [--vault-root PATH] [--report DIR]
"""

import argparse
import json
import sys
from pathlib import Path

from .commands.migrate import Migrate
from .commands.scan import Scan
from .commands.survey import Survey
from .commands.validate import Validate
from .config import DEFAULT_REPORT_DIR


def get_hentown_root() -> Path:
    """
    Detect hentown root by finding the modules/ directory.

    Returns:
        Absolute path to hentown root.

    Raises:
        RuntimeError if hentown root cannot be found.
    """
    # Start from current directory and walk up.
    current = Path.cwd()
    while current != current.parent:
        if (current / "modules").exists() and (current / "AGENTS.md").exists():
            return current
        current = current.parent

    raise RuntimeError(
        "Could not find hentown root. "
        "Please run from within the hentown directory or use --hentown-root."
    )


def cmd_survey(args: argparse.Namespace) -> int:
    """Run the survey command."""
    hentown_root = Path(args.hentown_root)
    report_dir = Path(args.report)
    report_dir.mkdir(parents=True, exist_ok=True)

    survey = Survey(hentown_root)
    data = survey.run()

    # Write JSON report.
    json_path = report_dir / "survey-report.json"
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"JSON report: {json_path}")

    # Write Markdown report.
    md_path = report_dir / "survey-report.md"
    with open(md_path, "w") as f:
        f.write(survey.report_markdown())
    print(f"Markdown report: {md_path}")

    print(f"✓ Survey complete: {data['files_found']} files found")
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    """Run the scan command."""
    hentown_root = Path(args.hentown_root)
    vault_root = Path(args.vault_root)
    report_dir = Path(args.report)
    report_dir.mkdir(parents=True, exist_ok=True)

    scan = Scan(hentown_root, vault_root)
    report = scan.report_json()

    # Write JSON report.
    json_path = report_dir / "scan-report.json"
    with open(json_path, "w") as f:
        f.write(report)
    print(f"Scan report: {json_path}")

    # Parse and print summary.
    data = json.loads(report)
    print(f"✓ Scan complete: {data['files_count']} files classified")
    if data["warnings"]:
        print(f"  ⚠ {len(data['warnings'])} warnings")

    return 0


def cmd_migrate(args: argparse.Namespace) -> int:
    """Run the migrate command."""
    hentown_root = Path(args.hentown_root)
    vault_root = Path(args.vault_root)
    report_dir = Path(args.report)
    overwrite = args.overwrite
    report_dir.mkdir(parents=True, exist_ok=True)

    migrate = Migrate(hentown_root, vault_root, overwrite=overwrite)
    report = migrate.report_json()

    # Write JSON report.
    json_path = report_dir / "migration-report.json"
    with open(json_path, "w") as f:
        f.write(report)
    print(f"Migration report: {json_path}")

    # Parse and print summary.
    data = json.loads(report)
    print(f"✓ Migration complete:")
    print(f"  • Migrated: {data['files_migrated']} files")
    print(f"  • Skipped: {data['files_skipped']} (collisions)")
    if data['errors']:
        print(f"  • Errors: {data['errors']}")
        return 1

    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Run the validate command."""
    vault_root = Path(args.vault_root)
    report_dir = Path(args.report)
    report_dir.mkdir(parents=True, exist_ok=True)

    validate = Validate(vault_root)
    report = validate.report_json()

    # Write JSON report.
    json_path = report_dir / "validate-report.json"
    with open(json_path, "w") as f:
        f.write(report)
    print(f"Validation report: {json_path}")

    # Parse and print summary.
    data = json.loads(report)
    if data["valid"]:
        print(f"✓ Validation passed!")
        return 0
    else:
        print(f"✗ Validation failed:")
        for err in data["errors"][:10]:
            print(f"  • {err['file']}: {err.get('error', 'unknown error')}")
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Refractor: vault migration tool for Obsidian",
        prog="refractor",
    )

    # Subcommands.
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # survey
    survey_parser = subparsers.add_parser(
        "survey",
        help="Phase 1.0: catalog metadata patterns (read-only)",
    )
    survey_parser.add_argument(
        "--hentown-root",
        default=None,
        help="Path to hentown root (auto-detected if not provided)",
    )
    survey_parser.add_argument(
        "--report",
        default=DEFAULT_REPORT_DIR,
        help=f"Directory for output reports (default: {DEFAULT_REPORT_DIR})",
    )

    # scan
    scan_parser = subparsers.add_parser(
        "scan",
        help="Phase 1.2: classify files and preview extraction",
    )
    scan_parser.add_argument(
        "--hentown-root",
        default=None,
        help="Path to hentown root (auto-detected if not provided)",
    )
    scan_parser.add_argument(
        "--vault-root",
        default=None,
        help="Path to vault root (defaults to hentown-root/modules/hentown-obsidian/vault)",
    )
    scan_parser.add_argument(
        "--report",
        default=DEFAULT_REPORT_DIR,
        help=f"Directory for output reports (default: {DEFAULT_REPORT_DIR})",
    )

    # migrate
    migrate_parser = subparsers.add_parser(
        "migrate",
        help="Phase 1.3: migrate files to vault with frontmatter",
    )
    migrate_parser.add_argument(
        "--hentown-root",
        default=None,
        help="Path to hentown root (auto-detected if not provided)",
    )
    migrate_parser.add_argument(
        "--vault-root",
        default=None,
        help="Path to vault root (defaults to hentown-root/modules/hentown-obsidian/vault)",
    )
    migrate_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing vault files",
    )
    migrate_parser.add_argument(
        "--report",
        default=DEFAULT_REPORT_DIR,
        help=f"Directory for output reports (default: {DEFAULT_REPORT_DIR})",
    )

    # validate
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate vault files against schema",
    )
    validate_parser.add_argument(
        "--vault-root",
        default=None,
        help="Path to vault root (defaults to hentown-root/modules/hentown-obsidian/vault)",
    )
    validate_parser.add_argument(
        "--report",
        default=DEFAULT_REPORT_DIR,
        help=f"Directory for output reports (default: {DEFAULT_REPORT_DIR})",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Detect hentown_root if not provided.
    if hasattr(args, "hentown_root") and args.hentown_root:
        hentown_root = Path(args.hentown_root)
    else:
        try:
            hentown_root = get_hentown_root()
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    if hasattr(args, "hentown_root"):
        args.hentown_root = hentown_root

    # Detect vault_root if not provided.
    if hasattr(args, "vault_root") and args.vault_root:
        args.vault_root = Path(args.vault_root)
    elif hasattr(args, "vault_root"):
        args.vault_root = hentown_root / "modules" / "hentown-obsidian" / "vault"

    # Execute command.
    if args.command == "survey":
        return cmd_survey(args)
    elif args.command == "scan":
        return cmd_scan(args)
    elif args.command == "migrate":
        return cmd_migrate(args)
    elif args.command == "validate":
        return cmd_validate(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
