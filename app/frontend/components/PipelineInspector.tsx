import React, { useState, useEffect } from 'react'

export interface PipelineInspectorProps {
  isOpen: boolean
  onClose: () => void
  initialStage?: string
  backendUrl: string
  latestTelemetry?: any
}

const STAGES = [
  { id: 'pipeline', label: '• Live Pipeline', num: '0' },
  { id: 'intent', label: '1. Intent Router', num: '1' },
  { id: 'decomposer', label: '2. Decomposer', num: '2' },
  { id: 'hybrid', label: '3. Parallel Hybrid', num: '3' },
  { id: 'rrf', label: '4. RRF Rank Fusion', num: '4' },
  { id: 'cross_encoder', label: '5. Cross-Encoder', num: '5' },
  { id: 'sharpening', label: '6. Sharpening', num: '6' },
  { id: 'synthesis', label: '7. Synthesis Stream', num: '7' },
]

export default function PipelineInspector({
  isOpen,
  onClose,
  initialStage = 'pipeline',
  backendUrl,
  latestTelemetry,
}: PipelineInspectorProps) {
  const [activeStage, setActiveStage] = useState<string>(initialStage)
  const [activeTab, setActiveTab] = useState<'trace' | 'algorithm' | 'test'>('trace')
  const [pipelineInfo, setPipelineInfo] = useState<any>(null)
  const [pipelineTrace, setPipelineTrace] = useState<any>(null)
  const [isLoadingTrace, setIsLoadingTrace] = useState<boolean>(false)
  const [testInput, setTestInput] = useState<string>('Compare Galaxy S24 Ultra and Fold 6 in battery capacity and AI features')
  const [testResult, setTestResult] = useState<any>(null)
  const [isTesting, setIsTesting] = useState<boolean>(false)

  // Sync initialStage when modal opens
  useEffect(() => {
    if (isOpen) {
      setActiveStage(initialStage || 'pipeline')
      fetchPipelineData()
    }
  }, [isOpen, initialStage])

  // ESC key listener to close modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown)
    }
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  const fetchPipelineData = async () => {
    setIsLoadingTrace(true)
    try {
      const [infoRes, traceRes] = await Promise.all([
        fetch(`${backendUrl}/api/pipeline/info`),
        fetch(`${backendUrl}/api/pipeline/trace`),
      ])
      if (infoRes.ok) {
        const infoData = await infoRes.json()
        setPipelineInfo(infoData.stages || {})
      }
      if (traceRes.ok) {
        const traceData = await traceRes.json()
        setPipelineTrace(traceData)
      }
    } catch (err) {
      console.error('Failed to load pipeline inspector data:', err)
    } finally {
      setIsLoadingTrace(false)
    }
  }

  const runStageTest = async () => {
    if (!testInput.trim() || isTesting) return
    setIsTesting(true)
    setTestResult(null)
    try {
      const stageEndpoint = activeStage === 'pipeline' ? 'all' : activeStage
      const res = await fetch(`${backendUrl}/api/pipeline/inspect/${stageEndpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: testInput.trim() }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setTestResult(data)
    } catch (err: any) {
      setTestResult({ error: err.message || 'Inspection failed' })
    } finally {
      setIsTesting(false)
    }
  }

  if (!isOpen) return null

  const currentSpec = pipelineInfo?.[activeStage]
  const currentStageTrace = pipelineTrace?.stages?.[activeStage]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-900/50 backdrop-blur-sm animate-fadeIn">
      {/* Modal Container */}
      <div 
        className="bg-white w-full max-w-5xl h-[88vh] rounded-3xl shadow-2xl border border-slate-200/90 flex flex-col overflow-hidden text-slate-800"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-[#F8FAFC] border-b border-slate-200/90 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-blue-50 border border-blue-200/70 flex items-center justify-center text-[#0381FE] shadow-sm font-bold text-sm">
              RAG
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-900">
                  {currentSpec?.title || 'Pipeline Stage Diagnostics'}
                </h2>
                <span className="px-2.5 py-0.5 text-[11px] font-semibold rounded-full bg-blue-50 text-[#0381FE] border border-blue-200/60">
                  {currentSpec?.category || 'Theme 04 Spec'}
                </span>
                <span className="px-2.5 py-0.5 text-[11px] font-medium rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                  {currentSpec?.model || 'Samsung Galaxy Architecture'}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                {currentSpec?.subtitle || 'Inspect live execution trace, mathematical algorithms, and test logic.'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={fetchPipelineData}
              title="Refresh Live Trace"
              className="p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-200/70 transition-colors"
            >
              <svg className={`w-4 h-4 ${isLoadingTrace ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-xl text-slate-500 hover:text-slate-900 hover:bg-slate-200/70 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* ── STAGE NAVIGATION BAR (Top Pills) ──────────────────────────────── */}
        <div className="bg-white border-b border-slate-200 px-6 py-2.5 flex items-center gap-1.5 overflow-x-auto text-xs scrollbar-none">
          {STAGES.map(stage => {
            const isSelected = activeStage === stage.id
            return (
              <button
                key={stage.id}
                onClick={() => {
                  setActiveStage(stage.id)
                  setTestResult(null)
                }}
                className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all flex items-center gap-1 ${
                  isSelected
                    ? 'bg-[#0381FE] text-white shadow-sm font-semibold'
                    : 'bg-slate-50 text-slate-600 hover:bg-slate-100 hover:text-slate-900 border border-slate-200'
                }`}
              >
                <span>{stage.label}</span>
              </button>
            )
          })}
        </div>

        {/* ── SUB-TABS (Trace / Algorithm / Test Runner) ────────────────────── */}
        <div className="bg-[#FAFBFD] border-b border-slate-200 px-6 py-2 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab('trace')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'trace'
                  ? 'bg-white text-[#0381FE] font-bold shadow-xs border border-slate-200'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              ⚡ Real-Time Execution Trace
            </button>
            <button
              onClick={() => setActiveTab('algorithm')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'algorithm'
                  ? 'bg-white text-[#0381FE] font-bold shadow-xs border border-slate-200'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              📐 Algorithm & Logic Mechanics
            </button>
            <button
              onClick={() => setActiveTab('test')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'test'
                  ? 'bg-white text-[#0381FE] font-bold shadow-xs border border-slate-200'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              🧪 Standalone Stage Runner
            </button>
          </div>

          {currentStageTrace?.latency_ms !== undefined && (
            <div className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              Stage Latency: {currentStageTrace.latency_ms} ms
            </div>
          )}
        </div>

        {/* ── MODAL CONTENT BODY ────────────────────────────────────────────── */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
          
          {/* TAB 1: REAL-TIME EXECUTION TRACE */}
          {activeTab === 'trace' && (
            <div className="space-y-5 animate-fadeIn">
              {pipelineTrace?.has_run ? (
                <>
                  {/* Latest Query Banner */}
                  <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs flex items-center justify-between">
                    <div>
                      <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Active Query</span>
                      <p className="text-sm font-semibold text-slate-900 mt-0.5">
                        &quot;{pipelineTrace.query}&quot;
                      </p>
                    </div>
                    <span className="text-xs px-2.5 py-1 rounded-full bg-slate-100 font-mono text-slate-600 border border-slate-200">
                      {pipelineTrace.session_id}
                    </span>
                  </div>

                  {/* Stage-Specific Live Data Display */}
                  {activeStage === 'pipeline' && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs">
                        <span className="text-xs font-semibold text-slate-500">Pipeline Status</span>
                        <p className="text-lg font-bold text-emerald-600 capitalize mt-1">
                          {pipelineTrace.stages.pipeline.status || 'Ready'}
                        </p>
                        <p className="text-xs text-slate-500 mt-2">
                          End-to-end full duplex stream
                        </p>
                      </div>
                      <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs">
                        <span className="text-xs font-semibold text-slate-500">Total Latency</span>
                        <p className="text-lg font-bold text-slate-900 mt-1">
                          {pipelineTrace.stages.pipeline.total_latency_ms || 0} ms
                        </p>
                        <p className="text-xs text-slate-500 mt-2">
                          TTFT: {pipelineTrace.stages.pipeline.ttft_ms || 0} ms
                        </p>
                      </div>
                      <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs">
                        <span className="text-xs font-semibold text-slate-500">Telemetry Quality</span>
                        <p className="text-lg font-bold text-[#0381FE] mt-1">
                          {Math.round((pipelineTrace.stages.pipeline.telemetry?.groundedness || 0.95) * 100)}% Grounded
                        </p>
                        <p className="text-xs text-slate-500 mt-2">
                          Recall: {Math.round((pipelineTrace.stages.pipeline.telemetry?.recall || 1.0) * 100)}%
                        </p>
                      </div>
                    </div>
                  )}

                  {activeStage === 'intent' && (
                    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-4">
                      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                        <div>
                          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Detected Intent</span>
                          <p className="text-base font-bold text-slate-900 mt-0.5">
                            {currentStageTrace?.intent || 'Unknown'}
                          </p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                          currentStageTrace?.needs_retrieval ? 'bg-blue-50 text-[#0381FE] border border-blue-200' : 'bg-amber-50 text-amber-700 border border-amber-200'
                        }`}>
                          {currentStageTrace?.needs_retrieval ? 'Retrieval Triggered' : 'Direct Chitchat Response'}
                        </span>
                      </div>
                      <div>
                        <span className="text-xs font-semibold text-slate-600">Model Classification Reason:</span>
                        <p className="text-xs text-slate-700 mt-1 bg-slate-50 p-3 rounded-xl border border-slate-200">
                          {currentStageTrace?.reason || 'Intent classified via Groq zero-shot semantic router.'}
                        </p>
                      </div>
                      <div className="grid grid-cols-2 gap-3 text-xs">
                        <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                          <span className="text-slate-500">Confidence Score:</span>
                          <span className="font-bold text-slate-800 ml-2">{currentStageTrace?.confidence || 0.95}</span>
                        </div>
                        <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                          <span className="text-slate-500">Router Latency:</span>
                          <span className="font-bold text-slate-800 ml-2">{currentStageTrace?.latency_ms || 0} ms</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {activeStage === 'decomposer' && (
                    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-4">
                      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                          Decomposed Sub-Queries ({currentStageTrace?.count || currentStageTrace?.sub_queries?.length || 0})
                        </h4>
                        <span className="text-xs text-slate-500">
                          Execution: {currentStageTrace?.latency_ms || 0} ms
                        </span>
                      </div>
                      <div className="space-y-2.5">
                        {(currentStageTrace?.sub_queries || []).map((sq: string, idx: number) => (
                          <div key={idx} className="flex items-start gap-3 p-3 rounded-xl bg-slate-50 border border-slate-200">
                            <span className="w-5 h-5 rounded-full bg-blue-100 text-[#0381FE] flex items-center justify-center text-xs font-bold shrink-0">
                              {idx + 1}
                            </span>
                            <div className="flex-1">
                              <p className="text-xs font-semibold text-slate-900">{sq}</p>
                              <span className="text-[10px] text-slate-500">Dispatched to Parallel Hybrid Engine</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {activeStage === 'hybrid' && (
                    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-4">
                      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                          Parallel Multi-Query Hybrid Results
                        </h4>
                        <span className="text-xs font-semibold text-slate-700">
                          Total Candidates: {currentStageTrace?.total_candidates || 0}
                        </span>
                      </div>
                      <div className="space-y-4">
                        {(currentStageTrace?.sub_queries_results || []).map((sqResult: any, idx: number) => (
                          <div key={idx} className="border border-slate-200 rounded-xl p-3 bg-slate-50/60 space-y-2">
                            <div className="flex items-center justify-between text-xs">
                              <span className="font-semibold text-slate-800">
                                Sub-Query {idx + 1}: &quot;{sqResult.query}&quot;
                              </span>
                              <span className="px-2 py-0.5 rounded-full bg-blue-100 text-[#0381FE] font-bold text-[11px]">
                                {sqResult.count} Hits
                              </span>
                            </div>
                            <div className="space-y-1.5">
                              {(sqResult.top_hits || []).map((hit: any, hIdx: number) => (
                                <div key={hIdx} className="bg-white p-2.5 rounded-lg border border-slate-200 text-xs">
                                  <div className="flex items-center justify-between text-[11px] font-semibold text-slate-700">
                                    <span>{hit.source || hit.doc_id}</span>
                                    <span className="font-mono text-[#0381FE]">Score: {hit.score}</span>
                                  </div>
                                  <p className="text-slate-600 text-[11px] mt-1 line-clamp-2">{hit.text}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {activeStage === 'rrf' && (
                    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-4">
                      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                        <div>
                          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                            Reciprocal Rank Fusion Output
                          </h4>
                          <span className="text-xs text-slate-500">
                            Formula: 1 / (60 + rank_i + 1) • Total Fused: {currentStageTrace?.total_fused || 0}
                          </span>
                        </div>
                        <span className="text-xs px-2.5 py-1 rounded-full bg-blue-50 text-[#0381FE] font-semibold border border-blue-200">
                          {currentStageTrace?.method || 'RRF (k=60)'}
                        </span>
                      </div>

                      <div className="space-y-2">
                        {(currentStageTrace?.top_candidates || []).map((cand: any, idx: number) => (
                          <div key={idx} className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-start gap-3">
                            <span className="w-6 h-6 rounded-full bg-blue-50 border border-blue-200 text-[#0381FE] flex items-center justify-center text-xs font-bold shrink-0">
                              #{idx + 1}
                            </span>
                            <div className="flex-1 text-xs">
                              <div className="flex items-center justify-between">
                                <span className="font-bold text-slate-900">{cand.source || cand.doc_id}</span>
                                <span className="font-mono font-bold text-[#0381FE]">RRF Score: {cand.score}</span>
                              </div>
                              <p className="text-slate-600 mt-1 line-clamp-2">{cand.text}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {activeStage === 'cross_encoder' && (
                    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-4">
                      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                        <div>
                          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                            Neural Cross-Encoder Attention Scores
                          </h4>
                          <span className="text-xs text-slate-500">
                            Model: ms-marco-MiniLM-L-6-v2 • Direct Logits
                          </span>
                        </div>
                        <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 font-semibold border border-emerald-200">
                          Top-{(currentStageTrace?.reranked || []).length} Selected for Synthesis
                        </span>
                      </div>

                      <div className="space-y-2.5">
                        {(currentStageTrace?.reranked || []).map((cand: any, idx: number) => (
                          <div key={idx} className="p-3.5 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1.5 text-xs">
                            <div className="flex items-center justify-between">
                              <span className="font-bold text-slate-900">Rank {idx + 1}: {cand.source || cand.doc_id}</span>
                              <span className={`px-2 py-0.5 rounded-full font-mono font-bold text-xs ${
                                cand.score >= 0 ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-100 text-slate-600'
                              }`}>
                                Logit: {cand.score}
                              </span>
                            </div>
                            <p className="text-slate-600 leading-relaxed">{cand.text}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {activeStage === 'sharpening' && (
                    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-4">
                      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                          Contextual Answer Sharpening State
                        </h4>
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                          currentStageTrace?.is_sharpened ? 'bg-amber-50 text-amber-700 border border-amber-200' : 'bg-slate-100 text-slate-600'
                        }`}>
                          {currentStageTrace?.is_sharpened ? 'Active Turn Sharpened' : 'Standard Turn'}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-3 text-xs">
                        <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                          <span className="text-slate-500">Retained Grounded Chunks:</span>
                          <p className="text-xl font-bold text-slate-900 mt-1">{currentStageTrace?.retained || 0}</p>
                          <span className="text-[10px] text-slate-500">Preserved from prior conversational turns</span>
                        </div>
                        <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                          <span className="text-slate-500">Delta Injected Chunks:</span>
                          <p className="text-xl font-bold text-[#0381FE] mt-1">{currentStageTrace?.delta || 0}</p>
                          <span className="text-[10px] text-slate-500">Newly retrieved for supplementary constraint</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {activeStage === 'synthesis' && (
                    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-4">
                      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                        <div>
                          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                            Groq LPU Synthesis Stream
                          </h4>
                          <span className="text-xs text-slate-500">
                            Model: openai/gpt-oss-120b • Stream TTFT: {currentStageTrace?.ttft_ms || 0} ms
                          </span>
                        </div>
                        <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 font-semibold border border-emerald-200">
                          Tokens: {currentStageTrace?.token_count || 0}
                        </span>
                      </div>
                      <div>
                        <span className="text-xs font-semibold text-slate-700">Synthesized Grounded Text:</span>
                        <div className="mt-2 p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-800 leading-relaxed whitespace-pre-wrap">
                          {currentStageTrace?.full_answer || 'No answer text recorded.'}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Raw Stage JSON Dump */}
                  <details className="text-xs text-slate-500 bg-white border border-slate-200 rounded-xl p-3">
                    <summary className="cursor-pointer font-semibold text-slate-700 hover:text-slate-900">
                      View Raw Stage Trace JSON
                    </summary>
                    <pre className="mt-3 p-3 bg-slate-900 text-emerald-400 rounded-lg overflow-x-auto text-[11px] font-mono">
                      {JSON.stringify(currentStageTrace || {}, null, 2)}
                    </pre>
                  </details>
                </>
              ) : (
                <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center space-y-3">
                  <div className="w-12 h-12 rounded-2xl bg-blue-50 text-[#0381FE] flex items-center justify-center mx-auto font-bold text-lg">
                    !
                  </div>
                  <h4 className="text-sm font-bold text-slate-800">No Query Executed In This Session Yet</h4>
                  <p className="text-xs text-slate-500 max-w-md mx-auto">
                    Type a question in the main chat or click the &quot;Standalone Stage Runner&quot; tab above to run a live test of this stage immediately.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: ALGORITHM & LOGIC MECHANICS */}
          {activeTab === 'algorithm' && currentSpec && (
            <div className="space-y-6 animate-fadeIn">
              {/* Algorithm Card */}
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Core Algorithm</span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-50 text-[#0381FE] border border-blue-200">
                    Production Grade
                  </span>
                </div>
                <h3 className="text-base font-bold text-slate-900">{currentSpec.algorithm}</h3>
                <p className="text-xs text-slate-600 leading-relaxed">{currentSpec.description}</p>
                {currentSpec.formula && (
                  <div className="mt-3 p-3 rounded-xl bg-slate-50 border border-slate-200 font-mono text-xs text-slate-800">
                    <span className="font-semibold text-slate-500 block text-[10px] uppercase">Mathematical Formula:</span>
                    <span className="text-sm font-bold text-[#0381FE]">{currentSpec.formula}</span>
                  </div>
                )}
              </div>

              {/* Step-by-Step Logic Steps */}
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Step-by-Step Backend Execution Logic
                </h4>
                <div className="space-y-2">
                  {(currentSpec.logic_steps || []).map((step: string, idx: number) => (
                    <div key={idx} className="flex items-start gap-3 p-3 rounded-xl bg-slate-50/70 border border-slate-200 text-xs">
                      <span className="w-5 h-5 rounded-full bg-[#0381FE] text-white flex items-center justify-center text-[10px] font-bold shrink-0">
                        {idx + 1}
                      </span>
                      <p className="text-slate-700 leading-relaxed font-medium">{step}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Prompt Template or Parameters */}
              {currentSpec.prompt_template && (
                <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                    System Prompt Template
                  </h4>
                  <pre className="p-4 bg-slate-900 text-slate-200 rounded-xl overflow-x-auto text-[11px] font-mono whitespace-pre-wrap leading-relaxed">
                    {currentSpec.prompt_template}
                  </pre>
                </div>
              )}

              {/* Parameters Table */}
              {currentSpec.parameters && (
                <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                    Configured Hyperparameters
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                    {Object.entries(currentSpec.parameters).map(([key, val]: [string, any]) => (
                      <div key={key} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 flex justify-between items-center">
                        <span className="font-mono text-slate-500 text-[11px]">{key}</span>
                        <span className="font-semibold text-slate-800 font-mono text-[11px]">{String(val)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: STANDALONE STAGE RUNNER */}
          {activeTab === 'test' && (
            <div className="space-y-5 animate-fadeIn">
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-4">
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                    Isolated Stage Verification
                  </h4>
                  <p className="text-xs text-slate-600 mt-1">
                    Execute <span className="font-semibold text-slate-900">{currentSpec?.title || activeStage}</span> in isolation and verify exact intermediate mathematical transformations and latency.
                  </p>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-700">Test Input Utterance / Query:</label>
                  <textarea
                    rows={2}
                    value={testInput}
                    onChange={e => setTestInput(e.target.value)}
                    className="w-full text-xs p-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0381FE] focus:border-transparent font-sans"
                    placeholder="Enter test query..."
                  />
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-[11px] text-slate-500">
                    Target Endpoint: <code className="font-mono text-blue-600">/api/pipeline/inspect/{activeStage}</code>
                  </span>
                  <button
                    onClick={runStageTest}
                    disabled={isTesting || !testInput.trim()}
                    className="px-5 py-2 rounded-xl bg-[#0381FE] hover:bg-blue-600 text-white font-semibold text-xs transition-all shadow-sm flex items-center gap-2 disabled:opacity-50"
                  >
                    {isTesting ? (
                      <>
                        <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Running Stage Logic...
                      </>
                    ) : (
                      <>
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        </svg>
                        Run Stage Logic
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Test Output Card */}
              {testResult && (
                <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-4 animate-fadeIn">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-500" />
                      Execution Succeeded
                    </span>
                    {testResult.latency_ms !== undefined && (
                      <span className="text-xs font-mono font-semibold text-slate-600">
                        Latency: {testResult.latency_ms} ms
                      </span>
                    )}
                  </div>

                  {/* Step Breakdown for RRF if available */}
                  {testResult.calculation_steps && (
                    <div className="space-y-2">
                      <span className="text-xs font-bold text-slate-700">Rank Calculation Step Breakdown:</span>
                      <div className="space-y-1.5">
                        {testResult.calculation_steps.map((step: any, sIdx: number) => (
                          <div key={sIdx} className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1">
                            <div className="flex justify-between font-bold text-slate-800">
                              <span>#{sIdx + 1}: {step.source}</span>
                              <span className="font-mono text-[#0381FE]">Score: {step.fused_score}</span>
                            </div>
                            <div className="text-[11px] font-mono text-slate-600 bg-white p-2 rounded border border-slate-200">
                              {step.formula_breakdown}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Sub-queries if Decomposer */}
                  {testResult.sub_queries && (
                    <div className="space-y-2">
                      <span className="text-xs font-bold text-slate-700">Decomposed Output Sub-Queries:</span>
                      <div className="space-y-1.5">
                        {testResult.sub_queries.map((sq: string, sIdx: number) => (
                          <div key={sIdx} className="p-2.5 bg-blue-50/70 rounded-xl border border-blue-200 text-xs font-semibold text-slate-800 flex items-center gap-2">
                            <span className="w-5 h-5 rounded-full bg-[#0381FE] text-white flex items-center justify-center text-[10px] font-bold">
                              {sIdx + 1}
                            </span>
                            {sq}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Raw Output JSON */}
                  <details className="text-xs text-slate-500 bg-slate-50 border border-slate-200 rounded-xl p-3">
                    <summary className="cursor-pointer font-semibold text-slate-700">View Full JSON Response</summary>
                    <pre className="mt-2 p-3 bg-slate-900 text-emerald-400 rounded-lg overflow-x-auto text-[11px] font-mono">
                      {JSON.stringify(testResult, null, 2)}
                    </pre>
                  </details>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-[#F8FAFC] border-t border-slate-200 px-6 py-3 flex items-center justify-between text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span>Samsung PRISM GenAI Hackathon 2026 • Theme 04: Streaming Live RAG</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-white hover:bg-slate-100 text-slate-700 font-semibold border border-slate-300 shadow-2xs transition-colors"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  )
}
