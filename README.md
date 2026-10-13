# Ps — CLI AI Agent v4.0

> A modular, terminal-based AI agent with a pluggable tool system, multi-model support, MCP integration, and a built-in browser automation engine.

**Creator:** Dark · [t.me/sii_3](https://t.me/sii_3) · [dark.ps](https://dark.ps)

---

## Overview

Ps is a command-line AI agent designed for power users and developers. It runs entirely in your terminal, routes your messages through a configurable AI model, and exposes a rich set of pluggable tools the model can invoke autonomously — from web search and file management to browser automation, code execution in a remote sandbox, and HuggingFace / GitHub integration.

The agent is built around three layers:

| Layer | Purpose |
|---|---|
| `main.py` | Entry point. Renders the logo, runs startup checks, and launches the interactive loop. |
| `core/` | Mode selection, model loading, verification, and startup environment checks. |
| `interpreter/` | Tool registry. Every `.py` file dropped here becomes an auto-discoverable tool the model can call. |

---

## Project Structure

```
agent/
├── main.py                  # Entry point
├── model.py                 # Model list (API + local)
├── identity.md              # Agent persona / system prompt
├── Line.md                  # Font setup instructions
│
├── api/                     # AI provider backends
│   ├── free_ai.py           # free.ai streaming backend
│   └── Cloudflare.py        # Cloudflare AI Playground WebSocket backend
│
├── core/                    # Internal runtime
│   ├── режим.py             # Mode selector (interactive loop)
│   ├── загрузка.py          # Model loader
│   ├── модели.py            # Local model helpers
│   ├── проверка.py          # Environment verification
│   └── verification/
│       └── kimi-token.md    # Kimi token storage
│
├── interpreter/             # ← Tool registry (add your tools here)
│   ├── __init__.py          # Auto-loader and tool dispatcher
│   ├── browser-agent.py     # Playwright browser automation
│   ├── download-web-files.py# File downloader
│   ├── environment.py       # System environment inspector
│   ├── github.py            # GitHub toolkit
│   ├── huggingface.py       # HuggingFace toolkit
│   ├── llm.py               # Kimi LLM file-context tool
│   ├── media.py             # Video inspection (FFmpeg/FFprobe)
│   ├── sandbox.py           # Remote code sandbox (Runlet)
│   ├── search-all-web.py    # Multi-source web search
│   └── upload-files.py      # Anonymous file upload (catbox.moe)
│
├── MCP/
│   └── mcp.json             # MCP server definitions
│
├── Projects/                # Working directory (agent's file workspace)
└── Logos/                   # Branding assets
```

---

## Built-in Tools

### 🔍 Web Search — `search-all-web.py`
Searches the web across multiple sources simultaneously.

| Source | What it returns |
|---|---|
| DuckDuckGo | General web results |
| Wikipedia | Encyclopedia articles |
| GitHub | Repositories |
| YouTube | Video results |
| Bing | Additional web results |

```
# Direct usage
python search-all-web.py "your query" [limit] [debug]
```

---

### 🌐 Browser Automation — `browser-agent.py`
Full headless browser control via Playwright.

| Function | Description |
|---|---|
| `status()` | Check Playwright availability |
| `open_page(url)` | Open a URL in a browser session |
| `inspect_page()` | Get page text, title, images, dimensions |
| `inspect_controls()` | List all interactive elements (buttons, inputs, etc.) |
| `click(selector)` | Click an element |
| `type_text(selector, text)` | Fill a text input |
| `press_key(selector, key)` | Press a keyboard key |
| `scroll(direction, amount)` | Scroll the page |
| `screenshot(path)` | Save a screenshot |
| `record_and_close()` | Save a video recording and close |
| `close()` | Close the current session |

Requires Playwright: `pip install playwright && playwright install chromium`

---

### 💻 Remote Code Sandbox — `sandbox.py`
Executes code in a remote Runlet sandbox. Supports Python, JavaScript, C++, and Java. Safe for running untrusted code without touching the local system.

```
python sandbox.py python 'print("hello")'
```

---

### 🐙 GitHub Toolkit — `github.py`
Interact with GitHub repositories without leaving the terminal.

| Action | Description |
|---|---|
| `search` | Search repositories by keyword |
| `info` | Get repo details (stars, forks, language, README) |
| `file` | Read a specific file from a repo |
| `tree` | Get the full file tree of a repo |
| `issues` | List open/closed issues |

Depth levels: `fast` · `medium` · `deep`

Public repos work without a token. Set `GITHUB_TOKEN` in your environment for private repos.

---

### 🤗 HuggingFace Toolkit — `huggingface.py`
Browse and inspect HuggingFace resources.

| Action | Description |
|---|---|
| `search-models` | Search AI models |
| `search-datasets` | Search datasets |
| `search-spaces` | Search Spaces apps |
| `info` | Get detailed model/dataset/space info |
| `file` | Read a file from a HF repo |

Set `HF_TOKEN` for gated or private resources.

---

### 📁 File Operations — `download-web-files.py` · `upload-files.py`
- **Download:** Fetches any file from a direct URL into the `Projects/` workspace (100 MB limit).
- **Upload:** Anonymously uploads a local file to catbox.moe and returns a public URL.

---

### 🤖 LLM Tool — `llm.py`
Sends a file + prompt to the Kimi model (moonshot.cn) and returns a streaming response. Useful for large-file analysis tasks.

```
python llm.py /path/to/file.py ~ "Summarize this file" ~ "You are a code reviewer" ~ kimi
```

Requires a Kimi refresh token — see `core/verification/kimi-token.md`.

---

### 🖥️ Environment Inspector — `environment.py`
Reports the full system state: OS, installed runtimes (`python`, `node`, `git`, `ffmpeg`, etc.), available browsers, writable paths, and network connectivity.

---

### 🎬 Media Inspector — `media.py`
Inspects video files and extracts frames using FFmpeg/FFprobe.

| Function | Description |
|---|---|
| `ffmpeg_status()` | Check FFmpeg availability |
| `inspect(path)` | Read video metadata and stream info |
| `extract_frame(video, output, timestamp)` | Extract a single frame as an image |

---

## AI Models

### API Models

Configured in `model.py`. Active by default:

| Model | Backend |
|---|---|
| `qwen7b` | `free_ai.py` (free.ai) |
| `glm-4.7-flash` | `Cloudflare.py` |
| `glm-5.2` | `Cloudflare.py` |

Commented out (ready to enable): `gemini-3.5-flash`, `kimi-k3`, `qwen-3.8-max`, `deepseek-v4-flash`, `claude-5.1-fable`, `gpt-5.6-luna`, and more.

Set the active model via environment variable:
```bash
export DarkPs_MODEL=qwen7b
```

### Local Models (GGUF)

The agent supports running models locally via `model.py`. Pre-configured entries:

| Model | Source |
|---|---|
| `iceAI` | `bartowski/darkps_ice-AI-GGUF` |
| `deepseek-v4-flash` | `ivanfioravanti/deepseek-v4-gguf` |
| `qwen3.6-35b` | `mudler/Qwen3.6-35B-A3B-NVFP4-GGUF` |
| `DeepSeek-r1` | `lmstudio-community/DeepSeek-R1-Distill-Qwen-32B-GGUF` |
| `DeepSeek-v3` | `gghfez/DeepSeek-V3-0324-Opus3-Styletune-GGUF` |

---

## MCP Integration

The agent ships with an MCP configuration at `MCP/mcp.json`. The following servers are pre-defined:

| Server | Purpose |
|---|---|
| `memory` | Persistent memory across sessions |
| `filesystem` | File system access |
| `fetch` | HTTP fetching |
| `time` | Current time/date |
| `git` | Git operations |
| `sqlite` | SQLite database access |
| `postgres` | PostgreSQL access |
| `github` | GitHub API |
| `google-drive` | Google Drive |
| `slack` | Slack integration |
| `puppeteer` | Browser automation |
| `brave-search` | Brave Search API |
| `everything` | MCP test server |

Servers requiring API keys (`github`, `brave-search`) have empty `env` entries — fill them in before use.

---

## Font Setup (Recommended)

For the best terminal experience, install JetBrains Mono Nerd Font.

**Termux:**
```bash
pkg install -y curl tar fontconfig-utils && rm -rf ~/fonts && mkdir -p ~/fonts ~/.local/share/fonts ~/.termux && curl -L https://github.com/ryanoasis/nerd-fonts/releases/latest/download/JetBrainsMono.tar.xz -o ~/fonts/font.tar.xz && tar -xJf ~/fonts/font.tar.xz -C ~/fonts && find ~/fonts -type f -name '*.ttf' -exec cp {} ~/.local/share/fonts/ \; && FONT="$(find ~/.local/share/fonts -type f -iname '*JetBrainsMono*NerdFont*Mono*Regular.ttf' | head -n1)" && cp "$FONT" ~/.termux/font.ttf && fc-cache -fv && termux-reload-settings
```

For other terminals, adapt the command to your platform.

---

## Adding a New Tool

Drop a `.py` file into `interpreter/`. The tool loader discovers it automatically — no registration or imports needed.

**Minimal template:**

```python
# interpreter/my-tool.py

# Usage (via TOOL: run_file, or directly):
# python my-tool.py <arg>
# Brief description of what this tool does.

def my_function(arg):
    """Describe what this function does."""
    # your logic here
    return result

if __name__ == '__main__':
    import sys
    print(my_function(sys.argv[1]))
```

**Rules:**
- The file's name becomes the tool name.
- Public functions (no leading `_`) are exposed to the model.
- Add a usage comment at the top — the model reads it to understand how to call the tool.
- The tool is lazy-loaded on first use, so startup time is unaffected.

---

## Adding a New API Model

Open `model.py` and add an entry to the `мс` list:

```python
мс = [
    ('your-model-name', 'your_backend'),   # ← add this line
    ('qwen7b', 'free_ai'),
    ...
]
```

Then create `api/your_backend.py` with a function matching the backend name:

```python
# api/your_backend.py

def your_backend(model, messages):
    """
    model    — model name string
    messages — list of {"role": ..., "content": ...} dicts
    Yield text chunks as they stream in.
    """
    # call your API here
    for chunk in response:
        yield chunk
```

The function must be a generator that yields string chunks. Look at `api/free_ai.py` for a minimal streaming example.

---

## Adding a Local Model

Open `model.py` and call `чит()` (or add directly to the `мо` list):

```python
# In model.py
чит(
    имя='my-model',
    ссылка='org/repo-GGUF',   # HuggingFace repo path
    подсказка='\n\n',
)
```

Or add it directly:

```python
мо.append(Модель(
    имя='my-model',
    ссылка='org/repo-GGUF',
    подсказка='\n\n',
))
```

Remove a local model by name:
```python
чвт('my-model')   # returns True if removed
```

---

## Kimi Token Setup

The `llm.py` tool uses Kimi (moonshot.cn) for large-file analysis tasks. To get a free token:

1. Visit [kimi.com](https://kimi.com) and sign in.
2. Open DevTools → enable mobile/desktop toggle.
3. Open the Console and run:
   ```js
   localStorage.getItem('refresh_token')
   ```
4. Copy the token (starts with `eyJ...`) and paste it into `core/verification/kimi-token.md`, replacing all existing content.

Alternatively, set the `KIMI_Token` environment variable.

---

## Requirements

- Python 3.10+
- `requests` library
- Optional: `playwright` (browser automation)
- Optional: `websocket-client` (Cloudflare backend)
- Optional: `ffmpeg` / `ffprobe` (media inspection)
- Optional: Node.js + `npx` (MCP servers)
- Optional: `uvx` (MCP servers)
