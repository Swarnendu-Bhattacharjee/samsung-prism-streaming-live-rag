"""
Query decomposition and intent classification for full-duplex conversational RAG.
Supports semantic routing, LLM-based decomposition, and deterministic syntactic fallback.
"""

from typing import List, Literal, Dict, Any
import re
import json
import asyncio

from src.core.config import settings
from src.core.llm_client import llm_chat

IntentType = Literal["complex_multi_query", "single_factual", "midflow_refinement", "conversational_greeting"]


SYSTEM_INTENT = """\
You are an intent classification and routing engine for a real-time conversational RAG system.
Evaluate the user's natural utterance and determine:
1. "intent":
   - "conversational_greeting": greetings, farewells, simple gratitude, pleasantries (no retrieval needed)
   - "single_factual": a single specific question (needs 1 search query)
   - "complex_multi_query": contains multiple distinct questions, comparisons, or multifaceted needs (needs 2-4 sub-queries)
   - "midflow_refinement": follow-up adding constraints or details to an active conversation ("also under $1000", "what about in low light")
2. "needs_retrieval": boolean (true/false)

Output strictly valid JSON:
{"intent": "conversational_greeting"|"single_factual"|"complex_multi_query"|"midflow_refinement", "needs_retrieval": true|false, "reason": "brief rationale"}
"""

SYSTEM_DECOMPOSE = """\
You are an expert query decomposition engine.
Decompose a complex natural language command into 2 to 4 crisp, standalone search sub-queries.

Rules:
- Each sub-query must be self-contained (resolve pronouns like 'it', 'they', 'the phone' to the actual subject).
- Make sub-queries concise and keyword-rich for hybrid vector + BM25 search.
- Do NOT number or bullet the sub-queries.
- Output strictly a JSON array of strings:
["sub-query 1", "sub-query 2", ...]
"""


async def classify_intent(question: str, has_prior_context: bool = False) -> Dict[str, Any]:
    """Classify whether the utterance needs retrieval and its complexity."""
    # Fast deterministic heuristic for low latency (<2ms)
    q_lower = question.lower().strip()

    # Greetings & Chitchat
    if re.match(r'^(hi|hello|hey|good morning|good evening|thanks|thank you|bye|who are you)\b', q_lower):
        return {
            "intent": "conversational_greeting",
            "needs_retrieval": False,
            "reason": "Standard pleasantry/greeting",
            "confidence": 0.98,
        }

    # Mid-flow refinement indicators
    refinement_starters = ["and also", "also", "what about", "how about", "what if", "focusing on", "only the", "actually", "wait", "can you add"]
    if has_prior_context and any(q_lower.startswith(rf) for rf in refinement_starters):
        return {
            "intent": "midflow_refinement",
            "needs_retrieval": True,
            "reason": "Conversational mid-flow detail injection",
            "confidence": 0.92,
        }

    # Multi-part indicators
    conjunction_patterns = [
        r'\b(and also|as well as|compared to|versus|vs\.?|furthermore|in addition to)\b',
        r'(\?.*?\?)', # Multiple question marks
    ]
    is_multi_part = any(re.search(pat, q_lower) for pat in conjunction_patterns) or q_lower.count(" and ") >= 2 or len(question.split()) > 18

    # Attempt LLM classification if API key is configured
    try:
        messages = [
            {"role": "system", "content": SYSTEM_INTENT},
            {"role": "user", "content": f"Utterance: {question}"},
        ]
        resp = await asyncio.wait_for(
            llm_chat(settings.llm_inference_model, messages, temperature=0.0),
            timeout=2.0
        )
        data = json.loads(re.sub(r'```(json)?', '', resp).strip())
        return {
            "intent": data.get("intent", "complex_multi_query" if is_multi_part else "single_factual"),
            "needs_retrieval": data.get("needs_retrieval", True),
            "reason": data.get("reason", "LLM classified"),
            "confidence": 0.95,
        }
    except Exception:
        # High precision fallback
        return {
            "intent": "complex_multi_query" if is_multi_part else "single_factual",
            "needs_retrieval": True,
            "reason": "Pattern-based heuristic classification",
            "confidence": 0.88,
        }


async def decompose_query(question: str) -> List[str]:
    """Decompose a complex natural command into 2-4 standalone sub-queries."""
    # Try LLM decomposition first
    try:
        messages = [
            {"role": "system", "content": SYSTEM_DECOMPOSE},
            {"role": "user", "content": f"Decompose this utterance into search queries:\n\n{question}"},
        ]
        resp = await asyncio.wait_for(
            llm_chat(settings.llm_inference_model, messages, temperature=0.2),
            timeout=2.5
        )
        clean_resp = re.sub(r'```(json)?', '', resp).strip()
        sub_queries = json.loads(clean_resp)
        if isinstance(sub_queries, list) and len(sub_queries) > 0:
            return [sq.strip() for sq in sub_queries if len(sq.strip()) > 3][:4]
    except Exception as e:
        pass

    # Deterministic syntactic decomposition fallback
    return syntactic_decompose(question)


def syntactic_decompose(text: str) -> List[str]:
    """
    Splits compound utterances into sub-queries using syntactic boundaries,
    coordinating conjunctions, and entity associations.
    """
    clean = text.strip()

    # Split on multiple sentence or question marks
    clauses = [c.strip() for c in re.split(r'[?;]+', clean) if len(c.strip()) > 5]
    if len(clauses) > 1:
        return clauses[:4]

    # Split on conjunction markers
    split_regex = r'\b(?:and also|as well as|additionally|plus|along with|compared to|versus|vs\.?)\b'
    parts = [p.strip() for p in re.split(split_regex, clean, flags=re.IGNORECASE) if len(p.strip()) > 4]

    if len(parts) >= 2:
        # Extract main subject if mentioned in first part
        subject_match = re.search(r'\b(s24 ultra|galaxy s24|galaxy ai|z fold6|z flip6|watch ultra|buds3 pro|pto|policy)\b', parts[0], re.I)
        subject = subject_match.group(0) if subject_match else ""

        results = []
        for i, p in enumerate(parts):
            p_clean = re.sub(r'^(what about|how about|tell me about|what is|can you explain)\s+', '', p, flags=re.I).strip()
            if subject and subject.lower() not in p_clean.lower():
                results.append(f"{subject} {p_clean}")
            else:
                results.append(p_clean)
        return results[:4]

    # Split on simple commas or single ' and ' if long
    if " and " in clean and len(clean.split()) > 10:
        halves = clean.split(" and ", 1)
        return [h.strip() for h in halves if len(h.strip()) > 5]

    return [clean]
