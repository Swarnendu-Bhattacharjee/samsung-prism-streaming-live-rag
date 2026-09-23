"""
Gemini Live API Backend

Implements the DuplexStream interface for Google's Gemini Live API,
enabling real-time bidirectional audio/text communication with
multimodal models.
"""

import os
import asyncio
from typing import AsyncIterator, Optional, Any
from dataclasses import dataclass, field

from .stream import (
    DuplexStream, Symbol, StreamEvent, StreamItem,
    Modality
)

# Gemini SDK import (deferred to allow module to load without it)
_genai = None
_types = None


def _ensure_genai():
    """Lazy import of google-genai SDK."""
    global _genai, _types
    if _genai is None:
        try:
            from google import genai
            from google.genai import types
            _genai = genai
            _types = types
        except ImportError:
            raise ImportError(
                "Gemini backend requires 'google-genai' package. "
                "Install with: pip install google-genai"
            )
    return _genai, _types


@dataclass
class GeminiConfig:
    """Configuration for Gemini Live connection."""
    model: str = "gemini-live-2.5-flash-preview"
    api_key: Optional[str] = None  # Falls back to GOOGLE_API_KEY env var

    # Audio settings
    input_sample_rate: int = 16000
    output_sample_rate: int = 24000

    # Response configuration
    response_modalities: list = field(default_factory=lambda: ["AUDIO"])

    # System instruction
    system_instruction: Optional[str] = None

    # Generation config
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None


class GeminiStream(DuplexStream):
    """
    Full-duplex stream implementation for Gemini Live API.

    Wraps the google-genai library's native audio session to provide
    a standardized streaming interface. Supports real-time audio
    input/output with transcription.

    Example:
        async with GeminiStream(GeminiConfig()) as stream:
            # Send audio
            await stream.send(Symbol.audio(audio_bytes))
            await stream.send_end()

            # Receive response
            async for item in stream.receive():
                if isinstance(item, Symbol):
                    play_audio(item.data)
    """

    def __init__(self, config: Optional[GeminiConfig] = None):
        self.config = config or GeminiConfig()
        self._client = None
        self._session = None
        self._session_context = None
        self._connected = False
        self._receive_queue: asyncio.Queue[StreamItem] = asyncio.Queue()
        self._receive_task: Optional[asyncio.Task] = None

    async def connect(self) -> None:
        """Establish connection to Gemini Live API."""
        if self._connected:
            return

        genai, types = _ensure_genai()

        # Initialize client
        api_key = self.config.api_key or os.environ.get("GOOGLE_API_KEY")
        if api_key:
            self._client = genai.Client(api_key=api_key)
        else:
            self._client = genai.Client()

        # Build session config
        session_config = {
            "response_modalities": self.config.response_modalities
        }

        if self.config.system_instruction:
            session_config["system_instruction"] = self.config.system_instruction

        # Connect to live session
        self._session_context = self._client.aio.live.connect(
            model=self.config.model,
            config=session_config
        )
        self._session = await self._session_context.__aenter__()
        self._connected = True

        # Start background receiver
        self._receive_task = asyncio.create_task(self._receive_loop())

    async def disconnect(self) -> None:
        """Close the Gemini Live session."""
        if not self._connected:
            return

        # Cancel receiver
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass

        # Close session
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)

        self._session = None
        self._session_context = None
        self._client = None
        self._connected = False

        # Signal end to any receivers
        await self._receive_queue.put(StreamEvent(type="disconnected"))

    async def send(self, symbol: Symbol) -> None:
        """Send a symbol to Gemini."""
        if not self._connected:
            raise RuntimeError("Stream not connected")

        _, types = _ensure_genai()

        if symbol.modality == Modality.AUDIO:
            await self._session.send_realtime_input(
                audio=types.Blob(
                    data=symbol.data,
                    mime_type=symbol.mime_type
                )
            )
        elif symbol.modality == Modality.TEXT:
            await self._session.send_realtime_input(
                text=symbol.text_value
            )
        else:
            raise ValueError(f"Unsupported modality for Gemini: {symbol.modality}")

    async def send_end(self) -> None:
        """Signal end of audio input stream."""
        if not self._connected:
            raise RuntimeError("Stream not connected")

        await self._session.send_realtime_input(audio_stream_end=True)

    async def _receive_loop(self) -> None:
        """Background task to receive from Gemini and queue items."""
        try:
            async for msg in self._session.receive():
                # Handle text (usually transcription)
                if getattr(msg, "text", None):
                    symbol = Symbol.text(
                        msg.text,
                        transcription=True  # Mark as transcription
                    )
                    await self._receive_queue.put(symbol)

                # Handle audio data
                if getattr(msg, "data", None):
                    symbol = Symbol.audio(
                        msg.data,
                        sample_rate=self.config.output_sample_rate
                    )
                    await self._receive_queue.put(symbol)

            # Session ended normally
            await self._receive_queue.put(StreamEvent(type="stream_end"))

        except asyncio.CancelledError:
            raise
        except Exception as e:
            await self._receive_queue.put(
                StreamEvent(type="error", data=str(e))
            )

    async def receive(self) -> AsyncIterator[StreamItem]:
        """Iterate over received symbols and events."""
        while self._connected or not self._receive_queue.empty():
            try:
                item = await asyncio.wait_for(
                    self._receive_queue.get(),
                    timeout=0.1
                )
                yield item

                # Stop on terminal events
                if isinstance(item, StreamEvent):
                    if item.type in ("disconnected", "stream_end"):
                        break

            except asyncio.TimeoutError:
                continue

    @property
    def is_connected(self) -> bool:
        """Check if connected to Gemini."""
        return self._connected


async def create_gemini_stream(
    model: str = "gemini-live-2.5-flash-preview",
    system_instruction: Optional[str] = None,
    **kwargs
) -> GeminiStream:
    """
    Factory function to create and connect a Gemini stream.

    Args:
        model: Gemini model ID
        system_instruction: Optional system prompt
        **kwargs: Additional GeminiConfig parameters

    Returns:
        Connected GeminiStream instance
    """
    config = GeminiConfig(
        model=model,
        system_instruction=system_instruction,
        **kwargs
    )
    stream = GeminiStream(config)
    await stream.connect()
    return stream
