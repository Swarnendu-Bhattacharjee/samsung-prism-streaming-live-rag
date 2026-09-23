"""
Hybrid retrieval with BM25 + dense fusion via Reciprocal Rank Fusion (RRF)
and Cross-Encoder reranking.
"""

from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
import time

from src.core.config import settings

# ── Global model caches ──────────────────────────────────────────────────────

_embed_model: Optional[SentenceTransformer] = None
_rerank_model: Optional[CrossEncoder] = None
_bm25_index: Optional[BM25Okapi] = None
_corpus_tokens: List[List[str]] = []


def get_embed_model() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(settings.embedding_model)
    return _embed_model


def get_rerank_model() -> CrossEncoder:
    global _rerank_model
    if _rerank_model is None:
        _rerank_model = CrossEncoder(settings.reranker_model)
    return _rerank_model


def build_bm25_index(documents: List[str]) -> BM25Okapi:
    """Build a BM25 index from a list of document strings."""
    global _bm25_index, _corpus_tokens
    _corpus_tokens = [doc.lower().split() for doc in documents]
    _bm25_index = BM25Okapi(_corpus_tokens) if _corpus_tokens else None
    return _bm25_index


def add_to_bm25(text: str):
    """Add a document to the BM25 index."""
    global _bm25_index, _corpus_tokens
    tokens = text.lower().split()
    _corpus_tokens.append(tokens)
    if len(_corpus_tokens) > 0:
        _bm25_index = BM25Okapi(_corpus_tokens)


class RetrievalResult:
    """A single retrieved chunk with metadata."""
    def __init__(self, doc_id: str, text: str, score: float, source: str = "", sub_query: str = ""):
        self.doc_id = doc_id
        self.text = text
        self.score = score
        self.source = source
        self.sub_query = sub_query

    def to_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "text": self.text,
            "score": round(self.score, 4),
            "source": self.source,
            "sub_query": self.sub_query,
        }


class RRFusion:
    """Reciprocal Rank Fusion across multiple ranked lists."""

    @staticmethod
    def fuse(results_lists: List[List[RetrievalResult]], k: int = 60) -> List[RetrievalResult]:
        """
        Fuse multiple ranked lists using RRF formula:
        score(d) = sum( 1.0 / (k + rank_i + 1) )
        """
        if not results_lists:
            return []

        # If a single flat list was passed, wrap it
        if len(results_lists) > 0 and not isinstance(results_lists[0], list):
            results_lists = [results_lists]

        score_map: Dict[str, float] = {}
        doc_map: Dict[str, RetrievalResult] = {}

        for results in results_lists:
            for rank, r in enumerate(results):
                key = f"{r.doc_id}_{hash(r.text[:50])}"
                score_map[key] = score_map.get(key, 0.0) + (1.0 / (k + rank + 1))
                if key not in doc_map:
                    doc_map[key] = r

        fused = []
        for key, score in sorted(score_map.items(), key=lambda x: x[1], reverse=True):
            r = doc_map[key]
            r.score = score
            fused.append(r)

        return fused


def hybrid_search(
    query: str,
    top_k: int = 5,
    sub_query: str = "",
) -> List[RetrievalResult]:
    """
    Hybrid search: dense embedding similarity + sparse BM25 keyword matching
    fused via Reciprocal Rank Fusion (RRF).
    """
    from src.ingestion.corpus import get_cached_chunks
    chunks = get_cached_chunks()
    if not chunks:
        return []

    # 1. Dense retrieval
    embed_model = get_embed_model()
    query_vec = embed_model.encode([query], normalize_embeddings=True)[0]
    dense_results = _dense_search(query_vec, query, top_k * settings.rerank_candidate_multiplier, sub_query)

    # 2. Sparse BM25 retrieval
    bm25_results = _bm25_search(query, top_k * settings.rerank_candidate_multiplier, sub_query)

    # 3. Fuse dense and sparse
    if bm25_results:
        fused = RRFusion.fuse([dense_results, bm25_results], k=settings.rrf_k)
        return fused[:top_k * settings.rerank_candidate_multiplier]

    return dense_results[:top_k * settings.rerank_candidate_multiplier]


def _dense_search(query_vec: np.ndarray, query: str, k: int, sub_query: str = "") -> List[RetrievalResult]:
    """Dense semantic retrieval via cosine similarity."""
    from src.ingestion.corpus import get_cached_chunks
    chunks = get_cached_chunks()
    if not chunks:
        return []

    embed_model = get_embed_model()
    chunk_texts = [c["text"] for c in chunks]
    chunk_vecs = embed_model.encode(chunk_texts, normalize_embeddings=True)

    similarities = chunk_vecs @ query_vec
    top_indices = np.argsort(similarities)[::-1][:k]

    results = []
    for idx in top_indices:
        chunk = chunks[idx]
        results.append(RetrievalResult(
            doc_id=chunk.get("doc_id", f"chunk-{idx}"),
            text=chunk["text"],
            score=float(similarities[idx]),
            source=chunk.get("source", ""),
            sub_query=sub_query or query,
        ))

    return results


def _bm25_search(query: str, k: int, sub_query: str = "") -> List[RetrievalResult]:
    """BM25 sparse retrieval."""
    global _bm25_index
    from src.ingestion.corpus import get_cached_chunks
    chunks = get_cached_chunks()

    if _bm25_index is None or not chunks:
        return []

    tokenized_query = query.lower().split()
    if not tokenized_query:
        return []

    scores = _bm25_index.get_scores(tokenized_query)
    top_indices = np.argsort(scores)[::-1][:k]

    results = []
    for idx in top_indices:
        if idx >= len(chunks):
            continue
        score = scores[idx]
        if score <= 0:
            continue
        chunk = chunks[idx]
        results.append(RetrievalResult(
            doc_id=chunk.get("doc_id", f"chunk-{idx}"),
            text=chunk["text"],
            score=float(score),
            source=chunk.get("source", ""),
            sub_query=sub_query or query,
        ))

    return results


def rerank_results(
    query: str,
    results: List[RetrievalResult],
    top_n: int = 3,
) -> List[RetrievalResult]:
    """Cross-encoder reranking of candidate chunks."""
    if not results:
        return []

    rerank_model = get_rerank_model()
    pairs = [(query, r.text) for r in results]
    scores = rerank_model.predict(pairs)

    ranked = sorted(zip(results, scores.tolist()), key=lambda x: x[1], reverse=True)
    reranked_results = []
    for r, score in ranked[:top_n]:
        r.score = float(score)
        reranked_results.append(r)

    return reranked_results
