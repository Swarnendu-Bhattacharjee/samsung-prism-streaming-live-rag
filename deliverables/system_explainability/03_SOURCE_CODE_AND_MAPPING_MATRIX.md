# 03. Source Code & Mapping Matrix
## Samsung PRISM GenAI Hackathon (Theme 04: Streaming Live RAG)

This document provides a component-by-component traceability matrix linking every architectural layer to exact file locations and code implementations across the repository.

---

## 1. Codebase Directory Topology

```
hackathon-rag/
├── app/
│   ├── backend/                        # FastAPI High-Performance Python Backend
│   │   ├── src/
│   │   │   ├── __main__.py             # Uvicorn entry point and CLI runner
│   │   │   ├── client.py               # Asynchronous Python SDK Client
│   │   │   ├── api/
│   │   │   │   ├── __init__.py
│   │   │   │   └── main.py             # FastAPI App, SSE query_stream & pipeline endpoints
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py           # Settings, Groq API keys, model configs
│   │   │   │   ├── models.py           # Pydantic models for queries, chunks, telemetry
│   │   │   │   └── synthesizer.py      # Speculative streaming synthesis & dual-mode logic
│   │   │   ├── retrieval/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── corpus.py           # Samsung product corpus seed data & documents
│   │   │   │   ├── decompose.py        # Intent router & multi-subquery decomposer
│   │   │   │   ├── hybrid.py           # BM25 + ChromaDB Dense Vector Search
│   │   │   │   ├── rrf.py              # Reciprocal Rank Fusion implementation (k=60)
│   │   │   │   ├── cross_encoder.py    # Neural Cross-Attention Re-ranking
│   │   │   │   └── sharpening.py       # Sliding-window token pruning (beta=0.5)
│   │   │   └── telemetry/
│   │   │       ├── __init__.py
│   │   │       └── collector.py        # Real-time metrics collector (TTFT, P99, tokens/sec)
│   │   ├── tests/                      # Automated pytest validation suite
│   │   ├── requirements.txt            # Python dependencies (fastapi, chromadb, groq, etc.)
│   │   └── backend-venv/               # Virtual environment
│   └── frontend/                       # Next.js 14 React Frontend (Samsung One UI)
│       ├── components/
│       │   ├── ChatInterface.tsx       # Message thread with stream token animation
│       │   ├── MessageItem.tsx         # Clean Samsung One UI message bubble & citations
│       │   ├── PipelineInspector.tsx   # Interactive 8-stage visual pipeline inspector
│       │   ├── TelemetryPanel.tsx      # Real-time latency, TTFT, and stage distribution charts
│       │   ├── CorpusManager.tsx       # Samsung product knowledge-base management UI
│       │   └── ScenarioSelector.tsx    # One-click hackathon demo queries
│       ├── pages/
│       │   ├── _app.tsx                # Next.js App wrapper & global styles
│       │   ├── index.tsx               # Main live interactive RAG dashboard
│       │   └── presentation.tsx        # In-App 12-slide interactive pitch deck
│       ├── styles/
│       │   └── globals.css             # Tailwind CSS & One UI Decent White tokens
│       ├── package.json                # Frontend dependencies
│       ├── next.config.js              # Next.js config & backend API proxy rewrites
│       └── vercel.json                 # Vercel deployment configuration
├── deliverables/                       # Official Hackathon Deliverables
│   ├── system_explainability/          # Explainable system documentation
│   ├── Samsung_PRISM_Live_Streaming_RAG_Pitch.pptx # Compiled PowerPoint deck
│   └── HACKATHON_PRESENTATION_GUIDE.md # Live presentation & speaking script
└── README.md                           # Master README & Developer Quickstart
```

---

## 2. Component Traceability Matrix

| Diagram Node | Architectural Layer | Primary Source File(s) | Key Functions / Classes |
| :--- | :--- | :--- | :--- |
| **`Tech -> mapping/source code`** | Product Knowledge Base | `app/backend/src/retrieval/corpus.py` | `get_default_corpus()`, `CorpusDocument`, `ProductSpec` |
| **`Tech -> Logic: Stage 0`** | Intent Router & Gate | `app/backend/src/retrieval/decompose.py` | `classify_intent()`, `needs_rag` decision gate |
| **`Tech -> Logic: Stage 1`** | Speculative Decomposer | `app/backend/src/retrieval/decompose.py` | `decompose_query()`, `speculative_prefetch()` |
| **`Tech -> Logic: Stage 2`** | Parallel Hybrid Search | `app/backend/src/retrieval/hybrid.py` | `BM25Index.search()`, `ChromaVectorStore.search()` |
| **`Tech -> Logic: Stage 3`** | Reciprocal Rank Fusion | `app/backend/src/retrieval/rrf.py` | `reciprocal_rank_fusion()`, $k=60$ normalization |
| **`Tech -> Logic: Stage 4`** | Cross-Encoder Re-Rank | `app/backend/src/retrieval/cross_encoder.py` | `CrossEncoderRanker.rerank()`, sigmoid scoring |
| **`Tech -> Logic: Stage 5`** | Context Sharpening | `app/backend/src/retrieval/sharpening.py` | `ContextSharpener.sharpen()`, $\beta=0.5$ pruning |
| **`Tech -> Logic: Stage 6`** | Speculative Stream | `app/backend/src/core/synthesizer.py` | `synthesize_stream()`, `synthesize_general_stream()` |
| **`Tech -> app: Backend`** | Asynchronous API Engine | `app/backend/src/api/main.py` | `query_stream()`, `/api/pipeline/*` endpoints |
| **`Tech -> app: Frontend`** | Interactive Client UI | `app/frontend/pages/index.tsx` | Main dashboard, SSE stream receiver, mode badge |
| **`Tech -> app: Inspector`** | Pipeline Visualizer | `app/frontend/components/PipelineInspector.tsx` | Stage execution trace, math formula modal, runner |
| **`Tech -> APK/SDK`** | Client Protocol Contract | `app/backend/src/client.py` | `LiveRAGClient.stream_query()`, async generator |
| **`Content/Manager -> Design`**| Samsung One UI Theme | `app/frontend/styles/globals.css` | Decent White palette, One UI pills, typography |
| **`Content/Manager -> Data`**| Real-Time Telemetry | `app/backend/src/telemetry/collector.py` | `TelemetryCollector.record_stage()`, TTFT metrics |
| **`Media -> ppt`** | Pitch Deck & Web Deck | `deliverables/Samsung_PRISM_Live_Streaming_RAG_Pitch.pptx`, `app/frontend/pages/presentation.tsx` | 12-slide structured pitch deck |
| **`Media -> README`** | Documentation & Guide | `README.md`, `HACKATHON_PRESENTATION_GUIDE.md` | Minute-by-minute speaking script, setup steps |

---

## 3. Client Protocol & API Contract (SDK)

The system exposes an asynchronous streaming protocol compliant with modern streaming SDKs:

```python
# SDK Client Example (app/backend/src/client.py)
import asyncio
from src.client import LiveRAGClient

async def main():
    client = LiveRAGClient(base_url="http://localhost:8000")
    
    # Dual-mode streaming handles both RAG and General queries automatically
    async for event in client.stream_query("Compare Galaxy S25 Ultra vs S24 Ultra display"):
        if event.type == "metadata":
            print(f"Mode: {event.data['mode']}, Sources: {len(event.data['sources'])}")
        elif event.type == "token":
            print(event.data["delta"], end="", flush=True)
        elif event.type == "telemetry":
            print(f"\n[TTFT: {event.data['ttft_ms']}ms | Speed: {event.data['tokens_per_sec']} tps]")

asyncio.run(main())
```
