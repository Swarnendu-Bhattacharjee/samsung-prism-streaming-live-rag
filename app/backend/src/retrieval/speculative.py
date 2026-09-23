"""
Speculative Early-Retrieval Engine for Full-Duplex Live Streaming RAG.
Enables pre-fetching and caching candidate chunks before the user finishes speaking.
"""

from typing import Dict, List, Optional
import time
import asyncio
from src.retrieval.hybrid import hybrid_search, RetrievalResult
from src.core.config import settings

class SpeculativeCache:
    """
    Maintains speculative retrieval states for in-flight streaming utterances.
    """
    def __init__(self):
        # Maps session_id -> { "last_partial": str, "timestamp": float, "candidates": List[RetrievalResult] }
        self._cache: Dict[str, dict] = {}

    def update_partial(self, session_id: str, partial_text: str) -> Optional[List[RetrievalResult]]:
        """
        Evaluate in-flight partial text. If enough informative content has accumulated,
        speculatively pre-retrieve candidates.
        """
        clean_text = partial_text.strip()
        if len(clean_text) < settings.speculative_char_threshold:
            return None

        # Check if query has changed significantly
        cached = self._cache.get(session_id)
        if cached:
            prev_text = cached.get("last_partial", "")
            # Only re-trigger if more than 3 words added
            if len(clean_text.split()) - len(prev_text.split()) < 3:
                return cached.get("candidates")

        # Speculatively retrieve top candidates
        candidates = hybrid_search(clean_text, top_k=settings.top_k)

        self._cache[session_id] = {
            "last_partial": clean_text,
            "timestamp": time.time(),
            "candidates": candidates,
        }
        return candidates

    def get_prewarmed(self, session_id: str, final_text: str) -> Optional[List[RetrievalResult]]:
        """
        Retrieve speculative results if valid and fresh (<10s).
        """
        cached = self._cache.get(session_id)
        if not cached:
            return None

        if time.time() - cached["timestamp"] > 10.0:
            return None

        # Check semantic or prefix relevance
        if cached["last_partial"].lower() in final_text.lower() or len(final_text.split()) >= len(cached["last_partial"].split()):
            return cached.get("candidates")
        return None

    def clear(self, session_id: str):
        self._cache.pop(session_id, None)


speculative_cache = SpeculativeCache()
