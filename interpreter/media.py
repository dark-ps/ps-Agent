from __future__ import annotations
import json, shutil, subprocess
from pathlib import Path

# Usage (via TOOL: run_file, or directly):
# python media.py
# "python" – "python3" -->> APPLIES TO THE SYSTEM
# Provides video inspection and frame extraction using FFmpeg and FFprobe.
#
# Functions:
# ffmpeg_status() – Check whether FFmpeg and FFprobe are available.
# inspect(path) – Read video metadata, format information, and stream details.
# extract_frame(video, output, timestamp) – Extract a single frame from a video
#                                             at the specified timestamp.
#
# Use this tool when you need to inspect video metadata, check media streams,
# determine video properties, or extract a frame/image from a video file.
#
# Files are restricted to the project root directory.

ROOT=Path(__file__).resolve().parents[1]

def ffmpeg_status():
    return {"ffmpeg":shutil.which("ffmpeg"),"ffprobe":shutil.which("ffprobe")}

def inspect(path):
    target=(ROOT/path).resolve()
    if ROOT not in target.parents and target!=ROOT:return {"ok":False,"error":"Path escapes project root"}
    if not target.exists():return {"ok":False,"error":f"Path not found: {path}"}
    ff=shutil.which("ffprobe")
    if not ff:return {"ok":False,"error":"ffprobe is unavailable"}
    try:
        p=subprocess.run([ff,"-v","error","-show_format","-show_streams","-of","json",str(target)],capture_output=True,text=True,timeout=30)
        data=json.loads(p.stdout or "{}")
        return {"ok":p.returncode==0,"path":str(target.relative_to(ROOT)),"metadata":data,"stderr":p.stderr}
    except Exception as e:return {"ok":False,"error":f"{type(e).__name__}: {e}"}

def extract_frame(video, output="Projects/frame.png", timestamp="00:00:01"):
    src=(ROOT/video).resolve(); dst=(ROOT/output).resolve()
    if ROOT not in src.parents or ROOT not in dst.parents:return {"ok":False,"error":"Path escapes project root"}
    if not src.exists():return {"ok":False,"error":"Video not found"}
    ff=shutil.which("ffmpeg")
    if not ff:return {"ok":False,"error":"ffmpeg is unavailable"}
    dst.parent.mkdir(parents=True,exist_ok=True)
    try:
        p=subprocess.run([ff,"-y","-ss",str(timestamp),"-i",str(src),"-frames:v","1",str(dst)],capture_output=True,text=True,timeout=60)
        return {"ok":p.returncode==0 and dst.exists(),"path":str(dst.relative_to(ROOT)),"stderr":p.stderr[-4000:]}
    except Exception as e:return {"ok":False,"error":f"{type(e).__name__}: {e}"}
