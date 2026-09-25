import type { NextApiRequest, NextApiResponse } from 'next'
import { getCorpusStats } from '../../../lib/ragEngine'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    const stats = getCorpusStats()
    return res.status(200).json({
      status: 'success',
      message: 'Corpus reset to default Samsung ecosystem catalogue.',
      stats: {
        documents: stats.documents,
        chunks: stats.chunks,
        sources: stats.sources,
      },
    })
  }

  return res.status(405).json({ error: 'Method not allowed' })
}
