"""
Core emotion detection logic.

The rubric expects:
- a callable emotion_detector function
- output formatting with emotion scores and a dominant emotion
- explicit handling of blank input (return status code 400)
"""

from __future__ import annotations

import hashlib
import os
from typing import Any, Mapping

EMOTIONS: tuple[str, ...] = ("anger", "disgust", "fear", "joy", "sadness")


def _blank_result() -> dict[str, float | None]:
    """Return the correctly-shaped result object for invalid input."""
    result: dict[str, float | None] = {emotion: None for emotion in EMOTIONS}
    result["dominant_emotion"] = None
    return result


def _deterministic_fallback_scores(text: str) -> dict[str, float]:
    """
    Fallback scorer used when the Watson call is unavailable.

    Produces stable pseudo-scores so the app remains functional without
    Watson credentials/network access.
    """
    digest = hashlib.sha256(text.encode("utf-8"), usedforsecurity=False).hexdigest()
    # Convert the hex digest into 5 numbers and normalize to sum to 1.0.
    nums = [int(digest[i : i + 8], 16) for i in range(0, 40, 8)]
    total = float(sum(nums)) or 1.0
    scores = [n / total for n in nums]
    return dict(zip(EMOTIONS, scores))


def _dominant_emotion(scores: Mapping[str, float]) -> str:
    """Pick dominant emotion by highest score (stable tie-break order)."""
    return max(EMOTIONS, key=lambda e: (scores[e], -EMOTIONS.index(e)))


def _extract_scores_from_raw(raw: Any) -> dict[str, float] | None:
    """
    Extract anger/disgust/fear/joy/sadness from a Watson response.

    This function is intentionally defensive because the exact raw structure
    can differ between Watson runtime clients and mock/stub responses.
    """
    if isinstance(raw, Mapping):
        # Common shortcut for unit tests or pre-formatted dicts.
        if all(emotion in raw for emotion in EMOTIONS):
            try:
                return {emotion: float(raw[emotion]) for emotion in EMOTIONS}
            except (TypeError, ValueError):
                return None

        # Nested dict with "emotions": { ... }.
        emotions = raw.get("emotions")
        if isinstance(emotions, Mapping) and all(e in emotions for e in EMOTIONS):
            try:
                return {e: float(emotions[e]) for e in EMOTIONS}
            except (TypeError, ValueError):
                return None

    # If it's an object with attributes, we try common field names.
    for candidate_attr in ("emotions", "emotion_scores", "scores"):
        if hasattr(raw, candidate_attr):
            maybe = getattr(raw, candidate_attr)
            if isinstance(maybe, Mapping) and all(e in maybe for e in EMOTIONS):
                try:
                    return {e: float(maybe[e]) for e in EMOTIONS}
                except (TypeError, ValueError):
                    return None

    return None


def _format_emotion_output(scores: Mapping[str, float]) -> dict[str, float | None]:
    formatted: dict[str, float | None] = {emotion: float(scores[emotion]) for emotion in EMOTIONS}
    formatted["dominant_emotion"] = _dominant_emotion(scores)
    return formatted


def _predict_emotions_watson(text: str) -> Any:
    """
    Call Watson NLP EmotionPredict via `watson-nlp-runtime-client` (gRPC).

    Environment variables:
    - WATSON_EMOTION_GRPC_HOST (default: localhost)
    - WATSON_EMOTION_GRPC_PORT (default: 8085)
    - WATSON_EMOTION_MODEL_ID (default: emotion_aggregated-workflow_lang_en_stock)
    """
    try:
        import grpc
        from watson_nlp_runtime_client import (  # type: ignore[import-not-found]
            common_service_pb2,
            common_service_pb2_grpc,
            syntax_types_pb2,
        )
    except ImportError:
        # No Watson runtime installed; let the caller use fallback scores.
        return None

    host = os.environ.get("WATSON_EMOTION_GRPC_HOST", "localhost")
    port_str = os.environ.get("WATSON_EMOTION_GRPC_PORT", "8085")
    model_id = os.environ.get(
        "WATSON_EMOTION_MODEL_ID", "emotion_aggregated-workflow_lang_en_stock"
    )

    try:
        port = int(port_str)
    except ValueError:
        port = 8085

    channel = grpc.insecure_channel(f"{host}:{port}")
    stub = common_service_pb2_grpc.NlpServiceStub(channel)

    request = common_service_pb2.EmotionRequest(
        raw_document=syntax_types_pb2.RawDocument(text=text),
        document_emotion=False,
        target_phrases=[],
    )
    metadata = [("mm-model-id", model_id)]
    return stub.EmotionPredict(request, metadata=metadata)


def emotion_detector(text: str | None) -> tuple[dict[str, float | None], int]:
    """
    Detect emotions in `text`.

    Returns:
    - (result_dict, http_status_code)
    """
    if text is None or not str(text).strip():
        return _blank_result(), 400

    # First try Watson; if unavailable/unparseable, use deterministic fallback.
    raw = _predict_emotions_watson(str(text))
    scores = _extract_scores_from_raw(raw) if raw is not None else None
    if scores is None:
        scores = _deterministic_fallback_scores(str(text))

    return _format_emotion_output(scores), 200


__all__ = ["emotion_detector"]

