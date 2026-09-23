"""
In-memory document corpus with text chunking, dynamic ingestion,
and pre-loaded Samsung Galaxy AI & Ecosystem knowledge base.
"""

import re
from typing import List, Dict, Optional
from src.core.config import settings

# In-memory corpus: list of chunks with metadata
_cached_chunks: List[dict] = []


def chunk_text(text: str, doc_id: str = "", source: str = "") -> List[dict]:
    """
    Split text into overlapping chunks using recursive character splitting.
    Returns list of chunk dicts with text, doc_id, source, and index.
    """
    chunks = []
    # Split on paragraphs first, then sections
    paragraphs = re.split(r'\n\s*\n', text)

    current_chunk = ""
    chunk_index = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_chunk) + len(para) > settings.chunk_size and current_chunk:
            if current_chunk.strip():
                chunks.append({
                    "text": current_chunk.strip(),
                    "doc_id": doc_id,
                    "source": source or doc_id,
                    "index": chunk_index,
                })
                chunk_index += 1
            current_chunk = para + " "
        else:
            current_chunk += para + " "

    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "doc_id": doc_id,
            "source": source or doc_id,
            "index": chunk_index,
        })

    return chunks


def add_document(text: str, doc_id: str = "", source: str = "") -> int:
    """Add a document to the in-memory corpus and update BM25 index."""
    global _cached_chunks
    from src.retrieval.hybrid import add_to_bm25

    new_chunks = chunk_text(text, doc_id, source)
    _cached_chunks.extend(new_chunks)
    for c in new_chunks:
        add_to_bm25(c["text"])
    return len(new_chunks)


def get_cached_chunks() -> List[dict]:
    """Get all cached chunks. Loads default demo corpus if empty."""
    global _cached_chunks
    if not _cached_chunks:
        load_demo_corpus()
    return _cached_chunks


def clear_corpus():
    """Clear the in-memory corpus."""
    global _cached_chunks
    _cached_chunks = []


def get_corpus_stats() -> dict:
    """Return corpus statistics."""
    chunks = get_cached_chunks()
    doc_ids = set(c.get("source", c.get("doc_id", "unknown")) for c in chunks)
    return {
        "chunks": len(chunks),
        "documents": len(doc_ids),
        "sources": list(doc_ids),
        "avg_chunk_length": round(sum(len(c["text"]) for c in chunks) / max(len(chunks), 1), 1),
    }


# ── Official Samsung PRISM Knowledge Base & Demo Corpus ──────────────────────

SAMSUNG_PRISM_DOCUMENTS = [
    {
        "doc_id": "samsung-s24-ultra",
        "source": "Samsung Galaxy S24 Ultra Specifications & Hardware",
        "text": """\
Section 1: Galaxy S24 Ultra Hardware Architecture & Performance
The Galaxy S24 Ultra features the Snapdragon 8 Gen 3 Mobile Platform for Galaxy with an enlarged vapor chamber that is 1.9 times larger than the S23 Ultra, providing sustained thermal dissipation under heavy AI inference and gaming workloads. The device comes with 12GB of LPDDR5X RAM and storage options of 256GB, 512GB, and 1TB UFS 4.0.

Section 2: Display & Durability
The phone features a 6.8-inch Dynamic AMOLED 2X flat display with 1-120Hz adaptive refresh rate and a peak brightness of 2,600 nits. It is protected by Corning Gorilla Armor glass, which reduces reflections by up to 75% and enhances scratch resistance by four times compared to standard aluminosilicate glass. The structural chassis is forged with Titanium Grade 2 for increased rigidity and drop resistance.

Section 3: Camera System & Quad Tele Mechanism
The camera system consists of a 200MP wide camera (f/1.7, OIS), a 12MP ultra-wide camera (f/2.2, 120-degree FOV), a 10MP telephoto camera (3x optical zoom, f/2.4), and a revolutionary 50MP periscope telephoto camera (5x optical zoom, 10x optical quality zoom via sensor crop, f/3.4, OIS). Nightography video uses gyro sensor data and enhanced noise reduction algorithms to distinguish between user hand shake and camera movement.

Section 4: Battery & Power Management
Equipped with a 5,000 mAh dual-cell lithium-ion battery. Charging supports 45W wired Fast Charging 2.0 (achieving 65% charge in approximately 30 minutes with the official Samsung 45W power adapter), 15W Fast Wireless Charging 2.0, and 4.5W Wireless PowerShare for charging Galaxy Buds and Watch."""
    },
    {
        "doc_id": "samsung-galaxy-ai",
        "source": "Samsung Galaxy AI Features & Intelligence Architecture",
        "text": """\
Section 1: Circle to Search with Google
Circle to Search allows users to circle, highlight, scribble on, or tap any image, video, or text on the screen to initiate a Google search without leaving the current application. It supports multimodal queries, allowing users to ask follow-up questions after circling an item.

Section 2: Live Translate & Interpreter
Live Translate delivers two-way, real-time voice and text translations for phone calls directly within the native Samsung Phone app. Translations are processed entirely on-device to protect user privacy without transmitting audio data to external servers. Supported languages include English, Spanish, French, German, Hindi, Mandarin Chinese, Japanese, Korean, Italian, Polish, Portuguese, Thai, and Vietnamese. Interpreter mode splits the screen into a top-and-bottom view for face-to-face conversations.

Section 3: Note Assist & Transcript Assist
Note Assist in Samsung Notes generates AI-powered summaries, creates pre-formatted templates, and translates meeting notes. Transcript Assist uses on-device STT (Speech-to-Text) and AI to transcribe, summarize, and translate audio recordings even when multiple speakers are talking simultaneously.

Section 4: Generative Edit & Photo Assist
Generative Edit uses cloud-based generative AI to fill in backgrounds when straightening tilted photos, resize or reposition objects, and seamlessly blend removed reflections and shadows. An AI watermark is embedded in the image metadata and bottom-left corner of the output."""
    },
    {
        "doc_id": "samsung-fold-flip",
        "source": "Galaxy Z Fold6 & Z Flip6 Foldable Innovations",
        "text": """\
Section 1: Galaxy Z Fold6 Multitasking & Form Factor
The Galaxy Z Fold6 weighs 239 grams and features a dual-rail FlexHinge with an enhanced shock-dispersion layer. When unfolded, the 7.6-inch main screen supports Multi-Active Window for running three applications side-by-side. The taskbar accommodates up to 4 recent apps and 8 pinned shortcuts. It includes S Pen Fold Edition compatibility.

Section 2: Galaxy Z Flip6 FlexWindow & Camera
The Galaxy Z Flip6 features a 3.4-inch Super AMOLED FlexWindow cover display with 60Hz refresh rate and a 6.7-inch FHD+ Dynamic AMOLED 2X main screen. The FlexWindow supports interactive widgets, suggested replies powered by Galaxy AI, and Auto Zoom with FlexCam for hands-free framing. The rear camera has been upgraded to a 50MP primary sensor with 2x in-sensor optical zoom.

Section 3: Thermal & Battery Improvements
For the first time in the Flip series, the Z Flip6 includes a customized vapor chamber cooling system. The battery capacity is increased to 4,000 mAh in the Flip6, while the Fold6 retains a 4,400 mAh battery with optimized power scheduling yielding up to 2 hours longer video playback."""
    },
    {
        "doc_id": "samsung-knox-security",
        "source": "Samsung Knox Vault & Security Framework",
        "text": """\
Section 1: Knox Vault Hardware Security
Samsung Knox Vault is an EAL5+ certified hardware execution environment physically isolated from the main application processor. It houses dedicated secure processors and tamper-resistant storage for biometric templates, cryptographic keys, PINs, and sensitive user credentials.

Section 2: Battery Protection Modes
One UI 6.1 introduces three Battery Protection levels to extend battery longevity:
1. Basic: Battery charges to 100% then pauses until dropping to 95%.
2. Adaptive: Pauses charging at 80% while you sleep and charges to 100% just before you wake up based on your sleep routine.
3. Maximum: Caps charging strictly at 80% to maximize total battery lifespan over several years.

Section 3: Knox Matrix & Auto Blocker
Knox Matrix provides private blockchain-based credential synchronization across verified Galaxy ecosystem devices. Auto Blocker prevents app installation from unauthorized sources, blocks malicious USB commands, and inspects app installations for malware."""
    },
    {
        "doc_id": "samsung-wearables",
        "source": "Galaxy Watch Ultra & Galaxy Buds3 Pro Guide",
        "text": """\
Section 1: Galaxy Watch Ultra Extreme Endurance
The Galaxy Watch Ultra is constructed from Grade 4 Titanium with 100-meter (10 ATM) water resistance and MIL-STD-810H military durability certification. It features a 3nm processor, dual-frequency GPS (L1 + L5), a customizable Quick Button, and an emergency siren capable of outputting 86 decibels up to 180 meters away. Battery life offers up to 100 hours in Power Saving mode.

Section 2: Galaxy Buds3 Pro Hi-Fi Audio & ANC
The Galaxy Buds3 Pro feature an all-new blade design with interactive Blade Lights. Equipped with 2-way speakers featuring planar tweeters and dual amplifiers. Supports 24-bit 96kHz ultra high-quality audio streaming via Samsung Seamless Codec (SSC). Adaptive ANC dynamically senses ambient noise and siren alarms to adjust cancellation intensity."""
    },
    {
        "doc_id": "company-policy",
        "source": "Company Policy & Operational Guidelines",
        "text": """\
Section 1: Leave and PTO Rules
All full-time employees accrue 15 paid time off (PTO) days per year for the first 3 years of tenure, and 20 days per year thereafter. Maximum PTO carryover into the subsequent calendar year is capped at 5 days. Requests require 48 hours advance notice in the portal.

Section 2: Hybrid & Remote Work Protocol
Eligible employees may work remotely up to 3 days per week with departmental director approval. Reimbursable hardware stipend includes up to $500 for ergonomic monitors and high-speed internet subsidies."""
    }
]


def load_demo_corpus():
    """Load the Samsung PRISM knowledge base and build the BM25 index."""
    global _cached_chunks
    from src.retrieval.hybrid import build_bm25_index

    _cached_chunks = []
    chunk_count = 0
    all_chunk_texts = []

    for doc in SAMSUNG_PRISM_DOCUMENTS:
        chunks = chunk_text(doc["text"], doc["doc_id"], doc["source"])
        _cached_chunks.extend(chunks)
        all_chunk_texts.extend([c["text"] for c in chunks])
        chunk_count += len(chunks)

    # Initialize BM25 index with all chunks
    build_bm25_index(all_chunk_texts)
    print(f"[Corpus] Loaded {len(SAMSUNG_PRISM_DOCUMENTS)} documents, {chunk_count} chunks into memory and BM25 index.")
    return chunk_count
