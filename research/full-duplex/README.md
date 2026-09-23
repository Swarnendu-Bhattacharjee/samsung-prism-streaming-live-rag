# Full-Duplex

Real-time bidirectional streaming for multimodal models.

## What is Full-Duplex?

In telecommunications, full-duplex means simultaneous two-way communication - you can talk and listen at the same time. We extend this concept to **any real-time sensorial perception**: audio, video, text, or any other modality that can be represented as a streaming sequence of symbols.

This library provides abstractions for building systems that can perceive and express concurrently through multimodal models (MMMs).

## Why This Matters

Traditional LLM interactions are half-duplex: you send a prompt, wait, receive a response. But real perception doesn't work that way. When you're in a conversation, you're simultaneously:

- **Perceiving**: Processing incoming audio, visual cues, context
- **Expressing**: Speaking, gesturing, reacting
- **Attending**: Selectively focusing on relevant signals

Full-duplex streaming is the foundation for modeling **attention** in a rigorous way - attention as the dynamic allocation of processing across concurrent symbol streams.

## Installation

```bash
pip install -r requirements.txt
```

For Gemini backend:
```bash
pip install google-genai
```

## Quick Start

```python
import asyncio
from full_duplex import GeminiStream, GeminiConfig, Symbol

async def main():
    config = GeminiConfig(
        model="gemini-live-2.5-flash-preview",
        system_instruction="You are a helpful assistant."
    )

    async with GeminiStream(config) as stream:
        # Send audio (e.g., from microphone)
        await stream.send(Symbol.audio(audio_bytes, sample_rate=16000))
        await stream.send_end()

        # Receive response (audio + transcription)
        async for item in stream.receive():
            if isinstance(item, Symbol):
                if item.modality == Modality.AUDIO:
                    play_audio(item.data)
                elif item.modality == Modality.TEXT:
                    print(f"Transcript: {item.text_value}")

asyncio.run(main())
```

## Core Concepts

### Symbol

A **Symbol** is the atomic unit of perception or expression - an audio chunk, a text token, a video frame. Symbols flow through streams and carry both data and metadata.

```python
# Create symbols
audio_symbol = Symbol.audio(pcm_bytes, sample_rate=16000)
text_symbol = Symbol.text("Hello, world")

# Access data
print(text_symbol.text_value)  # "Hello, world"
print(audio_symbol.metadata["sample_rate"])  # 16000
```

### DuplexStream

A **DuplexStream** is a bidirectional channel for sending and receiving symbols. It represents a live connection to a multimodal model or other streaming endpoint.

```python
class DuplexStream(ABC):
    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def send(self, symbol: Symbol) -> None: ...
    async def send_end(self) -> None: ...
    def receive(self) -> AsyncIterator[StreamItem]: ...
```

### StreamEvent

**StreamEvents** are control signals that occur alongside symbol flow: connection lifecycle, stream boundaries, interrupts, errors.

```python
@dataclass
class StreamEvent:
    type: Literal["connected", "disconnected", "stream_end", "interrupt", "error"]
    data: Optional[Any] = None
```

### DuplexSession

A **DuplexSession** wraps a stream with utilities for common patterns like concurrent send/receive loops and interrupt handling (barge-in).

```python
session = DuplexSession(stream)

async def mic_input():
    while recording:
        yield Symbol.audio(read_mic())

await session.run_duplex(sender=mic_input)
```

## Backends

### GeminiStream (Cloud)

Connects to Google's Gemini Live API for real-time multimodal conversations.

```python
from full_duplex import GeminiStream, GeminiConfig

config = GeminiConfig(
    model="gemini-live-2.5-flash-preview",
    input_sample_rate=16000,
    output_sample_rate=24000,
    response_modalities=["AUDIO"],
)
```

**Environment**: Set `GOOGLE_API_KEY` or pass `api_key` to config.

### Future Backends

- **LocalStream**: Local models via llama.cpp or similar
- **OpenAIStream**: OpenAI Realtime API
- **CompositeStream**: Multiplex across multiple backends

## Toward Attention

This library is a stepping stone toward formalizing **attention** as a first-class concept in AI systems. The hypothesis:

> Attention is the dynamic allocation of processing capacity across concurrent symbol streams, governed by relevance, urgency, and resource constraints.

Full-duplex streaming provides the substrate - concurrent perception and expression. Future work will build on this to model:

- **Selective attention**: Which symbols to process deeply vs. skim
- **Sustained attention**: Maintaining focus across time
- **Divided attention**: Processing multiple streams simultaneously
- **Attentional control**: Meta-level policies for attention allocation

## License

MIT
