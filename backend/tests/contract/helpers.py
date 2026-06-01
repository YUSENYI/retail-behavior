from __future__ import annotations

from pathlib import Path

import yaml


def load_openapi() -> dict:
    root = Path(__file__).resolve().parents[3]
    return yaml.safe_load((root / "specs/001-retail-behavior-analytics/contracts/openapi.yaml").read_text(encoding="utf-8"))


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
