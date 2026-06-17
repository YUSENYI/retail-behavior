from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from math import exp, sqrt
import os
from pathlib import Path
from threading import Lock
from typing import Protocol

from domain.common import utcnow
from services.behavior_event_repository import BehaviorEventRecord


DEFAULT_MODEL_NAME = "BAAI/bge-small-zh-v1.5"
BEHAVIOR_WEIGHTS = {
    "browse": 0.2,
    "search": 0.3,
    "click": 0.4,
    "favorite": 0.65,
    "cart_add": 0.85,
    "order_submit": 0.95,
    "payment_success": 1.15,
}


class EmbeddingBackend(Protocol):
    model_name: str
    mode: str
    load_error: str | None

    def encode(self, texts: list[str]) -> list[list[float]]: ...


@dataclass(slots=True)
class ProductSignal:
    product_id: str
    name: str
    category: str
    brand: str
    tag: str
    price: float
    text: str


class SentenceTransformerBackend:
    def __init__(self, model_name: str, cache_dir: Path) -> None:
        self.model_name = model_name
        self.mode = "sentence-transformers"
        self.load_error: str | None = None
        self._model = None
        self._cache_dir = cache_dir
        self._lock = Lock()

    def encode(self, texts: list[str]) -> list[list[float]]:
        with self._lock:
            if self._model is None:
                try:
                    from sentence_transformers import SentenceTransformer

                    self._cache_dir.mkdir(parents=True, exist_ok=True)
                    self._model = SentenceTransformer(self.model_name, cache_folder=str(self._cache_dir))
                    self.load_error = None
                except Exception as exc:  # pragma: no cover - depends on local model runtime
                    self.load_error = str(exc)
                    raise
            vectors = self._model.encode(texts, normalize_embeddings=True)
        return [list(map(float, vector)) for vector in vectors]


class HashEmbeddingBackend:
    """Deterministic fallback used when the real model dependency is unavailable."""

    def __init__(self, load_error: str | None = None) -> None:
        self.model_name = "fallback-hash-embedding"
        self.mode = "fallback"
        self.load_error = load_error

    def encode(self, texts: list[str]) -> list[list[float]]:
        return [_hash_embedding(text) for text in texts]


class AIUserPreferenceService:
    def __init__(self, backend: EmbeddingBackend | None = None) -> None:
        self.backend = backend or _get_embedding_backend()

    def classify(
        self,
        events: list[BehaviorEventRecord],
        target_id: str | None = None,
        top_n: int = 5,
    ) -> dict[str, object]:
        usable_events = [
            event
            for event in events
            if event.product_id and (target_id in (None, "all") or event.user_id == target_id)
        ]
        products = _product_signals(usable_events)
        if not usable_events or not products:
            return self._empty_result()

        product_ids = list(products)
        product_vectors = self._encode([products[product_id].text for product_id in product_ids])
        vectors_by_product = dict(zip(product_ids, product_vectors, strict=True))
        users = sorted({event.user_id for event in usable_events if event.user_id})
        items = [
            self._classify_user(user_id, usable_events, products, vectors_by_product, top_n)
            for user_id in users
        ]
        return {
            "model": self._model_info(),
            "behaviorWeights": BEHAVIOR_WEIGHTS,
            "items": [item for item in items if item["categories"]],
            "generatedAt": utcnow().isoformat(),
        }

    def _classify_user(
        self,
        user_id: str,
        events: list[BehaviorEventRecord],
        products: dict[str, ProductSignal],
        vectors_by_product: dict[str, list[float]],
        top_n: int,
    ) -> dict[str, object]:
        user_events = [event for event in events if event.user_id == user_id and event.product_id in products]
        category_events: dict[str, list[BehaviorEventRecord]] = defaultdict(list)
        behavior_scores: dict[str, float] = defaultdict(float)
        user_vector: list[float] | None = None
        total_weight = 0.0

        for event in user_events:
            product = products[str(event.product_id)]
            weight = _event_weight(event)
            if weight <= 0:
                continue
            category_events[product.category].append(event)
            behavior_scores[product.category] += weight
            vector = vectors_by_product[product.product_id]
            user_vector = _add_vectors(user_vector, vector, weight)
            total_weight += weight

        if user_vector is None or total_weight <= 0:
            return {"userId": user_id, "primaryCategory": None, "primaryConfidence": 0, "categories": []}

        user_vector = [value / total_weight for value in user_vector]
        max_behavior = max(behavior_scores.values() or [1])
        categories = []
        for category, category_user_events in category_events.items():
            category_vectors = [
                vectors_by_product[str(event.product_id)]
                for event in category_user_events
                if event.product_id in vectors_by_product
            ]
            category_vector = _mean_vector(category_vectors)
            similarity = _cosine(user_vector, category_vector)
            behavior_confidence = behavior_scores[category] / max_behavior
            confidence = round(max(0, similarity) * 70 + behavior_confidence * 30, 2)
            categories.append(
                {
                    "category": category,
                    "confidence": min(confidence, 100),
                    "semanticSimilarity": round(similarity, 4),
                    "behaviorScore": round(behavior_scores[category], 4),
                    "actionMix": _action_mix(category_user_events),
                    "evidenceProducts": _evidence_products(category_user_events, products),
                }
            )
        categories.sort(key=lambda item: item["confidence"], reverse=True)
        primary = categories[0] if categories else None
        return {
            "userId": user_id,
            "primaryCategory": primary["category"] if primary else None,
            "primaryConfidence": primary["confidence"] if primary else 0,
            "categories": categories[:top_n],
        }

    def _encode(self, texts: list[str]) -> list[list[float]]:
        try:
            return self.backend.encode(texts)
        except Exception as exc:
            fallback = HashEmbeddingBackend(str(exc))
            self.backend = fallback
            return fallback.encode(texts)

    def _model_info(self) -> dict[str, object]:
        return {
            "name": self.backend.model_name,
            "mode": self.backend.mode,
            "cacheDir": str(_model_cache_dir()),
            "loaded": self.backend.mode == "sentence-transformers" and self.backend.load_error is None,
            "loadError": self.backend.load_error,
        }

    def _empty_result(self) -> dict[str, object]:
        return {
            "model": self._model_info(),
            "behaviorWeights": BEHAVIOR_WEIGHTS,
            "items": [],
            "generatedAt": utcnow().isoformat(),
        }


def _build_embedding_backend() -> EmbeddingBackend:
    if os.getenv("AI_PREFERENCE_DISABLE_MODEL") == "1":
        return HashEmbeddingBackend()
    return SentenceTransformerBackend(os.getenv("AI_PREFERENCE_MODEL", DEFAULT_MODEL_NAME), _model_cache_dir())


_BACKEND: EmbeddingBackend | None = None
_BACKEND_LOCK = Lock()


def _get_embedding_backend() -> EmbeddingBackend:
    global _BACKEND
    with _BACKEND_LOCK:
        if _BACKEND is None:
            _BACKEND = _build_embedding_backend()
        return _BACKEND


def _model_cache_dir() -> Path:
    configured = os.getenv("AI_MODEL_CACHE_DIR")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[3] / "var" / "ai_models"


def _product_signals(events: list[BehaviorEventRecord]) -> dict[str, ProductSignal]:
    products: dict[str, ProductSignal] = {}
    for event in events:
        if not event.product_id:
            continue
        metadata = event.metadata or {}
        product_id = str(event.product_id)
        category = str(metadata.get("category") or "未分类")
        name = str(metadata.get("productName") or metadata.get("name") or product_id)
        brand = str(metadata.get("brand") or "")
        tag = str(metadata.get("tag") or "")
        price = _float(metadata.get("price"))
        text = "；".join(
            part
            for part in [
                f"商品名称：{name}",
                f"品牌：{brand}" if brand else "",
                f"商品分类：{category}",
                f"商品标签：{tag}" if tag else "",
                f"搜索词：{event.search_keyword}" if event.search_keyword else "",
                f"价格：{price:.0f}" if price else "",
            ]
            if part
        )
        products[product_id] = ProductSignal(product_id, name, category, brand, tag, price, text)
    return products


def _event_weight(event: BehaviorEventRecord) -> float:
    weight = BEHAVIOR_WEIGHTS.get(event.event_type, 0)
    if weight <= 0:
        return 0
    price = _float((event.metadata or {}).get("price"))
    if event.event_type == "payment_success" and price > 0:
        weight *= 1 + min(price / 1000, 0.6)
    if isinstance(event.occurred_at, datetime):
        age_days = max((utcnow() - event.occurred_at).total_seconds() / 86400, 0)
        weight *= exp(-age_days / 30)
    return weight


def _action_mix(events: list[BehaviorEventRecord]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for event in events:
        counts[event.event_type] += 1
    return dict(sorted(counts.items()))


def _evidence_products(
    events: list[BehaviorEventRecord], products: dict[str, ProductSignal]
) -> list[dict[str, object]]:
    scores: dict[str, float] = defaultdict(float)
    for event in events:
        if event.product_id:
            scores[str(event.product_id)] += _event_weight(event)
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:3]
    return [
        {
            "productId": product_id,
            "productName": products[product_id].name,
            "score": round(score, 4),
        }
        for product_id, score in ranked
        if product_id in products
    ]


def _hash_embedding(text: str, dimensions: int = 384) -> list[float]:
    vector = [0.0] * dimensions
    normalized = text.strip().lower()
    grams = [normalized[index : index + 2] for index in range(max(len(normalized) - 1, 1))]
    for gram in grams or [normalized]:
        digest = sha256(gram.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1 if digest[4] % 2 == 0 else -1
        vector[index] += sign
    norm = sqrt(sum(value * value for value in vector)) or 1
    return [value / norm for value in vector]


def _add_vectors(base: list[float] | None, vector: list[float], weight: float) -> list[float]:
    if base is None:
        return [value * weight for value in vector]
    return [left + right * weight for left, right in zip(base, vector, strict=True)]


def _mean_vector(vectors: list[list[float]]) -> list[float]:
    if not vectors:
        return []
    return [sum(values) / len(vectors) for values in zip(*vectors, strict=True)]


def _cosine(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = sqrt(sum(a * a for a in left))
    right_norm = sqrt(sum(b * b for b in right))
    denominator = left_norm * right_norm
    return numerator / denominator if denominator else 0


def _float(value: object) -> float:
    try:
        return max(float(value), 0)
    except (TypeError, ValueError):
        return 0
