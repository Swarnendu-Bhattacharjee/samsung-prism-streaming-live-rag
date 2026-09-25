import { useState, useRef, useEffect, useCallback, useMemo } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import { marked } from 'marked'
import PipelineInspector from '../components/PipelineInspector'


interface Source {
  doc_id: string
  score: number
  source: string
  text: string
  sub_query?: string
}

interface SubQuery {
  index: number
  query: string
  hits?: number
}

interface Telemetry {
  recall: number
  groundedness: number
  ttft_ms: number
  latency_ms: number
  token_count: number
  cost_usd: number
  is_sharpened: boolean
  sources_count: number
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  subQueries?: SubQuery[]
  sources?: Source[]
  intent?: string
  isSharpened?: boolean
  sharpeningStats?: { retained: number; delta: number }
  telemetry?: Telemetry | null
  speculativeHit?: boolean
  routingMode?: { needs_rag: boolean; mode: string; reason?: string }
}


interface Scenario {
  id: string
  title: string
  prompt: string
  category: string
  description: string
}

const getBackendUrl = () => {
  if (typeof window === 'undefined') return ''
  const envUrl = process.env.NEXT_PUBLIC_BACKEND_URL
  if (envUrl) {
    if (
      window.location.hostname !== 'localhost' &&
      window.location.hostname !== '127.0.0.1' &&
      (envUrl.includes('localhost') || envUrl.includes('127.0.0.1'))
    ) {
      return ''
    }
    return envUrl.replace(/\/+$/, '')
  }
  return ''
}

const BACKEND_URL = typeof window !== 'undefined' ? getBackendUrl() : ''

// Configure marked for clean inline output
marked.setOptions({
  gfm: true,
  breaks: true,
})

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [activeStage, setActiveStage] = useState<string>('idle')
  const [currentSubQueries, setCurrentSubQueries] = useState<SubQuery[]>([])
  const [currentSources, setCurrentSources] = useState<Source[]>([])
  const [activeIntent, setActiveIntent] = useState<any>(null)
  const [speculativeCount, setSpeculativeCount] = useState<number>(0)
  const [selectedSource, setSelectedSource] = useState<Source | null>(null)
  const [showCorpusModal, setShowCorpusModal] = useState(false)
  const [corpusStats, setCorpusStats] = useState<any>({ documents: 0, chunks: 0, sources: [] })
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [customTitle, setCustomTitle] = useState('')
  const [customContent, setCustomContent] = useState('')
  const [uploadSuccess, setUploadSuccess] = useState('')
  const [isInspectorOpen, setIsInspectorOpen] = useState<boolean>(false)
  const [inspectorStage, setInspectorStage] = useState<string>('pipeline')

  const openInspector = (stageId: string) => {
    setInspectorStage(stageId)
    setIsInspectorOpen(true)
  }


  // Aggregated Telemetry HUD
  const [sessionTelemetry, setSessionTelemetry] = useState({
    totalTurns: 0,
    avgRecall: 1.0,
    avgGroundedness: 0.95,
    avgTtft: 110,
    avgLatency: 280,
    totalCost: 0.0,
  })

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const recognitionRef = useRef<any>(null)

  // Initialize session ID and fetch status
  useEffect(() => {
    const sId = `session-${Math.random().toString(36).substring(2, 9)}`
    setSessionId(sId)

    fetch(`${BACKEND_URL}/api/corpus`)
      .then(res => res.json())
      .then(data => setCorpusStats(data))
      .catch(() => {})

    fetch(`${BACKEND_URL}/api/scenarios`)
      .then(res => res.json())
      .then(data => setScenarios(data))
      .catch(() => {})
  }, [])

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isStreaming, currentSubQueries])

  // Speculative early-retrieval pre-fetch on partial typing
  const handleInputChange = (val: string) => {
    setInput(val)
    if (val.trim().length >= 20 && !isStreaming) {
      fetch(`${BACKEND_URL}/api/speculative`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, partial_text: val.trim() }),
      })
        .then(res => res.json())
        .then(data => {
          if (data.prewarmed) setSpeculativeCount(data.candidate_count)
        })
        .catch(() => {})
    } else {
      setSpeculativeCount(0)
    }
  }

  // Web Speech API Voice Recognition
  const toggleVoiceInput = () => {
    if (typeof window === 'undefined') return
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) {
      alert('Speech Recognition is not supported by your browser. Please type or use the scenario presets.')
      return
    }

    if (isListening) {
      recognitionRef.current?.stop()
      setIsListening(false)
      return
    }

    const recognition = new SpeechRecognition()
    recognitionRef.current = recognition
    recognition.continuous = false
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onstart = () => setIsListening(true)
    recognition.onresult = (event: any) => {
      let interim = ''
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        interim += event.results[i][0].transcript
      }
      handleInputChange(interim)
    }
    recognition.onerror = () => setIsListening(false)
    recognition.onend = () => setIsListening(false)
    recognition.start()
  }

  // Simulated Voice Streaming (Streams at human talking tempo ~150 wpm)
  const simulateVoiceStream = async (text: string) => {
    if (isStreaming) return
    setInput('')
    const words = text.split(' ')
    let accumulated = ''

    for (let i = 0; i < words.length; i++) {
      accumulated += (i === 0 ? '' : ' ') + words[i]
      setInput(accumulated)
      if (accumulated.length >= 20) {
        fetch(`${BACKEND_URL}/api/speculative`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: sessionId, partial_text: accumulated }),
        })
          .then(res => res.json())
          .then(data => {
            if (data.prewarmed) setSpeculativeCount(data.candidate_count)
          })
          .catch(() => {})
      }
      await new Promise(r => setTimeout(r, 55))
    }

    await new Promise(r => setTimeout(r, 200))
    executeStreamingQuery(accumulated)
  }

  // Core Streaming Execution
  const executeStreamingQuery = async (queryText: string) => {
    const q = queryText.trim()
    if (!q || isStreaming) return

    setInput('')
    setSpeculativeCount(0)
    setIsStreaming(true)
    setActiveStage('intent')
    setCurrentSubQueries([])
    setCurrentSources([])
    setActiveIntent(null)

    const userMessage: Message = { role: 'user', content: q, timestamp: Date.now() }
    setMessages(prev => [...prev, userMessage])

    let answerAccumulator = ''
    let receivedSources: Source[] = []
    let receivedSubQueries: SubQuery[] = []
    let receivedIntent: any = null
    let receivedRouting: { needs_rag: boolean; mode: string; reason?: string } | null = null
    let isSharpened = false
    let sharpeningMeta = { retained: 0, delta: 0 }
    let speculativeHit = false
    let turnTelemetry: Telemetry | null = null

    try {
      const response = await fetch(`${BACKEND_URL}/api/query/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: q,
          session_id: sessionId,
          top_k: 5,
          rerank_top_n: 3,
        }),
      })

      if (!response.ok) throw new Error(`Server returned HTTP ${response.status}`)
      const reader = response.body?.getReader()
      if (!reader) throw new Error('No readable stream available')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const events = buffer.split('\n\n')
        buffer = events.pop() || ''

        for (const ev of events) {
          if (!ev.trim()) continue
          const lines = ev.split('\n')
          let eventType = 'message'
          let dataStr = ''

          for (const line of lines) {
            if (line.startsWith('event:')) eventType = line.replace('event:', '').trim()
            if (line.startsWith('data:')) dataStr = line.replace('data:', '').trim()
          }

          if (!dataStr) continue
          try {
            const data = JSON.parse(dataStr)

            if (eventType === 'speculative_hit') {
              speculativeHit = true
            } else if (eventType === 'routing_decision') {
              receivedRouting = data
              if (!data.needs_rag) {
                setActiveStage('synthesis')
              }
            } else if (eventType === 'bypass') {
              setActiveStage('synthesis')
            } else if (eventType === 'intent') {
              receivedIntent = data
              setActiveIntent(data)
              setActiveStage('intent')
            } else if (eventType === 'decomposition') {
              setActiveStage('decomposition')
              const sqs = (data.sub_queries || []).map((query: string, index: number) => ({ index, query }))
              receivedSubQueries = sqs
              setCurrentSubQueries(sqs)
            } else if (eventType === 'sub_query_step') {
              setActiveStage('retrieval')
              setCurrentSubQueries(prev =>
                prev.map(sq => (sq.index === data.index ? { ...sq, hits: data.hits } : sq))
              )
            } else if (eventType === 'fusion') {
              setActiveStage('fusion')
            } else if (eventType === 'sharpening') {
              isSharpened = true
              sharpeningMeta = { retained: data.retained, delta: data.delta }
              setActiveStage('sharpening')
            } else if (eventType === 'sources') {
              receivedSources = data
              setCurrentSources(data)
              setActiveStage('rerank')
            } else if (eventType === 'token') {
              setActiveStage('synthesis')
              answerAccumulator += data.token
              setMessages(prev => {
                const last = prev[prev.length - 1]
                const effectiveRouting = receivedRouting || (receivedSources.length > 0 ? { needs_rag: true, mode: 'hybrid_rag_plus_general' } : { needs_rag: false, mode: 'direct_general_api' })
                if (last && last.role === 'assistant') {
                  return [
                    ...prev.slice(0, -1),
                    {
                      ...last,
                      content: answerAccumulator,
                      subQueries: receivedSubQueries,
                      sources: receivedSources,
                      intent: receivedIntent?.intent,
                      routingMode: effectiveRouting,
                      isSharpened,
                      sharpeningStats: sharpeningMeta,
                      speculativeHit,
                    },
                  ]
                } else {
                  return [
                    ...prev,
                    {
                      role: 'assistant',
                      content: answerAccumulator,
                      timestamp: Date.now(),
                      subQueries: receivedSubQueries,
                      sources: receivedSources,
                      intent: receivedIntent?.intent,
                      routingMode: effectiveRouting,
                      isSharpened,
                      sharpeningStats: sharpeningMeta,
                      speculativeHit,
                    },
                  ]
                }
              })
            } else if (eventType === 'telemetry') {
              turnTelemetry = data
              setSessionTelemetry(prev => {
                const turns = prev.totalTurns + 1
                return {
                  totalTurns: turns,
                  avgRecall: Number(((prev.avgRecall * prev.totalTurns + data.recall) / turns).toFixed(2)),
                  avgGroundedness: Number(((prev.avgGroundedness * prev.totalTurns + data.groundedness) / turns).toFixed(2)),
                  avgTtft: Math.round((prev.avgTtft * prev.totalTurns + data.ttft_ms) / turns),
                  avgLatency: Math.round((prev.avgLatency * prev.totalTurns + data.latency_ms) / turns),
                  totalCost: Number((prev.totalCost + data.cost_usd).toFixed(6)),
                }
              })
            } else if (eventType === 'done') {
              setActiveStage('complete')
              if (turnTelemetry) {
                setMessages(prev => {
                  const last = prev[prev.length - 1]
                  if (last && last.role === 'assistant') {
                    return [...prev.slice(0, -1), { ...last, telemetry: turnTelemetry }]
                  }
                  return prev
                })
              }
            }
          } catch (err) {
            console.error('SSE parse error:', err)
          }
        }
      }
    } catch (err: any) {
      console.error('Streaming error:', err)
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `Unable to complete query stream (${err.message}). Verify backend connection (${BACKEND_URL || 'serverless pipeline'}).`,
          timestamp: Date.now(),
        },
      ])
    } finally {
      setIsStreaming(false)
      setActiveStage('idle')
    }
  }

  // Handle Form Submit
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isStreaming) return
    executeStreamingQuery(input)
  }

  // Reset Session
  const handleResetSession = async () => {
    const newSession = `session-${Math.random().toString(36).substring(2, 9)}`
    setSessionId(newSession)
    setMessages([])
    setCurrentSubQueries([])
    setCurrentSources([])
    setActiveIntent(null)
    await fetch(`${BACKEND_URL}/api/chat/clear`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    }).catch(() => {})
  }

  // Ingest Document
  const handleUploadDocument = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!customTitle || !customContent) return
    try {
      const res = await fetch(`${BACKEND_URL}/api/upload`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: customTitle, content: customContent, session_id: sessionId }),
      })
      const data = await res.json()
      setCorpusStats(data.corpus_stats)
      setUploadSuccess(`Indexed "${customTitle}" into ${data.chunks_added} chunks!`)
      setCustomTitle('')
      setCustomContent('')
      setTimeout(() => setUploadSuccess(''), 4000)
    } catch (err) {
      alert('Failed to upload document')
    }
  }

  return (
    <>
      <Head>
        <title>Samsung PRISM · Streaming Live RAG (Theme 04)</title>
        <meta name="description" content="Samsung Products Conversational Live Streaming RAG" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📱</text></svg>" />
      </Head>

      {/* Main Container - Clean Samsung One UI White Theme */}
      <div className="flex h-screen bg-[#F8FAFC] text-slate-800 font-sans antialiased overflow-hidden">
        
        {/* ── LEFT & CENTER: CHAT & PIPELINE ─────────────────────────────────── */}
        <div className="flex-1 flex flex-col h-full border-r border-slate-200/80 bg-white shadow-sm">
          
          {/* Samsung One UI Header */}
          <header className="h-16 border-b border-slate-200/80 px-6 flex items-center justify-between bg-white z-20">
            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-2xl bg-[#0381FE] flex items-center justify-center text-white shadow-sm">
                <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="font-bold text-base tracking-tight text-slate-900">
                    Samsung Streaming Live RAG
                  </h1>
                  <span className="px-2.5 py-0.5 text-[11px] font-semibold rounded-full bg-blue-50 text-[#0381FE] border border-blue-200/60">
                    PRISM Theme 04
                  </span>
                  <span className="px-2.5 py-0.5 text-[11px] font-semibold rounded-full bg-amber-50 text-amber-700 border border-amber-200/60 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
                    Groq LPU™ Ultra Fast
                  </span>
                </div>
                <p className="text-xs text-slate-500 font-normal">
                  Samsung Products & Galaxy Ecosystem • Speculative Retrieval & Answer Sharpening
                </p>
              </div>
            </div>

            {/* Header Actions */}
            <div className="flex items-center gap-3">
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-200 text-xs font-medium text-slate-600">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                <span>{corpusStats.documents} Samsung Products ({corpusStats.chunks} Chunks)</span>
              </div>

              <Link
                href="/presentation"
                className="px-3.5 py-1.5 rounded-xl bg-blue-50 hover:bg-blue-100 text-xs font-semibold text-[#034EA2] transition-colors flex items-center gap-1.5 border border-blue-200"
                title="Open 12-Slide Pitch Deck Presentation"
              >
                <svg className="w-3.5 h-3.5 text-[#0381FE]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                </svg>
                Pitch Deck
              </Link>

              <button
                onClick={() => setShowCorpusModal(true)}
                className="px-3.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-slate-700 transition-colors flex items-center gap-1.5 border border-slate-200"
              >
                <svg className="w-3.5 h-3.5 text-[#0381FE]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                Knowledge Store
              </button>

              <button
                onClick={handleResetSession}
                className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                title="Reset session"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
            </div>
          </header>

          {/* ── CLEAN ONE UI PIPELINE STEPPER (INTERACTIVE STAGE INSPECTORS) ─────────────────── */}
          <div className="bg-[#F8FAFC] border-b border-slate-200 px-6 py-2.5 flex items-center justify-between text-xs overflow-x-auto gap-2">
            <button
              onClick={() => openInspector('pipeline')}
              className="flex items-center gap-1.5 text-slate-700 hover:text-[#0381FE] font-semibold text-xs pr-3 border-r border-slate-200 transition-all cursor-pointer group shrink-0"
              title="Click to inspect End-to-End Live Pipeline Architecture & Process"
            >
              <span className="text-[#0381FE] animate-pulse">●</span>
              <span>Live Pipeline</span>
              <svg className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all text-[#0381FE]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>

            <div className="flex items-center gap-1.5">
              <button
                onClick={() => openInspector('intent')}
                title="Click to view Intent Router backend logic, rules & Groq classification"
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all cursor-pointer hover:shadow-xs hover:scale-[1.02] active:scale-[0.98] ${
                  activeStage === 'intent' ? 'bg-[#0381FE] text-white shadow-sm font-semibold' : 'bg-white text-slate-700 hover:bg-slate-50 hover:text-slate-900 border border-slate-200'
                }`}
              >
                1. Intent Router
              </button>
              <span className="text-slate-300">→</span>

              <button
                onClick={() => openInspector('decomposer')}
                title="Click to view Query Decomposer backend logic & multi-query sub-tasks"
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all cursor-pointer hover:shadow-xs hover:scale-[1.02] active:scale-[0.98] ${
                  activeStage === 'decomposition' ? 'bg-[#0381FE] text-white shadow-sm font-semibold' : 'bg-white text-slate-700 hover:bg-slate-50 hover:text-slate-900 border border-slate-200'
                }`}
              >
                2. Decomposer
              </button>
              <span className="text-slate-300">→</span>

              <button
                onClick={() => openInspector('hybrid')}
                title="Click to view Parallel Hybrid (Dense 384-dim + BM25Okapi) retrieval processes"
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all cursor-pointer hover:shadow-xs hover:scale-[1.02] active:scale-[0.98] ${
                  activeStage === 'retrieval' ? 'bg-[#0381FE] text-white shadow-sm font-semibold' : 'bg-white text-slate-700 hover:bg-slate-50 hover:text-slate-900 border border-slate-200'
                }`}
              >
                3. Parallel Hybrid
              </button>
              <span className="text-slate-300">→</span>

              <button
                onClick={() => openInspector('rrf')}
                title="Click to view Reciprocal Rank Fusion 1/(60+rank) mathematical calculation"
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all cursor-pointer hover:shadow-xs hover:scale-[1.02] active:scale-[0.98] ${
                  activeStage === 'fusion' ? 'bg-[#0381FE] text-white shadow-sm font-semibold' : 'bg-white text-slate-700 hover:bg-slate-50 hover:text-slate-900 border border-slate-200'
                }`}
              >
                4. RRF Rank Fusion
              </button>
              <span className="text-slate-300">→</span>

              <button
                onClick={() => openInspector('cross_encoder')}
                title="Click to view Cross-Encoder transformer attention logits & passage scoring"
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all cursor-pointer hover:shadow-xs hover:scale-[1.02] active:scale-[0.98] ${
                  activeStage === 'rerank' ? 'bg-[#0381FE] text-white shadow-sm font-semibold' : 'bg-white text-slate-700 hover:bg-slate-50 hover:text-slate-900 border border-slate-200'
                }`}
              >
                5. Cross-Encoder
              </button>
              <span className="text-slate-300">→</span>

              <button
                onClick={() => openInspector('sharpening')}
                title="Click to view Conversational Sharpening context blending & delta retention"
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all cursor-pointer hover:shadow-xs hover:scale-[1.02] active:scale-[0.98] ${
                  activeStage === 'sharpening' ? 'bg-amber-500 text-white shadow-sm font-semibold' : 'bg-white text-slate-700 hover:bg-slate-50 hover:text-slate-900 border border-slate-200'
                }`}
              >
                6. Sharpening
              </button>
              <span className="text-slate-300">→</span>

              <button
                onClick={() => openInspector('synthesis')}
                title="Click to view Synthesis Stream Groq LPU grounded prompt & token generation"
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all cursor-pointer hover:shadow-xs hover:scale-[1.02] active:scale-[0.98] ${
                  activeStage === 'synthesis' ? 'bg-emerald-600 text-white shadow-sm font-semibold' : 'bg-white text-slate-700 hover:bg-slate-50 hover:text-slate-900 border border-slate-200'
                }`}
              >
                7. Synthesis Stream
              </button>
            </div>

            {/* Speculative Pre-Warm Badge or Inspector Hint */}
            <div className="flex items-center gap-2 shrink-0">
              {speculativeCount > 0 ? (
                <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 text-[#0381FE] border border-blue-200 font-semibold text-xs animate-pulse">
                  <span className="w-2 h-2 rounded-full bg-[#0381FE]" />
                  Speculative Cache: {speculativeCount} pre-fetched
                </div>
              ) : (
                <button
                  onClick={() => openInspector('pipeline')}
                  className="hidden xl:flex items-center gap-1 px-2.5 py-1 rounded-full bg-blue-50/70 hover:bg-blue-100 text-[#0381FE] border border-blue-200/60 font-semibold text-[11px] transition-colors"
                >
                  <span>🔍 Click to Inspect</span>
                </button>
              )}
            </div>
          </div>

          {/* ── CHAT MESSAGES AREA ───────────────────────────────────────────── */}
          <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6 bg-[#F8FAFC]">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center max-w-xl mx-auto text-center space-y-5">
                <div className="w-16 h-16 rounded-3xl bg-blue-50 border border-blue-200/80 flex items-center justify-center text-[#0381FE] shadow-sm">
                  <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 tracking-tight">Samsung Live Streaming Assistant</h3>
                  <p className="text-sm text-slate-600 mt-2 leading-relaxed max-w-md mx-auto">
                    Full-duplex conversational RAG for Samsung products. Ask multi-part questions about Galaxy phones, laptops, watches, TVs, and smart appliances in one natural utterance.
                  </p>
                </div>

                {/* Benchmark quick-buttons */}
                <div className="w-full text-left space-y-2 pt-2">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block px-1">
                    Preset Evaluation Scenarios:
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    {scenarios.slice(0, 4).map(sc => (
                      <button
                        key={sc.id}
                        onClick={() => simulateVoiceStream(sc.prompt)}
                        className="p-3.5 rounded-2xl bg-white hover:bg-blue-50/40 border border-slate-200 hover:border-[#0381FE]/50 text-left transition-all shadow-sm group"
                      >
                        <div className="text-xs font-bold text-slate-900 group-hover:text-[#0381FE] flex items-center justify-between">
                          <span>{sc.title}</span>
                          <span className="text-[11px] text-[#0381FE] font-medium opacity-0 group-hover:opacity-100 transition-opacity">Simulate ➔</span>
                        </div>
                        <p className="text-xs text-slate-500 mt-1 line-clamp-2 leading-relaxed">{sc.prompt}</p>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              messages.map((m, idx) => (
                <div key={idx} className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
                  
                  {/* User Bubble */}
                  {m.role === 'user' ? (
                    <div className="max-w-2xl bg-gradient-to-r from-blue-600 to-[#0381FE] text-white px-5 py-3.5 rounded-2xl rounded-tr-sm shadow-sm text-sm leading-relaxed">
                      {m.content}
                    </div>
                  ) : (
                    /* Assistant Bubble */
                    <div className="max-w-3xl w-full bg-white border border-slate-200/90 rounded-2xl rounded-tl-sm p-6 shadow-sm space-y-4">
                      
                      {/* Pipeline Status Badges */}
                      <div className="flex flex-wrap items-center gap-2 text-xs">
                        {m.routingMode ? (
                          m.routingMode.needs_rag ? (
                            <span className="px-3 py-1 rounded-full bg-blue-50 text-[#0381FE] font-semibold border border-blue-200/80 flex items-center gap-1.5 shadow-2xs">
                              <span className="w-2 h-2 rounded-full bg-[#0381FE]" />
                              ⚡ Hybrid RAG ({m.sources?.length || 0} Grounded Docs) + General API
                            </span>
                          ) : (
                            <span className="px-3 py-1 rounded-full bg-purple-50 text-purple-700 font-semibold border border-purple-200/80 flex items-center gap-1.5 shadow-2xs">
                              <span className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" />
                              🌐 Direct General API (RAG Bypassed)
                            </span>
                          )
                        ) : (
                          m.sources && m.sources.length > 0 ? (
                            <span className="px-3 py-1 rounded-full bg-blue-50 text-[#0381FE] font-semibold border border-blue-200/80 flex items-center gap-1.5 shadow-2xs">
                              <span className="w-2 h-2 rounded-full bg-[#0381FE]" />
                              ⚡ Hybrid RAG ({m.sources.length} Grounded Docs) + General API
                            </span>
                          ) : (
                            <span className="px-3 py-1 rounded-full bg-purple-50 text-purple-700 font-semibold border border-purple-200/80 flex items-center gap-1.5 shadow-2xs">
                              <span className="w-2 h-2 rounded-full bg-purple-500" />
                              🌐 Direct General API (RAG Bypassed)
                            </span>
                          )
                        )}

                        {m.intent && (
                          <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 font-medium border border-slate-200">
                            Intent: <strong className="text-slate-900">{m.intent}</strong>
                          </span>
                        )}

                        {m.speculativeHit && (
                          <span className="px-2.5 py-1 rounded-full bg-blue-50 text-[#0381FE] font-medium border border-blue-200 flex items-center gap-1.5">
                            <span className="w-2 h-2 rounded-full bg-[#0381FE]" />
                            Speculative Pre-warmed Hit (-120ms)
                          </span>
                        )}

                        {m.isSharpened && (
                          <span className="px-2.5 py-1 rounded-full bg-amber-50 text-amber-800 font-medium border border-amber-200 flex items-center gap-1.5">
                            ✨ Context Sharpened ({m.sharpeningStats?.retained} retained + {m.sharpeningStats?.delta} delta)
                          </span>
                        )}
                      </div>

                      {/* Routing Rationale Note if present */}
                      {m.routingMode?.reason && (
                        <div className="text-[11px] text-slate-600 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl flex items-center gap-1.5">
                          <span className="font-semibold text-slate-800">Routing Decision:</span>
                          <span>{m.routingMode.reason}</span>
                        </div>
                      )}

                      {/* Decomposed Sub-Queries Pills */}
                      {m.subQueries && m.subQueries.length > 1 && (
                        <div className="bg-[#F8FAFC] rounded-xl p-3.5 border border-slate-200 space-y-2">
                          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
                            Decomposed Sub-Queries ({m.subQueries.length}):
                          </span>
                          <div className="flex flex-wrap gap-2">
                            {m.subQueries.map((sq, sIdx) => (
                              <span key={sIdx} className="px-3 py-1 rounded-lg bg-white border border-slate-200 text-[#0381FE] text-xs font-medium shadow-2xs">
                                Sub-Query {sIdx + 1}: {sq.query} {sq.hits !== undefined && `(${sq.hits} hits)`}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Formatted Markdown Content (No raw syntax view) */}
                      <div
                        className="samsung-markdown text-sm text-slate-800 leading-relaxed"
                        dangerouslySetInnerHTML={{ __html: marked.parse(m.content) }}
                      />

                      {/* Sources Cards */}
                      {m.sources && m.sources.length > 0 && (
                        <div className="pt-3 border-t border-slate-100">
                          <div className="text-xs font-semibold text-slate-500 mb-2 flex items-center justify-between">
                            <span>Grounded Product Citations ({m.sources.length}):</span>
                            <span className="text-slate-400 font-normal">Click to view verified source text</span>
                          </div>
                          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                            {m.sources.map((src, sIdx) => (
                              <button
                                key={sIdx}
                                onClick={() => setSelectedSource(src)}
                                className="p-3 rounded-xl bg-slate-50 hover:bg-blue-50/50 border border-slate-200 hover:border-[#0381FE]/40 text-left transition-all group"
                              >
                                <div className="text-xs font-semibold text-slate-900 group-hover:text-[#0381FE] truncate">
                                  {src.source}
                                </div>
                                <div className="text-[11px] text-slate-500 mt-1">
                                  Relevance Score: <strong className="text-emerald-600 font-semibold">{src.score.toFixed(3)}</strong>
                                </div>
                              </button>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Telemetry Footer */}
                      {m.telemetry && (
                        <div className="pt-3 flex flex-wrap items-center justify-between text-xs text-slate-500 border-t border-slate-100">
                          <div className="flex items-center gap-4">
                            <span>
                              TTFT: <strong className="text-emerald-600 font-semibold">{m.telemetry.ttft_ms} ms</strong>
                            </span>
                            <span>
                              Recall: <strong className="text-[#0381FE] font-semibold">{(m.telemetry.recall * 100).toFixed(0)}%</strong>
                            </span>
                            <span>
                              Faithfulness: <strong className="text-indigo-600 font-semibold">{(m.telemetry.groundedness * 100).toFixed(0)}%</strong>
                            </span>
                            <span>
                              Latency: <strong className="text-slate-700 font-semibold">{m.telemetry.latency_ms} ms</strong>
                            </span>
                          </div>
                          <div>
                            Cost: <strong className="text-slate-600 font-semibold">${m.telemetry.cost_usd.toFixed(6)}</strong>
                          </div>
                        </div>
                      )}

                    </div>
                  )}

                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* ── BOTTOM INPUT BAR (One UI Squircles & Decent White) ─────────────── */}
          <div className="p-4 bg-white border-t border-slate-200">
            <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex items-end gap-2.5">
              <div className="relative flex-1">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={e => handleInputChange(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSubmit(e)
                    }
                  }}
                  rows={2}
                  disabled={isStreaming}
                  placeholder={
                    isListening
                      ? 'Listening to speech in real time...'
                      : 'Ask a complex question about Samsung products or add follow-up details mid-flow...'
                  }
                  className="w-full bg-[#F8FAFC] border border-slate-200 focus:border-[#0381FE] focus:bg-white rounded-2xl px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0381FE]/20 resize-none font-sans transition-all"
                />

                {/* Voice Input Button */}
                <button
                  type="button"
                  onClick={toggleVoiceInput}
                  className={`absolute right-3.5 bottom-3.5 p-2 rounded-xl transition-colors ${
                    isListening
                      ? 'bg-rose-500 text-white animate-pulse'
                      : 'text-slate-400 hover:text-[#0381FE] hover:bg-slate-200/60'
                  }`}
                  title={isListening ? 'Stop recording' : 'Speak voice input'}
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </button>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={!input.trim() || isStreaming}
                className="px-5 py-3.5 rounded-2xl bg-[#0381FE] hover:bg-blue-600 text-white font-semibold text-sm disabled:opacity-50 disabled:cursor-not-allowed shadow-sm transition-all flex items-center justify-center flex-shrink-0"
              >
                {isStreaming ? (
                  <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                )}
              </button>
            </form>
          </div>

        </div>

        {/* ── RIGHT PANEL: SAMSUNG JURY BENCHMARKS & TELEMETRY HUD ────────────── */}
        <div className="w-80 lg:w-96 flex flex-col h-full bg-[#F8FAFC] border-l border-slate-200/80 p-5 space-y-5 overflow-y-auto">
          
          {/* Telemetry Scorecard */}
          <div className="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                Evaluation Telemetry HUD
              </h2>
              <span className="text-[10px] text-emerald-700 font-semibold bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                Live Active
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 text-center">
              <div className="bg-blue-50/70 p-3.5 rounded-2xl border border-blue-100">
                <span className="text-[11px] text-slate-500 block font-medium">AVG TTFT</span>
                <span className="text-xl font-bold text-[#0381FE]">
                  {sessionTelemetry.avgTtft} <span className="text-xs font-normal">ms</span>
                </span>
                <span className="text-[10px] text-slate-500 block mt-0.5">Target: &lt;150ms</span>
              </div>

              <div className="bg-emerald-50/70 p-3.5 rounded-2xl border border-emerald-100">
                <span className="text-[11px] text-slate-500 block font-medium">RECALL</span>
                <span className="text-xl font-bold text-emerald-600">
                  {(sessionTelemetry.avgRecall * 100).toFixed(0)}%
                </span>
                <span className="text-[10px] text-slate-500 block mt-0.5">Multi-query hits</span>
              </div>

              <div className="bg-indigo-50/70 p-3.5 rounded-2xl border border-indigo-100">
                <span className="text-[11px] text-slate-500 block font-medium">FAITHFULNESS</span>
                <span className="text-xl font-bold text-indigo-600">
                  {(sessionTelemetry.avgGroundedness * 100).toFixed(0)}%
                </span>
                <span className="text-[10px] text-slate-500 block mt-0.5">Citation Grounded</span>
              </div>

              <div className="bg-slate-50 p-3.5 rounded-2xl border border-slate-200">
                <span className="text-[11px] text-slate-500 block font-medium">TOTAL TURNS</span>
                <span className="text-xl font-bold text-slate-800">
                  {sessionTelemetry.totalTurns}
                </span>
                <span className="text-[10px] text-slate-500 block mt-0.5">Active Session</span>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-100 text-xs text-slate-500 flex justify-between">
              <span>Estimated Cost:</span>
              <span className="text-slate-800 font-semibold">${sessionTelemetry.totalCost.toFixed(6)}</span>
            </div>
          </div>

          {/* Preset Benchmark Scenarios (100% Samsung Products) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                Samsung Product Scenarios
              </h2>
              <span className="text-xs text-slate-400 font-normal">Click to run</span>
            </div>

            <div className="space-y-2.5">
              {scenarios.map(sc => (
                <div
                  key={sc.id}
                  onClick={() => simulateVoiceStream(sc.prompt)}
                  className="p-4 rounded-2xl bg-white hover:bg-blue-50/50 border border-slate-200 hover:border-[#0381FE]/50 cursor-pointer transition-all shadow-sm group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900 group-hover:text-[#0381FE]">
                      {sc.title}
                    </span>
                    <span className="text-[10px] font-semibold text-[#0381FE] px-2 py-0.5 rounded-full bg-blue-50 border border-blue-200">
                      Run ➔
                    </span>
                  </div>
                  <span className="text-[11px] text-[#0381FE] font-medium mt-1 block">
                    {sc.category}
                  </span>
                  <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
                    {sc.prompt}
                  </p>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>

      {/* ── MODAL: SOURCE DOCUMENT INSPECTOR ─────────────────────────────────── */}
      {selectedSource && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white border border-slate-200 rounded-3xl max-w-2xl w-full p-6 space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">{selectedSource.source}</h3>
                <span className="text-xs text-slate-500">Doc ID: {selectedSource.doc_id} • Score: {selectedSource.score.toFixed(4)}</span>
              </div>
              <button
                onClick={() => setSelectedSource(null)}
                className="p-1.5 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                ✕
              </button>
            </div>
            <div className="max-h-80 overflow-y-auto text-xs text-slate-700 leading-relaxed bg-[#F8FAFC] p-4 rounded-2xl border border-slate-200 whitespace-pre-wrap">
              {selectedSource.text}
            </div>
            <div className="flex justify-end">
              <button
                onClick={() => setSelectedSource(null)}
                className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-slate-700 transition-colors"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── MODAL: SAMSUNG KNOWLEDGE STORE ───────────────────────────────────── */}
      {showCorpusModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white border border-slate-200 rounded-3xl max-w-2xl w-full p-6 space-y-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900">Samsung Products Knowledge Store</h3>
                <span className="text-xs text-slate-500">Live indexed products available for full-duplex hybrid retrieval</span>
              </div>
              <button
                onClick={() => setShowCorpusModal(false)}
                className="p-1.5 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                ✕
              </button>
            </div>

            {/* Indexed Products List */}
            <div className="space-y-2">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Indexed Samsung Products ({corpusStats.documents}):
              </span>
              <div className="max-h-44 overflow-y-auto space-y-1.5 pr-1 text-xs">
                {(corpusStats.sources || []).map((src: string, i: number) => (
                  <div key={i} className="p-2.5 rounded-xl bg-[#F8FAFC] border border-slate-200 flex items-center justify-between text-slate-800">
                    <span className="font-medium truncate">{src}</span>
                    <span className="text-[#0381FE] text-[11px] font-semibold">Indexed ✓</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Ingestion Form */}
            <form onSubmit={handleUploadDocument} className="space-y-3 pt-3 border-t border-slate-100">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
                Ingest Additional Samsung Product Manual or Specs:
              </span>
              <input
                type="text"
                placeholder="Product Title (e.g., Samsung Galaxy Ring Specifications)"
                value={customTitle}
                onChange={e => setCustomTitle(e.target.value)}
                className="w-full bg-[#F8FAFC] border border-slate-200 rounded-xl px-3.5 py-2 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-[#0381FE]"
              />
              <textarea
                rows={3}
                placeholder="Paste product specifications, user guide, or feature description..."
                value={customContent}
                onChange={e => setCustomContent(e.target.value)}
                className="w-full bg-[#F8FAFC] border border-slate-200 rounded-xl px-3.5 py-2 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-[#0381FE]"
              />

              {uploadSuccess && (
                <div className="text-xs text-emerald-700 bg-emerald-50 p-2.5 rounded-xl border border-emerald-200 font-medium">
                  {uploadSuccess}
                </div>
              )}

              <div className="flex justify-between items-center pt-2">
                <button
                  type="button"
                  onClick={() => {
                    fetch(`${BACKEND_URL}/api/corpus/reset`, { method: 'POST' })
                      .then(res => res.json())
                      .then(data => setCorpusStats(data.stats))
                  }}
                  className="text-xs text-slate-500 hover:text-rose-600"
                >
                  Reset Default Products
                </button>
                <button
                  type="submit"
                  disabled={!customTitle || !customContent}
                  className="px-4 py-2 rounded-xl bg-[#0381FE] hover:bg-blue-600 text-white font-semibold text-xs disabled:opacity-50 transition-colors"
                >
                  Index Product Specs
                </button>
              </div>
            </form>

          </div>
        </div>
      )}

      {/* ── REAL-TIME BACKEND LOGIC PIPELINE INSPECTOR MODAL ───────────── */}
      <PipelineInspector
        isOpen={isInspectorOpen}
        onClose={() => setIsInspectorOpen(false)}
        initialStage={inspectorStage}
        backendUrl={BACKEND_URL}
        latestTelemetry={sessionTelemetry}
      />

    </>
  )
}
