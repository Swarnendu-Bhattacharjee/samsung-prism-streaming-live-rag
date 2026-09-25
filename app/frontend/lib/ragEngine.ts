import path from 'path'
import fs from 'fs'

export interface KnowledgeSection {
  section: string
  text: string
}

export interface KnowledgeDocument {
  doc_id: string
  title: string
  category: string
  source: string
  tags: string[]
  sections: KnowledgeSection[]
}

export interface ChunkItem {
  id: string
  doc_id: string
  source: string
  title: string
  category: string
  section: string
  text: string
  word_count: number
}

export interface SearchResult {
  doc_id: string
  source: string
  title: string
  section: string
  text: string
  score: number
  sub_query?: string
}

let _cachedKnowledgeBase: KnowledgeDocument[] | null = null
let _cachedChunks: ChunkItem[] | null = null

export function getKnowledgeBase(): KnowledgeDocument[] {
  if (_cachedKnowledgeBase) return _cachedKnowledgeBase

  try {
    const dataPath = path.join(process.cwd(), 'data', 'samsung_knowledge_base.json')
    if (fs.existsSync(dataPath)) {
      const raw = fs.readFileSync(dataPath, 'utf-8')
      _cachedKnowledgeBase = JSON.parse(raw)
      return _cachedKnowledgeBase!
    }
  } catch (err) {
    console.error('[RAG Engine] Error reading knowledge base JSON from disk:', err)
  }

  // Fallback if file not found at process.cwd()
  try {
    const altPath = path.join(process.cwd(), 'app', 'frontend', 'data', 'samsung_knowledge_base.json')
    if (fs.existsSync(altPath)) {
      const raw = fs.readFileSync(altPath, 'utf-8')
      _cachedKnowledgeBase = JSON.parse(raw)
      return _cachedKnowledgeBase!
    }
  } catch (err) {
    console.error('[RAG Engine] Error reading knowledge base from alt path:', err)
  }

  _cachedKnowledgeBase = []
  return _cachedKnowledgeBase
}

export function getAllChunks(): ChunkItem[] {
  if (_cachedChunks) return _cachedChunks

  const docs = getKnowledgeBase()
  const chunks: ChunkItem[] = []

  docs.forEach((doc, docIdx) => {
    doc.sections.forEach((sec, secIdx) => {
      chunks.push({
        id: `${doc.doc_id}_${secIdx}`,
        doc_id: doc.doc_id,
        source: doc.source,
        title: doc.title,
        category: doc.category,
        section: sec.section,
        text: `Section: ${sec.section}\n${sec.text}`,
        word_count: sec.text.split(/\s+/).length,
      })
    })
  })

  _cachedChunks = chunks
  return _cachedChunks
}

export function getCorpusStats() {
  const docs = getKnowledgeBase()
  const chunks = getAllChunks()
  const sources = docs.map((d) => d.source)
  const totalLength = chunks.reduce((acc, c) => acc + c.text.length, 0)

  return {
    documents: docs.length,
    chunks: chunks.length,
    sources,
    avg_chunk_length: chunks.length > 0 ? Math.round(totalLength / chunks.length) : 0,
    categories: Array.from(new Set(docs.map((d) => d.category))),
  }
}

// ── DUAL-MODE DECISION GATE ──────────────────────────────────────────────────

const SAMSUNG_KEYWORDS = [
    'samsung', 'galaxy', 's25', 's24', 's23', 's22', 'ultra', 'fold', 'fold6', 'fold5',
    'flip', 'flip6', 'flip5', 'tab', 's10', 's9', 'book', 'book4', 'book5', 'pro 360',
    'watch', 'buds', 'buds3', 'ring', 'knox', 'smartthings', 'dex', 'one ui', 'now bar',
    'flexwindow', 'flexcam', 'blade', 'exynos', 'isocell', 'bespoke', 'jet bot', 'neo qled',
    'oled', 'the frame', 'family hub', 'optiwash', 'snapdragon 8 elite', 'dimensity 9300',
    'spen', 's pen', 'nightography', 'circle to search', 'live translate', 'generative edit',
    'gorilla armor', 'titanium'
]

const HARDWARE_ATTRIBUTES = [
  'battery', 'display', 'screen', 'camera', 'megapixel', 'charging', 'processor',
  'chipset', 'benchmark', 'ram', 'storage', 'weight', 'npu', 'hinge', 'specs',
  'durability', 'ip68', 'ip48', 'brightness', 'nits', 'refresh rate', 'sensor'
]

export function classifyIntent(query: string): {
  needs_rag: boolean
  mode: string
  intent: string
  reason: string
  confidence: number
} {
  const lower = query.toLowerCase().trim()

  // 1. Direct Greetings & Conversational Chitchat -> Direct General API
  if (/^(hi|hello|hey|good morning|good afternoon|good evening|thanks|thank you|bye|who are you|how are you|tell me a joke|what can you do|what is your name)\b/i.test(lower)) {
    return {
      needs_rag: false,
      mode: 'direct_general_api',
      intent: 'conversational_greeting',
      reason: 'Standard conversational pleasantry/greeting; handled directly by General LLM API.',
      confidence: 0.99,
    }
  }

  const hasSamsungKeyword = SAMSUNG_KEYWORDS.some((kw) => lower.includes(kw))
  const hasAttributeKeyword = HARDWARE_ATTRIBUTES.some((attr) => lower.includes(attr))

  // 2. Clear Samsung Product or Spec Query -> Hybrid RAG
  if (hasSamsungKeyword) {
    return {
      needs_rag: true,
      mode: 'hybrid_rag_plus_general',
      intent: 'samsung_product_factual',
      reason: 'Query targets official Samsung hardware specs, pricing, comparisons, or ecosystem capabilities.',
      confidence: 0.98,
    }
  }

  // 3. Ambiguous Hardware Attribute Query -> Hybrid RAG
  if (hasAttributeKeyword) {
    return {
      needs_rag: true,
      mode: 'hybrid_rag_plus_general',
      intent: 'hardware_attribute_query',
      reason: 'Query references device specifications; grounded against Samsung product catalog.',
      confidence: 0.88,
    }
  }

  // 4. Everything else (General Science, Math, Coding, World Knowledge) -> Direct General API
  return {
    needs_rag: false,
    mode: 'direct_general_api',
    intent: 'general_world_knowledge',
    reason: 'Query pertains to general world knowledge, science, or concepts outside Samsung catalogue. Retrieval bypassed for ultra-fast TTFT.',
    confidence: 0.92,
  }
}

// ── QUERY DECOMPOSER ─────────────────────────────────────────────────────────

export function decomposeQuery(query: string): string[] {
  const lower = query.toLowerCase()

  if (lower.includes('compare') || lower.includes('vs') || lower.includes('difference between')) {
    // Generate sub-queries for comparative attributes
    const subQueries = [query]
    if (lower.includes('camera')) subQueries.push(`${query} camera sensor megapixels zoom optical`)
    if (lower.includes('battery') || lower.includes('charging')) subQueries.push(`${query} battery mAh wired fast charging hours`)
    if (lower.includes('processor') || lower.includes('chip') || lower.includes('performance')) subQueries.push(`${query} processor chipset cpu gpu npu benchmark`)
    if (lower.includes('display') || lower.includes('screen')) subQueries.push(`${query} display resolution refresh rate nits brightness`)
    
    return subQueries.slice(0, 3)
  }

  return [query]
}

// ── PARALLEL HYBRID RETRIEVAL (BM25 + DENSE) & RRF ───────────────────────────

function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter((w) => w.length > 1)
}

export function bm25Search(query: string, topK: number = 8): { chunk: ChunkItem; score: number }[] {
  const chunks = getAllChunks()
  const qTokens = tokenize(query)
  if (qTokens.length === 0) return []

  const k1 = 1.5
  const b = 0.75
  const avgdl = chunks.reduce((sum, c) => sum + tokenize(c.text).length, 0) / Math.max(chunks.length, 1)

  // Document frequencies
  const df: Record<string, number> = {}
  chunks.forEach((chunk) => {
    const words = new Set(tokenize(chunk.text))
    words.forEach((w) => {
      df[w] = (df[w] || 0) + 1
    })
  })

  const N = chunks.length
  const scored = chunks.map((chunk) => {
    const docWords = tokenize(chunk.text)
    const docLen = docWords.length
    const wordFreq: Record<string, number> = {}
    docWords.forEach((w) => {
      wordFreq[w] = (wordFreq[w] || 0) + 1
    })

    let score = 0
    qTokens.forEach((term) => {
      const tf = wordFreq[term] || 0
      if (tf > 0) {
        const docFreq = df[term] || 1
        const idf = Math.log(1 + (N - docFreq + 0.5) / (docFreq + 0.5))
        const numerator = tf * (k1 + 1)
        const denominator = tf + k1 * (1 - b + b * (docLen / avgdl))
        score += idf * (numerator / denominator)
      }
    })

    // Boost exact matches of product names (e.g. S25 Ultra, Fold6)
    if (chunk.text.toLowerCase().includes(query.toLowerCase())) {
      score += 3.5
    }

    return { chunk, score }
  })

  return scored
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, topK)
}

export function semanticSearch(query: string, topK: number = 8): { chunk: ChunkItem; score: number }[] {
  const chunks = getAllChunks()
  const qTokens = tokenize(query)
  if (qTokens.length === 0) return []

  // Cosine-like keyword overlap weighted by length and entity presence
  const scored = chunks.map((chunk) => {
    const chunkTokens = tokenize(chunk.text)
    const chunkSet = new Set(chunkTokens)
    let overlap = 0

    qTokens.forEach((t) => {
      if (chunkSet.has(t)) overlap += 1
    })

    const norm = Math.sqrt(qTokens.length * Math.min(chunkTokens.length, 100))
    const score = norm > 0 ? overlap / norm : 0

    return { chunk, score }
  })

  return scored
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, topK)
}

export function reciprocalRankFusion(
  bm25Hits: { chunk: ChunkItem; score: number }[],
  semanticHits: { chunk: ChunkItem; score: number }[],
  k: number = 60,
  topN: number = 5
): SearchResult[] {
  const rrfScores: Record<string, { chunk: ChunkItem; rrf: number; bm25Rank: number; denseRank: number }> = {}

  bm25Hits.forEach((hit, rankIdx) => {
    const rank = rankIdx + 1
    if (!rrfScores[hit.chunk.id]) {
      rrfScores[hit.chunk.id] = { chunk: hit.chunk, rrf: 0, bm25Rank: rank, denseRank: 999 }
    }
    rrfScores[hit.chunk.id].rrf += 1 / (k + rank)
    rrfScores[hit.chunk.id].bm25Rank = rank
  })

  semanticHits.forEach((hit, rankIdx) => {
    const rank = rankIdx + 1
    if (!rrfScores[hit.chunk.id]) {
      rrfScores[hit.chunk.id] = { chunk: hit.chunk, rrf: 0, bm25Rank: 999, denseRank: rank }
    }
    rrfScores[hit.chunk.id].rrf += 1 / (k + rank)
    rrfScores[hit.chunk.id].denseRank = rank
  })

  const sorted = Object.values(rrfScores)
    .sort((a, b) => b.rrf - a.rrf)
    .slice(0, topN)

  return sorted.map((item) => ({
    doc_id: item.chunk.doc_id,
    source: item.chunk.source,
    title: item.chunk.title,
    section: item.chunk.section,
    text: item.chunk.text,
    score: parseFloat((item.rrf * 100).toFixed(4)),
  }))
}

// ── CONTEXT SHARPENING (beta = 0.5) ──────────────────────────────────────────

export function sharpenContext(
  sources: SearchResult[],
  query: string,
  beta: number = 0.5
): { sharpenedText: string; sources: SearchResult[]; stats: { rawTokens: number; sharpenedTokens: number; reduction: string } } {
  const qTokens = new Set(tokenize(query))

  const sharpenedSources = sources.map((src, idx) => {
    const sentences = src.text.split(/(?<=[.!?])\s+/)
    if (sentences.length <= 1) return src

    // Score sentences
    const scoredSentences = sentences.map((st) => {
      const sTokens = tokenize(st)
      let match = 0
      sTokens.forEach((t) => {
        if (qTokens.has(t)) match += 1
      })
      const score = match / Math.max(sTokens.length, 1)
      return { text: st, score }
    })

    const maxScore = Math.max(...scoredSentences.map((s) => s.score), 0.01)
    const threshold = maxScore * beta

    const retained = scoredSentences
      .filter((s, sIdx) => s.score >= threshold || sIdx === 0)
      .map((s) => s.text)
      .join(' ')

    return {
      ...src,
      text: retained,
    }
  })

  // Format context with [DOC-x] anchors
  const sharpenedText = sharpenedSources
    .map((src, idx) => `[DOC-${idx + 1}] Source: ${src.source} (${src.section})\n${src.text}`)
    .join('\n\n')

  const rawWordCount = sources.reduce((acc, s) => acc + s.text.split(/\s+/).length, 0)
  const sharpenedWordCount = sharpenedSources.reduce((acc, s) => acc + s.text.split(/\s+/).length, 0)
  const reduction = rawWordCount > 0 ? (((rawWordCount - sharpenedWordCount) / rawWordCount) * 100).toFixed(1) + '%' : '0%'

  return {
    sharpenedText,
    sources: sharpenedSources,
    stats: {
      rawTokens: Math.round(rawWordCount * 1.3),
      sharpenedTokens: Math.round(sharpenedWordCount * 1.3),
      reduction,
    },
  }
}
