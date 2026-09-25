import type { NextApiRequest, NextApiResponse } from 'next'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const sampleTrace = {
    has_run: true,
    last_updated: Date.now() / 1000,
    query: "Compare Galaxy S25 Ultra vs S24 Ultra display and camera",
    session_id: "session_live_demo",
    stages: {
      pipeline: {
        status: "completed",
        query: "Compare Galaxy S25 Ultra vs S24 Ultra display and camera",
        start_time: Date.now() / 1000 - 1.2,
      },
      intent: {
        intent: "samsung_product_factual",
        needs_rag: true,
        mode: "hybrid_rag_plus_general",
        confidence: 0.98,
        latency_ms: 12.4,
      },
      decomposition: {
        sub_queries: [
          "Compare Galaxy S25 Ultra vs S24 Ultra display and camera",
          "Galaxy S25 Ultra vs S24 Ultra Dynamic AMOLED 2X nits brightness",
          "Galaxy S25 Ultra 200MP camera vs S24 Ultra 5x periscope telephoto"
        ],
        count: 3,
        latency_ms: 28.5,
      },
      hybrid: {
        sub_query_hits: [
          { index: 0, query: "Compare Galaxy S25 Ultra vs S24 Ultra display and camera", hits: 12 },
          { index: 1, query: "Galaxy S25 Ultra vs S24 Ultra Dynamic AMOLED 2X nits brightness", hits: 15 },
          { index: 2, query: "Galaxy S25 Ultra 200MP camera vs S24 Ultra 5x periscope telephoto", hits: 14 }
        ],
        total_unique_candidates: 24,
        latency_ms: 32.1,
      },
      rrf: {
        total_fused: 18,
        method: "RRF (k=60)",
        latency_ms: 4.2,
      },
      cross_encoder: {
        top_candidates: [
          { doc_id: "samsung-galaxy-s25-ultra", score: 8.92, source: "Samsung Galaxy S25 Ultra Official Technical Documentation" },
          { doc_id: "samsung-galaxy-s24-ultra", score: 7.45, source: "Samsung Galaxy S24 Ultra Technical Specification Sheet" },
          { doc_id: "samsung-semiconductor-exynos-isocell", score: 5.12, source: "Samsung Semiconductor Technical Briefing" }
        ],
        latency_ms: 22.8,
      },
      sharpening: {
        is_sharpened: true,
        retained: 14,
        delta: 6,
        reduction: "42.4%",
        latency_ms: 6.5,
      },
      synthesis: {
        mode: "hybrid_rag_plus_general",
        ttft_ms: 118,
        tokens_per_sec: 152.4,
        total_tokens: 342,
        latency_ms: 1120.0,
      }
    }
  }

  return res.status(200).json(sampleTrace)
}
