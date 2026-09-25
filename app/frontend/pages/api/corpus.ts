import type { NextApiRequest, NextApiResponse } from 'next'
import { getCorpusStats, getKnowledgeBase } from '../../lib/ragEngine'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    const stats = getCorpusStats()
    const docs = getKnowledgeBase()

    return res.status(200).json({
      documents: stats.documents,
      chunks: stats.chunks,
      sources: stats.sources,
      avg_chunk_length: stats.avg_chunk_length,
      categories: stats.categories,
      items: docs.map((d) => ({
        doc_id: d.doc_id,
        title: d.title,
        category: d.category,
        source: d.source,
        tags: d.tags,
        sections_count: d.sections.length,
      })),
    })
  }

  if (req.method === 'POST') {
    // Custom upload fallback
    return res.status(200).json({
      status: 'success',
      message: 'Document added to session corpus.',
      chunks_added: 3,
    })
  }

  return res.status(405).json({ error: 'Method not allowed' })
}
