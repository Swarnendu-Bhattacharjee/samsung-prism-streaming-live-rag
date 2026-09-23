"""
LLM client supporting Groq LPU, Google Gemini, OpenAI, Anthropic, Ollama,
and high-quality local offline extractive synthesis.
"""

from typing import List, Optional, AsyncGenerator
import os
import re
import asyncio
import json

from src.core.config import settings

# ── Provider Detection ─────────────────────────────────────────────────────────

def _detect_provider(model: str) -> str:
    """Detect LLM provider from settings or model name."""
    if settings.llm_provider and settings.llm_provider != "auto":
        return settings.llm_provider.lower()

    if settings.groq_api_key or os.environ.get("GROQ_API_KEY"):
        return "groq"

    name = model.lower()
    if "gemini" in name:
        return "gemini"
    if "claude" in name:
        return "anthropic"
    if any(t in name for t in ("llama", "qwen", "deepseek", "phi", "gemma", "ollama")):
        return "ollama"
    return "openai"


# ── Unified Chat Completion ───────────────────────────────────────────────────

async def llm_chat(
    model: str,
    messages: List[dict],
    temperature: float = 0.0,
    max_tokens: int = 2048,
) -> str:
    """Chat completion returning complete response text."""
    provider = _detect_provider(model)

    if provider == "groq":
        return await _groq_chat(model, messages, temperature, max_tokens)
    elif provider == "gemini":
        return await _gemini_chat(model, messages, temperature, max_tokens)
    elif provider == "openai":
        return await _openai_chat(model, messages, temperature, max_tokens)
    elif provider == "anthropic":
        return await _anthropic_chat(model, messages, temperature, max_tokens)
    elif provider == "ollama":
        return await _ollama_chat(model, messages, temperature, max_tokens)
    else:
        return _offline_chat(messages)


# ── Unified Token Streaming ───────────────────────────────────────────────────

async def llm_stream(
    model: str,
    messages: List[dict],
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> AsyncGenerator[str, None]:
    """Stream chat completions token-by-token."""
    provider = _detect_provider(model)

    if provider == "groq":
        async for token in _groq_stream(model, messages, temperature, max_tokens):
            yield token
    elif provider == "gemini":
        async for token in _gemini_stream(model, messages, temperature, max_tokens):
            yield token
    elif provider == "openai":
        async for token in _openai_stream(model, messages, temperature, max_tokens):
            yield token
    elif provider == "anthropic":
        async for token in _anthropic_stream(model, messages, temperature, max_tokens):
            yield token
    elif provider == "ollama":
        async for token in _ollama_stream(model, messages, temperature, max_tokens):
            yield token
    else:
        async for token in _offline_stream(messages):
            yield token


# ── Groq Provider (Ultra-Fast LPU) ────────────────────────────────────────────

def _get_groq_key() -> str:
    return settings.groq_api_key or os.environ.get("GROQ_API_KEY", "")

async def _groq_chat(model: str, messages: List[dict], temperature: float, max_tokens: int) -> str:
    api_key = _get_groq_key()
    if not api_key:
        return _offline_chat(messages)
    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=api_key)
        # Use valid Groq model
        groq_model = model if ("gpt-oss" in model or "qwen" in model) else "openai/gpt-oss-20b"
        response = await client.chat.completions.create(
            model=groq_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        print(f"[Groq Chat Error]: {e}, falling back to offline generator")
        return _offline_chat(messages)


async def _groq_stream(model: str, messages: List[dict], temperature: float, max_tokens: int) -> AsyncGenerator[str, None]:
    api_key = _get_groq_key()
    if not api_key:
        async for token in _offline_stream(messages):
            yield token
        return
    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=api_key)
        groq_model = model if ("gpt-oss" in model or "qwen" in model) else "openai/gpt-oss-120b"
        stream = await client.chat.completions.create(
            model=groq_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as e:
        print(f"[Groq Stream Error]: {e}, falling back to offline stream")
        async for token in _offline_stream(messages):
            yield token


# ── Gemini Provider ───────────────────────────────────────────────────────────

def _get_gemini_key() -> Optional[str]:
    return (
        settings.gemini_api_key
        or os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
    )

async def _gemini_chat(model: str, messages: List[dict], temperature: float, max_tokens: int) -> str:
    api_key = _get_gemini_key()
    if not api_key:
        return _offline_chat(messages)
    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        prompt = "\n\n".join(
            f"{m.get('role', 'user').upper()}: {m.get('content', '')}"
            for m in messages
        )
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model if "gemini" in model else "gemini-2.5-flash",
            contents=prompt,
        )
        return response.text or ""
    except Exception as e:
        print(f"[Gemini Error]: {e}, falling back to offline generator")
        return _offline_chat(messages)


async def _gemini_stream(model: str, messages: List[dict], temperature: float, max_tokens: int) -> AsyncGenerator[str, None]:
    api_key = _get_gemini_key()
    if not api_key:
        async for token in _offline_stream(messages):
            yield token
        return
    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        prompt = "\n\n".join(
            f"{m.get('role', 'user').upper()}: {m.get('content', '')}"
            for m in messages
        )
        response_stream = await asyncio.to_thread(
            client.models.generate_content_stream,
            model=model if "gemini" in model else "gemini-2.5-flash",
            contents=prompt,
        )
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
                await asyncio.sleep(0.01)
    except Exception as e:
        print(f"[Gemini Stream Error]: {e}, falling back to offline stream")
        async for token in _offline_stream(messages):
            yield token


# ── OpenAI Provider ───────────────────────────────────────────────────────────

def _get_openai_key() -> Optional[str]:
    return settings.openai_api_key or os.environ.get("OPENAI_API_KEY")

async def _openai_chat(model: str, messages: List[dict], temperature: float, max_tokens: int) -> str:
    api_key = _get_openai_key()
    if not api_key:
        return _offline_chat(messages)
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        print(f"[OpenAI Error]: {e}, using offline fallback")
        return _offline_chat(messages)


async def _openai_stream(model: str, messages: List[dict], temperature: float, max_tokens: int) -> AsyncGenerator[str, None]:
    api_key = _get_openai_key()
    if not api_key:
        async for token in _offline_stream(messages):
            yield token
        return
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
                await asyncio.sleep(0.005)
    except Exception as e:
        print(f"[OpenAI Stream Error]: {e}")
        async for token in _offline_stream(messages):
            yield token


# ── Anthropic Provider ────────────────────────────────────────────────────────

def _get_anthropic_key() -> Optional[str]:
    return settings.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")

async def _anthropic_chat(model: str, messages: List[dict], temperature: float, max_tokens: int) -> str:
    api_key = _get_anthropic_key()
    if not api_key:
        return _offline_chat(messages)
    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=api_key)
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msgs = [m for m in messages if m["role"] != "system"]

        res = await client.messages.create(
            model=model if "claude" in model else "claude-3-5-haiku-20241022",
            max_tokens=max_tokens,
            system=system_msg,
            messages=user_msgs,
            temperature=temperature,
        )
        return res.content[0].text
    except Exception as e:
        print(f"[Anthropic Error]: {e}")
        return _offline_chat(messages)


async def _anthropic_stream(model: str, messages: List[dict], temperature: float, max_tokens: int) -> AsyncGenerator[str, None]:
    api_key = _get_anthropic_key()
    if not api_key:
        async for token in _offline_stream(messages):
            yield token
        return
    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=api_key)
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msgs = [m for m in messages if m["role"] != "system"]

        async with client.messages.stream(
            model=model if "claude" in model else "claude-3-5-haiku-20241022",
            max_tokens=max_tokens,
            system=system_msg,
            messages=user_msgs,
            temperature=temperature,
        ) as stream:
            async for text in stream.text_stream:
                yield text
                await asyncio.sleep(0.005)
    except Exception as e:
        print(f"[Anthropic Stream Error]: {e}")
        async for token in _offline_stream(messages):
            yield token


# ── Ollama Provider (Local Server) ────────────────────────────────────────────

async def _ollama_chat(model: str, messages: List[dict], temperature: float, max_tokens: int) -> str:
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "http://localhost:11434/api/chat",
                json={"model": model, "messages": messages, "stream": False},
            )
            if resp.status_code == 200:
                return resp.json().get("message", {}).get("content", "")
    except Exception:
        pass
    return _offline_chat(messages)


async def _ollama_stream(model: str, messages: List[dict], temperature: float, max_tokens: int) -> AsyncGenerator[str, None]:
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream(
                "POST",
                "http://localhost:11434/api/chat",
                json={"model": model, "messages": messages, "stream": True},
            ) as response:
                if response.status_code == 200:
                    async for line in response.aiter_lines():
                        if line:
                            data = json.loads(line)
                            chunk = data.get("message", {}).get("content", "")
                            if chunk:
                                yield chunk
                                await asyncio.sleep(0.01)
                    return
    except Exception:
        pass
    async for token in _offline_stream(messages):
        yield token


# ── High-Quality Offline Grounded Synthesizer ───────────────────────────────────

def _extract_question_and_context(messages: List[dict]) -> tuple[str, str]:
    question = ""
    context = ""
    for m in messages:
        c = m.get("content", "")
        if m.get("role") == "user":
            question = c
        elif m.get("role") == "system" and "Context (retrieved and reranked):" in c:
            parts = c.split("Context (retrieved and reranked):")
            if len(parts) > 1:
                context = parts[1].split("Question:")[0].strip()
    return question, context


def _offline_chat(messages: List[dict]) -> str:
    question, context = _extract_question_and_context(messages)

    if not context or "(no relevant context found)" in context:
        return f"Based on Samsung product documentation, I could not locate details addressing: \"{question}\"."

    sources = []
    current_source = "Source"
    current_text = []

    for line in context.split("\n"):
        line_clean = line.strip()
        if line_clean.startswith("[Source") and "]" in line_clean:
            if current_text:
                sources.append((current_source, " ".join(current_text)))
                current_text = []
            current_source = line_clean.replace("[", "").replace("]", "")
        elif line_clean and not line_clean.startswith("---"):
            current_text.append(line_clean)
    if current_text:
        sources.append((current_source, " ".join(current_text)))

    response_lines = [
        f"### Grounded Response for: *\"{question}\"*\n",
    ]

    for src_name, src_content in sources[:3]:
        sentences = [s.strip() for s in re.split(r'(?<=[.?!])\s+', src_content) if len(s.strip()) > 20]
        summary_sentences = sentences[:3]
        if summary_sentences:
            response_lines.append(f"**From {src_name}:**")
            for sent in summary_sentences:
                response_lines.append(f"• {sent}")
            response_lines.append("")

    return "\n".join(response_lines)


async def _offline_stream(messages: List[dict]) -> AsyncGenerator[str, None]:
    full_text = _offline_chat(messages)
    words = re.findall(r'\S+|\n', full_text)
    for word in words:
        if word == '\n':
            yield '\n'
        else:
            yield word + ' '
        await asyncio.sleep(0.01)
