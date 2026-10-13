from __future__ import annotations
import importlib.util, os, platform, shutil, socket, subprocess, sys, json
from pathlib import Path

# Usage (via TOOL: run_file, or directly):
# python inspect-environment.py
# "python" – "python3" -->> APPLIES TO THE SYSTEM
# Inspects the current execution environment and returns system capabilities,
# installed runtimes, available browsers, writable paths, network connectivity,
# and selected Python module availability.
#
# Functions:
# inspect_environment() – Returns detailed environment and capability information.
# command_available() – Checks whether a system command is installed and returns its path.
# run_probe() – Executes a system command with a timeout and returns stdout, stderr,
#                return code, and execution status.
#
# Use this tool when you need to determine what the current environment supports
# before running code, using a browser, accessing files, or selecting an available
# runtime or system utility.

def _cmd(name):
    return shutil.which(name) or ""

def inspect_environment():
    browsers={}
    for n in ("google-chrome","google-chrome-stable","chromium","chromium-browser","firefox","brave","brave-browser","microsoft-edge","msedge"):
        p=_cmd(n)
        if p: browsers[n]=p
    runtimes={}
    for n in ("python","python3","node","npm","npx","pnpm","yarn","bun","git","curl","wget","ffmpeg","ffprobe","unzip","tar","zip","termux-open-url","termux-api"):
        p=_cmd(n)
        if p: runtimes[n]=p
    gui=bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY") or platform.system()=="Windows" or platform.system()=="Darwin")
    writable=[]
    for p in (Path.cwd(), Path.home(), Path("/tmp")):
        try:
            if p.exists() and os.access(p,os.W_OK): writable.append(str(p))
        except Exception: pass
    return {
        "ok":True,"os":platform.system(),"release":platform.release(),"machine":platform.machine(),
        "python":platform.python_version(),"termux":bool(os.environ.get("TERMUX_VERSION") or _cmd("termux-info")),
        "shell":os.environ.get("SHELL") or os.environ.get("ComSpec") or "",
        "gui":gui,"browsers":browsers,"runtimes":runtimes,"writable_paths":writable,
        "network": _network(),
        "python_modules": {m: bool(importlib.util.find_spec(m)) for m in ("playwright","PIL","cv2","requests")},
    }

def _network():
    try:
        socket.create_connection(("1.1.1.1",443),2).close()
        return True
    except Exception: return False

def command_available(command):
    return {"command":command,"path":_cmd(command),"available":bool(_cmd(command))}

def run_probe(command, timeout=10):
    try:
        p=subprocess.run(command,shell=True,capture_output=True,text=True,timeout=timeout)
        return {"ok":p.returncode==0,"returncode":p.returncode,"stdout":p.stdout[:8000],"stderr":p.stderr[:8000]}
    except Exception as e:
        return {"ok":False,"error":f"{type(e).__name__}: {e}"}
