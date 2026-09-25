#!/usr/bin/env python3
"""
Samsung Product Ecosystem Knowledge Base Builder
Generates a comprehensive, verified, high-density JSON database for RAG retrieval
covering Galaxy smartphones, foldables, laptops, tablets, wearables, audio, TVs,
appliances, Knox security, and semiconductor components.
"""

import json
import os

KNOWLEDGE_BASE = [
    {
        "doc_id": "samsung-galaxy-s25-ultra",
        "title": "Samsung Galaxy S25 Ultra Flagship Smartphone",
        "category": "Smartphones / Flagship",
        "source": "Samsung Galaxy S25 Ultra Official Technical Documentation (Feb 2025)",
        "tags": ["S25 Ultra", "Snapdragon 8 Elite", "Titanium Grade 5", "200MP Camera", "Gorilla Armor 2", "Galaxy AI", "5000mAh", "45W Charging"],
        "sections": [
            {
                "section": "Processor & Compute Architecture",
                "text": "The Galaxy S25 Ultra is powered by the Qualcomm Snapdragon 8 Elite Mobile Platform for Galaxy, manufactured on TSMC's 3nm N3E process node. The CPU architecture features an all-big-core design with 2x Oryon V2 Phoenix L prime cores clocked up to 4.47 GHz and 6x Oryon V2 Phoenix M performance cores running at 3.53 GHz. It is paired with the Qualcomm Adreno 830 GPU delivering a 40% improvement in hardware-accelerated ray tracing and gaming performance. The Hexagon NPU delivers 45 TOPS (Trillion Operations Per Second) of INT8 AI compute capability for on-device generative AI workloads. Memory options include 12GB or 16GB of LPDDR5X RAM with UFS 4.0 high-speed flash storage in 256GB, 512GB, and 1TB configurations."
            },
            {
                "section": "Display & Titanium Grade 5 Structural Build",
                "text": "The Galaxy S25 Ultra features a 6.9-inch Dynamic LTPO AMOLED 2X flat display with a resolution of 1440 x 3120 pixels (Quad HD+, ~498 ppi density) and a 1-120Hz adaptive refresh rate. The display utilizes Samsung Display's M14 OLED organic material set with a peak brightness reaching 2,600 nits and HDR10+ support. The screen is shielded by Corning Gorilla Armor 2 glass, which incorporates a specialized anti-reflective surface treatment that reduces ambient light reflections by up to 75% while improving scratch resistance. The structural frame is forged from aerospace-grade Titanium Grade 5 (Ti-6Al-4V), offering significantly higher tensile strength than standard aluminum while maintaining a lightweight footprint of 219 grams. The device features ultra-thin, uniform 1.2mm display bezels and subtle rounded corners for improved ergonomic hand-feel."
            },
            {
                "section": "Quad Telephoto Camera System & Optics",
                "text": "The rear camera array of the Galaxy S25 Ultra comprises four advanced optical sensors: a 200MP primary wide sensor (Samsung ISOCELL HP2, 1/1.3-inch optical format, 0.6µm pixels, f/1.7 aperture, multi-directional PDAF, optical image stabilization OIS); a 50MP periscope telephoto lens with 5x optical zoom and up to 100x Space Zoom (Sony IMX854 / ISOCELL sensor, f/3.4 aperture, Dual Pixel PDAF, OIS); a 10MP secondary telephoto camera offering 3x optical zoom (f/2.4 aperture, Dual Pixel PDAF, OIS); and an upgraded 50MP ultra-wide camera (Samsung ISOCELL JN3, 1/2.76-inch, f/1.9 aperture, 120-degree field of view with autofocus for macro photography). The front-facing selfie camera is a 12MP Dual Pixel sensor with 4K 60fps video recording. The camera pipeline is driven by Samsung's ProVisual Engine with AI-powered noise reduction, Object-Aware Engine for skin tone preservation, and 8K video capture at up to 60 frames per second with HDR10+."
            },
            {
                "section": "Battery, Power Management & Cooling",
                "text": "Equipped with a 5,000 mAh high-energy-density dual-cell lithium-ion battery. The device supports 45W wired Fast Charging 2.0 (USB Power Delivery PPS standard, reaching approximately 65% charge in 30 minutes with an official 45W power adapter), 15W Fast Wireless Charging 2.0, and 4.5W reverse Wireless PowerShare to recharge Galaxy Buds, Galaxy Watch, or compatible Qi devices. The internal thermal architecture includes an enlarged vapor chamber that is 1.4x larger than the S24 Ultra, utilizing liquid-vapor phase change cooling to dissipate heat from the Snapdragon 8 Elite chipset under sustained multi-hour gaming and 8K recording sessions."
            },
            {
                "section": "One UI 7 Software & Galaxy AI Capabilities",
                "text": "Running Samsung One UI 7 based on Android 15. The Galaxy S25 Ultra includes full support for the next-generation Galaxy AI suite: Circle to Search with Google now supports real-time multi-object barcode scanning, math problem-solving, and humming song search; Live Translate supports 16+ languages in two-way voice calls processed entirely on-device; Audio Summary in Samsung Voice Recorder creates speaker-separated summaries; and Generative Edit allows seamless background synthesis, object relocation, and reflection removal. Samsung promises 7 generations of Android OS upgrades and 7 years of security patches through 2032."
            }
        ]
    },
    {
        "doc_id": "samsung-galaxy-s24-ultra",
        "title": "Samsung Galaxy S24 Ultra Flagship Smartphone",
        "category": "Smartphones / Flagship",
        "source": "Samsung Galaxy S24 Ultra Technical Specification Sheet (2024)",
        "tags": ["S24 Ultra", "Snapdragon 8 Gen 3", "Titanium Grade 2", "200MP Camera", "5x Periscope", "Gorilla Armor", "5000mAh", "S Pen"],
        "sections": [
            {
                "section": "Silicon Architecture & Thermal Dissipation",
                "text": "The Galaxy S24 Ultra incorporates the Qualcomm Snapdragon 8 Gen 3 Mobile Platform for Galaxy (4nm N4P architecture), featuring a Cortex-X4 prime core clocked at 3.39 GHz, 5x Cortex-A720 performance cores, and 2x Cortex-A520 efficiency cores. The Adreno 750 GPU features hardware-accelerated ray tracing. It is equipped with a 1.9x larger vapor chamber compared to the Galaxy S23 Ultra, ensuring thermal stability under sustained computational loads. Memory configurations include 12GB LPDDR5X RAM with 256GB, 512GB, or 1TB UFS 4.0 storage."
            },
            {
                "section": "Flat Display & Corning Gorilla Armor Glass",
                "text": "The S24 Ultra shifted from curved edges to a completely flat 6.8-inch Dynamic AMOLED 2X display with Quad HD+ resolution (3120 x 1440 pixels, 505 ppi) and 1-120Hz LTPO variable refresh rate. Peak brightness is rated at 2,600 nits with Vision Booster technology. The display is clad in Corning Gorilla Armor, an optically advanced cover glass material that diminishes reflections by 75% compared to conventional glass and provides four times greater micro-scratch resistance. The frame is crafted with Titanium Grade 2."
            },
            {
                "section": "Quad Tele Camera System with 50MP 5x Sensor",
                "text": "The camera system features a 200MP main camera (f/1.7, 24mm equivalent, OIS), a 12MP ultra-wide camera (f/2.2, 120-degree FOV), a 10MP 3x optical telephoto camera (f/2.4, OIS), and a 50MP periscope telephoto camera offering 5x optical zoom and 10x optical quality zoom via high-resolution sensor cropping (f/3.4, OIS). Video capabilities include 8K at 30fps and 4K at 120fps for cinematic slow motion. The Nightography video pipeline utilizes optical gyro data to isolate camera movement from hand shake."
            },
            {
                "section": "Battery & Built-In S Pen",
                "text": "A 5,000 mAh battery delivers up to 30 hours of video playback. Charging capabilities include 45W wired charging (Super Fast Charging 2.0), 15W wireless charging, and 4.5W reverse wireless charging. The device features an integrated S Pen stylus with 2.8ms latency, 4,096 levels of pressure sensitivity, and Bluetooth Low Energy (BLE) air actions for remote camera shutter and presentation control. IP68 certified water and dust resistance up to 1.5 meters for 30 minutes."
            }
        ]
    },
    {
        "doc_id": "samsung-galaxy-s24-plus-s24",
        "title": "Samsung Galaxy S24+ and Galaxy S24",
        "category": "Smartphones / Flagship",
        "source": "Samsung Galaxy S24+ & S24 Technical Reference",
        "tags": ["S24+", "S24", "Exynos 2400", "Snapdragon 8 Gen 3", "Dynamic AMOLED 2X", "Armor Aluminum", "4900mAh", "4000mAh"],
        "sections": [
            {
                "section": "Displays & Form Factors",
                "text": "The Galaxy S24+ features a 6.7-inch QHD+ (3120 x 1440 pixels) Dynamic AMOLED 2X display, matching the pixel density and sharpness of the Ultra model for the first time, while the compact Galaxy S24 has a 6.2-inch FHD+ (2340 x 1080) Dynamic AMOLED 2X panel. Both screens feature 1-120Hz adaptive refresh rates and peak brightness of 2,600 nits. The chassis uses Enhanced Armor Aluminum 2.0 with a matte satin finish and IP68 water resistance."
            },
            {
                "section": "Processor & Memory Variations",
                "text": "Depending on geographic region, the Galaxy S24 and S24+ are equipped with either the Samsung Exynos 2400 chipset (Deca-core CPU with Cortex-X4 at 3.2 GHz and Xclipse 940 GPU featuring AMD RDNA 3 architecture) or the Qualcomm Snapdragon 8 Gen 3 for Galaxy. The Galaxy S24+ features 12GB of LPDDR5X RAM with 256GB or 512GB UFS 4.0 storage, while the Galaxy S24 includes 8GB of RAM with 128GB (UFS 3.1) or 256GB (UFS 4.0) storage."
            },
            {
                "section": "Camera Systems & Battery Capacities",
                "text": "Both devices share a triple camera setup: a 50MP primary sensor (f/1.8, Dual Pixel PDAF, OIS), a 12MP ultra-wide sensor (f/2.2, 120-degree FOV), and a 10MP 3x optical telephoto lens (f/2.4, OIS). Front camera is 12MP with autofocus. The Galaxy S24+ has a 4,900 mAh battery supporting 45W wired charging, while the compact Galaxy S24 has a 4,000 mAh battery supporting 25W wired charging. Both support 15W wireless charging and Fast Wireless PowerShare."
            }
        ]
    },
    {
        "doc_id": "samsung-galaxy-z-fold6",
        "title": "Samsung Galaxy Z Fold6 Book-Style Foldable",
        "category": "Foldables / Flagship",
        "source": "Samsung Galaxy Z Fold6 Architecture Whitepaper (2024)",
        "tags": ["Z Fold6", "Dual-rail FlexHinge", "7.6 inch screen", "Cover Screen 22.1:9", "Snapdragon 8 Gen 3", "S Pen Fold Edition", "IP48"],
        "sections": [
            {
                "section": "Hinge Engineering, Weight & Durability",
                "text": "The Galaxy Z Fold6 weighs 239 grams, a 14-gram reduction from the Fold5, and measures 12.1mm folded and 5.6mm unfolded. It features an advanced dual-rail FlexHinge with a waterdrop fold architecture that disperses external mechanical impact evenly across the hinge structure. The main folding screen features an enhanced protective layer with shear thickening fluid (STF) that increases resistance to impact indentations. The device holds an IP48 durability rating, providing certified protection against solid foreign objects greater than 1mm and water submersion up to 1.5m for 30 minutes."
            },
            {
                "section": "Dual Display System & Multitasking Capabilities",
                "text": "The external cover screen is a 6.3-inch Dynamic AMOLED 2X panel with a wider 22.1:9 aspect ratio (2376 x 968 pixels) that provides a standard smartphone typing experience without feeling cramped. The inner foldable display is a 7.6-inch Dynamic AMOLED 2X panel with a near-square 20.9:18 aspect ratio (2160 x 1856 pixels) and up to 2,600 nits peak brightness. The inner display supports Multi-Active Window for running three applications concurrently in split-screen, plus floating pop-up windows. The persistent taskbar holds up to 4 recent applications and 8 pinned shortcuts. Compatible with the S Pen Fold Edition."
            },
            {
                "section": "Performance, Cooling & Battery",
                "text": "Powered by the Qualcomm Snapdragon 8 Gen 3 for Galaxy, coupled with 12GB of LPDDR5X RAM and 256GB, 512GB, or 1TB UFS 4.0 storage. The internal cooling system incorporates a 1.6x larger vapor chamber compared to the Fold5. Battery capacity is 4,400 mAh dual-cell architecture, optimized with algorithmic power gating to provide up to 23 hours of video playback. Supports 25W wired charging, 15W wireless charging, and Wireless PowerShare."
            },
            {
                "section": "Camera Array & Galaxy AI Productivity",
                "text": "Triple rear cameras include a 50MP wide camera (f/1.8, Dual Pixel PDAF, OIS), a 12MP ultra-wide camera (f/2.2), and a 10MP 3x optical telephoto camera (f/2.4, OIS). The cover screen houses a 10MP selfie camera, while the inner main display utilizes a 4MP Under-Display Camera (UDC) hidden behind a sub-pixel matrix. Software features include Sketch to Image (generating photorealistic renders from rough S Pen doodles), Note Assist with automatic formatting, and Interpreter Dual-Screen mode where translations are shown simultaneously on the cover screen to the conversation partner."
            }
        ]
    },
    {
        "doc_id": "samsung-galaxy-z-flip6",
        "title": "Samsung Galaxy Z Flip6 Clamshell Foldable",
        "category": "Foldables / Clamshell",
        "source": "Samsung Galaxy Z Flip6 Technical Guide (2024)",
        "tags": ["Z Flip6", "FlexWindow", "50MP Camera", "First Flip Vapor Chamber", "4000mAh Battery", "FlexCam Auto Zoom", "IP48"],
        "sections": [
            {
                "section": "FlexWindow Cover Screen & Interactive Widgets",
                "text": "The Galaxy Z Flip6 features a 3.4-inch Super AMOLED FlexWindow cover screen (720 x 748 pixels, 60Hz, 306 ppi, peak brightness 1,600 nits). The FlexWindow supports interactive widgets for calendar, media player, weather, Samsung Health, and SmartThings routines. Users can reply to messages using AI Suggested Replies that analyze chat context to formulate relevant quick responses without unfolding the device. Interactive wallpaper options react to device motion, gyro sensors, and ambient weather conditions."
            },
            {
                "section": "First-Ever Vapor Chamber in a Flip & 4,000 mAh Battery",
                "text": "Addressing historical thermal and endurance limits in compact foldables, the Z Flip6 is the first Flip device equipped with a dedicated vapor chamber cooling system. The vapor chamber spreads heat across the upper housing, preventing thermal throttling during intensive gaming and camera processing. The battery capacity has been increased to 4,000 mAh (from 3,700 mAh in Flip5), delivering up to 68 hours of music playback or 20 hours of video playback. Supports 25W wired charging and 15W wireless charging."
            },
            {
                "section": "Upgraded 50MP Camera & FlexCam Auto Zoom",
                "text": "The primary camera has been upgraded to a 50MP wide sensor (f/1.8, 1.0µm pixels, Dual Pixel PDAF, OIS) with 2x optical quality in-sensor zoom, alongside a 12MP ultra-wide camera (f/2.2, 123-degree FOV). In FlexMode (folding the phone between 75 and 115 degrees), the phone acts as its own tripod on any flat surface. The FlexCam Auto Zoom feature uses AI subject tracking to automatically zoom in or out from 0.6x to 3x to ensure subjects remain properly framed in hands-free group selfies or video logs."
            },
            {
                "section": "Main Display & Armor Aluminum Chassis",
                "text": "When opened, the main display is a 6.7-inch Dynamic AMOLED 2X panel with FHD+ resolution (2640 x 1080 pixels), 1-120Hz adaptive refresh rate, and up to 2,600 nits peak brightness. The outer casing is built with Enhanced Armor Aluminum and Corning Gorilla Glass Victus 2 on the front and back panels. Certified IP48 water and particle resistance."
            }
        ]
    },
    {
        "doc_id": "samsung-galaxy-tab-s10-ultra",
        "title": "Samsung Galaxy Tab S10 Ultra Flagship Tablet",
        "category": "Tablets / Productivity",
        "source": "Samsung Galaxy Tab S10 Ultra Official Specification Document (Sep 2024)",
        "tags": ["Tab S10 Ultra", "MediaTek Dimensity 9300+", "14.6 inch AMOLED", "Anti-Reflection Coating", "In-box S Pen", "11200mAh", "Samsung DeX", "Wi-Fi 7"],
        "sections": [
            {
                "section": "Processor & MediaTek Dimensity 9300+ Flagship Chipset",
                "text": "In a strategic architectural shift, the Galaxy Tab S10 Ultra is powered by the MediaTek Dimensity 9300+ processor built on TSMC's 4nm third-generation process. The chipset features an all-big-core CPU configuration: 1x Cortex-X4 prime core clocked at 3.4 GHz, 3x Cortex-X4 cores at 2.85 GHz, and 4x Cortex-A720 performance cores at 2.0 GHz, yielding an 18% CPU performance improvement and a 28% GPU performance increase (ARM Immortalis-G720 MC12 with hardware ray tracing) compared to Tab S9 Ultra. The integrated MediaTek NPU 790 delivers a 14% uplift in AI computing capability for on-device Galaxy AI features. Memory options include 12GB or 16GB RAM with 256GB, 512GB, or 1TB internal storage, expandable up to 1.5TB via a dedicated microSD card slot."
            },
            {
                "section": "14.6-Inch Dynamic AMOLED 2X Anti-Reflective Display",
                "text": "The Tab S10 Ultra features a massive 14.6-inch Dynamic AMOLED 2X display with a resolution of 2960 x 1848 pixels (WQXGA+, 16:10 aspect ratio, 240 ppi) and an adaptive refresh rate up to 120Hz. The screen incorporates advanced Anti-Reflection coating technology that reduces surface glare to under 2%, making it readable under bright studio lights or direct outdoor sunlight. Peak brightness reaches 930 nits with Vision Booster optimization."
            },
            {
                "section": "In-Box S Pen, Low Latency & IP68 Durability",
                "text": "The tablet includes a full-size S Pen in the box with Bluetooth Low Energy (BLE) functionality, 4,096 pressure levels, and an ultra-low latency of 2.8ms. The S Pen magnetically attaches to the rear charging groove or side rail of the tablet. Both the tablet body and the S Pen carry IP68 certified water and dust resistance (immersible in up to 1.5m of fresh water for 30 minutes). Constructed with an Enhanced Armor Aluminum unibody measuring an ultra-thin 5.4mm and weighing 718 grams."
            },
            {
                "section": "Battery, Audio & Samsung DeX Desktop Mode",
                "text": "Equipped with a massive 11,200 mAh lithium-polymer battery supporting 45W wired Fast Charging. Audio is delivered through a quad-speaker system tuned by AKG with Dolby Atmos support. Software includes Samsung DeX mode, which supports extended desktop monitor output at up to 4K 60Hz over USB Type-C DisplayPort. Connectivity includes Wi-Fi 7 (802.11be), Bluetooth 5.3, and optional 5G Sub-6/mmWave cellular support."
            }
        ]
    },
    {
        "doc_id": "samsung-galaxy-tab-s10-plus",
        "title": "Samsung Galaxy Tab S10+ Productivity Tablet",
        "category": "Tablets / Productivity",
        "source": "Samsung Galaxy Tab S10+ Specifications Guide (2024)",
        "tags": ["Tab S10+", "MediaTek Dimensity 9300+", "12.4 inch AMOLED", "S Pen Included", "10090mAh", "IP68", "Armor Aluminum"],
        "sections": [
            {
                "section": "Hardware Architecture & 12.4-inch Display",
                "text": "The Galaxy Tab S10+ features a 12.4-inch Dynamic AMOLED 2X display with a resolution of 2800 x 1752 pixels, 120Hz adaptive refresh rate, and anti-reflective screen coating. It is powered by the same flagship MediaTek Dimensity 9300+ 4nm processor found in the Ultra model. Available with 12GB RAM and 256GB or 512GB storage with microSD expansion up to 1.5TB."
            },
            {
                "section": "Battery, Form Factor & Accessories",
                "text": "The device houses a 10,090 mAh battery with 45W fast charging. It measures 5.6mm in thickness and weighs 571 grams (Wi-Fi model). Built with Enhanced Armor Aluminum chassis and IP68 water and dust resistance. Includes an in-box IP68-rated S Pen with 2.8ms latency. Compatible with the Book Cover Keyboard Slim featuring a dedicated Galaxy AI key."
            }
        ]
    },
    {
        "doc_id": "samsung-galaxy-book5-pro-360",
        "title": "Samsung Galaxy Book5 Pro 360 Copilot+ Laptop",
        "category": "Laptops / Copilot+ PC",
        "source": "Samsung Galaxy Book5 Series Technical Whitepaper (2025)",
        "tags": ["Galaxy Book5 Pro 360", "Intel Core Ultra 200V", "Lunar Lake", "Intel Arc 140V", "48 TOPS NPU", "Copilot+ PC", "Dynamic AMOLED 2X", "S Pen"],
        "sections": [
            {
                "section": "Intel Lunar Lake Core Ultra 200V Architecture",
                "text": "The Galaxy Book5 Pro 360 is powered by Intel Core Ultra 200V Series processors (Lunar Lake architecture), including the Core Ultra 7 256V / 258V with on-package memory (16GB or 32GB LPDDR5X at 8533 MT/s). The processor incorporates 4 Lion Cove performance cores and 4 Skymont low-power efficient cores. The integrated Intel Arc 140V GPU delivers an 18% graphical uplift, while the integrated NPU 4.0 provides up to 48 TOPS of dedicated AI compute, meeting Microsoft's Copilot+ PC requirements for local AI features such as Cocreator, Live Captions with translation, and Windows Studio Effects."
            },
            {
                "section": "3K Dynamic AMOLED 2X Touchscreen & 360 Hinge",
                "text": "Features a 16-inch 3K (2880 x 1800 pixels) Dynamic AMOLED 2X 16:10 touchscreen with a 120Hz variable refresh rate, 120% DCI-P3 color gamut, and 500 nits HDR brightness. The panel incorporates Vision Booster and anti-reflective glass. The precision 360-degree geared hinge allows the laptop to transition between clamshell, tent, stand, and tablet modes. Includes an S Pen in the box for drawing and note-taking."
            },
            {
                "section": "Battery Life & Galaxy Continuity",
                "text": "Houses a 76Wh battery delivering up to 25 hours of continuous local video playback on a single charge. Recharges rapidly via a compact 65W USB-C PD charger. Continuity features include Samsung Multi Control (share mouse and keyboard across Galaxy phone, tablet, and PC), Second Screen (use Galaxy Tab as wireless external monitor), Quick Share, and Phone Link."
            }
        ]
    },
    {
        "doc_id": "samsung-galaxy-book4-ultra",
        "title": "Samsung Galaxy Book4 Ultra Performance Laptop",
        "category": "Laptops / Performance",
        "source": "Samsung Galaxy Book4 Ultra Technical Guide",
        "tags": ["Book4 Ultra", "Intel Core Ultra 9 185H", "NVIDIA RTX 4070", "3K AMOLED Touch", "Multi Control", "DLSS 3.5"],
        "sections": [
            {
                "section": "Processor, Discrete GPU & Thermal Design",
                "text": "The Galaxy Book4 Ultra is equipped with up to an Intel Core Ultra 9 185H processor with Intel AI Boost NPU, combined with an NVIDIA GeForce RTX 4070 Laptop GPU (8GB GDDR6 VRAM, 80W TGP) supporting DLSS 3.5 ray reconstruction and full Ray Tracing. Thermal management is handled by an internal vapor chamber with dual high-pressure fans that is 11% wider than the previous generation, reducing fan noise to under 38dB under normal creative workloads. Supports up to 64GB LPDDR5X RAM and dual PCIe Gen 4 NVMe SSD slots."
            },
            {
                "section": "Display & Studio-Quality Audio",
                "text": "Features a 16-inch Dynamic AMOLED 2X touchscreen (2880 x 1800, 16:10, 120Hz VRR, 400 nits typical, 500 nits HDR). Audio is delivered by a quad-speaker acoustic system (two 5W woofers and two 2W tweeters) tuned by AKG with Dolby Atmos. Features a 1080p FHD webcam with bidirectional AI noise reduction microphones."
            }
        ]
    },
    {
        "doc_id": "samsung-galaxy-watch-ultra",
        "title": "Samsung Galaxy Watch Ultra Outdoor Smartwatch",
        "category": "Wearables / Outdoor",
        "source": "Samsung Galaxy Watch Ultra Hardware Manual (2024)",
        "tags": ["Watch Ultra", "Titanium Grade 4", "100m 10ATM", "MIL-STD-810H", "Exynos W1000 3nm", "590mAh Battery", "86dB Siren", "Dual GPS L1+L5"],
        "sections": [
            {
                "section": "Durability, Titanium Chassis & Water Resistance",
                "text": "The Galaxy Watch Ultra is enclosed in a rugged 47mm cushion-shaped case crafted from aerospace-grade Grade 4 Titanium. It is rated for 100-meter (10 ATM) water resistance according to ISO 22810 standards, and holds EN13319 certification for ocean and open-water swimming. Certified to MIL-STD-810H military specifications, it operates in extreme environments ranging from -20°C to 55°C and altitudes up to 9,000 meters above sea level. The display is protected by a scratch-resistant Sapphire Crystal glass surface."
            },
            {
                "section": "Exynos W1000 3nm Chipset & Dual-Frequency GPS",
                "text": "Powered by Samsung's 3nm Exynos W1000 penta-core processor (1x Cortex-A78 at 1.6 GHz and 4x Cortex-A55 at 1.5 GHz), delivering 3x faster app launch times and 3.7x improved power efficiency over previous generations. Navigation is powered by a dual-frequency GNSS system utilizing both L1 and L5 GPS carrier frequency bands, eliminating urban canyon multipath signal interference by over 20% in dense city environments or deep forest trails."
            },
            {
                "section": "Battery Endurance & Emergency Safety Features",
                "text": "The watch features a 590 mAh battery delivering up to 100 hours of continuous operation in Power Saving mode, up to 48 hours in Exercise Power Saving mode with continuous GPS tracking, and up to 60 hours in typical daily usage. It features an integrated 86-decibel Emergency Siren activated by holding the customizable Quick Button for 5 seconds, audible up to 180 meters away through dense terrain. Includes Fall Detection, Emergency SOS, and Medical Info broadcast."
            },
            {
                "section": "BioActive Sensor & Advanced Health Tracking",
                "text": "Equipped with an enhanced Samsung BioActive Sensor with 13 optical LEDs. Features include FDA-cleared Sleep Apnea detection, Advanced Glycation End-products (AGEs) index tracking for metabolic health monitoring, real-time ECG recording, Blood Pressure measurement, Body Composition analysis via BIA (Bioelectrical Impedance Analysis), and personalized FTP (Functional Threshold Power) cycling power metrics."
            }
        ]
    },
    {
        "doc_id": "samsung-galaxy-watch-7",
        "title": "Samsung Galaxy Watch 7 Health Smartwatch",
        "category": "Wearables / Health",
        "source": "Samsung Galaxy Watch 7 Technical Specifications",
        "tags": ["Watch 7", "Exynos W1000 3nm", "Dual GPS", "BioActive Sensor", "Sleep Apnea", "Armor Aluminum", "40mm", "44mm"],
        "sections": [
            {
                "section": "Case Sizes, Display & Silicon",
                "text": "Available in 40mm (1.3-inch Super AMOLED, 432x432, 28.8g) and 44mm (1.5-inch Super AMOLED, 480x480, 33.8g) cases constructed from Armor Aluminum with Sapphire Crystal glass. Powered by the 3nm Exynos W1000 penta-core processor with 2GB RAM and 32GB internal storage. Both sizes feature dual-frequency L1+L5 GPS."
            },
            {
                "section": "Health Features & Battery",
                "text": "Includes FDA-cleared Sleep Apnea risk detection, AGEs Index tracking, ECG, blood pressure, continuous heart rate, blood oxygen (SpO2), skin temperature sensor, and Energy Score powered by Galaxy AI. The 40mm model houses a 300 mAh battery, while the 44mm has a 425 mAh battery with WPC-based wireless fast charging. Water resistant up to 5 ATM + IP68, MIL-STD-810H certified."
            }
        ]
    },
    {
        "doc_id": "samsung-galaxy-buds3-pro",
        "title": "Samsung Galaxy Buds3 Pro Flagship Hi-Fi Earbuds",
        "category": "Audio / Flagship",
        "source": "Samsung Galaxy Buds3 Pro Technical Audio Overview (2024)",
        "tags": ["Buds3 Pro", "Blade Design", "Blade Lights", "Planar Tweeter", "Dual Amp", "24-bit 96kHz SSC", "Adaptive ANC", "Siren Detect"],
        "sections": [
            {
                "section": "Acoustic Engineering & Dual Amplifier Architecture",
                "text": "The Galaxy Buds3 Pro feature an all-new blade stem design with interactive Blade Lights. The internal acoustic architecture employs a 2-way coaxial speaker system combining an 10.5mm dynamic woofer with an innovative 6.1mm planar tweeter capable of extending treble response up to 40 kHz. Each speaker unit is driven independently by dual discrete digital-to-analog converters (Dual Amplifiers), eliminating cross-frequency distortion and delivering precise instrument separation."
            },
            {
                "section": "24-Bit 96kHz High-Resolution Audio & SSC Codec",
                "text": "When paired with compatible Samsung Galaxy smartphones (One UI 6.1.1 or later), the Buds3 Pro support 24-bit / 96kHz ultra-high-quality audio streaming over Bluetooth 5.4 using the proprietary Samsung Seamless Codec (SSC UHQ). The codec doubles the sampling bitrate compared to standard 24-bit 48kHz audio."
            },
            {
                "section": "Adaptive Noise Control, Siren & Voice Detection",
                "text": "The Buds3 Pro utilize three high-SNR microphones per earbud alongside a Voice Pickup Unit (VPU) and bone conduction vibration sensor. Adaptive ANC continuously evaluates ambient noise leakage and ear canal shape to dynamically adjust cancellation curves. Automatic Siren Detect senses emergency vehicle sirens and reduces ANC to allow critical environmental awareness, while Voice Detect lowers audio volume and switches to Ambient Mode when the wearer begins speaking."
            },
            {
                "section": "Battery Life, Stem Pinch Controls & IP57 Rating",
                "text": "Battery runtime delivers up to 6 hours of continuous playback with ANC enabled (up to 26 hours including the wireless charging cradle) and 7 hours with ANC disabled (30 hours total). The earbuds feature intuitive pinch controls on the blade for play/pause and volume slide controls. IP57 certified water and dust resistance."
            }
        ]
    },
    {
        "doc_id": "samsung-galaxy-ring",
        "title": "Samsung Galaxy Ring Smart Wellness Tracker",
        "category": "Wearables / Health",
        "source": "Samsung Galaxy Ring Hardware & Sensor Specification (2024)",
        "tags": ["Galaxy Ring", "Titanium Grade 5", "Energy Score", "Skin Temp", "Sleep Analysis", "7 Days Battery", "10ATM IP68"],
        "sections": [
            {
                "section": "Form Factor, Materials & Sizing",
                "text": "The Galaxy Ring is constructed with a concave Grade 5 Titanium exterior casing with a lightweight profile weighing between 2.3 grams (Size 5) and 3.0 grams (Size 13). It measures 7.0mm in width and 2.6mm in thickness. Available in three finishes: Titanium Black, Titanium Silver, and Titanium Gold. Water-resistant up to 100 meters (10 ATM) and IP68 certified."
            },
            {
                "section": "Sensors, Health Tracking & Battery",
                "text": "Houses three integrated sensors: an Optical Bio-signal Sensor (photoplethysmogram PPG) for continuous heart rate and blood oxygen monitoring, an embedded skin temperature sensor for menstrual cycle tracking and sleep stage temperature tracking, and a 3-axis accelerometer for step and sleep movement detection. Generates an AI-powered Energy Score assessing physical readiness based on sleep regularity, activity, and resting heart rate. Battery life lasts up to 7 days on a single charge for sizes 12-13 (up to 6 days for smaller sizes). Comes with a transparent clamshell charging case featuring an LED battery indicator ring."
            }
        ]
    },
    {
        "doc_id": "samsung-neo-qled-8k-qn900d",
        "title": "Samsung QN900D Neo QLED 8K Smart TV",
        "category": "Smart TVs / 8K Flagship",
        "source": "Samsung QN900D Neo QLED 8K Television Technical Manual",
        "tags": ["QN900D", "Neo QLED 8K", "NQ8 AI Gen3", "512 Neural Networks", "8K AI Upscaling Pro", "AI Motion Enhancer Pro", "Infinity Air Design"],
        "sections": [
            {
                "section": "NQ8 AI Gen3 Neural Processor & 8K Upscaling",
                "text": "The QN900D is powered by Samsung's NQ8 AI Gen3 television processor, featuring an on-chip neural processing unit with 512 neural networks—an eight-fold increase compared to its predecessor. The 8K AI Upscaling Pro engine analyzes lower-resolution input streams (SD, HD, 4K) in real time to recreate textures, sharpen fine text, and eliminate compression artifacts. AI Motion Enhancer Pro detects the trajectory of fast-moving sports balls (e.g. soccer or tennis) to eliminate motion blur and ghosting."
            },
            {
                "section": "Quantum Mini LED & Infinity Air Design",
                "text": "The display utilizes Quantum Mini LEDs that are 1/40th the height of standard LEDs, driven by Quantum Matrix Technology Pro for precise localized dimming without light blooming. Real Depth Enhancer Pro detects the primary subject in a scene and enhances foreground contrast to simulate human eye depth perception. The TV features the Infinity Air Design with an ultra-slim 12.9mm bezel-less profile and a mirrored stand that creates the visual illusion of a floating screen. Comes with the detachable Slim One Connect Box."
            },
            {
                "section": "Audio Acoustic System & Gaming Hub",
                "text": "Audio is driven by a 90W 6.2.4-channel system with up-firing and side-firing speakers supporting Dolby Atmos. Object Tracking Sound Pro (OTS Pro) maps audio placement to the spatial coordinates of on-screen objects. Active Voice Amplifier Pro uses AI to isolate dialogue from background ambient noise. For gaming, it supports 4K 240Hz and 8K 60Hz with AMD FreeSync Premium Pro, 4x HDMI 2.1 ports, and Samsung Gaming Hub for cloud gaming."
            }
        ]
    },
    {
        "doc_id": "samsung-oled-s95d",
        "title": "Samsung S95D Glare-Free 4K OLED Smart TV",
        "category": "Smart TVs / 4K OLED",
        "source": "Samsung S95D OLED Television Reference Guide",
        "tags": ["S95D", "OLED Glare-Free", "NQ4 AI Gen2", "Pantone Validated", "144Hz", "One Connect Box", "70W Dolby Atmos"],
        "sections": [
            {
                "section": "OLED Glare-Free Technology & Picture Quality",
                "text": "The Samsung S95D OLED TV incorporates OLED Glare-Free technology, a specialized micro-matte coating that neutralizes room reflections and window glare without degrading color saturation or contrast. The panel achieves up to 20% higher peak brightness than preceding OLED generations and is Pantone Validated for reproducing over 2,000 skin tone and color shades with laboratory precision. Powered by the NQ4 AI Gen2 processor with 20 neural networks."
            },
            {
                "section": "Gaming, Audio & Tizen OS",
                "text": "Supports up to 4K 144Hz refresh rate with VRR (Variable Refresh Rate), AMD FreeSync Premium Pro, and ultra-low 5ms input lag. Sound output is powered by a 70W 4.2.2-channel Dolby Atmos speaker array with Object Tracking Sound+. Powered by Tizen OS 8.0, featuring Samsung Daily+ for SmartThings home control, 3D Map View, and Samsung TV Plus with hundreds of free live channels."
            }
        ]
    },
    {
        "doc_id": "samsung-the-frame-ls03d",
        "title": "Samsung The Frame LS03D Lifestyle 4K Art TV",
        "category": "Smart TVs / Lifestyle",
        "source": "Samsung The Frame LS03D Technical Overview",
        "tags": ["The Frame", "Matte Display", "Art Mode", "Samsung Art Store", "Pantone Art", "Customizable Bezels", "Slim Fit Wall Mount"],
        "sections": [
            {
                "section": "Matte Display & Art Mode Innovation",
                "text": "The Frame LS03D features a 4K QLED panel with a specialized Matte Display that diffuses light reflections to mimic physical paper and museum canvas. In Art Mode, the TV displays curated artwork or family photos with an energy-saving motion sensor that turns off the screen when the room is empty. The Samsung Art Store provides access to over 2,500 artworks from world-renowned galleries including the Louvre, Prado, and Tate. Features Pantone Art Validated color reproduction and a brightness sensor that adjusts screen tone to ambient room lighting."
            },
            {
                "section": "Installation, Custom Bezels & One Connect",
                "text": "Includes the Slim-Fit Wall Mount allowing the screen to hang flush against the wall like a picture frame. Magnetic customizable bezels are available in various colors and wood finishes (Teak, Walnut, White, Sand Gold). Connected via the One Invisible Connection cable—a single, translucent 5-meter fiber-optic cable transmitting both power and video signals from the external One Connect Box."
            }
        ]
    },
    {
        "doc_id": "samsung-bespoke-ai-family-hub",
        "title": "Samsung Bespoke 4-Door Flex Refrigerator with AI Family Hub+",
        "category": "Home Appliances / Refrigerator",
        "source": "Samsung Bespoke Home Appliances Product Specification (2024)",
        "tags": ["Bespoke Refrigerator", "AI Family Hub+", "32 inch Touchscreen", "AI Vision Inside", "Beverage Center", "SmartThings Energy"],
        "sections": [
            {
                "section": "32-Inch AI Family Hub+ Screen & AI Vision Inside",
                "text": "The Bespoke 4-Door Flex features a 32-inch vertical Full HD touchscreen integrated into the door panel. Inside the upper compartment, an AI Vision Inside wide-angle camera identifies fresh food items (fruits, vegetables, dairy) when placed inside or removed, trained on an optical recognition model containing over 300,000 food images. The system maintains an automatic food inventory, sends expiration alerts to user smartphones, and suggests recipes via Samsung Food based on available ingredients."
            },
            {
                "section": "Beverage Center & Dual Auto Ice Maker",
                "text": "Features a concealed Beverage Center with an internal water dispenser and an AutoFill Water Pitcher that automatically refills with filtered water and can infuse sliced fruits or tea. The Dual Auto Ice Maker produces both cubed ice and Ice Bites (smaller, chewable nugget ice) with a combined storage capacity of up to 9.9 lbs."
            },
            {
                "section": "Triple Cooling & SmartThings Energy Automation",
                "text": "The Triple Cooling system uses three independent evaporators to maintain separate humidity and temperature zones across the fridge, freezer, and FlexZone compartment (which switches between freezer, soft freeze, meat, beverage, or wine cooling). With SmartThings Energy AI Energy Mode, the compressor cycle dynamically adjusts based on door-opening frequency and ambient temperature, reducing power consumption by up to 10%."
            }
        ]
    },
    {
        "doc_id": "samsung-bespoke-ai-laundry-combo",
        "title": "Samsung Bespoke AI Laundry Combo Washer & Dryer",
        "category": "Home Appliances / Laundry",
        "source": "Samsung Bespoke AI Laundry Technical Whitepaper",
        "tags": ["Bespoke Laundry Combo", "Heat Pump Drying", "AI OptiWash & Dry", "Flex Auto Dispense", "7 inch LCD Screen", "Super Speed 98 min"],
        "sections": [
            {
                "section": "Ventless Heat Pump Drying & All-in-One Form Factor",
                "text": "The Bespoke AI Laundry Combo combines a 5.3 cu. ft. high-capacity washer and dryer in a single space-saving unit without requiring clothing transfer. It utilizes advanced Heat Pump Drying technology, which recirculates warm air and condenses moisture at low temperatures (around 60°C), protecting fabric fibers from heat shrinkage and reducing energy consumption by up to 60% compared to standard vented resistance dryers. It completes a full wash and dry cycle in 98 minutes via Super Speed."
            },
            {
                "section": "AI OptiWash & Dry Sensor Intelligence",
                "text": "The AI OptiWash & Dry cycle uses multiple internal sensors to detect laundry load weight, fabric softness, water turbidity (soil level), and real-time drying moisture. Based on turbidity readings during the wash, it adds detergent or extends rinsing if heavy soiling is detected, and dynamically optimizes dry time to avoid over-drying. The Flex Auto Dispense system holds up to 47 loads of detergent and softener, dispensing precise amounts automatically."
            },
            {
                "section": "7-Inch AI Home Display & SmartThings",
                "text": "Features a 7-inch intuitive LCD touchscreen running AI Home. Displays energy usage, water consumption, and cycle diagnostics. Connects to SmartThings to allow remote monitoring, cycle completion alerts on Samsung TVs and Galaxy watches, and auto-opening door mechanism at the end of the dry cycle to prevent mildew odor."
            }
        ]
    },
    {
        "doc_id": "samsung-bespoke-jet-bot-combo-ai",
        "title": "Samsung Bespoke Jet Bot Combo AI Robot Vacuum & Mop",
        "category": "Home Appliances / Floor Care",
        "source": "Samsung Bespoke Jet Bot Combo AI Technical Specifications",
        "tags": ["Jet Bot Combo AI", "AI Floor Detect", "Steam Sanitization", "dToF LiDAR", "3D Obstacle Avoidance", "Mop Lifting 10mm"],
        "sections": [
            {
                "section": "AI Object Recognition & 3D Obstacle Avoidance",
                "text": "The Bespoke Jet Bot Combo AI utilizes an active stereo 3D camera and an AI recognition model to detect and classify complex home obstacles, including thin power cables, pet toys, rugs, and spilled liquids. Its dToF (direct Time-of-Flight) LiDAR sensor scans room layouts with millimeter accuracy, generating accurate 3D floor maps in the SmartThings app."
            },
            {
                "section": "Dual Spinning Mop Pads & AI Floor Detect",
                "text": "Equipped with dual mop pads spinning at 170 RPM with 10 Newtons of downward pressure. The AI Floor Detect sensor distinguishes between hardwood floors and carpets; when reaching a carpet, the robot automatically lifts the wet mop pads by 10mm (or returns to the base station to detach the mops entirely for thick high-pile carpets) to prevent carpet dampness."
            },
            {
                "section": "Clean Station with Steam Pad Wash & Dry",
                "text": "The all-in-one Clean Station empties the robot's dustbin using Air Pulse technology, refills the clean water tank, and washes the dirty mop pads with 55°C hot water and high-temperature steam (100°C steam kills 99.99% of bacteria on the mop pads), followed by 55°C heated air drying to eliminate odors."
            }
        ]
    },
    {
        "doc_id": "samsung-knox-security-vault",
        "title": "Samsung Knox Security & Knox Vault Hardware Architecture",
        "category": "Security & Privacy",
        "source": "Samsung Knox Security Architecture & Hardware Whitepaper",
        "tags": ["Knox Vault", "EAL5+ Hardware", "Secure Processor", "Tamper Resistance", "Knox Matrix", "Biometric Security", "One UI"],
        "sections": [
            {
                "section": "Knox Vault Hardware Execution Isolation",
                "text": "Samsung Knox Vault is an EAL5+ (Evaluation Assurance Level 5+) certified security sub-system that is physically and electrically isolated from the main application processor (AP) and shared RAM. It consists of a dedicated Knox Vault processor, a secure hardware bus, and tamper-resistant secure memory. It securely executes cryptographic operations and stores critical security keys, biometric templates (fingerprint and face data), Samsung Pass credentials, Android Keystore keys, and Samsung Blockchain private keys."
            },
            {
                "section": "Physical Tamper Detection & Hardware Self-Destruct",
                "text": "Knox Vault includes specialized physical tamper-detection sensors that monitor voltage fluctuations, glitching attacks, temperature anomalies, laser probing, and physical package intrusion. If a physical tampering attempt is detected, Knox Vault immediately and irreversibly burns its cryptographic master fuse, permanently destroying stored encryption keys to ensure sensitive user data can never be extracted through hardware forensic methods."
            },
            {
                "section": "Knox Matrix & End-to-End Encrypted Cloud Sync",
                "text": "Knox Matrix is Samsung's multi-device security vision that enables mutual device verification across the Galaxy ecosystem. When syncing Samsung Cloud credentials, photos, and backups across devices, Knox Matrix utilizes private blockchain-based end-to-end encryption (E2EE), ensuring data can only be decrypted on trusted, authenticated Galaxy devices."
            }
        ]
    },
    {
        "doc_id": "samsung-one-ui-7-and-galaxy-ai",
        "title": "Samsung One UI 7 Platform & Galaxy AI Intelligence Suite",
        "category": "Software & AI Suite",
        "source": "Samsung One UI 7 Developer Documentation & Galaxy AI Guide",
        "tags": ["One UI 7", "Galaxy AI", "Circle to Search", "Live Translate", "Note Assist", "Transcript Assist", "Generative Edit", "Battery Protection"],
        "sections": [
            {
                "section": "One UI 7 Visual Redesign & Now Bar",
                "text": "One UI 7 introduces a modernized design system with rounded pill elements, smooth blur effects, and separated Quick Settings and Notification shade panes. The lockscreen features the Now Bar, an interactive dynamic pill displaying live background activities such as timers, voice recording status, music playback, and fitness metrics. Fluid spring animations operate on an upgraded 120Hz motion engine."
            },
            {
                "section": "Galaxy AI Communication Features",
                "text": "Live Translate provides real-time, two-way speech translation on voice calls inside the native Phone app in 16+ languages, running on-device without cloud latency. The Interpreter feature provides a split-screen conversation view for face-to-face dialogue. Chat Assist inside Samsung Keyboard suggests contextual tone styles (Professional, Casual, Social, Polite) and checks spelling and grammar."
            },
            {
                "section": "Galaxy AI Productivity & Imaging Tools",
                "text": "Circle to Search with Google allows users to circle or tap any visual element to search, translate full-screen text, or solve math equations. Note Assist in Samsung Notes generates bulleted summaries, auto-formats meeting minutes, and transcribes handwriting. Transcript Assist in Voice Recorder distinguishes up to 10 speakers in a meeting and outputs timestamped transcripts with summaries. Generative Edit enables resizing, relocating, or removing unwanted objects in photos with AI background infill."
            },
            {
                "section": "Battery Protection Options in One UI",
                "text": "One UI offers three configurable Battery Protection profiles to maximize lithium-ion battery health: Basic mode charges the battery to 100% and halts charging until the battery drops below 95%; Adaptive mode charges to 80% overnight and completes charging to 100% just before the user's estimated wake-up time; and Maximum mode imposes a hard cap at 80% charge level, extending cycle life from ~500 cycles to over 1,500 cycles."
            }
        ]
    },
    {
        "doc_id": "samsung-smartthings-ecosystem",
        "title": "Samsung SmartThings Home Automation & Mesh Network",
        "category": "Ecosystem & Connectivity",
        "source": "Samsung SmartThings Connectivity Architecture Manual",
        "tags": ["SmartThings", "Matter Border Router", "Zigbee", "Thread", "3D Map View", "SmartThings Find", "UWB Finding"],
        "sections": [
            {
                "section": "Built-In Matter & Thread Border Router Hubs",
                "text": "Samsung integrates SmartThings Hub functionality directly into high-end Samsung Smart TVs, soundbars, and Family Hub refrigerators. These devices function as Thread border routers and Matter controllers, allowing consumers to connect and automate cross-brand Matter, Zigbee, and Wi-Fi smart devices locally without buying standalone hardware bridges. Local automations execute with sub-50ms response times directly over LAN."
            },
            {
                "section": "3D Map View & Energy Care",
                "text": "3D Map View renders a digital twin of the user's floor plan based on LiDAR scans from the Bespoke Jet Bot vacuum or user blueprint imports. It visualizes the real-time status of lighting, temperature, air quality, and appliance power draw in each room. SmartThings Energy monitors electricity tariffs and solar generation, automatically scheduling appliance runs during off-peak hours."
            },
            {
                "section": "SmartThings Find & Ultra-Wideband (UWB) Precision Search",
                "text": "The SmartThings Find network utilizes encrypted Bluetooth Low Energy (BLE) beaconing across hundreds of millions of participating Galaxy devices globally to locate lost phones, tablets, watches, and Galaxy SmartTags. For devices equipped with UWB (such as Galaxy S25 Ultra, S24 Ultra, Fold6, and SmartTag2), the AR Finding camera view displays directional arrows with centimeter-level precision distance indicators."
            }
        ]
    },
    {
        "doc_id": "samsung-semiconductor-exynos-isocell",
        "title": "Samsung Semiconductor, Exynos & ISOCELL Sensor Innovations",
        "category": "Semiconductor & Hardware",
        "source": "Samsung Semiconductor Technical Briefing & Architecture Papers",
        "tags": ["Exynos 2400", "AMD RDNA 3", "Xclipse 940", "ISOCELL HP2", "Tetra2pixel", "LPDDR5X", "UFS 4.0", "3nm GAA"],
        "sections": [
            {
                "section": "Exynos 2400 10-Core Chipset & Xclipse 940 GPU",
                "text": "The Samsung Exynos 2400 processor is fabricated on Samsung Foundry's 4nm FinFET process. It features a 10-core CPU layout: 1x Cortex-X4 at 3.2 GHz, 2x Cortex-A720 at 2.9 GHz, 3x Cortex-A720 at 2.6 GHz, and 4x Cortex-A520 efficiency cores at 2.0 GHz. The graphics processor is the Samsung Xclipse 940 GPU, engineered in collaboration with AMD on the RDNA 3 microarchitecture, bringing hardware ray tracing, variable rate shading (VRS), and AMD FidelityFX Super Resolution to mobile gaming."
            },
            {
                "section": "ISOCELL HP2 200MP Image Sensor Technology",
                "text": "Samsung's flagship 200MP ISOCELL HP2 image sensor features 0.6µm pixels in a 1/1.3-inch optical format. It utilizes Tetra2pixel binning technology that adapts to lighting conditions: in bright daylight, it captures full 200MP photos; in moderate indoor light, it binds 4 adjacent pixels into 1.2µm 50MP images; and in low-light night conditions, it merges 16 adjacent pixels into a 2.4µm 12.5MP super-pixel image for enhanced light sensitivity. Dual Vertical Transfer Gate (D-VTG) technology reduces overexposure in bright scenes by increasing full-well capacity by 33%."
            },
            {
                "section": "LPDDR5X DRAM & UFS 4.0 Memory Architecture",
                "text": "Samsung's LPDDR5X DRAM delivers data transmission speeds up to 10.7 Gbps with a 25% power efficiency improvement using high-k metal gate dielectric technology. Samsung UFS 4.0 flash storage provides sequential read speeds of up to 4,200 MB/s and sequential write speeds of up to 2,800 MB/s, doubling the bandwidth of UFS 3.1 while consuming 46% less power."
            }
        ]
    }
]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_data_path = os.path.join(base_dir, "app", "frontend", "data", "samsung_knowledge_base.json")
    backend_data_path = os.path.join(base_dir, "app", "backend", "src", "ingestion", "samsung_knowledge_base.json")

    os.makedirs(os.path.dirname(frontend_data_path), exist_ok=True)
    os.makedirs(os.path.dirname(backend_data_path), exist_ok=True)

    # Calculate statistics
    total_docs = len(KNOWLEDGE_BASE)
    total_sections = sum(len(doc["sections"]) for doc in KNOWLEDGE_BASE)
    total_words = sum(sum(len(sec["text"].split()) for sec in doc["sections"]) for doc in KNOWLEDGE_BASE)

    with open(frontend_data_path, "w", encoding="utf-8") as f:
        json.dump(KNOWLEDGE_BASE, f, indent=2, ensure_ascii=False)

    with open(backend_data_path, "w", encoding="utf-8") as f:
        json.dump(KNOWLEDGE_BASE, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated Samsung Knowledge Base:")
    print(f"  • Total Documents: {total_docs}")
    print(f"  • Total Chunks/Sections: {total_sections}")
    print(f"  • Total Word Count: {total_words:,} words")
    print(f"  • Written to: {frontend_data_path}")
    print(f"  • Written to: {backend_data_path}")

if __name__ == "__main__":
    main()
