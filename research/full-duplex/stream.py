"""
Full-Duplex Stream Abstraction

Defines the core abstraction for bidirectional streaming of symbols.
A "symbol" is any discrete unit of perception or expression - audio chunks,
video frames, text tokens, or any other modality.

This abstraction aims to provide a foundation for modeling attention as
a streaming sequence of symbols, where the system can simultaneously
perceive (receive) and express (send) without blocking.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    AsyncIterator, Optional, Any, Callable, Awaitable,
    Generic, TypeVar, Union, Literal
)
from enum import Enum
import asyncio
from datetime import datetime


class Modality(Enum):
    """Supported modalities for symbols."""
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"
    IMAGE = "image"
    # Future: tactile, proprioceptive, etc.


@dataclass
class Symbol:
    """
    A discrete unit of perception or expression.

    Symbols are the atomic units flowing through a full-duplex stream.
    They can represent any modality and carry both data and metadata.
    """
    modality: Modality
    data: bytes
    mime_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)

    # For audio: sample rate, channels, etc.
    # For video: width, height, fps, etc.
    # For text: encoding, language, etc.

    @classmethod
    def audio(cls, data: bytes, sample_rate: int = 16000,
              channels: int = 1, **kwargs) -> "Symbol":
        """Create an audio symbol."""
        return cls(
            modality=Modality.AUDIO,
            data=data,
            mime_type=f"audio/pcm;rate={sample_rate}",
            metadata={"sample_rate": sample_rate, "channels": channels, **kwargs}
        )

    @classmethod
    def text(cls, text: str, encoding: str = "utf-8", **kwargs) -> "Symbol":
        """Create a text symbol."""
        return cls(
            modality=Modality.TEXT,
            data=text.encode(encoding),
            mime_type=f"text/plain;charset={encoding}",
            metadata={"encoding": encoding, **kwargs}
        )

    @property
    def text_value(self) -> Optional[str]:
        """Get text content if this is a text symbol."""
        if self.modality == Modality.TEXT:
            encoding = self.metadata.get("encoding", "utf-8")
            return self.data.decode(encoding)
        return None


@dataclass
class StreamEvent:
    """
    Events that occur on a stream beyond symbol flow.

    These include lifecycle events (connect, disconnect),
    control signals (end of stream, interrupts), and
    metadata updates.
    """
    type: Literal[
        "connected",
        "disconnected",
        "stream_end",
        "interrupt",
        "error",
        "metadata"
    ]
    data: Optional[Any] = None
    timestamp: datetime = field(default_factory=datetime.now)


# Type for items flowing through the stream
StreamItem = Union[Symbol, StreamEvent]


class DuplexStream(ABC):
    """
    Abstract base class for full-duplex streaming connections.

    A DuplexStream can simultaneously send and receive symbols.
    This enables real-time bidirectional communication with
    multimodal models or other streaming endpoints.

    The stream operates on the principle that perception and
    expression are concurrent, not sequential - you can listen
    while speaking, see while acting.
    """

    @abstractmethod
    async def connect(self) -> None:
        """
        Establish the streaming connection.

        After connecting, send() and receive() can be called
        concurrently.
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Gracefully close the streaming connection.

        Ensures all pending symbols are flushed before closing.
        """
        pass

    @abstractmethod
    async def send(self, symbol: Symbol) -> None:
        """
        Send a symbol to the remote endpoint.

        This should not block on receiving a response.
        """
        pass

    @abstractmethod
    async def send_end(self) -> None:
        """
        Signal the end of the current send stream.

        For audio, this indicates the user has stopped speaking.
        The connection remains open for receiving responses.
        """
        pass

    @abstractmethod
    def receive(self) -> AsyncIterator[StreamItem]:
        """
        Iterate over incoming symbols and events.

        This is an async generator that yields symbols as they
        arrive from the remote endpoint. It should be consumed
        concurrently with sending.

        Yields:
            StreamItem: Either a Symbol or a StreamEvent
        """
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the stream is currently connected."""
        pass

    async def __aenter__(self) -> "DuplexStream":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.disconnect()


class DuplexSession:
    """
    High-level session wrapper for full-duplex communication.

    Provides utilities for common patterns like:
    - Concurrent send/receive loops
    - Automatic transcription handling
    - Interrupt/barge-in support
    """

    def __init__(self, stream: DuplexStream):
        self.stream = stream
        self._receive_task: Optional[asyncio.Task] = None
        self._send_task: Optional[asyncio.Task] = None
        self._interrupted = False

        # Callbacks
        self.on_symbol: Optional[Callable[[Symbol], Awaitable[None]]] = None
        self.on_event: Optional[Callable[[StreamEvent], Awaitable[None]]] = None

    async def run_duplex(
        self,
        sender: Callable[[], AsyncIterator[Symbol]],
        receiver: Optional[Callable[[StreamItem], Awaitable[None]]] = None
    ) -> None:
        """
        Run concurrent send and receive loops.

        Args:
            sender: Async generator yielding symbols to send
            receiver: Optional callback for received items.
                      If not provided, uses on_symbol/on_event callbacks.
        """
        async def send_loop():
            async for symbol in sender():
                if self._interrupted:
                    break
                await self.stream.send(symbol)
            await self.stream.send_end()

        async def receive_loop():
            async for item in self.stream.receive():
                if self._interrupted:
                    break
                if receiver:
                    await receiver(item)
                elif isinstance(item, Symbol) and self.on_symbol:
                    await self.on_symbol(item)
                elif isinstance(item, StreamEvent) and self.on_event:
                    await self.on_event(item)

        self._send_task = asyncio.create_task(send_loop())
        self._receive_task = asyncio.create_task(receive_loop())

        await asyncio.gather(self._send_task, self._receive_task)

    def interrupt(self) -> None:
        """
        Interrupt the current exchange (barge-in).

        Cancels any ongoing send/receive and prepares for
        a new exchange.
        """
        self._interrupted = True
        if self._send_task and not self._send_task.done():
            self._send_task.cancel()
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()

    def reset(self) -> None:
        """Reset interrupt state for a new exchange."""
        self._interrupted = False


# Type alias for stream factories
StreamFactory = Callable[..., DuplexStream]
