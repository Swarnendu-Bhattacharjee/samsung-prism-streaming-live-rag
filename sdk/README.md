# 📦 Samsung PRISM Streaming Live RAG Client SDK
**Theme 04: Full-Duplex Streaming Conversational RAG**  
**Team: DQL**

A lightweight, zero-dependency Python SDK to interact with the Streaming Live RAG backend over Server-Sent Events (SSE).

---

## 🚀 Quick Usage

```python
from sdk.samsung_rag_client import StreamingRAGClient

# Initialize client
client = StreamingRAGClient(base_url="http://localhost:8000")

# 1. Health check
print(client.health())

# 2. Stream a comparative query with live event processing
for msg in client.stream_query("iphone 16 vs s24"):
    event = msg["event"]
    data = msg["data"]
    
    if event == "intent":
        print(f"Routing Intent: {data.get('intent')} (Needs RAG: {data.get('needs_rag')})")
    elif event == "token":
        print(data.get("token", ""), end="", flush=True)
    elif event == "telemetry":
        print(f"\n[Telemetry] TTFT: {data.get('ttft_ms')}ms | Recall: {data.get('recall')}")
```

---

## ⚡ Supported Events
- `pipeline_start`: Initial timestamp and session handshake.
- `intent`: Low-latency intent classification (`direct_general_api`, `samsung_product_factual`, or `competitor_comparison`).
- `routing_decision`: Explicit routing mode and architectural reason.
- `decomposition`: Sub-queries emitted by the query decomposer.
- `sub_query_step`: Parallel sparse and dense retrieval candidate count.
- `fusion`: Reciprocal Rank Fusion statistics ($k=60$).
- `sharpening`: Context sentence pruning stats ($\beta=0.5$).
- `sources`: Grounded verified `[DOC-x]` candidate metadata.
- `token`: Incremental streaming token with TTFT latency.
- `telemetry`: Final recall, groundedness score, TTFT, and cost metrics.
- `done`: Stream completion.
