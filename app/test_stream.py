import asyncio
import json
from src.api.main import app, sessions
from src.ingestion.corpus import load_demo_corpus
from src.retrieval.hybrid import hybrid_search, RRFusion, rerank_results
from src.retrieval.decompose import classify_intent, decompose_query
from src.core.synthesizer import synthesize_stream
from src.core.config import settings

async def debug_stream():
    print("Loading corpus...")
    load_demo_corpus()
    print(f"Corpus: {len(__import__('src.ingestion.corpus', fromlist=['_cached_chunks'])._cached_chunks)} chunks")
    
    question = "What is PTO?"
    session_id = "debug"
    
    print("\n=== Classify ===")
    intent = await classify_intent(question)
    print(f"Intent: {intent}")
    
    sub_queries = await decompose_query(question) if intent == "complex" else [question]
    print(f"Sub-queries: {sub_queries}")
    
    print("\n=== Retrieve ===")
    all_results = []
    for sq in sub_queries:
        results = hybrid_search(sq, top_k=10)
        all_results.extend(results)
        print(f"  {sq}: {len(results)} results")
    print(f"  Total: {len(all_results)}")
    
    print("\n=== RRF ===")
    fused = RRFusion.fuse(all_results, k=60)
    print(f"  Fused: {len(fused)}")
    
    print("\n=== Rerank ===")
    reranked = rerank_results(question, fused, top_n=3)
    print(f"  Reranked: {len(reranked)}")
    for r in reranked:
        print(f"    [{r.doc_id}] {r.score:.3f}")
    
    print("\n=== Stream tokens ===")
    count = 0
    async for token in synthesize_stream(question, reranked, session_id):
        count += 1
        if count <= 3 or count % 10 == 0:
            print(f"  [{count}] {repr(token)}")
    print(f"  Total: {count} tokens")

asyncio.run(debug_stream())
