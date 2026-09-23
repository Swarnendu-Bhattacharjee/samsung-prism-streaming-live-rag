"""
Conversational Mid-Flow Answer Sharpening Engine.
Allows supplementary detail or follow-up constraints to sharpen existing
retrieval context without restarting search from scratch.
"""

from typing import List, Dict, Tuple
from src.retrieval.hybrid import RetrievalResult, hybrid_search, rerank_results
from src.core.config import settings

class ContextualSharpeningEngine:
    """
    Maintains session-scoped retrieval contexts and blends new in-flow constraints
    with previous grounded knowledge.
    """
    def __init__(self):
        # Maps session_id -> List[RetrievalResult] (last grounded candidates)
        self._session_contexts: Dict[str, List[RetrievalResult]] = {}

    def get_context(self, session_id: str) -> List[RetrievalResult]:
        return self._session_contexts.get(session_id, [])

    def update_context(self, session_id: str, results: List[RetrievalResult]):
        self._session_contexts[session_id] = results[:5]

    def clear(self, session_id: str):
        self._session_contexts.pop(session_id, None)

    def sharpen(
        self,
        session_id: str,
        refinement_query: str,
        top_n: int = 3,
    ) -> Tuple[List[RetrievalResult], Dict[str, int]]:
        """
        Sharpen previous retrieved context using the new supplementary detail.
        Returns:
            - sharpened_results: List of reranked RetrievalResult
            - stats: {"retained": int, "delta": int}
        """
        previous_results = self.get_context(session_id)
        if not previous_results:
            # Cold start if no context exists
            new_results = hybrid_search(refinement_query, top_k=top_n * 2)
            reranked = rerank_results(refinement_query, new_results, top_n=top_n)
            self.update_context(session_id, reranked)
            return reranked, {"retained": 0, "delta": len(reranked)}

        # 1. Retrieve delta candidates matching the new constraint
        delta_candidates = hybrid_search(refinement_query, top_k=settings.top_k)

        # 2. Boost existing context documents with retention score
        boosted_previous = []
        for r in previous_results:
            boosted_r = RetrievalResult(
                doc_id=r.doc_id,
                text=r.text,
                score=r.score + settings.context_retention_boost,
                source=r.source,
                sub_query=f"[Prior Context] {r.sub_query}",
            )
            boosted_previous.append(boosted_r)

        # 3. Merge prior context with delta candidates
        combined = boosted_previous + delta_candidates

        # 4. Rerank merged candidate set against the combined user intent
        reranked = rerank_results(refinement_query, combined, top_n=top_n)

        # Count retained vs delta
        prev_ids = {r.doc_id for r in previous_results}
        retained_count = sum(1 for r in reranked if r.doc_id in prev_ids)
        delta_count = len(reranked) - retained_count

        self.update_context(session_id, reranked)

        return reranked, {
            "retained": retained_count,
            "delta": delta_count,
        }


sharpening_engine = ContextualSharpeningEngine()
