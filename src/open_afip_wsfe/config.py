"""JSON loading helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).expanduser().open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def load_config(path: str | Path) -> dict[str, Any]:
    return _load_json(path)


def load_invoice_request(path: str | Path) -> dict[str, Any]:
    return _load_json(path)

