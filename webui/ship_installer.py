#!/usr/bin/env python3
"""Build the curl-ready DarkPs installer (pi-style).

Produces in webui/deploy/:

  install.sh            POSIX installer with __DARKPS_URL__ and the
                        archive digest (__DARKPS_SHA__) injected
  agent.tar.gz          the agent payload the installer downloads
  agent.tar.gz.sha256   informational sidecar (installer uses the
                        embedded digest instead — no CRLF pitfalls)

Serve the directory and everything works:

  curl -fsSL <url>/install.sh | sh
"""

import argparse
import hashlib
import io
import os
import tarfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "webui" / "deploy"
SRC = ROOT / "install.sh"


def build_payload() -> bytes:
    excludes_name = {
        ".venv",
        "__pycache__",
        ".git",
        ".darkps",
        "Logos",
        "Projects",
        "deploy",
    }
    excludes_prefix = ("webui/sessions/", "webui/deploy/", "_")
    suffix_drop = (".pyc", ".log", ".out", ".err")
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in excludes_name]
            for name in sorted(filenames):
                p = Path(dirpath) / name
                rel = p.relative_to(ROOT)
                s = str(rel).replace("\\", "/")
                if any(s.startswith(x) for x in excludes_prefix):
                    continue
                if any(s.endswith(x) for x in suffix_drop):
                    continue
                if s == "install.sh":      # installer ships itself separately
                    continue
                info = tf.gettarinfo(str(p), arcname=str(rel))
                try:
                    info.uid = info.gid = 0
                    info.uname = info.gname = "root"
                    info.mtime = int(time.time())
                except Exception:
                    pass
                with open(p, "rb") as fh:
                    tf.addfile(info, fh)
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:7862",
                    help="base URL injected into install.sh (DARKPS_URL)")
    args = ap.parse_args()

    payload = build_payload()
    digest = hashlib.sha256(payload).hexdigest()

    text = SRC.read_text(encoding="utf-8")
    for marker in ("__DARKPS_URL__", "__DARKPS_SHA__"):
        if marker not in text:
            raise SystemExit(f"install.sh is missing the {marker} placeholder")
    text = text.replace("__DARKPS_URL__", args.url.rstrip("/"))
    text = text.replace("__DARKPS_SHA__", digest)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "install.sh").write_text(text, encoding="utf-8", newline="\n")
    (OUT_DIR / "agent.tar.gz").write_bytes(payload)
    with open(OUT_DIR / "agent.tar.gz.sha256", "w", newline="\n", encoding="ascii") as fh:
        fh.write(digest + "\n")

    for f in ("install.sh", "agent.tar.gz", "agent.tar.gz.sha256"):
        p = OUT_DIR / f
        print(f"{f:24s} {p.stat().st_size / 1024:8.1f} KB")
    print(f"sha256: {digest}")


if __name__ == "__main__":
    main()
