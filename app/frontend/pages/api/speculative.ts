import type { NextApiRequest, NextApiResponse } from 'next'
import { bm25Search } from '../../lib/ragEngine'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const { partial_text = '' } = req.body || {}
  const hits = partial_text.trim().length >= 10 ? bm25Search(partial_text, 3) : []

  return res.status(200).json({
    prewarmed: hits.length > 0,
    candidate_count: hits.length,
    candidates: hits.map((h) => ({ title: h.chunk.title, section: h.chunk.section })),
  })
}
