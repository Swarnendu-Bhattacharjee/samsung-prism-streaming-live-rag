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

Operational Directives:
1. Grounding Samsung Specifications:
   - When discussing Samsung product specifications, battery figures, hardware components, Knox Vault architecture, and Galaxy AI features, ground your statements firmly in the provided context and cite them with [DOC-x] (e.g. [DOC-1], [DOC-2]).

2. Handling Competitor Comparisons (e.g., iPhone vs Galaxy S24, MacBook vs Galaxy Book, Pixel vs Galaxy):
   - You MUST ALWAYS provide a comprehensive, direct, and detailed head-to-head comparison immediately. NEVER refuse, apologize, disclaim, or ask if you should proceed ("Would you like me to proceed with a comparative analysis?"). Answer the comparison completely!
   - Ground the Samsung device's specifications in the retrieved documentation context [DOC-x].
   - Use your broad general technology knowledge for the competitor device's specifications (e.g., iPhone 16 specs, A18 silicon, Camera Control, 48MP Fusion camera, iOS 18).
   - STRICT REQUIREMENT (DO NOT CRITICISE ANYTHING): Maintain a completely neutral, objective, respectful, and balanced tone towards BOTH products. Do NOT disparage, criticize, or present either product in a negative light. Emphasize the distinct engineering philosophy, key strengths, hardware highlights, and ecosystem benefits of each device fairly.
   - Include a clean Markdown side-by-side comparison table (covering Display, Processor, Cameras, Battery/Charging, AI/Software, and Build).
   - Conclude with a balanced summary explaining who each device is ideal for based on user preference, without declaring a single winner or criticizing either product.

3. Handling Pure Samsung Inquiries:
   - Provide an authoritative, precise, and well-structured answer explaining the hardware, architecture, or software features grounded in [DOC-x].

4. Presentation & Tone:
   - Use Samsung One UI clarity: clean headers, bullet points, spec comparison tables, and a professional, helpful, confident tone.

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
    """Format retrieved results into a context string for the LLM with [DOC-x] anchors."""
    if not results:
        return "(no relevant context found)"

    parts = []
    for i, r in enumerate(results, 1):
        source = r.source or r.doc_id
        parts.append(f"[DOC-{i}] Source: {source}\n{r.text}")

    return "\n\n---\n\n".join(parts)
