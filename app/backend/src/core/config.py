"""
Core configuration for Streaming Live RAG (Samsung PRISM Theme 04).
Powered by Groq LPU for high-speed full-duplex inference.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # LLM Provider: "groq", "gemini", "openai", "anthropic", "ollama", or "local"
    llm_provider: str = "groq"

    # Groq Models (Frontier 120B for synthesis, fast 20B for decomposition)
    llm_model: str = "openai/gpt-oss-120b"
    llm_inference_model: str = "openai/gpt-oss-20b"

    # Embedding model (CPU/GPU lightweight)
    embedding_model: str = "all-MiniLM-L6-v2"

    # Cross-encoder reranker
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Retrieval parameters
    top_k: int = 5
    rerank_top_n: int = 3
    rerank_candidate_multiplier: int = 3
    rrf_k: int = 60

    # Chunking
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Speculative early-retrieval
    speculative_char_threshold: int = 20
    speculative_enabled: bool = True

    # Mid-flow sharpening boost
    context_retention_boost: float = 0.25

    # API Keys
    groq_api_key: str = os.environ.get("GROQ_API_KEY", "your_groq_api_key_here")
    gemini_api_key: Optional[str] = os.environ.get("GEMINI_API_KEY", "")
    openai_api_key: Optional[str] = os.environ.get("OPENAI_API_KEY", "")
    anthropic_api_key: Optional[str] = os.environ.get("ANTHROPIC_API_KEY", "")

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
