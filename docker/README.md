# Connaissance Docker Stack

Syncthing + Git-Watcher stack for vault synchronization and automated GitHub backup.

## What This Does

- **Syncthing** syncs the vault between local machines and thumper (Proxmox VM)
- **Git-Watcher** monitors the vault and auto-commits/pushes changes to GitHub
- Combined: local Obsidian edits → Syncthing sync → git commit/push in ~15 seconds

## Prerequisites

- Docker and Docker Compose installed on thumper
- GitHub PAT created (see deployment plan, Phase 4.1)
- `modules/connaissance/vault/` directory exists on thumper
- Git repo cloned to `/opt/connaissance/`

## Deployment on thumper

### 1. Copy Stack Files

```bash
cd /opt/stacks
cp -r /path/to/modules/connaissance/docker connaissance-sync
cd connaissance-sync
```

### 2. Create `.env` File

```bash
cp .env.example .env
# Edit .env with your GitHub PAT and details
nano .env
```

```bash
GITHUB_PAT=ghp_xxxxxxxxxxxx
GITHUB_USER=jjurach
GITHUB_REPO=connaissance
GITHUB_EMAIL=phaedrus@example.com
VAULT_PATH=/vault
```

### 3. Create Syncthing Config Volume

```bash
mkdir -p syncthing-config
```

### 4. Deploy Stack

```bash
docker compose up -d
```

### 5. Configure Syncthing

1. Open `http://192.168.0.121:8384` (Syncthing Web UI)
2. Go to Settings → Advanced → Environment Variables
3. Set ignore patterns:
   ```
   (?d)\.obsidian/workspace*
   (?d)\.sync-conflict-*
   (?d)\.git
   (?d)__pycache__
   (?d)\.pytest_cache
   ```
4. Add your local machine as a device:
   - Get device ID from local Syncthing UI
   - Click "Add Remote Device" on thumper
   - Confirm pairing on local side
5. Share `vault` folder from thumper to local

### 6. Verify Sync

```bash
# Check Syncthing logs
docker compose logs -f syncthing

# Check git-watcher logs
docker compose logs -f git-watcher
```

### 7. Test End-to-End

1. Edit a note in Obsidian on your local machine
2. Save the note
3. Within 10-15 seconds, check:
   - Syncthing UI (should show sync complete)
   - Git-watcher logs (should show commit)
   - GitHub (should show new commit)

## Troubleshooting

### Syncthing not syncing
- Check Syncthing web UI (port 8384)
- Verify devices are paired (both show as "Connected")
- Check ignore patterns (`.obsidian/workspace` should be ignored)

### Git-watcher not committing
- Check logs: `docker compose logs git-watcher`
- Verify `.env` has correct GitHub PAT
- Test git manually: `cd /opt/connaissance && git status`

### "Permission denied" errors
- Verify phaedrus owns `/opt/connaissance`: `ls -ld /opt/connaissance`
- Ensure `.ssh` directory is readable by container: `chmod 700 ~/.ssh`

### Push fails with "repository not found"
- Verify GitHub repo exists and is accessible: `https://github.com/jjurach/connaissance`
- Verify PAT has `repo` scope
- Try manual push: `cd /opt/connaissance && git push`

## Stack Files

- `docker-compose.yml` - Service definitions (Syncthing + git-watcher)
- `.env.example` - Template for environment variables
- `git-watcher.sh` - Bash script using inotify to watch vault and auto-commit
- `syncthing-config/` - Syncthing configuration (created on first run)

## Notes

- Git-watcher waits **10 seconds** after each file change before committing (debounce)
- Syncthing ignores `.obsidian/workspace*` and `.sync-conflict*` files
- GitHub PAT should be regenerated every 90 days (set reminder)
- Logs are available via `docker compose logs [service]`
