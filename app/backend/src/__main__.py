"""
Streaming Live RAG — Entry point.
Samsung Prism Hackathon · Theme 04
"""

from src.api.main import app
from src.core.config import settings
from src.ingestion.corpus import load_demo_corpus
import uvicorn


def main():
    # Pre-load demo corpus
    print("=" * 56)
    print("  Streaming Live RAG — Samsung Prism Hackathon")
    print("  Theme 04: Full-duplex conversational RAG")
    print("=" * 56)
    print()
    print("Loading demo corpus...")
    count = load_demo_corpus()
    print(f"  Loaded {count} chunks from demo documents")
    print()

    # Warm up models
    print("Warming up embedding model...")
    from src.retrieval.hybrid import get_embed_model
    get_embed_model()
    print("  ✓ Embedding model ready")
    print()

    print("Warming up reranker...")
    from src.retrieval.hybrid import get_rerank_model
    get_rerank_model()
    print("  ✓ Reranker ready")
    print()

    print(f"Starting FastAPI server on http://localhost:8000")
    print(f"  API docs: http://localhost:8000/docs")
    print(f"  Health:   http://localhost:8000/health")
    print()
    print("Ready for queries!")
    print()

    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
