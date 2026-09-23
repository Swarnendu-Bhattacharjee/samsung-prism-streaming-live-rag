"""
Full-Duplex: Real-time Multimodal Streaming

A framework for bidirectional streaming communication with multimodal models (MMMs).
Provides abstractions for modeling perception and expression as concurrent streams
of symbols.

Quick Start:
    from full_duplex import GeminiStream, GeminiConfig, Symbol

    async with GeminiStream(GeminiConfig()) as stream:
        # Send audio
        await stream.send(Symbol.audio(audio_bytes))
        await stream.send_end()

        # Receive response
        async for item in stream.receive():
            if isinstance(item, Symbol):
                process(item)

Core Concepts:
    - Symbol: Atomic unit of perception/expression (audio chunk, text token, etc.)
    - DuplexStream: Bidirectional channel for sending/receiving symbols
    - StreamEvent: Lifecycle and control signals (connect, disconnect, interrupt)

Backends:
    - GeminiStream: Google Gemini Live API (cloud, multimodal)
    - (Future) LocalStream: Local models via llama.cpp, etc.
"""

from .stream import (
    # Core types
    Symbol,
    StreamEvent,
    StreamItem,
    Modality,

    # Abstract interface
    DuplexStream,
    DuplexSession,

    # Factory type
    StreamFactory,
)

from .gemini import (
    GeminiStream,
    GeminiConfig,
    create_gemini_stream,
)

__version__ = "0.1.0"
__all__ = [
    # Core types
    "Symbol",
    "StreamEvent",
    "StreamItem",
    "Modality",

    # Abstract interface
    "DuplexStream",
    "DuplexSession",
    "StreamFactory",

    # Gemini backend
    "GeminiStream",
    "GeminiConfig",
    "create_gemini_stream",
]
