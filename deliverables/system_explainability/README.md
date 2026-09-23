# Explainable System Directory
## Samsung PRISM GenAI Hackathon (3rd Edition, 2026–27)
### Theme 04: Streaming Live RAG (Dual-Mode Speculative Conversational System)

Welcome to the **System Explainability Hub**. This directory provides 100% white-box transparency into the architecture, mathematical formulations, codebase topology, performance benchmarks, and judge defenses for the Samsung PRISM Live Streaming RAG system.

---

## Directory Navigation

1. **[01. Domains & System Architecture](file:///home/swarnendu/hackathon-rag/deliverables/system_explainability/01_DOMAINS_AND_SYSTEM_ARCHITECTURE.md)**
   * Complete mapping of the official Hackathon organizational graph (`Tech`, `Media`, `Content/Manager`, `Deliverables`).
   * Component relationships, data flow diagrams, and domain governance.

2. **[02. Algorithmic Logic Deep Dive](file:///home/swarnendu/hackathon-rag/deliverables/system_explainability/02_ALGORITHMIC_LOGIC_DEEP_DIVE.md)**
   * Mathematical formulas for all 7 pipeline stages.
   * Intent Router dual-mode gate, BM25Okapi, MiniLM-L6-v2 vector embeddings.
   * Reciprocal Rank Fusion ($k=60$), Cross-Encoder logits ($\sigma(W \cdot H)$), sliding-window context sharpening ($\beta=0.5$), and SSE speculative streaming.

3. **[03. Source Code & Mapping Matrix](file:///home/swarnendu/hackathon-rag/deliverables/system_explainability/03_SOURCE_CODE_AND_MAPPING_MATRIX.md)**
   * File-by-file directory topology linking hackathon requirements directly to code implementations.
   * Asynchronous Python SDK and TypeScript client contracts.

4. **[04. Metrics, Telemetry & Evaluation](file:///home/swarnendu/hackathon-rag/deliverables/system_explainability/04_METRICS_TELEMETRY_AND_EVALUATION.md)**
   * Live empirical benchmarks: TTFT ($118\text{ ms}$), streaming throughput ($150+\text{ tps}$), context compression ($42.4\%$), and citation precision ($96.8\%$).
   * Hybrid vs Dense vector retrieval comparative analysis.
   * Groq LPU vs Cloud GPU hardware cost comparison.

5. **[05. Devil's Advocate Defense & Technical Rebuttals](file:///home/swarnendu/hackathon-rag/deliverables/system_explainability/05_DEVILS_ADVOCATE_DEFENSE.md)**
   * Proactive answers to tough judge questions: multi-stage latency overhead, hallucination boundaries, edge device NPU deployment, and SKU keyword matching.

6. **[06. Video Demo & Walkthrough Script](file:///home/swarnendu/hackathon-rag/deliverables/system_explainability/06_VIDEO_DEMO_WALKTHROUGH_SCRIPT.md)**
   * Turnkey 3-minute and 5-minute video recording scripts with timestamped scenes, exact queries to run, and speaking points.

---

## Live System Endpoints
* **Frontend Web App**: `http://localhost:3000`
* **In-App Pitch Deck**: `http://localhost:3000/presentation`
* **Backend REST/SSE API**: `http://localhost:8000`
* **Interactive API Documentation (Swagger)**: `http://localhost:8000/docs`
* **Pipeline Diagnostic Endpoints**:
  * `GET /api/pipeline/info` - Stage metadata and mathematical formulas.
  * `GET /api/pipeline/trace` - Live execution traces and stage latencies.
  * `POST /api/pipeline/inspect/{stage_id}` - Real-time isolated stage evaluation.
