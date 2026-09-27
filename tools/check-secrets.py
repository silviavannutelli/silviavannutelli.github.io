#!/usr/bin/env python3
"""Refuse to ship if a credential or secret file is in the site tree."""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".vercel"}
SKIP_EXT = {".woff2", ".jpg", ".jpeg", ".png", ".gif", ".webp"}
NAME_DENY = re.compile(r"(\.env($|\.)|credentials\.json$|secrets\.json$|id_rsa$|id_ed25519$|\.pem$|\.key$)", re.I)
PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk_live_[A-Za-z0-9]{8,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z\-_]{20,}\b"),
    re.compile(
        r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|session_secret|"
        r"admin_password|blob_read_write_token|cursor_api_key)\s*[:=]\s*['\"][^'\"]{6,}"
    ),
]


def main():
    bad = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if NAME_DENY.search(name):
                bad.append(os.path.relpath(os.path.join(dirpath, name), ROOT) + " (secret filename)")
                continue
            if os.path.splitext(name)[1].lower() in SKIP_EXT:
                continue
            path = os.path.join(dirpath, name)
            try:
                text = open(path, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            for pattern in PATTERNS:
                if pattern.search(text):
                    bad.append(os.path.relpath(path, ROOT))
                    break
    if bad:
        print("secret scan failed:")
        print("\n".join(bad))
        return 1
    print("secret scan ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
