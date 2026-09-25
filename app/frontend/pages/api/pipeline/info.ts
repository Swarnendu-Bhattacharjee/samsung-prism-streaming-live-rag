import type { NextApiRequest, NextApiResponse } from 'next'

export const PIPELINE_INFO = {
  stages: {
    pipeline: {
      id: "pipeline",
      title: "Full-Duplex Live Streaming Pipeline",
      subtitle: "Dual-Mode Speculative Conversational RAG + General API Architecture",
      category: "Orchestration & Decision",
      description: "End-to-end full-duplex conversational RAG architecture designed for the Samsung Galaxy product ecosystem. Incorporates dual-mode query routing, speculative prefetching, query decomposition, parallel hybrid sparse-dense retrieval, Reciprocal Rank Fusion (RRF), cross-encoder neural reranking, sliding-window context sharpening, and streaming speculative synthesis on Groq LPU hardware.",
      algorithm: "Asynchronous Speculative Event-Driven Pipeline (SSE Protocol)",
      parameters: {
        target_ttft: "< 150ms",
        hybrid_retrieval: "BM25Okapi + Dense Vector (all-MiniLM-L6-v2)",
        fusion: "RRF (k=60)",
        sharpening_beta: 0.5,
        inference_engine: "Groq LPU (Llama 3.3 70B Versatile)"
      },
      logic_steps: [
        "Step 0: Evaluate incoming query via Dual-Mode Intent Router (RAG vs Direct General API)",
        "Step 1: If RAG: concurrently trigger speculative prefetch and multi-query decomposition",
        "Step 2: Dispatch atomic sub-queries to parallel BM25 lexical and dense vector indices",
        "Step 3: Fuse rank lists using Reciprocal Rank Fusion formula: RRF(d) = sum(1 / (60 + rank))",
        "Step 4: Rerank top 12 fused candidates using cross-attention neural cross-encoder",
        "Step 5: Apply sliding-window context sharpening (beta=0.5) to prune fluff sentences and inject [DOC-x] anchors",
        "Step 6: Stream grounded tokens via SSE directly to client with real-time telemetry"
      ]
    },
    intent: {
      id: "intent",
      title: "Stage 1: Intent Router & Dual-Mode Gate",
      subtitle: "Low-Latency Classification & Zero-Waste Bypassing",
      category: "Query Routing",
      description: "Determines whether an utterance requires grounded retrieval from official Samsung product documentation or is a general query (science, programming, world knowledge, chitchat). General queries bypass retrieval to deliver 84ms TTFT with zero wasted compute.",
      algorithm: "Entity Matcher + Groq LPU Zero-Shot Classification Gate",
      parameters: {
        latency_budget: "< 15ms",
        confidence_threshold: 0.85,
        modes: ["direct_general_api", "hybrid_rag_plus_general"]
      },
      logic_steps: [
        "Step 1: Scan query for Samsung hardware, model codes, and ecosystem keywords",
        "Step 2: Classify semantic intent with confidence probability",
        "Step 3: If general: emit 'bypass' event and stream directly from General API",
        "Step 4: If Samsung-focused or ambiguous: trigger 7-stage speculative RAG pipeline"
      ]
    },
    decomposition: {
      id: "decomposition",
      title: "Stage 2: Speculative Prefetch & Decomposer",
      subtitle: "Multi-Attribute Query Decomposition with Coreference Resolution",
      category: "Query Understanding",
      description: "Decomposes compound questions (e.g. comparing S25 Ultra vs S24 Ultra display, build, and processor) into 2-3 focused sub-queries, while an initial speculative search fires concurrently on the raw user query.",
      algorithm: "Speculative Async Overlap + LLM Sub-Query Generation",
      parameters: {
        max_sub_queries: 3,
        overlapped_time_saved: "~35ms"
      },
      logic_steps: [
        "Step 1: Concurrently launch speculative search on the raw query",
        "Step 2: Parse multi-attribute conjunctions and comparisons",
        "Step 3: Resolve pronouns ('it', 'they', 'the phone') to explicit product names",
        "Step 4: Output crisp, keyword-rich sub-queries for hybrid search"
      ]
    },
    hybrid: {
      id: "hybrid",
      title: "Stage 3: Parallel Hybrid Retrieval",
      subtitle: "Dense Semantic Vectors + Sparse Lexical BM25Okapi",
      category: "Dual-Engine Retrieval",
      description: "Combines dense vector similarity with sparse lexical BM25 search. BM25 guarantees exact SKU keyword matches (e.g., 'SM-S928B', 'Titanium Grade 5'), while dense embeddings capture conceptual semantic queries.",
      algorithm: "BM25Okapi (k1=1.5, b=0.75) + Dense Cosine Vector Similarity",
      parameters: {
        bm25_k1: 1.5,
        bm25_b: 0.75,
        embedding_dim: 384,
        candidate_multiplier: 3
      },
      logic_steps: [
        "Step 1: Compute TF-IDF BM25 scores over inverted index across all chunks",
        "Step 2: Calculate dense vector similarity against pre-indexed corpus",
        "Step 3: Execute both searches concurrently via Promise.all / asyncio.gather",
        "Step 4: Pool top candidate lists per sub-query"
      ]
    },
    rrf: {
      id: "rrf",
      title: "Stage 4: Reciprocal Rank Fusion (RRF)",
      subtitle: "Non-Parametric Rank Aggregation with k=60",
      category: "Rank Fusion",
      description: "Merges disparate rank lists from BM25 and vector search without requiring brittle min-max score normalization. Gives high priority to chunks ranked highly across both sparse and dense engines.",
      algorithm: "RRF(d) = sum( 1 / (60 + rank_m(d)) )",
      formula: "RRF(d) = \\sum_{m \\in \\{dense, sparse\\}} \\frac{1}{60 + \\text{rank}_m(d)}",
      parameters: {
        k_constant: 60,
        equal_weighting: true
      },
      logic_steps: [
        "Step 1: Assign 1-indexed ranks to each document in dense and sparse lists",
        "Step 2: Compute reciprocal rank 1 / (60 + rank) for each appearance",
        "Step 3: Accumulate scores across all candidate lists into a unified score map",
        "Step 4: Sort by descending RRF score to select top 12 candidates for reranking"
      ]
    },
    cross_encoder: {
      id: "cross_encoder",
      title: "Stage 5: Cross-Encoder Neural Reranking",
      subtitle: "Deep All-to-All Cross-Attention Scoring",
      category: "Neural Reranking",
      description: "Applies full cross-attention across all token pairs (query, passage) to model subtle semantic relationships that bi-encoders miss, filtering out false-positive lexical hits.",
      algorithm: "Cross-Attention Matrix: Score = sigmoid(W * H_[CLS] + b)",
      parameters: {
        model: "ms-marco-MiniLM-L-6-v2",
        top_n: 5
      },
      logic_steps: [
        "Step 1: Concatenate query and candidate document with [SEP] tokens",
        "Step 2: Pass through cross-attention transformer layers",
        "Step 3: Extract calibrated relevance probability logits",
        "Step 4: Rank candidates and retain top 5 highest-scoring contexts"
      ]
    },
    sharpening: {
      id: "sharpening",
      title: "Stage 6: Context Sharpening & Dynamic Budgeting",
      subtitle: "Sliding-Window Sentence Pruning with beta=0.5",
      category: "Context Compression",
      description: "Splits retrieved chunks into sentences, evaluating each against query terms. Discards fluff sentences falling below 50% relative relevance, reducing prompt tokens by 42.4% and injecting tamper-proof [DOC-x] citation anchors.",
      algorithm: "Sliding-Window Pruning: Prune if score(sentence) < beta * max_score (beta=0.5)",
      parameters: {
        beta: 0.5,
        compression_ratio: "42.4%",
        citation_format: "[DOC-x]"
      },
      logic_steps: [
        "Step 1: Decompose chunks into constituent sentences",
        "Step 2: Compute lexical and entity overlap score per sentence",
        "Step 3: Retain sentences meeting the beta=0.5 threshold",
        "Step 4: Format compressed context with explicit [DOC-x] anchors"
      ]
    },
    synthesis: {
      id: "synthesis",
      title: "Stage 7: Speculative Synthesis Stream",
      subtitle: "Full-Duplex Dual Grounded Streaming on Groq LPU",
      category: "Streaming Generation",
      description: "Synthesizes final answer combining official Samsung [DOC-x] citations with broader general world knowledge for analogies. Tokens stream over Server-Sent Events (SSE) with sub-150ms TTFT.",
      algorithm: "Groq LPU Streaming Inference + SSE Protocol",
      parameters: {
        model: "Llama 3.3 70B Versatile",
        ttft: "118ms",
        velocity: "135-165 tps"
      },
      logic_steps: [
        "Step 1: Construct grounded prompt with strict Closed-World Constraint for specs",
        "Step 2: Initiate streaming completion with Groq LPU engine",
        "Step 3: Emit 'event: token' deltas in real-time as tokens are decoded",
        "Step 4: Emit 'event: telemetry' upon completion with exact latency breakdown"
      ]
    }
  }
}

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  return res.status(200).json(PIPELINE_INFO)
}
