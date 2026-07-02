#!/usr/bin/env python3
"""Scan a repository for common secrets and private AFIP/ARCA data."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ALLOWED_CUITS = {"20111111112", "20222222223", "20333333334"}
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "dist", "build"}
SKIP_SUFFIXES = {".pyc", ".pyo", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip"}

BEGIN = "-----" + "BEGIN"
PRIVATE_KEY = "PRIVATE " + "KEY"

PATTERNS = [
    ("private key", re.compile(BEGIN + r" [A-Z ]*" + PRIVATE_KEY + "-----")),
    ("certificate", re.compile(BEGIN + r" CERTIFICATE-----")),
    ("possible CAE", re.compile(r"\b\d{14}\b")),
]
CUIT_RE = re.compile(r"\b(?:20|23|24|27|30|33|34)\d{9}\b")
LOCAL_DENYLIST = ".audit-secrets.local.txt"
EXTRA_PATTERNS_ENV = "AUDIT_SECRETS_EXTRA_PATTERNS"


def iter_files(root: Path):
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() not in SKIP_SUFFIXES:
            yield path


def load_extra_patterns(root: Path) -> list[tuple[str, re.Pattern[str]]]:
    patterns: list[tuple[str, re.Pattern[str]]] = []
    local_file = root / LOCAL_DENYLIST
    if local_file.exists():
        for line_number, line in enumerate(local_file.read_text(encoding="utf-8").splitlines(), 1):
            value = line.strip()
            if not value or value.startswith("#"):
                continue
            patterns.append((f"{LOCAL_DENYLIST}:{line_number}", re.compile(value, re.IGNORECASE)))

    env_value = os.environ.get(EXTRA_PATTERNS_ENV, "")
    if env_value.strip():
        patterns.append((EXTRA_PATTERNS_ENV, re.compile(env_value, re.IGNORECASE)))

    return patterns


def audit(root: Path) -> list[str]:
    findings: list[str] = []
    patterns = PATTERNS + load_extra_patterns(root)
    for path in iter_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(root)
        for cuit in CUIT_RE.findall(text):
            if cuit not in ALLOWED_CUITS:
                findings.append(f"{rel}: unexpected CUIT-like value {cuit}")
        if rel == Path(LOCAL_DENYLIST):
            continue
        for label, pattern in patterns:
            if pattern.search(text):
                findings.append(f"{rel}: matched {label}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit repository for secrets/private data.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root")
    args = parser.parse_args()
    findings = audit(Path(args.root).resolve())
    if findings:
        print("Secret audit failed:")
        for finding in findings:
            print(f" - {finding}")
        return 1
    print("Secret audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
