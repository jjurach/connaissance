# Documentation System Workflow

A survey of documentation and knowledge management systems suitable for planning,
execution summarization, multi-device sync, multi-modal input, and agentic workflow
integration — with a focus on free or hobbyist-affordable solutions.

---

## The Core Problem

The goal is a documentation system that:

1. **Syncs across devices** — Linux home box, MacBook (work), mobile phone
2. **Accepts multi-modal input** — keyboard, voice dictation (STT), possibly images
3. **Triggers agentic processing** — a new "inbox" document should notify an AI agent
4. **Runs on local compute** — Linux hardware preferred; AWS acceptable for some parts
5. **Is free or hobbyist-affordable** — no commercial subscriptions unless clearly worth it

The biggest gap across existing tools is the connection between voice dictation and
agentic workflows. Most tools handle one or the other but not both cleanly.

---

## Option A: Obsidian + Plugin Stack

**Best for:** Developers who want local-first Markdown files with a rich plugin ecosystem.

### What Obsidian Is

Obsidian is a desktop/mobile Markdown editor that stores notes as plain `.md` files in
a local "vault" directory. The plugin ecosystem (1,000+ community plugins) provides most
of the functionality described below. The app itself is free; two paid services exist:
Obsidian Sync ($4–16/month) and Obsidian Publish (hosting).

### Sync Across Devices

**Option A1: Obsidian Sync (paid, $4/month standard)**
- Zero-configuration; works on all platforms including iOS
- E2E encrypted (AES-256); version history included
- Students/faculty/nonprofits: 40% discount
- Verdict: Lowest friction, small monthly cost

**Option A2: obsidian-git + GitHub (free)**
- Plugin: `obsidian-git` by Vinzent03
- Auto-commits and auto-pulls on a configurable interval (e.g., every 5 minutes)
- Desktop (Linux/Mac): Full git binary — reliable
- Android: Works via isomorphic-git (JavaScript git implementation built into plugin)
- iOS: Most friction; options:
  - **a-Shell** (free terminal app) + shell script that syncs vault on open/close
  - **Working Copy** (~$20 one-time) — proper iOS git client that mounts vault into Files app
  - **iSH** (free Linux shell emulator) — community-documented approach
- Verdict: Free, works everywhere, iOS requires manual setup

**Option A3: Syncthing (free, peer-to-peer)**
- Files sync directly between devices over LAN or relay; no cloud account needed
- Linux: native daemon; Mac: native app; Android: use F-Droid fork (official removed from Play Store 2024)
- iOS: **Möbius Sync** (free tier 1 GB cap; $10/year unlimited)
- No version history by default (has a file versioning option)
- Verdict: Cleanest free option if you control all devices; Möbius Sync bridging required for iOS

**Option A4: Remotely Save plugin (free, self-hosted)**
- Syncs vault to S3-compatible storage, WebDAV, Dropbox, or OneDrive
- Run MinIO on your Linux box and expose it — fully local hosted sync
- Works across all platforms including mobile
- Verdict: Good for total local control; requires running MinIO

### STT → Obsidian Inbox Pipeline

The recommended pipeline for local, CPU-based Linux processing:

```
Mobile/Mac: Record audio
     ↓
  Syncthing (sync audio file to Linux)
     ↓
Linux box: ~/vault/recordings/
     ↓
  local-whisper-obsidian (systemd service watching recordings/)
     ↓
  faster-whisper (CPU, int8 quantized) transcription
     ↓
  (optional) LLM polish — Ollama/local or Claude API
     ↓
  Write .md to ~/vault/inbox/
     ↓
  inotifywait or systemd path unit detects new .md
     ↓
  Webhook to n8n or direct agent call
```

**Recording tools:**

| Platform | Tool | Notes |
|----------|------|-------|
| Linux | `arecord -d 60 -r 16000 -f S16_LE output.wav` | ALSA, zero deps |
| Linux | `ffmpeg -f alsa -i default -ar 16000 -ac 1 output.wav` | Universal |
| Mac | `ffmpeg -f avfoundation -i ":0" output.wav` | CLI |
| Mac | Voice Memos (built-in) | M4A, free |
| iOS | Voice Memos | M4A, free; Airdrop/Syncthing to Linux |
| Android | Voice Record Pro (free) | WAV, Syncthing to Linux |

**STT processing (all local, no API costs):**

- **faster-whisper** — 4x faster than original Whisper, runs on CPU with int8 quantization.
  `pip install faster-whisper`. Transcribes 1 min audio in ~30–60 sec on modern CPU (small model).
- **whisper.cpp** — C++ implementation, no Python required, runs on Linux/Mac, very fast with AVX2.
- **local-whisper-obsidian** — [github.com/serg-markovich/local-whisper-obsidian](https://github.com/serg-markovich/local-whisper-obsidian)
  A near-complete implementation: systemd service + inotifywait watcher + faster-whisper + YAML frontmatter Markdown output.
  Use `close_write` events (not `create`) to avoid race conditions with Syncthing writes.

**Obsidian STT plugins (in-app dictation):**

- **Whisper Plugin** (nikdanilov/whisper-obsidian-plugin) — most popular; records audio
  within Obsidian, sends to OpenAI Whisper API ($0.006/min) or a local Whisper HTTP server.
  Point at a local `faster-whisper-server` instance for zero API costs.
- **Obsidian Transcription** (djmango) — transcribes audio files linked in notes, supports
  local Whisper ASR server.
- **Voxtral Transcribe** (new, beta as of early 2026) — dictation with voice commands
  for note structure.

**Output format (YAML frontmatter in generated .md):**
```yaml
---
date: 2026-04-12T14:30:00
tags: [voice-note, inbox]
audio: "[[recordings/2026-04-12_voice.m4a]]"
status: unprocessed
---
```

### Triggering Agent Processing

After a note lands in `vault/inbox/`, trigger an agent via:

**Pattern 1: inotifywait (Linux, simplest)**
```bash
inotifywait -m -e close_write --format '%f' ~/vault/inbox/ |
while read filename; do
  curl -X POST http://localhost:5678/webhook/obsidian-inbox \
    -H 'Content-Type: application/json' \
    -d "{\"file\": \"$filename\"}"
done
```
Package: `inotify-tools`. Use `close_write` not `create`. Works as a systemd service.

**Pattern 2: systemd path unit (Linux, production-grade)**
```ini
# /etc/systemd/system/obsidian-inbox.path
[Path]
PathChanged=/home/user/vault/inbox
Unit=obsidian-inbox.service
[Install]
WantedBy=multi-user.target
```
Managed by systemd — logging via journald, auto-restart on failure.

**Pattern 3: n8n Local File Trigger (orchestration layer)**
n8n self-hosted (Docker, free community edition) has a "Local File Trigger" node. When
a new `.md` appears in `vault/inbox/`, trigger a workflow that reads the file, calls
Claude API (native n8n Anthropic node), writes results back to vault, and sends a
Slack/notification. n8n cloud starts at $20/month; self-hosted is free.

**Pattern 4: obsidian-post-webhook plugin (manual trigger)**
Plugin: [obsidian-post-webhook](https://github.com/Masterb1234/obsidian-post-webhook) v1.2.5.
Adds a command palette entry (bindable to hotkey): sends full note content + YAML frontmatter
as JSON POST to any webhook. Good for manually triggering processing of a specific note
rather than auto-processing everything.

**Pattern 5: Watchman (cross-platform, Linux + Mac)**
Facebook's Watchman (`brew install watchman` / `apt install watchman`) is a cross-platform
file watcher daemon with trigger expressions. Runs on both Linux and Mac — useful for
triggering the same agent code from either machine.

### Limitations of Obsidian

- No native REST API or webhooks — everything goes through plugins or filesystem watching
- Mobile plugin support is limited; some desktop plugins don't run on iOS/Android
- Not a team collaboration tool (no real-time co-editing, no comments/reviews)
- For project management (issues, epics, sprints), Obsidian is the wrong tool

---

## Option B: Outline (Self-Hosted Team Wiki)

**Best for:** Team documentation, structured wikis with strong agentic webhook support.

Outline is an open-source team wiki ([getoutline.com](https://www.getoutline.com)).
Self-host via Docker (MIT license). Cloud hosted starts at $10/month for teams.

**Sync:** Web-based; no native mobile app (mobile browser works). Not suitable as a
primary mobile capture tool.

**API:** Full documented REST API at getoutline.com/developers.

**Webhooks:** Native webhook support in admin UI. Events: `documents.create`,
`documents.update`, `collections.create`, etc. POST JSON, signed with HMAC-SHA256,
automatic retry with exponential backoff. This is the **best webhook story** among
self-hosted tools for agentic integration.

**STT/dictation:** No native support — would need a browser extension or companion script.

**Verdict:** Use Outline as the "published" documentation layer for team content, not as
the personal inbox/capture tool. Combine with Obsidian for capture → Outline for
structured docs.

---

## Option C: AppFlowy (Self-Hosted Notion Alternative)

**Best for:** Local-first Notion replacement with a full REST API.

AppFlowy ([appflowy.io](https://appflowy.io)) is open-source (AGPL) and fully
self-hostable via Docker. AppFlowy Cloud (hosted) has a free tier.

**Sync:** Desktop (Linux/Mac/Windows), iOS, Android, web — all platforms covered.

**API:** OpenAPI REST API available for self-hosted instances. Newer and less battle-tested
than Notion's API. Community is actively expanding it.

**Agentic integration:** API exists; ecosystem tooling is smaller than Notion's. You would
build connectors.

**STT:** No native support.

**Verdict:** Best choice if you want Notion-like features without a cloud subscription and
are comfortable self-hosting. The API is the key advantage over Logseq.

---

## Option D: Logseq (Local-First, File-Based)

**Best for:** Personal knowledge management with a graph view; pairs well with the
Obsidian STT pipeline approach.

Logseq stores notes as local Markdown/Org-mode files. The plugin
`logseq-n8n-webhook` can call n8n workflows from within Logseq.

**Sync:** Desktop (Linux/Mac/Windows), iOS, Android. Logseq Sync ($5/month) or
use git/Syncthing.

**Agentic:** File-based means inotifywait works just like with Obsidian. The
forthcoming DB mode may complicate direct file watching.

**Verdict:** Interchangeable with Obsidian for the purposes of this pipeline.
Obsidian has a larger plugin community; Logseq has a stronger graph/backlink model.

---

## Option E: Notion (Cloud, Freemium)

**Best for:** Ecosystem integration; best mobile UX; most agent framework support.

**Free tier:** Unlimited pages and databases; 1000 AI responses/month; no version history.

**API:** Full REST API, good documentation. Most AI agent frameworks have Notion connectors.
No native webhooks — polling or third-party (Zapier/Make.com) required.

**STT:** No native support. Use the pipeline above and write results to Notion via API.

**Cost:** Free tier is viable for solo use. Teams: $10/user/month.

**Verdict:** Best for integrating with external agents that already have Notion connectors.
Not local-first; requires internet connection. Not ideal if local compute is the priority.

---

## Recommended Architecture for Hentown

Given the stated goals (Linux home box as compute, MacBook for work, mobile for capture,
free/affordable, local-first, agentic triggers), this is the recommended baseline:

```
CAPTURE LAYER
├── Mobile: Voice Memos / Voice Record Pro → Syncthing → Linux box
├── Mac: ffmpeg / Voice Memos → Syncthing → Linux box
└── Linux: arecord or ffmpeg → already local

PROCESSING LAYER (Linux home box)
├── local-whisper-obsidian systemd service (inotifywait on recordings/)
├── faster-whisper (CPU, int8, small model)
├── (optional) Ollama + local LLM for text polish
└── Write .md to vault/inbox/ with YAML frontmatter

SYNC LAYER
├── Syncthing: Linux ↔ Mac ↔ Android
└── Möbius Sync ($10/yr) or a-Shell (free): iOS
    Alternative: obsidian-git + GitHub (free, more iOS friction)

TRIGGER LAYER
├── systemd path unit or inotifywait watching vault/inbox/
└── Webhook → n8n (self-hosted, free) → Claude API → write result back to vault

DOCUMENTATION LAYER
└── Obsidian (free app, vault = plain Markdown files)
    Plugins: obsidian-git, Whisper plugin (pointed at local server), post-webhook
```

**Total recurring cost (baseline):** $0 (if git sync) or $10/year (Möbius Sync for iOS).

**Total recurring cost (with Obsidian Sync):** $4/month ($48/year) — eliminates all sync
complexity across all platforms.

---

## Where Current Solutions Fall Short

| Goal | Gap |
|------|-----|
| One-tap mobile dictation → agent processed | Requires multi-step: record → sync → process → notify. No turnkey solution. |
| STT quality on CPU | faster-whisper `small` model is good but not perfect; `medium` is slow on CPU |
| iOS git sync | All free iOS git options require manual setup; Working Copy ($20) is the smooth path |
| In-Obsidian dictation on mobile | Whisper plugin has limited mobile support; Voxtral is beta |
| Agent writes back to inbox | Easy with file writes; Obsidian picks them up automatically |
| Team collaboration in Obsidian | Obsidian is not a team tool; Outline fills this gap |

---

## Expectations to Level-Set

- **Perfect mobile STT pipeline is not one tool** — it is a combination of: recording app
  + sync daemon + Linux processing service. This is a 2–4 component setup, not a single app.
- **Obsidian is not Jira/Linear** — it has no issue tracker, sprint planner, or assignee
  fields out of the box. Dataview plugin can simulate some of this but it is not a PM tool.
- **Local LLM polish is slower** — a local Ollama model will take 15–30 seconds to polish
  a transcription; Claude API takes ~2 seconds but costs a fraction of a cent per note.
- **n8n is powerful but complex** — it is a full workflow automation platform; start with
  a simple inotifywait + curl webhook before adding n8n.

---

## Hentown's Role

Hentown already contains building blocks (voice processing via `second_voice`, AI provider
integration via `mellona`, agent orchestration via `hatchery`). The opportunity is to build
a thin glue layer that:

1. Wraps `faster-whisper` or `local-whisper-obsidian` with a config-driven systemd service
2. Adds an LLM polish step via `mellona`
3. Emits a webhook or drops a message into an agent queue after inbox write
4. Provides Obsidian plugin compatibility (YAML frontmatter, wikilink audio reference)

This keeps hentown as a small plugin to featureful systems (Obsidian, n8n, Syncthing)
rather than reimplementing them.

---

## References

- [Obsidian Pricing](https://obsidian.md/pricing)
- [obsidian-git plugin](https://github.com/Vinzent03/obsidian-git)
- [iOS free git sync via a-Shell (Obsidian Forum)](https://forum.obsidian.md/t/mobile-automatic-sync-with-github-on-ios-for-free-via-a-shell/46150)
- [Syncthing + Möbius Sync (Obsidian Forum)](https://forum.obsidian.md/t/sync-mac-pc-and-ios-using-syncthing-mobius-sync/72022)
- [local-whisper-obsidian pipeline](https://github.com/serg-markovich/local-whisper-obsidian)
- [faster-whisper (SYSTRAN)](https://github.com/SYSTRAN/faster-whisper)
- [Whisper Obsidian Plugin](https://github.com/nikdanilov/whisper-obsidian-plugin)
- [obsidian-post-webhook plugin](https://github.com/Masterb1234/obsidian-post-webhook)
- [Outline REST API + Webhooks](https://docs.getoutline.com/s/guide/doc/webhooks-gB7HYhS6yq)
- [AppFlowy REST API](https://github.com/AppFlowy-IO/documentations/blob/main/documentation/appflowy-cloud/openapi/README.md)
- [Watchman file watcher](https://facebook.github.io/watchman/)
- [n8n self-hosted](https://n8n.io/self-hosted/)
