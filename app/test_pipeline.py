import asyncio
import time
from src.ingestion.corpus import load_demo_corpus, get_corpus_stats
from src.retrieval.hybrid import hybrid_search, RRFusion, rerank_results
from src.retrieval.decompose import classify_intent, decompose_query
from src.retrieval.sharpening import sharpening_engine
from src.core.synthesizer import synthesize_stream
from src.core.metrics import metrics_tracker

async def run_comprehensive_test():
    print("=================================================================")
    print("    SAMSUNG PRISM THEME 04: STREAMING LIVE RAG TEST SUITE       ")
    print("=================================================================\n")

    # 1. Corpus Loading
    print("▶ STEP 1: Corpus Initialization")
    count = load_demo_corpus()
    stats = get_corpus_stats()
    print(f"  ✓ Documents: {stats['documents']}, Chunks: {stats['chunks']}")
    assert stats['chunks'] > 0, "Corpus chunks must be > 0"

    # 2. Intent Classification
    print("\n▶ STEP 2: Intent Classification")
    turn1_query = "Compare Galaxy S24 Ultra and Fold 6 battery capacity, cooling vapor chamber, and Live Translate language support."
    intent = await classify_intent(turn1_query)
    print(f"  Query: \"{turn1_query[:60]}...\"")
    print(f"  Intent: {intent['intent']} (Needs retrieval: {intent['needs_retrieval']})")

    # 3. Query Decomposition
    print("\n▶ STEP 3: Multi-Query Decomposition")
    sub_queries = await decompose_query(turn1_query)
    print(f"  Decomposed into {len(sub_queries)} sub-queries:")
    for i, sq in enumerate(sub_queries, 1):
        print(f"    [{i}] {sq}")
    assert len(sub_queries) >= 2, "Complex query should be decomposed into multiple sub-queries"

    # 4. Multi-Query Parallel Hybrid Retrieval
    print("\n▶ STEP 4: Parallel Hybrid Search (Dense Vector + BM25)")
    subquery_results = []
    all_retrieved = []
    for sq in sub_queries:
        res = hybrid_search(sq, top_k=5, sub_query=sq)
        subquery_results.append(res)
        all_retrieved.extend(res)
        print(f"    Sub-query '{sq[:35]}...' -> {len(res)} chunks")

    # 5. Reciprocal Rank Fusion (RRF)
    print("\n▶ STEP 5: Reciprocal Rank Fusion (k=60)")
    fused = RRFusion.fuse(subquery_results, k=60)
    print(f"  ✓ Fused {len(all_retrieved)} multi-query hits into {len(fused)} unique ranked candidates")

    # 6. Cross-Encoder Reranking
    print("\n▶ STEP 6: Cross-Encoder Reranking (ms-marco-MiniLM-L-6-v2)")
    reranked = rerank_results(turn1_query, fused, top_n=3)
    print(f"  ✓ Top {len(reranked)} Reranked Documents:")
    for i, r in enumerate(reranked, 1):
        print(f"    [{i}] Score: {r.score:.4f} | Source: {r.source}")
        print(f"        Snippet: {r.text[:90]}...")
    assert len(reranked) > 0, "Reranked results must not be empty"

    # Save to sharpening context
    session_id = "test-session-live"
    sharpening_engine.update_context(session_id, reranked)

    # 7. Grounded Token Synthesis & TTFT
    print("\n▶ STEP 7: Grounded Token Synthesis (Streaming)")
    tokens = []
    t_start = time.time()
    ttft_ms = None
    async for token in synthesize_stream(turn1_query, reranked, session_id):
        if ttft_ms is None:
            ttft_ms = (time.time() - t_start) * 1000
        tokens.append(token)

    full_answer = "".join(tokens)
    print(f"  ✓ TTFT: {ttft_ms:.1f}ms | Total Tokens: {len(tokens)}")
    print(f"  ✓ Answer Preview:\n{full_answer[:250]}...\n")

    # 8. Mid-Flow Conversational Sharpening (Turn 2)
    print("▶ STEP 8: Conversational Mid-Flow Sharpening (Turn 2)")
    turn2_refinement = "And also, what about the maximum battery protection threshold and 45W fast charging speed?"
    print(f"  Refinement Query: \"{turn2_refinement}\"")
    sharpened_results, stats_s = sharpening_engine.sharpen(session_id, turn2_refinement, top_n=3)
    print(f"  ✓ Sharpened Context: Retained {stats_s['retained']} prior context docs, added {stats_s['delta']} new delta docs.")
    for i, r in enumerate(sharpened_results, 1):
        print(f"    [{i}] Source: {r.source} | Score: {r.score:.4f}")

    # 9. Metrics Tracking
    print("\n▶ STEP 9: Telemetry & Evaluation Metrics")
    recall = metrics_tracker.compute_recall(sub_queries, all_retrieved)
    groundedness = metrics_tracker.compute_groundedness(full_answer, reranked)
    cost = metrics_tracker.estimate_cost(120, len(tokens), "local")
    print(f"  ✓ Retrieval Recall: {recall * 100:.1f}%")
    print(f"  ✓ Answer Groundedness / Faithfulness: {groundedness * 100:.1f}%")
    print(f"  ✓ Time-to-First-Token (TTFT): {ttft_ms:.1f}ms")
    print(f"  ✓ Cost per turn: ${cost:.6f}")

    print("\n✅ ALL SYSTEM TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
