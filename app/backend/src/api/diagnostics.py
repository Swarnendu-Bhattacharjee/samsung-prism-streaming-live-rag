"""
Pipeline Diagnostics & Stage Inspection for Samsung PRISM Live Streaming RAG.
Theme 04: Full-Duplex Conversational Streaming RAG.
Provides deep-dive stage metadata, algorithms, live execution traces, and standalone stage tests.
"""

from typing import Dict, Any, List, Optional
import time
import re
import numpy as np

from src.core.config import settings
from src.retrieval.hybrid import (
    hybrid_search,
    rerank_results,
    RRFusion,
    get_embed_model,
    get_rerank_model,
    _dense_search,
    _bm25_search,
    RetrievalResult,
)
from src.retrieval.decompose import classify_intent, decompose_query, SYSTEM_INTENT, SYSTEM_DECOMPOSE
from src.retrieval.sharpening import sharpening_engine
from src.retrieval.speculative import speculative_cache
from src.core.synthesizer import _format_context, SYSTEM_SYNTH
from src.ingestion.corpus import get_cached_chunks

STAGE_SPECS: Dict[str, Dict[str, Any]] = {
    "pipeline": {
        "id": "pipeline",
        "title": "Full-Duplex Live Streaming Pipeline",
        "subtitle": "End-to-End Speculative Conversational RAG Architecture",
        "category": "Orchestration",
        "description": "Orchestrates concurrent speculative caching, intent routing, parallel query decomposition, dense+sparse hybrid retrieval, Reciprocal Rank Fusion, deep cross-encoder reranking, mid-flow sharpening, and Groq LPU grounded token streaming under 150ms TTFT.",
        "algorithm": "Speculative Full-Duplex Conversational Orchestration with Server-Sent Events (SSE)",
        "model": f"Groq LPU ({settings.llm_model}) + all-MiniLM-L6-v2 + ms-marco-MiniLM-L-6-v2",
        "parameters": {
            "llm_provider": settings.llm_provider,
            "llm_synthesis_model": settings.llm_model,
            "llm_inference_model": settings.llm_inference_model,
            "embedding_model": settings.embedding_model,
            "reranker_model": settings.reranker_model,
            "rrf_k": settings.rrf_k,
            "top_k": settings.top_k,
            "rerank_top_n": settings.rerank_top_n,
            "context_retention_boost": settings.context_retention_boost,
        },
        "logic_steps": [
            "0. Asynchronous Voice / Keystroke listener pre-warms candidate chunks via speculative cache",
            "1. Intent Router classifies query (complex_multi_query vs single_factual vs midflow_refinement vs chitchat)",
            "2. Decomposer splits multi-aspect queries into 2-4 standalone sub-queries resolving coreferences",
            "3. Parallel Hybrid runs 384-dim Dense Cosine Search and BM25Okapi inverted index concurrently",
            "4. RRF Rank Fusion merges ranked lists with zero-parameter 1/(k + rank) normalization",
            "5. Cross-Encoder computes deep all-to-all transformer cross-attention logits to prune irrelevant candidates",
            "6. Contextual Sharpening retains prior session entities and blends new delta constraints mid-flow",
            "7. Grounded Token Synthesizer streams verifiable tokens via Groq LPU with explicit [Source X] citations",
        ],
    },
    "intent": {
        "id": "intent",
        "title": "Stage 1: Intent Router",
        "subtitle": "Deterministic Fast-Path + Groq Zero-Shot Semantic Router",
        "category": "Classification & Semantic Routing",
        "description": "Determines whether an utterance requires retrieval, detects mid-flow conversational refinements, and classifies single vs complex multi-part queries in < 2ms (heuristic) or ~1.1s (Groq LLM).",
        "algorithm": "Heuristic Regex Filter + Few-Shot Semantic Classification",
        "model": f"Groq LPU ({settings.llm_inference_model})",
        "prompt_template": SYSTEM_INTENT,
        "parameters": {
            "fast_path_latency": "< 2ms",
            "llm_temperature": 0.0,
            "timeout_seconds": 2.0,
        },
        "logic_steps": [
            "Step 1: Check for chitchat/greeting patterns (hi, hello, thanks) -> skip retrieval if matched",
            "Step 2: Check for mid-flow refinement prefixes ('and also', 'what about') when active session context exists -> trigger Sharpening",
            "Step 3: Check for conjunction patterns ('and also', 'compared to', 'vs') or multiple question marks -> complex_multi_query",
            "Step 4: Dispatch to Groq LPU zero-shot classification to produce strict JSON with intent, needs_retrieval, confidence, and reason",
        ],
    },
    "decomposer": {
        "id": "decomposer",
        "title": "Stage 2: Query Decomposer",
        "subtitle": "Multi-Aspect Semantic Decomposition & Entity Disambiguation",
        "category": "Query Understanding",
        "description": "Breaks compound, multi-entity questions into 2 to 4 independent, crisp search queries. Resolves pronouns ('it', 'they', 'the phone') to explicit entities to maximize retrieval precision.",
        "algorithm": "Structured LLM Decomposition with Coreference Resolution",
        "model": f"Groq LPU ({settings.llm_inference_model})",
        "prompt_template": SYSTEM_DECOMPOSE,
        "parameters": {
            "max_sub_queries": 4,
            "temperature": 0.0,
            "output_format": "JSON Array of Strings",
        },
        "logic_steps": [
            "Step 1: Parse user question and identify conjunctions, entity comparisons, or multi-topic questions",
            "Step 2: Resolve ambiguous pronouns and implicit references back to named Samsung products",
            "Step 3: Generate keyword-rich, standalone sub-queries optimized for both vector and lexical search engines",
            "Step 4: Validate JSON format; if parsing fails, execute deterministic syntactic sentence-splitting fallback",
        ],
    },
    "hybrid": {
        "id": "hybrid",
        "title": "Stage 3: Parallel Hybrid Retrieval",
        "subtitle": "Dense Vector (SentenceTransformer) + Sparse Lexical (BM25Okapi)",
        "category": "Dual-Engine Retrieval",
        "description": "Executes dense semantic embeddings search (all-MiniLM-L6-v2) and sparse keyword search (BM25Okapi) concurrently across each sub-query, capturing both conceptual meaning and exact model numbers/specs.",
        "algorithm": "Cosine Similarity (Dense 384-dim) + BM25Okapi TF-IDF Inverted Index",
        "model": f"SentenceTransformer ({settings.embedding_model}) + BM25Okapi",
        "parameters": {
            "dense_embedding_dim": 384,
            "similarity_metric": "Cosine Similarity (A · B / ||A|| ||B||)",
            "bm25_k1": 1.5,
            "bm25_b": 0.75,
            "candidate_multiplier": settings.rerank_candidate_multiplier,
            "top_k_per_branch": settings.top_k * settings.rerank_candidate_multiplier,
        },
        "logic_steps": [
            "Step 1: Compute 384-dimensional dense vector embeddings of the sub-query using all-MiniLM-L6-v2 on CUDA",
            "Step 2: Calculate cosine similarity dot product against pre-computed corpus chunk vectors",
            "Step 3: Tokenize sub-query and compute BM25Okapi term frequency/inverse document frequency (TF-IDF) scores",
            "Step 4: Filter out non-matching chunks and merge candidate pools per sub-query",
        ],
    },
    "rrf": {
        "id": "rrf",
        "title": "Stage 4: Reciprocal Rank Fusion (RRF)",
        "subtitle": "Zero-Parameter Non-Parametric Rank Aggregation",
        "category": "Rank Fusion",
        "description": "Fuses multiple ranked lists from dense vector search and sparse BM25 across all sub-queries without requiring score calibration or threshold tuning.",
        "algorithm": "Reciprocal Rank Fusion: RRF(d) = sum( 1 / (k + rank_i + 1) )",
        "formula": "RRF(d) = \\sum_{q \\in Q} \\sum_{m \\in \\{dense, sparse\\}} \\frac{1}{k + \\text{rank}(d, m, q)}, \\quad k = 60",
        "model": "Deterministic Mathematical Aggregator",
        "parameters": {
            "k_constant": settings.rrf_k,
            "default_k": 60,
            "weight_policy": "Equal rank weight across dense and lexical engines",
        },
        "logic_steps": [
            "Step 1: Assign each document chunk its 1-indexed rank within each sub-query list and engine list",
            "Step 2: Apply the inverse rank formula: 1 / (60 + rank) for each appearance",
            "Step 3: Accumulate the reciprocal scores for identical chunks across all lists into a score map",
            "Step 4: Sort accumulated scores in descending order to generate the master candidate pool for reranking",
        ],
    },
    "cross_encoder": {
        "id": "cross_encoder",
        "title": "Stage 5: Cross-Encoder Reranker",
        "subtitle": "Deep All-to-All Full Cross-Attention Neural Ranking",
        "category": "Neural Reranking",
        "description": "Applies a full cross-attention transformer (ms-marco-MiniLM-L-6-v2) where query tokens and document tokens attend to each other simultaneously, eliminating bi-encoder representation compression limits.",
        "algorithm": "Full Cross-Attention Self-Attention Matrix: Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V",
        "model": f"CrossEncoder ({settings.reranker_model})",
        "parameters": {
            "model_checkpoint": "cross-encoder/ms-marco-MiniLM-L-6-v2",
            "top_n_final": settings.rerank_top_n,
            "score_type": "Unbounded Cross-Attention Logits (-inf to +inf)",
        },
        "logic_steps": [
            "Step 1: Construct joint token pairs: [CLS] Query Tokens [SEP] Candidate Chunk Tokens [SEP]",
            "Step 2: Pass pairs through 6-layer transformer encoder with all-to-all cross-attention across all tokens",
            "Step 3: Extract the classification head logit corresponding to passage relevance",
            "Step 4: Sort candidates by raw logit and select the Top-N (default 3) highest scoring grounded contexts",
        ],
    },
    "sharpening": {
        "id": "sharpening",
        "title": "Stage 6: Contextual Answer Sharpening",
        "subtitle": "Mid-Flow Incremental Constraint Blending Without Search Restarts",
        "category": "Conversational Memory & Context Blending",
        "description": "Maintains an active conversation entity memory. When a user asks a follow-up constraint ('what about the 45W charger?'), it retains existing grounded context, retrieves only the delta constraint, and sharpens the answer.",
        "algorithm": "Sliding-Window Entity Retention with Soft Retention Boosting (Score_boosted = Score + beta)",
        "model": "ContextualSharpeningEngine + Dynamic Delta Injection",
        "parameters": {
            "context_retention_boost": settings.context_retention_boost,
            "beta": 0.5,
            "window_size": 5,
        },
        "logic_steps": [
            "Step 1: Check session store for prior grounded context chunks from previous conversational turns",
            "Step 2: If follow-up constraint is detected, retrieve new delta candidates matching the new constraint",
            "Step 3: Apply retention boost beta (+0.5) to previously verified context documents",
            "Step 4: Cross-Encoder reranks the combined pool of retained + delta chunks against the full conversational context",
            "Step 5: Measure and report retained chunk count vs delta chunk count in telemetry",
        ],
    },
    "synthesis": {
        "id": "synthesis",
        "title": "Stage 7: Synthesis Stream",
        "subtitle": "Grounded Citation Injection & Groq LPU Ultra-Low TTFT Token Engine",
        "category": "Generation & Streaming",
        "description": "Formats verified context chunks with explicit [Source X] citations and streams hallucination-free tokens via Groq LPU inference directly to the browser with < 150ms target TTFT.",
        "algorithm": "Grounded Few-Shot Prompt Injection + Server-Sent Events (SSE) Token Generator",
        "model": f"Groq LPU ({settings.llm_model})",
        "prompt_template": SYSTEM_SYNTH,
        "parameters": {
            "llm_provider": settings.llm_provider,
            "temperature": 0.3,
            "target_ttft_ms": "< 150ms",
            "chunk_format": "[Source {i}: {source}]\\n{text}",
            "anti_hallucination_policy": "Strict context constraint: Refuse ungrounded extrapolation",
        },
        "logic_steps": [
            "Step 1: Format reranked chunks into clean context blocks with explicit [Source 1], [Source 2] labels",
            "Step 2: Inject system anti-hallucination guardrails into the prompt",
            "Step 3: Call Groq AsyncGroq chat completion with stream=True",
            "Step 4: Measure Time to First Token (TTFT) on the arrival of chunk index 1",
            "Step 5: Yield tokens one-by-one via SSE 'event: token' with index and TTFT metrics",
            "Step 6: Compute faithfulness grounding and recall metrics upon stream completion",
        ],
    },
}


class PipelineTraceManager:
    """Stores the latest real-time pipeline execution trace and intermediate step results."""

    def __init__(self):
        self.latest_trace: Dict[str, Any] = {
            "has_run": False,
            "last_updated": None,
            "query": "",
            "session_id": "",
            "stages": {
                "pipeline": {},
                "intent": {},
                "decomposer": {},
                "hybrid": {},
                "rrf": {},
                "cross_encoder": {},
                "sharpening": {},
                "synthesis": {},
            },
        }

    def start_trace(self, query: str, session_id: str):
        self.latest_trace = {
            "has_run": True,
            "last_updated": time.time(),
            "query": query,
            "session_id": session_id,
            "stages": {
                "pipeline": {
                    "status": "running",
                    "query": query,
                    "session_id": session_id,
                    "start_time": time.time(),
                },
                "intent": {},
                "decomposer": {},
                "hybrid": {},
                "rrf": {},
                "cross_encoder": {},
                "sharpening": {},
                "synthesis": {},
            },
        }

    def update_stage(self, stage_name: str, data: Dict[str, Any]):
        if stage_name in self.latest_trace["stages"]:
            self.latest_trace["stages"][stage_name].update(data)
            self.latest_trace["last_updated"] = time.time()

    def get_trace(self) -> Dict[str, Any]:
        return self.latest_trace


trace_manager = PipelineTraceManager()


# ── Standalone Stage Diagnostic Inspectors ────────────────────────────────────

async def inspect_intent_stage(query: str, has_prior_context: bool = False) -> Dict[str, Any]:
    t0 = time.time()
    info = await classify_intent(query, has_prior_context=has_prior_context)
    latency_ms = round((time.time() - t0) * 1000, 1)
    return {
        "stage": "intent",
        "query": query,
        "result": info,
        "latency_ms": latency_ms,
        "spec": STAGE_SPECS["intent"],
    }


async def inspect_decomposer_stage(query: str) -> Dict[str, Any]:
    t0 = time.time()
    sub_queries = await decompose_query(query)
    latency_ms = round((time.time() - t0) * 1000, 1)
    return {
        "stage": "decomposer",
        "query": query,
        "sub_queries": sub_queries,
        "count": len(sub_queries),
        "latency_ms": latency_ms,
        "spec": STAGE_SPECS["decomposer"],
    }


def inspect_hybrid_stage(query: str, top_k: int = 5) -> Dict[str, Any]:
    t0 = time.time()
    embed_model = get_embed_model()
    query_vec = embed_model.encode([query], normalize_embeddings=True)[0]

    dense = _dense_search(query_vec, query, k=top_k)
    bm25 = _bm25_search(query, k=top_k)
    latency_ms = round((time.time() - t0) * 1000, 1)

    return {
        "stage": "hybrid",
        "query": query,
        "dense_results": [r.to_dict() for r in dense],
        "bm25_results": [r.to_dict() for r in bm25],
        "dense_count": len(dense),
        "bm25_count": len(bm25),
        "vector_dim": 384,
        "latency_ms": latency_ms,
        "spec": STAGE_SPECS["hybrid"],
    }


def inspect_rrf_stage(query: str, top_k: int = 5, k_constant: int = 60) -> Dict[str, Any]:
    t0 = time.time()
    embed_model = get_embed_model()
    query_vec = embed_model.encode([query], normalize_embeddings=True)[0]

    dense = _dense_search(query_vec, query, k=top_k)
    bm25 = _bm25_search(query, k=top_k)
    fused = RRFusion.fuse([dense, bm25], k=k_constant)
    latency_ms = round((time.time() - t0) * 1000, 1)

    # Detailed rank step breakdown
    calculation_steps = []
    for r in fused[:top_k]:
        dense_rank = next((idx + 1 for idx, d in enumerate(dense) if d.doc_id == r.doc_id), None)
        bm25_rank = next((idx + 1 for idx, b in enumerate(bm25) if b.doc_id == r.doc_id), None)
        calc_str = []
        if dense_rank:
            calc_str.append(f"Dense Rank {dense_rank} -> 1/({k_constant}+{dense_rank}) = {round(1.0/(k_constant+dense_rank), 5)}")
        if bm25_rank:
            calc_str.append(f"BM25 Rank {bm25_rank} -> 1/({k_constant}+{bm25_rank}) = {round(1.0/(k_constant+bm25_rank), 5)}")

        calculation_steps.append({
            "doc_id": r.doc_id,
            "source": r.source,
            "fused_score": round(r.score, 5),
            "dense_rank": dense_rank,
            "bm25_rank": bm25_rank,
            "formula_breakdown": " + ".join(calc_str),
            "text_snippet": r.text[:120] + "...",
        })

    return {
        "stage": "rrf",
        "query": query,
        "k_constant": k_constant,
        "fused_results": [r.to_dict() for r in fused[:top_k]],
        "calculation_steps": calculation_steps,
        "latency_ms": latency_ms,
        "spec": STAGE_SPECS["rrf"],
    }


def inspect_cross_encoder_stage(query: str, top_n: int = 3) -> Dict[str, Any]:
    t0 = time.time()
    candidates = hybrid_search(query, top_k=6)
    rerank_model = get_rerank_model()
    pairs = [(query, r.text) for r in candidates]
    scores = rerank_model.predict(pairs) if pairs else []

    scored_candidates = []
    for r, score in zip(candidates, scores.tolist() if hasattr(scores, 'tolist') else scores):
        scored_candidates.append({
            "doc_id": r.doc_id,
            "source": r.source,
            "raw_logit": round(float(score), 4),
            "text": r.text,
        })

    scored_candidates.sort(key=lambda x: x["raw_logit"], reverse=True)
    selected = scored_candidates[:top_n]
    pruned = scored_candidates[top_n:]
    latency_ms = round((time.time() - t0) * 1000, 1)

    return {
        "stage": "cross_encoder",
        "query": query,
        "selected_top_n": selected,
        "pruned_candidates": pruned,
        "total_evaluated": len(scored_candidates),
        "latency_ms": latency_ms,
        "spec": STAGE_SPECS["cross_encoder"],
    }


def inspect_sharpening_stage(query: str, session_id: str = "demo-session") -> Dict[str, Any]:
    prior_context = sharpening_engine.get_context(session_id)
    reranked, stats = sharpening_engine.sharpen(session_id, query, top_n=3)
    return {
        "stage": "sharpening",
        "query": query,
        "session_id": session_id,
        "prior_chunks_count": len(prior_context),
        "retained_count": stats["retained"],
        "delta_count": stats["delta"],
        "results": [r.to_dict() for r in reranked],
        "spec": STAGE_SPECS["sharpening"],
    }


def inspect_synthesis_stage(query: str) -> Dict[str, Any]:
    candidates = hybrid_search(query, top_k=3)
    reranked = rerank_results(query, candidates, top_n=3)
    formatted_context = _format_context(reranked)
    formatted_prompt = SYSTEM_SYNTH.format(context=formatted_context, question=query)

    return {
        "stage": "synthesis",
        "query": query,
        "formatted_context": formatted_context,
        "system_prompt": formatted_prompt,
        "sources": [r.to_dict() for r in reranked],
        "spec": STAGE_SPECS["synthesis"],
    }
