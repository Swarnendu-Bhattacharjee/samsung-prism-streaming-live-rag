import type { NextApiRequest, NextApiResponse } from 'next'

export const SCENARIOS = [
  {
    id: "s25-vs-s24-ultra",
    title: "S25 Ultra vs S24 Ultra Comparison",
    prompt: "Compare Galaxy S25 Ultra vs S24 Ultra in terms of camera, titanium build, and processor.",
    category: "Hardware Comparison",
    description: "Evaluates multi-attribute comparison between Snapdragon 8 Elite and 8 Gen 3, Titanium Grade 5 vs 2, and new 50MP ultrawide camera."
  },
  {
    id: "fold6-multitasking",
    title: "Galaxy Z Fold6 Multitasking & Hinge",
    prompt: "How does the Galaxy Z Fold6 dual-rail FlexHinge and Multi-Active Window work for productivity?",
    category: "Foldables",
    description: "Evaluates foldable engineering, 239g weight reduction, IP48 protection, and 3-app split screen multitasking."
  },
  {
    id: "tab-s10-ultra-dimensity",
    title: "Tab S10 Ultra MediaTek Dimensity 9300+",
    prompt: "Why did Samsung choose the MediaTek Dimensity 9300+ for Galaxy Tab S10 Ultra and what are its display specs?",
    category: "Tablets",
    description: "Analyzes the 14.6-inch Dynamic AMOLED 2X anti-reflection coating and Dimensity 9300+ all-big-core architecture."
  },
  {
    id: "watch-ultra-endurance",
    title: "Galaxy Watch Ultra Extreme Durability",
    prompt: "What are the extreme durability and battery specs of the Galaxy Watch Ultra?",
    category: "Wearables",
    description: "Evaluates Grade 4 Titanium case, 100m water resistance, 86dB siren, and 3nm Exynos W1000 chipset."
  },
  {
    id: "general-science-bypass",
    title: "Direct General API (RAG Bypassed)",
    prompt: "Explain the difference between mitosis and meiosis in two sentences.",
    category: "Dual-Mode Routing",
    description: "Demonstrates the Dual-Mode Decision Gate bypassing RAG for sub-100ms TTFT on general science queries."
  }
]

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  return res.status(200).json(SCENARIOS)
}
