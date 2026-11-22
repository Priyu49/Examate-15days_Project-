"""Bounded in-process cache for repeated soil question answers."""

from functools import lru_cache

from app.rag import answer_question


@lru_cache(maxsize=128)
def _cached_answer(normalized_question: str, top_k: int) -> dict:
    return answer_question(normalized_question, top_k=top_k)


def cached_answer(question: str, top_k: int = 3) -> dict:
    """Reuse identical normalized questions; return a fresh response object."""
    normalized = " ".join(question.split()).casefold()
    result = dict(_cached_answer(normalized, top_k))
    result["question"] = question
    result["citations"] = [dict(citation) for citation in result.get("citations", [])]
    return result
