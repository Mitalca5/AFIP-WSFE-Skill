#!/usr/bin/env python3
"""Scan a repository for common secrets and private AFIP/ARCA data."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ALLOWED_CUITS = {"20111111112", "20222222223", "20333333334"}
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "dist", "build"}
SKIP_SUFFIXES = {".pyc", ".pyo", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip"}

BEGIN = "-----" + "BEGIN"
PRIVATE_KEY = "PRIVATE " + "KEY"
PRIVATE_NAMES = "santa_" + "julia|la_" + "victorica|romina|verdini|santos"
PRIVATE_PATHS = r"\.open" + r"claw|legal/" + r"certificados|certificados/"

PATTERNS = [
    ("private key", re.compile(BEGIN + r" [A-Z ]*" + PRIVATE_KEY + "-----")),
    ("certificate", re.compile(BEGIN + r" CERTIFICATE-----")),
    ("possible CAE", re.compile(r"\b\d{14}\b")),
    ("private AFIP path", re.compile(PRIVATE_PATHS, re.IGNORECASE)),
    ("named private readme", re.compile(PRIVATE_NAMES, re.IGNORECASE)),
]
CUIT_RE = re.compile(r"\b(?:20|23|24|27|30|33|34)\d{9}\b")


def iter_files(root: Path):
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() not in SKIP_SUFFIXES:
            yield path


def audit(root: Path) -> list[str]:
    findings: list[str] = []
    for path in iter_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(root)
        if rel == Path("scripts/audit_secrets.py"):
            continue
        for cuit in CUIT_RE.findall(text):
            if cuit not in ALLOWED_CUITS:
                findings.append(f"{rel}: unexpected CUIT-like value {cuit}")
        for label, pattern in PATTERNS:
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
