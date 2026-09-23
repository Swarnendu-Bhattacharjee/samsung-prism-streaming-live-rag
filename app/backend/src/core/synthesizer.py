"""
Synthesizer: combine retrieved context into a grounded answer.
Streams tokens via SSE-compatible async generator.
"""

from typing import List, AsyncGenerator
import asyncio

from src.retrieval.hybrid import RetrievalResult
from src.core.llm_client import llm_stream
from src.core.config import settings


SYSTEM_SYNTH = """\
You are a helpful assistant for a document Q&A system.
Answer the user's question using ONLY the provided context.
Do NOT hallucinate or make up information not in the context.
Cite sources by mentioning the document they come from.

Context (retrieved and reranked):
{context}

Question: {question}

Instructions:
- Answer concisely and accurately
- Reference the source document when citing facts
- If the context doesn't contain enough information, say so
- Use the language the question was asked in
"""


async def synthesize_stream(
    question: str,
    results: List[RetrievalResult],
    session_id: str = "",
) -> AsyncGenerator[str, None]:
    """
    Stream a grounded answer based on retrieved and reranked context.
    Yields tokens one at a time for SSE delivery.
    """
    # Format context from results
    context = _format_context(results)

    messages = [
        {"role": "system", "content": SYSTEM_SYNTH.format(
            context=context,
            question=question,
        )},
        {"role": "user", "content": question},
    ]

    # Stream from LLM
    async for token in llm_stream(
        model=settings.llm_model,
        messages=messages,
        temperature=0.3,
    ):
        yield token


def _format_context(results: List[RetrievalResult]) -> str:
    """Format retrieved results into a context string for the LLM."""
    if not results:
        return "(no relevant context found)"

    parts = []
    for i, r in enumerate(results, 1):
        source = r.source or r.doc_id
        parts.append(f"[Source {i}: {source}]\n{r.text}")

    return "\n\n---\n\n".join(parts)
