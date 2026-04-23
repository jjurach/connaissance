#!/bin/sh
# Git Watcher: Monitor vault directory and auto-commit/push changes
#
# This script watches the vault directory for file changes and automatically
# commits and pushes them to GitHub after a quiet period.
#
# Requirements: git, inotify-tools, curl
# Environment variables: GITHUB_PAT, GITHUB_USER, GITHUB_REPO, VAULT_PATH, GIT_QUIET_PERIOD

set -e

VAULT_PATH="${VAULT_PATH:-.}"
QUIET_PERIOD="${GIT_QUIET_PERIOD:-10}"
GITHUB_PAT="${GITHUB_PAT}"
GITHUB_USER="${GITHUB_USER}"
GITHUB_REPO="${GITHUB_REPO}"

if [ -z "$GITHUB_PAT" ] || [ -z "$GITHUB_USER" ] || [ -z "$GITHUB_REPO" ]; then
    echo "ERROR: GITHUB_PAT, GITHUB_USER, and GITHUB_REPO must be set"
    exit 1
fi

# Configure git with GitHub PAT
git config --global user.name "${GIT_AUTHOR_NAME:-connaissance-watcher}"
git config --global user.email "${GIT_AUTHOR_EMAIL:-phaedrus@example.com}"

# Set up git remote with GitHub PAT authentication
REMOTE_URL="https://${GITHUB_USER}:${GITHUB_PAT}@github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE_URL"
git config credential.helper store

echo "🔍 Git Watcher started. Monitoring $VAULT_PATH"
echo "   Quiet period: ${QUIET_PERIOD}s"
echo "   Repository: ${GITHUB_USER}/${GITHUB_REPO}"
echo ""

# Start inotifywait to monitor vault directory
# close_write: file was written and closed
# moved_to: file was moved into vault
# delete: file was deleted
inotifywait -m -r -e close_write,moved_to,delete \
    --exclude '\.obsidian/workspace|\.sync-conflict|\.git|__pycache__|\.pytest_cache' \
    "$VAULT_PATH" |
while read -r dir action file; do
    # Ignore certain files/patterns
    case "$file" in
        *.tmp|*.swp|.DS_Store|Thumbs.db)
            continue
            ;;
    esac

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Change detected: $dir$file ($action)"

    # Wait for quiet period (no more changes for N seconds)
    sleep "$QUIET_PERIOD"

    # Check if there are actual changes to commit
    if ! git diff --quiet --cached && ! git diff --quiet; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📝 Quiet period complete, committing changes..."

        # Pull first to avoid conflicts
        if ! git pull --rebase origin main 2>/dev/null; then
            echo "⚠️  Pull failed (repo may not exist yet on remote), continuing with local commit"
        fi

        # Stage all changes (including .sync-conflict files)
        git add -A

        # Commit
        TIMESTAMP=$(date -Iseconds)
        if git commit -m "Vault auto-update: $TIMESTAMP" 2>/dev/null; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Committed"

            # Push to GitHub
            if git push -u origin main 2>/dev/null; then
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 Pushed to GitHub"
            else
                echo "⚠️  Push failed (check PAT, branch name, or network)"
            fi
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️  No changes to commit"
        fi
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️  No changes detected"
    fi
done
