from __future__ import annotations

import json
import os
from pathlib import Path
import sys

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("USE_IN_MEMORY_REPOSITORY", "1")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def load_fixture(name: str = "retail_behavior_sample.json") -> dict:
    return json.loads((ROOT / "tests" / "fixtures" / name).read_text(encoding="utf-8"))
