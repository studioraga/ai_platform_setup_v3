#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

python3 - <<'PY'
from pathlib import PurePosixPath
import re
import struct
import subprocess
import sys


def git(*args):
    return subprocess.check_output(
        ["git", *args], stderr=subprocess.PIPE
    )


entries = git("ls-files", "--stage", "-z").split(b"\0")
entries = [e for e in entries if e]

if not entries:
    raise SystemExit("FAIL: Git index is empty")

forbidden_parts = {
    ".venv", ".venvs", "node_modules", "__pycache__",
    ".pytest_cache", ".ruff_cache", ".terraform",
    "dist", "build", "reports", "backups", "patches",
    "secrets", "source-verification", "test-results",
    "playwright-report", ".git",
}

forbidden_names = {
    "kubectl", "helm", "terraform", "az", "azd",
    "id_rsa", "id_ed25519",
    ".env", ".envs", ".env.local", ".env.production",
}

forbidden_extensions = (
    ".whl", ".zip", ".tar", ".tar.gz", ".tgz",
    ".deb", ".rpm", ".exe", ".dll", ".so",
    ".a", ".o", ".pyc", ".p12", ".pfx",
    ".pem", ".key", ".sqlite", ".db",
    ".asc", ".gpg",
)

allowed_png = {
    "labs/react-ui/src/assets/hero.png",
}

violations = []
png_count = 0
total_bytes = 0

for entry in entries:
    header, separator, raw_path = entry.partition(b"\t")

    if not separator:
        violations.append(("<unknown>", "invalid index record"))
        continue

    path = raw_path.decode("utf-8", "surrogateescape")
    parts = PurePosixPath(path).parts
    basename = parts[-1]
    lower = path.lower()

    metadata = header.split()
    if len(metadata) != 3:
        violations.append((path, "invalid index metadata"))
        continue

    mode, oid, stage = metadata

    if stage != b"0":
        violations.append((path, "unmerged index entry"))
        continue

    # Only regular tracked files are permitted.
    # Reject symlinks (120000) and submodules (160000).
    if mode not in (b"100644", b"100755"):
        violations.append((path, f"unexpected mode {mode.decode()}"))
        continue

    if (
        any(part in forbidden_parts for part in parts)
        or any(part.startswith("backup") for part in parts)
        or any(part.startswith(".env") for part in parts)
        or basename in forbidden_names
        or ".pre-" in path
        or lower.endswith(forbidden_extensions)
        or path.startswith("labs/cloud-tool-install/")
    ):
        violations.append((path, "forbidden artifact path"))
        continue

    try:
        blob = git("cat-file", "blob", oid.decode())
    except subprocess.CalledProcessError:
        violations.append((path, "unreadable staged object"))
        continue

    size = len(blob)
    total_bytes += size

    if path in allowed_png:
        png_count += 1

        if size > 1024 * 1024:
            violations.append((path, "PNG exceeds 1 MiB"))
            continue

        if (
            not blob.startswith(b"\x89PNG\r\n\x1a\n")
            or len(blob) < 24
            or blob[12:16] != b"IHDR"
        ):
            violations.append((path, "invalid PNG signature/IHDR"))
            continue

        width, height = struct.unpack(">II", blob[16:24])
        if not (0 < width <= 4096 and 0 < height <= 4096):
            violations.append((path, "invalid PNG dimensions"))
            continue

    elif size > 2 * 1024 * 1024:
        violations.append((path, "text file exceeds 2 MiB"))
        continue

    elif b"\x00" in blob:
        violations.append((path, "unexpected binary content"))
        continue

    if re.search(
        rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        blob,
    ):
        violations.append((path, "private-key content"))

    if re.search(
        rb"(?im)^\s*(?:POSTGRES_PASSWORD|QDRANT_API_KEY)"
        rb"\s*=\s*[A-Za-z0-9+/_=-]{20,}\s*$",
        blob,
    ):
        violations.append((path, "possible embedded credential"))

if violations:
    for path, reason in violations:
        print(f"FAIL: {path}: {reason}", file=sys.stderr)
    raise SystemExit(2)

print(
    f"PASS: {len(entries)} indexed source files; "
    f"{png_count} approved PNG; "
    f"{total_bytes} staged bytes"
)
print("LIMITATION: independent secret scan and review still required")
PY
