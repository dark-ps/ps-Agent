# ps-Agent WebUI

A premium black-and-white browser UI wired to the *real* ps-Agent internals — no mock mode,
no extra framework. One HTML file, one Python bridge.

## Run

```bash
# from the repo root (ps-Agent/)
python webui/bridge.py
# or windowless on Windows:
pythonw webui/bridge.py
```

Open **http://127.0.0.1:7861** in a browser.

Custom port: set `PS_UI_PORT` before starting (`PS_UI_PORT=9000 python webui/bridge.py`).

## What it does

- **Streaming chat** over SSE (`GET/POST /api/chat`) driven by the agent's real model
  backends (`scripts/wtf.py` → `api/free_ai.py` / `api/Cloudflare.py`).
- **Real tool execution** through `ps/dark.py` (`ви`), including the 65+ MCP tools from the
  agent's MCP manager. Tool cards show arguments and truncated results inline.
- **Dangerous-tool approval gate** — the agent's own `опасные_инстр` set (shell, install,
  delete, cleanup …) triggers a confirmation card; nothing runs until you allow it.
- **Ask gates** — when the model asks a question (`ASK:`), you reply inline and the turn
  continues.
- **Model switching** via the sidebar (`/api/models`, `POST /api/model`) — `qwen7b`
  (free.ai), `glm-4.7-flash`, `glm-5.2` (Cloudflare). The default is the project's own
  (`model.py` → `wtf.тм()`); a model you pick is remembered across restarts in
  `webui/.model.json`.
- **Realtime thinking stream** — the agent's `THINK:` reasoning streams token-by-token
  into a collapsible *Thinking* block (auto-collapses when the answer starts, reopens if
  the model reasons again after a tool run).
- **Sessions** — persisted to `webui/sessions/<sid>.json`; list, resume, rename, delete
  plus a per-session system prompt reseed are handled by `/api/session/*` and
  `/api/history`.
- **MCP / Skills management** — the sidebar exposes the live MCP server list (running /
  down, tool counts) with hot add/remove (rewrites `MCP/mcp.json` and reloads), and the
  skills registry with hot add (`~/.darkps/skills/`).
- **Terminal-grade UX** — OpenCode-flavored dark console: monospace everything, TUI-style
  steps and statusline, thin 1px borders, the pinwheel ps mark as an animated SVG (draws
  in on load, spins while the agent works, pulses green on success / shakes red on failure).
- **Restricted accent colors** — black/white primaries only; green (`--ok`) and red
  (`--bad`) appear strictly for success/failure semantics (tool states, errors, gate
  results).
- **Light/dark theme** — dark is the default (OpenCode style); toggle in the header,
  persisted in `localStorage`.

## Architecture

```
browser (webui/index.html)
   │  fetch (SSE)
   ▼
webui/bridge.py          ── stdlib-only HTTP/SSE bridge (port 7861)
   │  imports
   ▼
scripts/wtf.py           ── streaming driver (по)
ps/dark.py               ── tool executor (ви), dangerous set, memory, MCP
interpreter/, services/  ── local tool + service registries
```

The bridge keeps per-session message history in memory (sessions are name-based, keyed by
the browser client). The system prompt is seeded from `identity.md` plus a live tool
catalog; workspace is `Projects/`.

## HTTP API

| Endpoint           | Method | Notes                                            |
|--------------------|--------|--------------------------------------------------|
| `/`                | GET    | serves `webui/index.html`                        |
| `/api/health`      | GET    | agent load status, current model, tool counts    |
| `/api/models`      | GET    | available models + current                       |
| `/api/model`       | POST   | `{"name": "glm-4.7-flash"}` — switch model       |
| `/api/tools`       | GET    | local tool registry summary                      |
| `/api/chat`        | POST   | `{"session": "...", "message": "..."}` — SSE     |
| `/api/answer`      | POST   | reply to an approval/ask gate `{"ask_id", ...}`  |
| `/api/stop`        | POST   | stop the running turn                            |
| `/api/new`         | POST   | reset a session                                  |
| `/api/sessions`    | GET    | persisted session list (title, timestamps)       |
| `/api/history`     | GET    | `?session=<sid>` — message history               |
| `/api/session/create` | POST | new session (empty, not persisted until used)   |
| `/api/session/delete` | POST | `{"session": ...}` — 409 if running             |
| `/api/session/rename` | POST | `{"session", "title"}`                          |
| `/api/mcp`         | GET    | MCP server inventory (running, tool counts)      |
| `/api/mcp/add`     | POST   | hot-add an MCP server + reload                   |
| `/api/mcp/remove`  | POST   | hot-remove an MCP server + reload                |
| `/api/skills`      | GET    | skills registry                                  |
| `/api/skills/add`  | POST   | add a skill to `~/.darkps/skills/` + rescan      |
| `/api/diag_cf`     | GET    | dev: direct Cloudflare backend check             |
| `/api/diag_po`     | GET/POST| dev: check the `по`/`з` streaming layer          |

## Notes

- Python 3.10+ recommended. Only stdlib + the agent's own dependencies are needed.
- Console output is reconfigured to UTF-8 internally (Windows code pages choke on the
  agent's Cyrillic text).
- If a previous instance still holds the port: find it with
  `Get-NetTCPConnection -LocalPort 7861` → `Stop-Process -Id <pid>`.
- Cloudflare Playground backends occasionally reject a new session with
  `Connection timed out` (per-IP session limits); the bridge retries once automatically
  with a delay and surfaces the failure in-chat if it persists.
- The repo's original sources are untouched by the WebUI; the bridge only reads and
  calls them (`webui/` additions are standalone).
