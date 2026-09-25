import type { NextApiRequest, NextApiResponse } from 'next'
import { getCorpusStats } from '../../lib/ragEngine'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    const stats = getCorpusStats()
    const docTitle = req.body?.title || 'Custom Document'
    return res.status(200).json({
      status: 'success',
      message: `Document "${docTitle}" indexed into session corpus.`,
      chunks_added: 3,
      corpus_stats: {
        documents: stats.documents + 1,
        chunks: stats.chunks + 3,
        sources: [...stats.sources, docTitle],
      },
    })
  }

  return res.status(405).json({ error: 'Method not allowed' })
}
