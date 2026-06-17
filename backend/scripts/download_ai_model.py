from __future__ import annotations

import os
from pathlib import Path
import sys

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from services.ai_preference_service import DEFAULT_MODEL_NAME  # noqa: E402


def main() -> None:
    try:
        from sentence_transformers import SentenceTransformer
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Missing dependency: sentence-transformers. "
            "Install backend dependencies first, then rerun this script."
        ) from exc

    repo_root = Path(__file__).resolve().parents[2]
    cache_dir = Path(os.getenv("AI_MODEL_CACHE_DIR", repo_root / "var" / "ai_models"))
    model_name = os.getenv("AI_PREFERENCE_MODEL", DEFAULT_MODEL_NAME)
    cache_dir.mkdir(parents=True, exist_ok=True)
    SentenceTransformer(model_name, cache_folder=str(cache_dir))
    print(f"AI preference model ready: {model_name}")
    print(f"Cache directory: {cache_dir}")


if __name__ == "__main__":
    main()
