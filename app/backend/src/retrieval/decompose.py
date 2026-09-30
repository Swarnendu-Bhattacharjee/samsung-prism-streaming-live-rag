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
You are an intelligent intent classification and routing engine for a dual-mode conversational RAG system.
The system operates with three distinct response modes:

1. "direct_general_api" (General API Mode - RAG Bypassed):
   Used when Samsung product documentation is NOT needed:
   - General world knowledge, science, history, coding (e.g., "What is photosynthesis?", "Who was Alan Turing?", "Write a python script").
   - Conversational pleasantries, greetings, chitchat (e.g., "Hi", "Tell me a joke", "How are you?").
   - Comparisons between two non-Samsung devices (e.g., "iPhone 16 vs Pixel 9").

2. "samsung_product_factual" (RAG Mode):
   Used when the user's query asks specifically about Samsung products or technology:
   - Galaxy smartphones, tablets, laptops, smartwatches, earbuds, TVs, or appliances (e.g., S24, S25 Ultra, Fold6, Flip6, Book4, Tab S10, Watch Ultra, Buds3 Pro, Neo QLED, Bespoke AI).
   - Samsung software, Knox Vault security, SmartThings, One UI, or Galaxy AI features (Circle to Search, Live Translate, Note Assist).

3. "competitor_comparison" (Balanced Hybrid RAG + General API Mode):
   Used when comparing a Samsung device with an external or competitor product (e.g., "iPhone 16 vs S24", "MacBook Pro vs Galaxy Book4 Ultra", "Pixel 9 Pro vs S24 Ultra"):
   - Needs retrieval for the Samsung device specs [DOC-x], combined with general world knowledge for the competitor device.
   - Requires a completely fair, balanced, respectful comparison without criticizing either device.

Evaluate the utterance and output strictly valid JSON:
{
  "intent": "competitor_comparison" | "samsung_product_factual" | "complex_multi_query" | "midflow_refinement" | "general_knowledge" | "conversational_greeting",
  "needs_retrieval": true | false,
  "needs_rag": true | false,
  "mode": "hybrid_rag_plus_general" | "direct_general_api",
  "reason": "Clear explanation of routing decision"
}
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
    """Classify whether the utterance needs RAG retrieval or can be served by General API."""
    q_lower = question.lower().strip()

    # 1. Greetings & Chitchat -> Direct General API (Type 1)
    if re.match(r'^(hi|hello|hey|good morning|good evening|thanks|thank you|bye|who are you|how are you|tell me a joke)\b', q_lower):
        return {
            "intent": "conversational_greeting",
            "needs_retrieval": False,
            "needs_rag": False,
            "mode": "direct_general_api",
            "reason": "Standard pleasantry/greeting; handled directly by General LLM API.",
            "confidence": 0.99,
        }

    # Mid-flow refinement indicators
    refinement_starters = ["and also", "also", "what about", "how about", "what if", "focusing on", "only the", "actually", "wait", "can you add"]
    if has_prior_context and any(q_lower.startswith(rf) for rf in refinement_starters):
        return {
            "intent": "midflow_refinement",
            "needs_retrieval": True,
            "needs_rag": True,
            "mode": "hybrid_rag_plus_general",
            "reason": "Conversational mid-flow detail injection; sharpening active context.",
            "confidence": 0.94,
        }

    # Multi-part indicators
    conjunction_patterns = [
        r'\b(and also|as well as|compared to|versus|vs\.?|furthermore|in addition to)\b',
        r'(\?.*?\?)', # Multiple question marks
    ]
    is_multi_part = any(re.search(pat, q_lower) for pat in conjunction_patterns) or q_lower.count(" and ") >= 2 or len(question.split()) > 18

    # Check for Samsung product keywords
    samsung_keywords = [
        "samsung", "galaxy", "s25", "s24", "s23", "ultra", "fold", "flip", "z fold", "z flip",
        "book5", "book4", "tab s10", "tab s9", "buds", "buds3", "watch ultra", "watch 7", "ring",
        "knox", "smartthings", "bespoke", "qled", "neo qled", "one ui", "provisual",
        "circle to search", "live translate", "note assist", "generative edit",
        "bixby", "dex", "vapor chamber", "armor aluminum", "gorilla armor",
        "dimensity 9300", "snapdragon 8 elite", "titanium"
    ]
    has_samsung_entity = any(kw in q_lower for kw in samsung_keywords)

    # Check for competitor keywords and comparison operators
    competitor_keywords = [
        "iphone", "apple", "ios", "macbook", "mac", "ipad", "airpods", "pixel",
        "google pixel", "snapdragon x elite", "intel core ultra", "dell",
        "thinkpad", "surface", "xiaomi", "oneplus", "huawei", "motorola", "oppo", "vivo"
    ]
    has_competitor = any(ck in q_lower for ck in competitor_keywords)
    has_comparison = any(re.search(pat, q_lower) for pat in [r'\b(vs\.?|versus|compare|comparison|difference between|better than)\b'])

    # 2. Competitor vs Samsung comparison (Type 3) -> competitor_comparison
    if (has_samsung_entity or has_prior_context) and (has_competitor or (has_comparison and has_competitor)):
        return {
            "intent": "competitor_comparison",
            "needs_retrieval": True,
            "needs_rag": True,
            "mode": "hybrid_rag_plus_general",
            "reason": "Balanced head-to-head comparison: Grounded Samsung specs [DOC-x] + General API competitor intelligence without bias.",
            "confidence": 0.98,
        }

    # Attempt LLM classification via Groq for precise semantic decision
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
        needs_rag = data.get("needs_rag", data.get("needs_retrieval", has_samsung_entity))
        return {
            "intent": data.get("intent", "complex_multi_query" if is_multi_part else ("samsung_product_factual" if has_samsung_entity else "general_knowledge")),
            "needs_retrieval": needs_rag,
            "needs_rag": needs_rag,
            "mode": "hybrid_rag_plus_general" if needs_rag else "direct_general_api",
            "reason": data.get("reason", "LLM classified routing requirement"),
            "confidence": 0.95,
        }
    except Exception:
        # High precision pattern-based fallback
        needs_rag = has_samsung_entity or has_prior_context
        return {
            "intent": "complex_multi_query" if (is_multi_part and needs_rag) else ("samsung_product_factual" if needs_rag else "general_knowledge"),
            "needs_retrieval": needs_rag,
            "needs_rag": needs_rag,
            "mode": "hybrid_rag_plus_general" if needs_rag else "direct_general_api",
            "reason": "Samsung product keyword detected -> RAG retrieved" if needs_rag else "General knowledge query -> Direct General API call",
            "confidence": 0.90,
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
    q_lower = clean.lower()

    # 1. Competitor vs Samsung comparison (e.g. "iphone 16 vs s24")
    competitor_keywords = ["iphone", "apple", "macbook", "pixel", "ipad", "airpods"]
    is_comparison = any(re.search(pat, q_lower) for pat in [r'\b(vs\.?|versus|compare|comparison|difference between)\b'])
    has_competitor = any(ck in q_lower for ck in competitor_keywords)

    if is_comparison and has_competitor:
        samsung_target = "Samsung Galaxy"
        if "s25 ultra" in q_lower: samsung_target = "Samsung Galaxy S25 Ultra"
        elif "s25" in q_lower: samsung_target = "Samsung Galaxy S25"
        elif "s24 ultra" in q_lower: samsung_target = "Samsung Galaxy S24 Ultra"
        elif "s24+" in q_lower or "s24 plus" in q_lower: samsung_target = "Samsung Galaxy S24+"
        elif "s24" in q_lower: samsung_target = "Samsung Galaxy S24"
        elif "s23 ultra" in q_lower: samsung_target = "Samsung Galaxy S23 Ultra"
        elif "s23" in q_lower: samsung_target = "Samsung Galaxy S23"
        elif "fold6" in q_lower or "fold 6" in q_lower: samsung_target = "Samsung Galaxy Z Fold6"
        elif "flip6" in q_lower or "flip 6" in q_lower: samsung_target = "Samsung Galaxy Z Flip6"
        elif "book4" in q_lower or "book 4" in q_lower: samsung_target = "Samsung Galaxy Book4 Ultra"
        elif "book5" in q_lower or "book 5" in q_lower: samsung_target = "Samsung Galaxy Book5"
        elif "tab s10" in q_lower: samsung_target = "Samsung Galaxy Tab S10 Ultra"
        elif "watch ultra" in q_lower: samsung_target = "Samsung Galaxy Watch Ultra"
        elif "buds3" in q_lower: samsung_target = "Samsung Galaxy Buds3 Pro"
        elif "ring" in q_lower: samsung_target = "Samsung Galaxy Ring"

        return [
            f"{samsung_target} display dynamic amoled and camera specifications",
            f"{samsung_target} processor chipset battery charging specifications",
            f"{samsung_target} Galaxy AI features and hardware architecture",
        ]

    # 2. Samsung vs Samsung comparison (e.g. "S25 Ultra vs S24 Ultra")
    if is_comparison and "s25" in q_lower and "s24" in q_lower:
        return [
            "Samsung Galaxy S25 Ultra processor Snapdragon 8 Elite titanium camera",
            "Samsung Galaxy S24 Ultra processor Snapdragon 8 Gen 3 titanium camera",
            "Galaxy S25 Ultra vs Galaxy S24 Ultra comparison specifications",
        ]

    # Split on multiple sentence or question marks
    clauses = [c.strip() for c in re.split(r'[?;]+', clean) if len(c.strip()) > 5]
    if len(clauses) > 1:
        return clauses[:4]

    # Split on conjunction markers
    split_regex = r'\b(?:and also|as well as|additionally|plus|along with|compared to|versus|vs\.?)\b'
    parts = [p.strip() for p in re.split(split_regex, clean, flags=re.IGNORECASE) if len(p.strip()) >= 3]

    if len(parts) >= 2:
        subject_match = re.search(r'\b(s25 ultra|s24 ultra|galaxy s24|galaxy ai|z fold6|z flip6|watch ultra|buds3 pro|tab s10)\b', clean, re.I)
        subject = subject_match.group(0) if subject_match else ""

        results = []
        for p in parts:
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
