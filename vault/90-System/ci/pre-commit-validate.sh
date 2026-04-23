#!/bin/bash
# Pre-commit hook to validate Obsidian vault frontmatter
# Run on staged .md files in vault/10-Projects/ and vault/00-Inbox/
#
# This is a stub. To integrate:
# 1. Copy or symlink to .git/hooks/pre-commit
# 2. Make executable: chmod +x .git/hooks/pre-commit
# 3. Adjust paths for your environment

set -e

# Get the repository root
REPO_ROOT=$(git rev-parse --show-toplevel)
VAULT_ROOT="${REPO_ROOT}/modules/hentown-obsidian/vault"

# Check if Python and jsonschema are available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

# Create a temporary report directory
REPORT_DIR=$(mktemp -d)
trap "rm -rf $REPORT_DIR" EXIT

# Run the validator
python3 -m modules.hentown_obsidian.scripts.refractor validate \
    --vault-root "$VAULT_ROOT" \
    --report "$REPORT_DIR" \
    || {
        echo "Validation failed. See report:"
        cat "$REPORT_DIR/validate-report.json"
        exit 1
    }

exit 0
