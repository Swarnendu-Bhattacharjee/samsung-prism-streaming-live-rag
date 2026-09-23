"""
Synthesizer: Dual-mode grounded streaming generator.
Supports:
1. Hybrid Grounded RAG + General API data synthesis (Samsung Context + General Knowledge).
2. Direct General API streaming (when RAG is bypassed for general queries).
Streams tokens via SSE-compatible async generator.
"""

from typing import List, AsyncGenerator
import asyncio

from src.retrieval.hybrid import RetrievalResult
from src.core.llm_client import llm_stream
from src.core.config import settings


SYSTEM_SYNTH_HYBRID = """\
You are an advanced Samsung AI Specialist powered by Groq LPU Ultra-Fast Inference.
You have access to TWO complementary information sources:
1. Grounded Samsung Product Documentation (retrieved via our Hybrid Vector + BM25 RRF & Cross-Encoder pipeline).
2. Broad general world knowledge, engineering principles, competitor specifications, and technical reasoning.

Instructions:
- When discussing Samsung product specifications, battery figures, hardware components, Knox Vault architecture, and Galaxy AI features, ground your statements firmly in the provided context and cite them with [Source X].
- You are EXPLICITLY PERMITTED and ENCOURAGED to use your general world knowledge and technical reasoning alongside the context—for example, explaining technical engineering concepts, providing fair comparisons with competitor devices (like iPhone, Pixel, or standard PC laptops), giving code examples, or answering general follow-up questions.
- Maintain a helpful, confident, articulate, and professional tone.

Context (retrieved and reranked):
{context}

Question: {question}
"""

SYSTEM_GENERAL_API = """\
You are an intelligent, articulate, and helpful AI assistant powered by Groq LPU Ultra-Fast Inference.
The user asked a general question or conversational query that does not require proprietary Samsung product documentation retrieval.
Respond directly, accurately, and comprehensively to the user's request using your broad general knowledge, technical expertise, coding ability, or reasoning skills.
Be clear, insightful, and engaging.
"""


async def synthesize_stream(
    question: str,
    results: List[RetrievalResult],
    session_id: str = "",
) -> AsyncGenerator[str, None]:
    """
    Stream a hybrid grounded answer based on BOTH retrieved Samsung context
    AND general LLM world knowledge.
    """
    context = _format_context(results)

    messages = [
        {"role": "system", "content": SYSTEM_SYNTH_HYBRID.format(
            context=context,
            question=question,
        )},
        {"role": "user", "content": question},
    ]

    async for token in llm_stream(
        model=settings.llm_model,
        messages=messages,
        temperature=0.3,
    ):
        yield token


async def synthesize_general_stream(
    question: str,
    session_id: str = "",
) -> AsyncGenerator[str, None]:
    """
    Stream a general answer directly from Groq LLM API without document retrieval.
    Used when the intent classifier determines no RAG retrieval is required.
    """
    messages = [
        {"role": "system", "content": SYSTEM_GENERAL_API},
        {"role": "user", "content": question},
    ]

    async for token in llm_stream(
        model=settings.llm_model,
        messages=messages,
        temperature=0.5,
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
