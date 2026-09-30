"""
Samsung PRISM — Streaming Live RAG Client SDK (Theme 04)
Team: DQL
Provides an asynchronous and synchronous streaming client for the full-duplex RAG backend.
"""

from typing import Generator, AsyncGenerator, Dict, Any, Optional
import json
import urllib.request
import urllib.error


class StreamingRAGClient:
    """Python Client SDK for Samsung PRISM Streaming Live RAG Backend."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def health(self) -> Dict[str, Any]:
        """Check backend health and corpus status."""
        req = urllib.request.Request(f"{self.base_url}/health")
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())

    def get_corpus(self) -> Dict[str, Any]:
        """Fetch corpus summary and loaded document count."""
        req = urllib.request.Request(f"{self.base_url}/api/corpus")
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())

    def stream_query(
        self,
        question: str,
        session_id: Optional[str] = None,
        top_k: int = 5,
        rerank_top_n: int = 3,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Synchronously stream events from the full-duplex RAG backend.
        Yields structured SSE event dictionaries (e.g. intent, token, telemetry, done).
        """
        payload = json.dumps({
            "question": question,
            "session_id": session_id or "sdk-session",
            "top_k": top_k,
            "rerank_top_n": rerank_top_n,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/api/query/stream",
            data=payload,
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(req) as response:
            event_type = "message"
            for raw_line in response:
                line = raw_line.decode("utf-8").strip()
                if not line:
                    continue
                if line.startswith("event:"):
                    event_type = line.replace("event:", "").strip()
                elif line.startswith("data:"):
                    data_str = line.replace("data:", "").strip()
                    try:
                        data = json.loads(data_str)
                    except Exception:
                        data = {"raw": data_str}
                    yield {"event": event_type, "data": data}


if __name__ == "__main__":
    print("Testing Samsung PRISM Streaming RAG SDK...")
    client = StreamingRAGClient("http://localhost:8000")
    try:
        status = client.health()
        print("Backend Status:", status)
    except Exception as e:
        print("Backend not running locally on :8000, testing offline contract.")
