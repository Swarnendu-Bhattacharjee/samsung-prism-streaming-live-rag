"""
Entry point for the Streaming Live RAG backend.
"""

import uvicorn
from src.api.main import app
from src.core.config import settings
from src.ingestion.corpus import load_demo_corpus


def main():
    # Pre-load demo corpus
    print("Loading demo corpus...")
    count = load_demo_corpus()
    print(f"Loaded {count} chunks from demo documents")

    # Warm up embedding model
    print("Warming up embedding model...")
    from src.retrieval.hybrid import get_embed_model
    get_embed_model()
    print("Embedding model ready")

    # Warm up reranker
    print("Warming up reranker...")
    from src.retrieval.hybrid import get_rerank_model
    get_rerank_model()
    print("Reranker ready")

    print(f"\nStarting Streaming Live RAG server on {settings.host}:{settings.port}")
    print(f"API docs: http://{settings.host}:{settings.port}/docs")
    print(f"Health:   http://{settings.host}:{settings.port}/health")
    print("\nReady for queries!")

    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
