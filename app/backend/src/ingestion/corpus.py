"""
Samsung Products & Galaxy Ecosystem Document Corpus.
Comprehensive knowledge base covering Samsung Galaxy smartphones, foldables,
laptops, tablets, smartwatches, audio, smart TVs, Bespoke AI appliances,
and Samsung Knox/SmartThings connectivity.
"""

import re
from typing import List, Dict, Optional
from src.core.config import settings

# In-memory corpus: list of chunks with metadata
_cached_chunks: List[dict] = []


def chunk_text(text: str, doc_id: str = "", source: str = "") -> List[dict]:
    """
    Split text into overlapping chunks using recursive section splitting.
    """
    chunks = []
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


# ── 100% Samsung Products & Device Ecosystem Knowledge Base ──────────────────

SAMSUNG_PRODUCTS_CORPUS = [
    {
        "doc_id": "samsung-s24-ultra",
        "source": "Samsung Galaxy S24 Ultra & Flagship Series",
        "text": """\
Section 1: Galaxy S24 Ultra Hardware Architecture & Performance
The Galaxy S24 Ultra features the Snapdragon 8 Gen 3 Mobile Platform for Galaxy with an enlarged vapor chamber that is 1.9 times larger than the S23 Ultra, providing sustained thermal dissipation under heavy AI inference and gaming workloads. The device comes with 12GB of LPDDR5X RAM and storage options of 256GB, 512GB, and 1TB UFS 4.0.

Section 2: Display & Titanium Chassis
The phone features a 6.8-inch Dynamic AMOLED 2X flat display with 1-120Hz adaptive refresh rate and a peak brightness of 2,600 nits. It is protected by Corning Gorilla Armor glass, which reduces reflections by up to 75% and enhances scratch resistance by four times compared to standard aluminosilicate glass. The structural chassis is forged with Titanium Grade 2 for increased rigidity and drop resistance.

Section 3: Camera System & Quad Tele Mechanism
The camera system consists of a 200MP wide camera (f/1.7, OIS), a 12MP ultra-wide camera (f/2.2, 120-degree FOV), a 10MP telephoto camera (3x optical zoom, f/2.4), and a revolutionary 50MP periscope telephoto camera (5x optical zoom, 10x optical quality zoom via sensor crop, f/3.4, OIS). Nightography video uses gyro sensor data and enhanced noise reduction algorithms to distinguish between user hand shake and camera movement.

Section 4: Battery & Power Management
Equipped with a 5,000 mAh dual-cell lithium-ion battery. Charging supports 45W wired Fast Charging 2.0 (achieving 65% charge in approximately 30 minutes with the official Samsung 45W power adapter), 15W Fast Wireless Charging 2.0, and 4.5W Wireless PowerShare for charging Galaxy Buds and Watch."""
    },
    {
        "doc_id": "samsung-fold-flip-6",
        "source": "Samsung Galaxy Z Fold6 & Z Flip6 Foldables",
        "text": """\
Section 1: Galaxy Z Fold6 Multitasking & Form Factor
The Galaxy Z Fold6 weighs 239 grams and features a dual-rail FlexHinge with an enhanced shock-dispersion layer. When unfolded, the 7.6-inch main screen supports Multi-Active Window for running three applications side-by-side. The taskbar accommodates up to 4 recent apps and 8 pinned shortcuts. It includes S Pen Fold Edition compatibility.

Section 2: Galaxy Z Flip6 FlexWindow & Camera
The Galaxy Z Flip6 features a 3.4-inch Super AMOLED FlexWindow cover display with 60Hz refresh rate and a 6.7-inch FHD+ Dynamic AMOLED 2X main screen. The FlexWindow supports interactive widgets, suggested replies powered by Galaxy AI, and Auto Zoom with FlexCam for hands-free framing. The rear camera has been upgraded to a 50MP primary sensor with 2x in-sensor optical zoom.

Section 3: Thermal & Battery Improvements
For the first time in the Flip series, the Z Flip6 includes a customized vapor chamber cooling system. The battery capacity is increased to 4,000 mAh in the Flip6, while the Fold6 retains a 4,400 mAh battery with optimized power scheduling yielding up to 2 hours longer video playback."""
    },
    {
        "doc_id": "samsung-galaxy-ai",
        "source": "Samsung Galaxy AI Intelligence Suite",
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
        "doc_id": "samsung-galaxy-book4",
        "source": "Samsung Galaxy Book4 Ultra & Pro Laptops",
        "text": """\
Section 1: Galaxy Book4 Ultra Compute & Graphics
The Galaxy Book4 Ultra is powered by Intel Core Ultra 9 / Ultra 7 processors with dedicated Neural Processing Units (NPUs) for local AI workloads. Graphics are driven by NVIDIA GeForce RTX 4070 or RTX 4050 Laptop GPUs with DLSS 3.5 ray reconstruction. It features a vapor chamber with dual fans delivering an 11% wider vapor dissipation chamber.

Section 2: Dynamic AMOLED 2X Touch Display
Features a 16-inch 3K (2880 x 1800) Dynamic AMOLED 2X touchscreen with 120Hz variable refresh rate, 120% DCI-P3 color volume, and Vision Booster technology for daylight visibility with anti-reflective glass.

Section 3: Galaxy Ecosystem Continuity
Galaxy Book4 includes Samsung Multi Control, allowing users to control their Galaxy smartphone or tablet using the laptop's keyboard and trackpad. Users can drag and drop files across devices, use a Galaxy Tab as a Second Screen, and access Phone Link with Microsoft Copilot integration."""
    },
    {
        "doc_id": "samsung-tab-s10",
        "source": "Samsung Galaxy Tab S10 Ultra & S9 Series",
        "text": """\
Section 1: Galaxy Tab S10 Ultra Display & Design
The Tab S10 Ultra boasts a massive 14.6-inch Dynamic AMOLED 2X display with an anti-reflective coating that drops glare under 2%. Constructed with Armor Aluminum chassis and IP68 water and dust resistance. Includes an ultra-low latency S Pen in the box with 2.8ms response time.

Section 2: Productivity & Samsung DeX
Supports wireless and wired Samsung DeX mode, converting the tablet interface into a full desktop environment with floating resizable windows. Galaxy AI features include Sketch to Image (converting S Pen drawings into detailed illustrations) and PDF Overlay Translation."""
    },
    {
        "doc_id": "samsung-wearables",
        "source": "Samsung Galaxy Watch Ultra, Watch 7 & Buds3 Pro",
        "text": """\
Section 1: Galaxy Watch Ultra Extreme Endurance
The Galaxy Watch Ultra is constructed from Grade 4 Titanium with 100-meter (10 ATM) water resistance and MIL-STD-810H military durability certification. It features a 3nm processor, dual-frequency GPS (L1 + L5), a customizable Quick Button, and an emergency siren capable of outputting 86 decibels up to 180 meters away. Battery life offers up to 100 hours in Power Saving mode.

Section 2: Galaxy Buds3 Pro Hi-Fi Audio & Adaptive ANC
The Galaxy Buds3 Pro feature an all-new blade design with interactive Blade Lights. Equipped with 2-way speakers featuring planar tweeters and dual amplifiers. Supports 24-bit 96kHz ultra high-quality audio streaming via Samsung Seamless Codec (SSC). Adaptive ANC dynamically senses ambient noise and siren alarms to adjust cancellation intensity."""
    },
    {
        "doc_id": "samsung-smart-tv",
        "source": "Samsung Neo QLED 8K & OLED Smart TVs",
        "text": """\
Section 1: Neo QLED 8K & NQ8 AI Gen3 Processor
The flagship QN900D Neo QLED 8K TV is powered by Samsung's NQ8 AI Gen3 processor with 512 neural networks (8x increase over previous generation). Features 8K AI Upscaling Pro, AI Motion Enhancer Pro for sports tracking, and Real Depth Enhancer Pro for mini-LED contrast precision.

Section 2: Samsung OLED & Glare-Free Technology
The S95D OLED series features OLED Glare-Free technology, reducing reflections while preserving deep blacks and Pantone-validated color accuracy. Powered by Tizen OS with Samsung Gaming Hub supporting cloud gaming from Xbox and GeForce NOW without a console."""
    },
    {
        "doc_id": "samsung-bespoke-appliances",
        "source": "Samsung Bespoke AI Home Appliances",
        "text": """\
Section 1: Bespoke 4-Door Flex Refrigerator with AI Family Hub+
Features a 32-inch touchscreen with AI Vision Inside, which uses internal cameras and a recognition model trained on over 300,000 food images to identify fresh food items and track expiration dates. Suggests recipes based on available ingredients.

Section 2: Bespoke AI Laundry Combo
An all-in-one washer and dryer unit utilizing heat pump drying technology. The AI Wash & Dry cycle uses internal sensors to detect fabric weight, soil level, and moisture, automatically dispensing the exact amount of detergent and adjusting cycle duration."""
    },
    {
        "doc_id": "samsung-knox-smartthings",
        "source": "Samsung Knox Vault Security & SmartThings Mesh",
        "text": """\
Section 1: Knox Vault Hardware Security
Samsung Knox Vault is an EAL5+ certified hardware execution environment physically isolated from the main application processor. It houses dedicated secure processors and tamper-resistant storage for biometric templates, cryptographic keys, PINs, and sensitive user credentials.

Section 2: Battery Protection Settings
One UI introduces three Battery Protection levels to extend battery longevity on Galaxy devices:
1. Basic: Battery charges to 100% then pauses until dropping to 95%.
2. Adaptive: Pauses charging at 80% while sleeping and charges to 100% before wake-up.
3. Maximum: Caps charging strictly at 80% to maximize total battery lifespan over several years.

Section 3: SmartThings Hub & Matter Support
Samsung SmartThings integrates a built-in Matter and Zigbee thread border router in Samsung TVs, soundbars, and Family Hub refrigerators, allowing seamless local control of cross-brand smart home devices without cloud latency."""
    }
]


def load_demo_corpus():
    """Load the Samsung Products knowledge base and build the BM25 index."""
    global _cached_chunks
    from src.retrieval.hybrid import build_bm25_index

    _cached_chunks = []
    chunk_count = 0
    all_chunk_texts = []

    for doc in SAMSUNG_PRODUCTS_CORPUS:
        chunks = chunk_text(doc["text"], doc["doc_id"], doc["source"])
        _cached_chunks.extend(chunks)
        all_chunk_texts.extend([c["text"] for c in chunks])
        chunk_count += len(chunks)

    # Initialize BM25 index with all chunks
    build_bm25_index(all_chunk_texts)
    print(f"[Corpus] Loaded {len(SAMSUNG_PRODUCTS_CORPUS)} Samsung product documents, {chunk_count} chunks into memory and BM25 index.")
    return chunk_count
