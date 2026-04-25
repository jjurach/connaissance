# Connaissance Sync Server (Thumper)

Syncthing + Git-Watcher stack for vault synchronization and automated GitHub backup.

## What This Does

- **Syncthing** syncs the vault between local machines and thumper (Proxmox VM)
- **Git-Watcher** monitors the vault and auto-commits/pushes changes to GitHub every ~15 seconds
- Combined: local Obsidian edits → Syncthing sync → git commit/push within ~20 seconds total

## Prerequisites

- Docker and Docker Compose installed on thumper
- GitHub PAT created (see below)
- `/opt/connaissance/` directory exists on thumper (git repo clone)
- `/opt/connaissance/vault/` directory created

## Deployment on Thumper

### 1. Deploy via Justfile (Recommended)

From hentown root:
```bash
cd modules/local-services
just deploy-connaissance-sync-server
```

This rsync's all stack files to `thumper:/opt/stacks/connaissance-sync-server/`

### 2. Manual Setup After Deployment

On thumper:
```bash
cd /opt/stacks/connaissance-sync-server
cp .env.example .env
nano .env  # Add your GitHub PAT and email
mkdir -p syncthing-config
docker compose up -d
```

### 3. Create GitHub Personal Access Token

If you don't have one:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. **Name:** `connaissance-git-watcher`
4. **Scopes:** Select `repo` (full control of private repos)
5. **Expiration:** 90 days
6. **Copy token** and paste into `.env` as `GITHUB_PAT=ghp_...`

**Important:** PAT will expire in 90 days. Set a reminder to rotate it quarterly.

### 4. Configure Syncthing

1. Open Syncthing Web UI: `http://192.168.0.121:8384`
2. Go to **Settings → Advanced → Environment Variables**
3. Add ignore patterns:
   ```
   (?d)\.obsidian/workspace*
   (?d)\.sync-conflict-*
   (?d)\.git
   (?d)__pycache__
   (?d)\.pytest_cache
   ```
4. Go to **Settings → Folders** and create/share the `vault` folder:
   - **Label:** vault
   - **Path:** /var/syncthing/vault
   - **Ignore Deletes:** (optional, recommended)

### 5. Pair with Desktop Device

On desktop (local machine):

1. Open http://localhost:8384 (Syncthing UI)
2. Copy **Device ID** (Settings → General)
3. Go back to thumper UI (192.168.0.121:8384)
4. Click **Add Remote Device**
5. Paste desktop device ID
6. Set sharing for `vault` folder
7. Accept pairing on desktop side

### 6. Verify Sync

Check logs:
```bash
docker compose logs -f syncthing
docker compose logs -f git-watcher
```

Expected output:
- Syncthing: "Syncing connected"
- Git-watcher: "🔍 Git Watcher started"

### 7. Test End-to-End

On desktop:

1. Edit a note in Obsidian (e.g., add a line to an existing note)
2. Save it
3. Within 5 seconds, check:
   - Syncthing Web UI: folder should show "Up to Date"
   - Git-watcher logs: should show new commit
   - GitHub: https://github.com/jjurach/connaissance should show new commit

Timeline: ~5s (sync) + ~10s (quiet period) + ~2s (commit/push) = **~20s total**

## Troubleshooting

### Syncthing not syncing

- **Issue:** Devices show "Disconnected" or "Not Connected"
- **Fix:** Check device IDs are exchanged correctly. In Syncthing UI, both devices should show green (Connected).
- **Fix:** Check firewall. Ports 22000/tcp+udp and 21027/udp must be open between desktop and thumper.

### Git-watcher not committing

- **Issue:** File changes sync but git-watcher logs show no activity
- **Fix:** Check git-watcher logs:
  ```bash
  docker compose logs -f git-watcher
  ```
- **Fix:** Verify `.env` has correct `GITHUB_PAT`. Test manually:
  ```bash
  docker compose exec git-watcher git remote -v
  ```

### "Permission denied" errors

- **Issue:** "Permission denied" when accessing `/opt/connaissance`
- **Fix:** Verify ownership:
  ```bash
  ls -ld /opt/connaissance  # Should be phaedrus:phaedrus
  ls -ld ~/.ssh              # Should be readable by root
  ```
- **Fix:** Add docker user to group:
  ```bash
  sudo usermod -a -G phaedrus $USER
  ```

### Push fails with "repository not found"

- **Issue:** Git-watcher logs show "Push failed"
- **Fix:** Verify GitHub PAT is correct and has `repo` scope
- **Fix:** Test manually:
  ```bash
  docker compose exec git-watcher \
    git push origin main
  ```

### Syncthing takes a long time to sync large files

- **Issue:** Files taking > 30 seconds to appear on remote
- **Fix:** Check Syncthing UI under **Stats**. Large files are normal (depends on file size).
- **Fix:** Check network latency between machines:
  ```bash
  ssh thumper "ping -c 3 $(hostname -I | awk '{print $1}')"
  ```

## Stack Files

- `docker-compose.yml` — Service definitions (Syncthing + git-watcher)
- `.env.example` — Template for environment variables
- `git-watcher.sh` — Bash script using inotify to watch vault and auto-commit
- `syncthing-config/` — Syncthing configuration (created on first `docker compose up -d`)

## Maintenance

### GitHub PAT Rotation (Quarterly)

Every 90 days, regenerate your PAT:

1. Go to https://github.com/settings/tokens
2. Find "connaissance-git-watcher" token
3. Click "Regenerate"
4. Copy new token
5. On thumper:
   ```bash
   cd /opt/stacks/connaissance-sync-server
   nano .env  # Update GITHUB_PAT=ghp_...
   docker compose restart git-watcher
   ```

### Logs & Monitoring

```bash
# View Syncthing logs
docker compose logs -f syncthing

# View git-watcher logs
docker compose logs -f git-watcher

# Combined logs
docker compose logs -f

# Check service health
docker compose ps
```

### Reset Syncthing Configuration

If you need to re-pair devices or reset config:

```bash
# Stop services
docker compose down

# Remove old config (WARNING: loses pairing info)
rm -rf syncthing-config/

# Restart
docker compose up -d

# Reconfigure Syncthing from scratch
# Open http://192.168.0.121:8384
```

## Notes

- Git-watcher waits **10 seconds** after each file change before committing (debounce period prevents thrashing)
- Syncthing ignores `.obsidian/workspace*` and `.sync-conflict*` files automatically
- GitHub PAT expires every 90 days (set reminder)
- Syncthing config is persisted in Docker volume `./syncthing-config/` (survives container restarts)
- Git-watcher is stateless; restarting it doesn't lose any data

## Quick Reference

```bash
# Start/stop stack
docker compose up -d
docker compose down

# View logs
docker compose logs -f [syncthing|git-watcher]

# Restart a service
docker compose restart git-watcher

# SSH into git-watcher container (for debugging)
docker compose exec git-watcher sh

# Check git status inside container
docker compose exec git-watcher git status
```
