# Ps WebUI bridge — wires the real ps-Agent internals to a local browser UI.
# Run from the repo root:   python webui/bridge.py
# UI lives at http://127.0.0.1:7861  — chat via SSE, real tool execution,
# confirmation prompts for dangerous tools, model switching.
#
# Silent console: python -X utf8 webui/bridge.py  (or pythonw)

import json
import os
import queue
import re
import sys
import threading
import time
import urllib.parse
import uuid

# Windows console (cp1252/cp1256 etc.) must not kill the process on Cyrillic text
for _stream in (sys.stdout, sys.stderr):
    if _stream and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT / "Projects"
WORKSPACE.mkdir(parents=True, exist_ok=True)
PORT = int(os.getenv("PS_UI_PORT", "7861"))

os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

# ------------------------------------------------------------------ agent boot
AGENT_OK = False
AGENT_ERR = ""
try:
    # NOTE: `import ps.dark as dark` would bind the *branding string* here, because
    # ps/__init__.py star-imports dark.py, whose global `dark = 't.me/sii_3'` shadows
    # the submodule attribute. Resolve the real module via sys.modules instead.
    import ps.dark  # noqa: F402  (registration only)
    dark = sys.modules["ps.dark"]  # tool executor, shortcut normalizer, memory, MCP
    import scripts.wtf as wtf  # model list + streaming driver
    import interpreter  # tool registry
    import services  # service tools
    import requests  # noqa: F401  (agent expects it)

    interpreter._set_workspace(WORKSPACE)

    _IDENTITY = (ROOT / "identity.md").read_text(encoding="utf-8", errors="replace").strip()
    MEMORY = dark.Вп()
    MCP = dark.McpMgr()
    SKILLS = dark.НвкРег()
    PF = dark.Пф(WORKSPACE)
    SEARCH = dark.Поиск()
    wtf.подготовить_онлайн()
    os.environ.setdefault("DarkPs_MODE", "online")
    # Model selection follows the project's own default (model.py `м` via wtf.тм());
    # the bridge only tracks the live value and exposes /api/model to switch it.
    AGENT_OK = True
except Exception as e:
    import traceback

    AGENT_ERR = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
    try:
        (ROOT / "webui" / "agent.log").write_text(AGENT_ERR, encoding="utf-8")
    except Exception:
        pass


def _tool_catalog_text():
    lines = []
    try:
        for inj in interpreter.список_инструментов():
            module = inj["module"]
            sigs = ",".join(
                module + "." + s
                for s in (inj.get("signatures") or [f["name"] for f in inj.get("functions", [])])
            )
            doc = (inj.get("doc") or "")[:80]
            prev = (inj.get("preview") or "")[:180].replace("\n", " ⏎ ")
            path = inj.get("path", "")
            run = (inj.get("run_command") or "")[:140]
            lines.append(
                f"  {module}: {sigs}"
                + (f" — {doc}" if doc else "")
                + (f" | path={path}" if path else "")
                + (f" | run={run}" if run else "")
                + (f" | preview={prev}" if prev else "")
            )
        for inj in services.список_сервисов():
            module = inj["module"]
            sigs = ",".join(inj.get("signatures") or inj.get("functions", []))
            doc = (inj.get("doc") or "")[:80]
            prev = (inj.get("preview") or "")[:220].replace("\n", " ⏎ ")
            lines.append(
                f"  [svc]{module}: {sigs}"
                + (f" — {doc}" if doc else "")
                + (f" | preview={prev}" if prev else "")
            )
    except Exception:
        pass
    return "\n".join(lines) if lines else "  (tool discovery failed)"


def _mcp_text():
    try:
        tools = MCP.список()
        return "\n".join(f"  MCP:{t['name']}: {t.get('description', '')[:80]}" for t in tools)
    except Exception:
        return ""


def _system_prompt():
    text = _IDENTITY
    text += "\n\n=== WORKSPACE ===\n"
    text += f"Working directory: {WORKSPACE}\n"
    text += "=== AVAILABLE TOOLS ===\n" + _tool_catalog_text()
    mcp = _mcp_text()
    if mcp:
        text += "\n=== MCP TOOLS ===\n" + mcp
    text += (
        "\n\nTOOL EXECUTION: Use TOOL: followed by a valid JSON object, for example"
        ' {"tool":"browser-agent.status","arguments":{}}. Call browser-agent.open_page and'
        " browser-agent.screenshot as functions in this process to preserve the browser"
        f" session. Tool source directory: {ROOT / 'interpreter'}. Shell cwd: {WORKSPACE}."
        " Relative interpreter/ paths are not relative to the shell cwd; use the absolute"
        " source directory to inspect tool files. Call listed functions directly using full"
        " module.function names and exact keyword parameters. Do not use run_file to invoke a"
        " function; run_file is for standalone CLI scripts. Emit exactly one TOOL call per"
        " response. Wait for TOOL RESULT before the next step. Use FINAL: for the completed"
        " answer in the user's language. THINK: for visible reasoning. CONTINUE: for progress."
    )
    return text


# ----------------------------------------------------------------- marker parse
_MARKERS = ("FINAL:", "THINK:", "TOOL:", "CONTINUE:", "ASK:", "PROGRESS:")
_HOLD = 12  # chars held back while a partial marker may be arriving
_KINDS = {
    "FINAL:": "final",
    "THINK:": "think",
    "CONTINUE:": "continue",
    "PROGRESS:": "progress",
    "ASK:": "ask",
    "TOOL:": "tool",
}


def _find_json_span(buf, start):
    """buf[start] is '{' -> index just past the matching '}', else None."""
    depth = 0
    instr = False
    esc = False
    for i in range(start, len(buf)):
        ch = buf[i]
        if esc:
            esc = False
            continue
        if instr:
            if ch == "\\":
                esc = True
            elif ch == '"':
                instr = False
            continue
        if ch == '"':
            instr = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i + 1
    return None


def _parse_turn(text):
    """Full parse of one model response: first tool call, final, think, ask, continue."""
    out = {"tool": None, "final": "", "think": "", "continue": "",
           "ask": "", "progress": "", "plain": "", "detail": ""}
    parts = []  # (kind, text)
    pos = 0
    n = len(text)
    kind = "raw"
    while True:
        nxt, found = n, None
        for m in _MARKERS:
            j = text.find(m, pos)
            if j != -1 and j < nxt:
                nxt, found = j, m
        seg = text[pos:nxt]
        if seg:
            parts.append((kind, seg))
        if found is None:
            break
        pos = nxt + len(found)
        kind = _KINDS[found]
        if kind == "tool":
            # try to consume a JSON object immediately after the TOOL: marker
            j3 = pos
            while j3 < n and text[j3].isspace():
                j3 += 1
            if j3 < n and text[j3] == "{":
                end = _find_json_span(text, j3)
                if end is not None:
                    try:
                        obj = json.loads(text[j3:end])
                    except Exception:
                        obj = None
                    if isinstance(obj, dict):
                        if not out["tool"]:
                            out["tool"] = obj
                        pos = end
                        kind = "detail"  # prose after the JSON object

    for k, seg in parts:
        seg = seg.strip()
        if not seg:
            continue
        if k == "final":
            out["final"] += ("\n" if out["final"] else "") + seg
        elif k == "think":
            out["think"] += ("\n" if out["think"] else "") + seg
        elif k == "continue":
            out["continue"] += ("\n" if out["continue"] else "") + seg
        elif k == "progress":
            out["progress"] += ("\n" if out["progress"] else "") + seg
        elif k == "ask":
            out["ask"] += ("\n" if out["ask"] else "") + seg
        elif k == "detail":
            out["detail"] += ("\n" if out["detail"] else "") + seg
        else:
            out["plain"] += ("\n" if out["plain"] else "") + seg
    return out


class StreamClassifier:
    """Incremental marker classifier: turn chunks into typed deltas."""

    def __init__(self, emit):
        self.emit = emit  # callable(dict) -> None
        self.buf = ""
        self.pos = 0
        self.kind = "raw"
        self.tool_done = False
        self.saw_final = False  # FINAL: segment already streamed as deltas

    def feed(self, chunk):
        self.buf += chunk
        self._flush(False)

    def finish(self):
        self._flush(True)

    def _next_marker(self, from_pos):
        best = None  # (j, marker); search the full buffer so completed markers are found
        for m in _MARKERS:
            j = self.buf.find(m, from_pos)
            if j != -1 and (best is None or j < best[0]):
                best = (j, m)
        return best

    def _flush(self, final):
        limit = len(self.buf) if final else len(self.buf) - _HOLD
        while True:
            hit = self._next_marker(self.pos)
            if hit is None:
                break
            j, m = hit
            self._seg(self.kind, self.buf[self.pos:j])
            self.pos = j + len(m)
            self.kind = _KINDS[m]
            if self.kind == "tool":
                self._try_tool(final)
                if self.kind == "tool" and not final:
                    return  # JSON still streaming in; hold everything back
        if self.kind == "tool":
            # no new marker since the TOOL: one — the JSON may have just completed
            self._try_tool(final)
        if self.kind == "tool":
            return  # never surface partial JSON as text
        tail = self.buf[self.pos:limit] if limit > self.pos else ""
        if tail:
            self.pos += len(tail)
            self._seg(self.kind, tail)

    def _try_tool(self, final):
        if self.tool_done:
            self.kind = "detail"
            return
        i = self.pos
        n = len(self.buf)
        while i < n and self.buf[i].isspace():
            i += 1
        if i < n and self.buf[i] == "{":
            end = _find_json_span(self.buf, i)
            if end is not None:
                try:
                    obj = json.loads(self.buf[i:end])
                except Exception:
                    obj = None
                if isinstance(obj, dict) and any(k in obj for k in ("tool", "action", "name")):
                    name = str(obj.get("tool") or obj.get("action") or obj.get("name") or "").strip()
                    args = obj.get("arguments") or obj.get("args") or obj.get("params") or {}
                    if not isinstance(args, dict):
                        args = {}
                    self.emit(
                        {
                            "type": "tool_call",
                            "name": name,
                            "args": args,
                            "danger": name.lower() in getattr(dark, "опасные_инстр", set()),
                        }
                    )
                    self.tool_done = True
                    self.pos = end
                    self.kind = "detail"
                    return
        # incomplete JSON: stay in 'tool' until more text arrives (or final flush)

    def _seg(self, kind, text):
        if not text or not text.strip():
            return
        if kind == "tool":
            return  # JSON payload arrives as a tool_call event, not text
        if kind == "detail":
            self.emit({"type": "detail", "text": text.strip()})
            return
        if kind == "final":
            self.saw_final = True
        self.emit({"type": "delta", "kind": kind, "text": text})


# ------------------------------------------------------------------- sessions
_SESSIONS = {}  # sid -> {"смс": [...], "busy": bool, "stop": Event, "meta": {...}}
_ANSWERS = {}  # ask_id -> queue.Queue
_META = {}     # sid -> {"created", "updated", "title"}
SESSDIR = ROOT / "webui" / "sessions"
SESSDIR.mkdir(parents=True, exist_ok=True)


def _now_ms():
    return int(time.time() * 1000)


def _new_state():
    return {"смс": ([{"role": "system", "content": _system_prompt()}] if AGENT_OK else []),
            "busy": False, "stop": threading.Event()}


def _session(sid):
    st = _SESSIONS.get(sid)
    if st is None:
        st = _new_state()
        _SESSIONS[sid] = st
        _load_session(sid, st)
    if sid not in _META:
        _META[sid] = {"created": _now_ms(), "updated": _now_ms(), "title": "(new)"}
    return st


def _fresh_session(sid, title=""):
    _SESSIONS[sid] = _new_state()
    _META[sid] = {"created": _now_ms(), "updated": _now_ms(), "title": title or "(new)"}
    _persist(sid)
    return _SESSIONS[sid]


def _sessfile(sid):
    return SESSDIR / ("".join(c for c in sid if c.isalnum() or c in "-_")[:64] + ".json")


def _persist(sid):
    """Save session to disk so it can be resumed across bridge restarts.
    Empty new sessions are not written — they materialize on first message."""
    st = _SESSIONS.get(sid)
    if not st or not AGENT_OK:
        return False
    try:
        if len(st["смс"]) < 2 and _META.get(sid, {}).get("title", "(new)") in ("(new)", ""):
            return False
        meta = _META.setdefault(sid, {"created": _now_ms(), "updated": _now_ms(), "title": "(new)"})
        meta["updated"] = _now_ms()
        meta["title"] = meta["title"] if meta.get("title") not in (None, "") else _first_title(st["смс"])
        data = {"session": sid, **meta, "msgs": st["смс"]}
        _sessfile(sid).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception:
        return False


def _first_title(msgs):
    for m in msgs:
        if m.get("role") == "user":
            return (m.get("content") or "")[:60] or "(new)"
    return "(new)"


def _load_session(sid, st):
    """Load a previously persisted session and merge into memory."""
    try:
        f = _sessfile(sid)
        if not f.is_file():
            return
        data = json.loads(f.read_text(encoding="utf-8"))
        _META[sid] = {"created": data.get("created"), "updated": data.get("updated"),
                      "title": data.get("title") or "(new)"}
        msgs = data.get("msgs") or []
        if AGENT_OK:
            rest = [m for i, m in enumerate(msgs) if not (i == 0 and m.get("role") == "system")]
            st["смс"] = [{"role": "system", "content": _system_prompt()}] + rest
    except Exception:
        pass


def _sessions_list():
    """List known sessions from disk and memory (empty untitled ones skipped)."""
    out = {}
    try:
        for f in SESSDIR.glob("*.json"):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                count = len(d.get("msgs") or [])
                title = d.get("title") or "(new)"
                if title in ("(new)", "") and count <= 1:
                    continue  # never used — don't clutter the list
                out[d.get("session") or f.stem] = {
                    "session": d.get("session") or f.stem,
                    "title": title,
                    "created": d.get("created"), "updated": d.get("updated"),
                    "count": count,
                }
            except Exception:
                pass
    except Exception:
        pass
    for sid in list(_SESSIONS.keys()):
        st = _SESSIONS[sid]
        meta_t = _META.get(sid, {}).get("title") or "(new)"
        if meta_t in ("(new)", "") and len(st["смс"]) <= 1:
            continue
        if sid in out:
            out[sid]["count"] = max(out[sid]["count"], len(st["смс"]))
    return sorted(out.values(), key=lambda x: (x.get("updated") or 0), reverse=True)


def _delete_session(sid):
    try:
        _sessfile(sid).unlink(missing_ok=True)
    except Exception:
        pass
    _SESSIONS.pop(sid, None)
    _META.pop(sid, None)
    return True


def _mcp_reload():
    """Recreate the MCP manager from mcp.json (hot add/remove)."""
    global MCP
    old = globals().get("MCP")
    mm = dark.McpMgr()
    MCP = mm
    if old is not None:
        try:
            old.стоп_все()
        except Exception:
            pass
    return True


def _mcp_config_path():
    p = ROOT / "MCP" / "mcp.json"
    if p.is_file():
        return p
    return Path.home() / ".darkps" / "mcp.json"


def _mcp_info():
    """Current servers, their tools, and config path — for the MCP panel."""
    servers = {}
    try:
        cfg = json.loads(_mcp_config_path().read_text(encoding="utf-8"))
        for name, serv in (cfg.get("servers") or {}).items():
            servers[name] = {
                "type": serv.get("type", "stdio"),
                "command": serv.get("command", ""),
                "args": serv.get("args", []),
                "url": serv.get("url", ""),
            }
    except Exception:
        pass
    live = {}
    for t in (MCP.список() if (AGENT_OK and MCP) else []):
        srv = t.get("_mcp_server", "?")
        live.setdefault(srv, []).append(t.get("name", "?"))
    for name, serv in servers.items():
        serv["running"] = name in live
        serv["tools"] = sorted(live.get(name, []))
    err = getattr(MCP, "_ошибка", "") if MCP else ""
    return {"ok": True, "config": str(_mcp_config_path()), "servers": servers,
            "error": err or ""}


def _mcp_add(data):
    """Write a server entry to mcp.json and hot-reload the MCP manager."""
    name = str(data.get("name") or "").strip()
    typ = str(data.get("type") or "stdio").strip()
    if not re.fullmatch(r"[A-Za-z0-9_\-\.]{1,40}", name):
        return {"ok": False, "error": "invalid server name"}
    p = _mcp_config_path()
    cfg = {"servers": {}}
    try:
        cfg = json.loads(p.read_text(encoding="utf-8"))
        cfg.setdefault("servers", {})
    except Exception:
        cfg = {"servers": {}}
    if typ == "sse":
        url = str(data.get("url") or "").strip()
        if not url.startswith(("http://", "https://")):
            return {"ok": False, "error": "invalid url"}
        entry = {"type": "sse", "url": url}
    else:
        command = str(data.get("command") or "").strip()
        if not command:
            return {"ok": False, "error": "command required"}
        args = data.get("args")
        if isinstance(args, str):
            args = args.split()
        if not isinstance(args, list):
            args = [a for a in (args or []) if a]
        entry = {"type": "stdio", "command": command, "args": [str(a) for a in args]}
        env = data.get("env")
        if isinstance(env, dict) and env:
            entry["env"] = {str(k): str(v) for k, v in env.items() if str(k).strip()}
    p.parent.mkdir(parents=True, exist_ok=True)
    cfg["servers"][name] = entry
    try:
        p.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        return {"ok": False, "error": f"could not write config: {e}"}
    _mcp_reload()
    err = getattr(MCP, "_ошибка", "")
    info = _mcp_info()
    alive = next((s for s in info.get("servers", {}).values() if s.get("running")), None)
    return {"ok": True, "mcp": info, "error": err or "",
            "note": "" if err == "" else f"reload produced errors: {err}",
            "added": name, "running_count": len(info.get("servers", {})) and alive is not None}


def _mcp_remove(name):
    name = str(name or "").strip()
    p = _mcp_config_path()
    try:
        cfg = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return {"ok": False, "error": f"could not read config: {e}"}
    if name not in (cfg.get("servers") or {}):
        return {"ok": False, "error": "no such server in config"}
    del cfg["servers"][name]
    try:
        p.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        return {"ok": False, "error": f"could not write config: {e}"}
    _mcp_reload()
    return {"ok": True, "mcp": _mcp_info()}


def _skills_dir():
    d = Path.home() / ".darkps" / "skills"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _skills_info():
    """Built-in + file skills, from the agent's own registry."""
    out = []
    try:
        for sk in SKILLS.список():
            params = getattr(sk, "прм", None) or []
            if not isinstance(params, list):
                params = []
            out.append({
                "name": getattr(sk, "им", "?"),
                "description": getattr(sk, "оп", "") or "",
                "parameters": [p.get("им", p.get("name", "?")) if isinstance(p, dict)
                               else str(p) for p in params],
            })
    except Exception as e:
        return {"ok": False, "error": str(e), "skills": []}
    return {"ok": True, "skills": out, "dir": str(_skills_dir())}


def _skill_add(data):
    """Register a new skill: a JSON file under ~/.darkps/skills + hot re-scan."""
    name = str(data.get("name") or "").strip()
    command = str(data.get("command") or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_\-]{1,40}", name):
        return {"ok": False, "error": "invalid skill name (A-Z a-z 0-9 _ -)"}
    if not command:
        return {"ok": False, "error": "command required, e.g. python script.py {запрос}"}
    params = data.get("parameters") or []
    if isinstance(params, str):
        params = [s.strip() for s in params.split(",") if s.strip()]
    skill = {"name": name, "command": command}
    desc = str(data.get("description") or "").strip()
    if desc:
        skill["description"] = desc
    plist = []
    for p in params:
        if isinstance(p, dict):
            p = str(p.get("name") or "").strip()
        p = str(p).strip()
        if p:
            plist.append({"name": p, "type": "str", "description": ""})
    if plist:
        skill["parameters"] = plist
    f = _skills_dir() / f"{name}.json"
    try:
        f.write_text(json.dumps(skill, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        return {"ok": False, "error": f"could not write skill file: {e}"}
    try:
        SKILLS._згрн()  # hot re-scan the skills folder
    except Exception as e:
        return {"ok": False, "error": f"registry re-scan failed: {e}"}
    return {"ok": True, **_skills_info()}


def _models():
    return {"models": wtf._н(wtf._сл()), "current": _CURRENT["model"]}


# The default follows model.py (`м` via wtf.тм()); a model picked in the UI is
# remembered across restarts in webui/.model.json and validated against the
# registry on boot (missing/invalid file -> plain project default).
_MODEL_FILE = ROOT / "webui" / ".model.json"


def _saved_model():
    try:
        v = json.loads(_MODEL_FILE.read_text(encoding="utf-8")).get("name")
        return str(v) if v else ""
    except Exception:
        return ""


def _remember_model(name):
    try:
        if name:
            _MODEL_FILE.write_text(json.dumps({"name": name}), encoding="utf-8")
        else:
            _MODEL_FILE.unlink(missing_ok=True)
    except Exception:
        pass


_sa = ""
_CURRENT = {"model": ""}
if AGENT_OK:
    try:
        _ok_names = {m["name"] for m in wtf._н(wtf._сл())}
        _sa = _saved_model()
        _CURRENT = {"model": _sa if _sa in _ok_names else wtf.тм()}
    except Exception:
        _CURRENT = {"model": wtf.тм()}


def _select_model(name):
    for m in wtf._н(wtf._сл()):
        if name in (m["name"], m["id"], m["label"]):
            _CURRENT["model"] = m["name"]
            os.environ["DarkPs_MODEL"] = m["name"]
            _remember_model(m["name"])
            return {"ok": True, **_models()}
    return {"ok": False, "error": "unknown model", **_models()}


def _sname(x):
    return x if isinstance(x, str) else str(x)


def _to_text(x):
    if isinstance(x, str):
        return x
    try:
        if isinstance(x, dict) and x.get("ok") is False and x.get("error"):
            return "✘ " + str(x["error"])
        return str(x)
    except Exception:
        return "<unprintable>"


def _trim(смс):
    try:
        from ps.dark import _trim_messages

        смс[:] = _trim_messages(смс)
    except Exception:
        try:
            total = sum(len(str(m.get("content", ""))) for m in смс)
            if total > 200_000:
                смс[:] = смс[-12:]
        except Exception:
            pass


# --------------------------------------------------------------------- the loop
MAX_ITERS = 25


def run_chat(sid, user_text, emit, stop):
    st = _SESSIONS[sid]
    st["busy"] = True
    try:
        _run_turn(sid, user_text, emit, stop)
    finally:
        st["busy"] = False
        # auto-title from the first exchange, then persist for resume
        if _META.get(sid, {}).get("title") in (None, "", "(new)"):
            _META[sid]["title"] = (user_text or "")[:60] or "(new)"
        _persist(sid)


def _run_turn(sid, user_text, emit, stop):
    st = _SESSIONS[sid]
    смс = st["смс"]
    смс.append({"role": "user", "content": user_text})
    try:
        MEMORY.чс("user", user_text, str(WORKSPACE))
    except Exception:
        pass

    nudges = 0
    same_tool = 0
    prev_tool = None

    for _it in range(MAX_ITERS):
        if stop.is_set():
            emit({"type": "stopped"})
            return
        emit({"type": "iter", "n": _it + 1})

        client = StreamClassifier(emit)
        raw = ""
        try:
            for chunk in wtf.по(None, "", _CURRENT["model"], смс):
                raw += chunk
                client.feed(chunk)
        except wtf.ApiServiceError as e:
            if stop.is_set():
                emit({"type": "stopped"})
                return
            backend_fail = getattr(e, "retry_after", None)
            wait = max(5, int(e.retry_after)) if backend_fail else 20
            attempts = getattr(emit, "backend_attempts", 0) + 1
            emit.backend_attempts = attempts
            if attempts >= 3:
                emit({"type": "error",
                      "text": f"Model backend unreachable after {attempts} attempts: {e}\n"
                              "Try a different model in the sidebar (e.g. qwen7b), then resend."})
                return
            emit({"type": "status", "text": f"Model backend hiccup ({e}); retrying in {wait}s…"})
            for _ in range(wait):
                if stop.is_set():
                    emit({"type": "stopped"})
                    return
                time.sleep(1)
            continue
        except Exception as e:
            emit({"type": "error", "text": f"Model backend: {type(e).__name__}: {e}"})
            return
        client.finish()
        if stop.is_set():
            emit({"type": "stopped"})
            return
        _log(f"iter={_it + 1} raw={raw[:600]!r}")
        if not raw.strip():
            emit({"type": "error", "text": "Empty model response."})
            return

        p = _parse_turn(raw)
        try:
            MEMORY.чс("assistant", raw[:2000], str(WORKSPACE))
        except Exception:
            pass

        if p["tool"]:
            нг = {"tool": str(p["tool"].get("tool") or p["tool"].get("action") or p["tool"].get("name") or ""),
                  "arguments": p["tool"].get("arguments") or p["tool"].get("args") or p["tool"].get("params") or {}}
            try:
                инс = dark.ии(нг, SEARCH)
            except Exception:
                инс = нг["tool"]
            if not isinstance(нг["arguments"], dict):
                try:
                    нг["arguments"] = json.loads(str(нг["arguments"]))
                except Exception:
                    нг["arguments"] = {}

            approved = True
            if инс in dark.опасные_инстр:
                try:
                    desc = dark._опасн_описание(инс, нг["arguments"])
                except Exception:
                    desc = f"Run: {инс}"
                aid = uuid.uuid4().hex[:10]
                q = queue.Queue(maxsize=1)
                _ANSWERS[aid] = q
                emit({"type": "confirm_wait", "ask_id": aid, "tool": инс,
                      "name": нг["tool"], "description": desc})
                try:
                    ans = q.get(timeout=600)
                except queue.Empty:
                    ans = {"ok": False}
                _ANSWERS.pop(aid, None)
                approved = bool(ans.get("ok"))

            агент_ = ""
            if not approved:
                инс_им, рзт = инс, "User declined this action. Do not retry it; ask for an alternative approach or continue with FINAL:."
                emit({"type": "tool_result", "name": _sname(инс_им), "ok": False, "brief": "declined"})
            else:
                try:
                    инс_им, рзт = dark.ви(WORKSPACE, нг, MCP, SKILLS, MEMORY, PF, SEARCH, None)
                except Exception as err:
                    инс_им, рзт = инс, f"Error: tool execution failed ({type(err).__name__}): {err}"
                try:
                    if инс_им == "поиск" and isinstance(рзт, dict):
                        агент_ = dark._форм_рез_поиск(рзт)
                    elif инс_им in ("чтение", "список", "github_чтение"):
                        агент_ = рзт if isinstance(рзт, str) else str(рзт)
                    else:
                        агент_ = dark._краткий_результат_инструмента(инс_им, нг["arguments"], рзт)
                except Exception:
                    агент_ = _to_text(рзт)[:400]
                агент_ = _to_text(агент_)
                emit({"type": "tool_result", "name": _sname(инс_им),
                      "ok": not _to_text(рзт).startswith(("✘", "Error:")), "brief": агент_[:400]})

            инс_им = _sname(инс_им)
            MODEL_TEXT = рзт if isinstance(рзт, str) else (агент_ or _to_text(рзт))
            смс.extend([
                {"role": "assistant", "content": raw},
                {"role": "system", "content": f"TOOL RESULT ({инс_им}):\n{MODEL_TEXT}"},
            ])

            fingerprint = (инс, json.dumps(нг["arguments"], sort_keys=True, default=str)[:200])
            if prev_tool == fingerprint:
                same_tool += 1
            else:
                same_tool = 0
            prev_tool = fingerprint
            if same_tool >= 6:
                смс.append({"role": "system",
                            "content": "You are repeating the same tool call. Stop and produce your FINAL: answer now with the information you already have."})
            _trim(смс)
            continue

        if p["ask"]:
            aid = uuid.uuid4().hex[:10]
            q = queue.Queue(maxsize=1)
            _ANSWERS[aid] = q
            emit({"type": "ask", "ask_id": aid, "text": p["ask"]})
            try:
                ans = q.get(timeout=600)
            except queue.Empty:
                ans = {"text": ""}
            _ANSWERS.pop(aid, None)
            reply = (ans.get("text") or "").strip() or "(no answer provided)"
            смс.extend([{"role": "assistant", "content": raw},
                        {"role": "user", "content": reply}])
            continue

        if p["final"]:
            if not client.saw_final:  # FINAL: text already streamed as deltas
                emit({"type": "final", "text": p["final"]})
            смс.append({"role": "assistant", "content": raw})
            _trim(смс)
            return

        if p["continue"]:
            emit({"type": "status", "text": p["continue"][:400]})
        if p["think"] and not (p["final"] or p["ask"] or p["tool"] or p["continue"] or p["plain"]):
            emit({"type": "status", "text": ("Thinking: " + p["think"])[:400]})

        if (p["continue"] or p["think"]) and not p["plain"]:
            nudges += 1
            смс.extend([
                {"role": "assistant", "content": raw},
                {"role": "system",
                 "content": ("You have not acted yet. In your next response output exactly one of:"
                             " TOOL: with a JSON tool call, CONTINUE: for progress, or FINAL: with"
                             " the complete answer. Do not only think.")},
            ])
            _trim(смс)
            if nudges >= 4:
                txt = p["continue"] or p["think"] or ""
                emit({"type": "final", "text": txt})
                смс.append({"role": "assistant", "content": raw})
                return
            continue

        plain = p["plain"] or p["final"] or p["continue"] or p["think"]
        if plain:
            emit({"type": "final", "text": plain})
            смс.append({"role": "assistant", "content": raw})
            _trim(смс)
            return

    emit({"type": "error", "text": "Turn limit reached without a final answer."})


# ------------------------------------------------------------------ HTTP layer
INDEX = ROOT / "webui" / "index.html"
MIME = {".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css",
        ".png": "image/png", ".svg": "image/svg+xml", ".ico": "image/x-icon", ".md": "text/plain"}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):  # keep console clean
        pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _no_store(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")

    def _send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self._no_store()
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        data = {}  # diag endpoints accept query-less GET too
        if path in ("/", "/index.html"):
            if INDEX.is_file():
                body = INDEX.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", MIME[".html"])
                self.send_header("Content-Length", str(len(body)))
                self._cors()
                self._no_store()
                self.end_headers()
                self.wfile.write(body)
            else:
                self._send_json({"error": "webui/index.html missing"}, 404)
            return
        if path == "/api/health":
            self._send_json({
                "ok": AGENT_OK,
                "version": "bridge-5",
                "model": _CURRENT["model"],
                "workspace": str(WORKSPACE),
                "tools": len(interpreter.список_инструментов()) if AGENT_OK else 0,
                "mcp": (len(MCP.список()) if AGENT_OK and MCP else 0),
                "sessions": len(_sessions_list()),
                "err": AGENT_ERR if not AGENT_OK else "",
            })
            return
        if path == "/api/sessions":
            self._send_json({"ok": True, "sessions": _sessions_list()})
            return
        if path == "/api/mcp":
            self._send_json(_mcp_info())
            return
        if path == "/api/skills":
            self._send_json(_skills_info())
            return
        if path == "/api/history":
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query or "")
            sid = (qs.get("session") or [""])[0]
            st = _session(sid)
            sm = st["смс"]
            # keep everything except the base system prompt (index 0)
            msgs = [m for i, m in enumerate(sm)
                    if not (i == 0 and m.get("role") == "system")]
            meta = _META.get(sid, {})
            self._send_json({"ok": True, "session": sid,
                             "title": meta.get("title") or "(new)",
                             "created": meta.get("created"), "updated": meta.get("updated"),
                             "busy": st["busy"], "messages": msgs})
            return
        if path == "/api/models":
            self._send_json(_models() if AGENT_OK else {"error": AGENT_ERR})
            return
        if path == "/api/tools":
            tools = interpreter.список_инструментов() if AGENT_OK else []
            slim = [{"module": t["module"], "doc": (t.get("doc") or t.get("hint") or "")[:160],
                     "functions": t.get("functions", []), "kind": t.get("kind", "")} for t in tools]
            self._send_json({"tools": slim})
            return
        if path == "/api/diag_cf" or path == "/api/diag_po":
            self._diag(path, {})
            return
        self._send_json({"error": "not found"}, 404)

    def _diag(self, path, data):
        if path == "/api/diag_cf":
            out, err = "", ""
            def _w():
                nonlocal out, err
                try:
                    import importlib.util as _iu
                    _sp = _iu.spec_from_file_location("_cf", str(ROOT / "api" / "Cloudflare.py"))
                    _cf = _iu.module_from_spec(_sp)
                    _sp.loader.exec_module(_cf)
                    for c in _cf.Cloudflare("glm-4.7-flash", [
                            {"role": "system", "content": "short"},
                            {"role": "user", "content": "Say FINAL: diag"}]):
                        out += str(c)
                        if len(out) > 200:
                            break
                except Exception as e:
                    err = f"{type(e).__name__}: {e}"
            th = threading.Thread(target=_w)
            th.start()
            th.join(timeout=150)
            self._send_json({"out": out[:300], "err": err})
            return
        if path == "/api/diag_po":
            variant = str(data.get("variant") or "tiny") if isinstance(data, dict) else "tiny"
            out, err = "", ""
            layer = str(data.get("layer") or "po")
            def _w2():
                nonlocal out, err
                try:
                    msgs = [{"role": "user", "content": ("Say FINAL: po-tiny" if variant != "full" else "Say FINAL: po-full")}]
                    if variant == "full":
                        msgs = [{"role": "system", "content": _system_prompt()},
                                {"role": "user", "content": "Say FINAL: po-full"}]
                    if layer == "z":
                        from scripts.услуга import з as _зу
                        for c in _зу("glm-4.7-flash", msgs):
                            out += json.dumps(c, ensure_ascii=False, default=str)[:200] + " | "
                            if len(out) > 400:
                                break
                    else:
                        for c in wtf.по(None, "", "glm-4.7-flash", msgs):
                            out += str(c)
                            if len(out) > 300:
                                break
                except Exception as e:
                    err = f"{type(e).__name__}: {e}"
            th2 = threading.Thread(target=_w2)
            th2.start()
            th2.join(timeout=150)
            self._send_json({"out": out[:400], "err": err})
            return
        self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        try:
            length = int(self.headers.get("Content-Length") or "0")
            raw = self.rfile.read(length).decode("utf-8", "replace") if length else "{}"
            data = json.loads(raw)
        except Exception:
            self._send_json({"error": "bad json"}, 400)
            return

        if path in ("/api/diag_cf", "/api/diag_po"):
            self._diag(path, data)
            return

        if path == "/api/model":
            self._send_json(_select_model(str(data.get("name") or "")))
            return

        if path == "/api/new":
            sid = str(data.get("session") or "")
            title = str(data.get("title") or "")
            if sid:
                _fresh_session(sid, title)
            self._send_json({"ok": True, **_models()})
            return

        if path == "/api/session/create":
            sid = str(data.get("session") or "") or uuid.uuid4().hex[:12]
            title = str(data.get("title") or "")[:60]
            st = _session(sid)
            if not st["busy"]:
                _fresh_session(sid, title)
            self._send_json({"ok": True, "session": sid})
            return

        if path == "/api/session/delete":
            sid = str(data.get("session") or "")
            st = _SESSIONS.get(sid)
            if st is not None and st["busy"]:
                self._send_json({"ok": False, "error": "session is busy"}, 409)
                return
            _delete_session(sid)
            self._send_json({"ok": True})
            return

        if path == "/api/session/rename":
            sid = str(data.get("session") or "")
            title = str(data.get("title") or "")[:80]
            st = _SESSIONS.get(sid)
            if st is not None and st["busy"]:
                self._send_json({"ok": False, "error": "session is busy"}, 409)
                return
            _META.setdefault(sid, {"created": _now_ms(), "updated": _now_ms(),
                                   "title": title or "(new)"})["title"] = title or "(new)"
            _persist(sid)
            self._send_json({"ok": True, "session": sid})
            return

        if path == "/api/mcp/add":
            self._send_json(_mcp_add(data))
            return

        if path == "/api/mcp/remove":
            self._send_json(_mcp_remove(str(data.get("name") or "")))
            return

        if path == "/api/skills/add":
            self._send_json(_skill_add(data))
            return

        if path == "/api/answer":
            aid = str(data.get("ask_id") or "")
            q = _ANSWERS.get(aid)
            if q is not None:
                try:
                    q.put_nowait(data)
                except queue.Full:
                    pass
            self._send_json({"ok": True})
            return

        if path == "/api/stop":
            sid = str(data.get("session") or "")
            _session(sid)["stop"].set()
            self._send_json({"ok": True})
            return

        if path == "/api/chat":
            if not AGENT_OK:
                self._sse_reply({"type": "error", "text": "Agent failed to load:\n" + AGENT_ERR})
                return
            text = str(data.get("message") or "").strip()
            sid = str(data.get("session") or "") or uuid.uuid4().hex[:12]
            if not text:
                self._sse_reply({"type": "error", "text": "Empty message."})
                return
            st = _session(sid)
            if st["busy"]:
                self._sse_reply({"type": "error", "text": "This session is still working. Stop it first."})
                return
            if st["stop"].is_set():
                st["stop"] = threading.Event()

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("X-Accel-Buffering", "no")
            self._cors()
            self.end_headers()

            q = queue.Queue(maxsize=4096)
            done = threading.Event()

            def emitter(obj):
                try:
                    q.put_nowait(obj)
                except queue.Full:
                    pass

            def worker():
                try:
                    run_chat(sid, text, emitter, st["stop"])
                finally:
                    done.set()

            threading.Thread(target=worker, daemon=True).start()
            try:
                while True:
                    try:
                        obj = q.get(timeout=45)
                    except queue.Empty:
                        if done.is_set():
                            break
                        self._sse({"type": "ping"})
                        continue
                    self._sse(obj)
                    if obj.get("type") in ("final", "error", "stopped"):
                        break
                while not q.empty():  # drain anything left
                    try:
                        self._sse(q.get_nowait())
                    except queue.Empty:
                        break
                self._sse({"type": "end"})
            except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
                done.set()
                st["stop"].set()
            return

        self._send_json({"error": "not found"}, 404)

    def _sse_reply(self, first):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self._cors()
        self.end_headers()
        self._sse(first)
        self._sse({"type": "end"})

    def _sse(self, obj):
        line = "data: " + json.dumps(obj, ensure_ascii=False) + "\n\n"
        self.wfile.write(line.encode("utf-8"))
        self.wfile.flush()


def _log(msg):
    try:
        with open(ROOT / "webui" / "server.log", "a", encoding="utf-8") as f:
            f.write(time.strftime("[%H:%M:%S] ") + str(msg) + "\n")
    except Exception:
        pass


def main():
    _log(f"listening http://127.0.0.1:{PORT} (agent_ok={AGENT_OK})")
    if not AGENT_OK:
        _log("agent load failed:\n" + AGENT_ERR)
    print(f"Ps UI  ->  http://127.0.0.1:{PORT}", flush=True)
    if not AGENT_OK:
        print("agent load failed:", AGENT_ERR.splitlines()[0] if AGENT_ERR else "", flush=True)
        print("full traceback: webui/agent.log", flush=True)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    server.daemon_threads = True
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
