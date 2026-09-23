import { NextResponse } from 'next/server'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function POST(req: Request) {
  const body = await req.text()
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
  
  const backendResponse = await fetch(`${backendUrl}/api/query/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body,
  })

  if (!backendResponse.ok) {
    return NextResponse.json(
      { error: 'Backend error', status: backendResponse.status },
      { status: backendResponse.status }
    )
  }

  // Stream the SSE response back to the client
  const stream = new ReadableStream({
    async start(controller) {
      const reader = backendResponse.body?.getReader()
      if (!reader) {
        controller.close()
        return
      }
      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          controller.enqueue(value)
        }
      } catch (err) {
        console.error('Stream proxy error:', err)
      } finally {
        controller.close()
      }
    }
  })

  // Build response headers from backend (minus hop-by-hop)
  const headers = new Headers()
  backendResponse.headers.forEach((value, key) => {
    if (!['content-encoding', 'transfer-encoding', 'connection'].includes(key)) {
      headers.set(key, value)
    }
  })
  headers.set('Content-Type', 'text/event-stream')
  headers.set('Cache-Control', 'no-cache')
  headers.set('Connection', 'keep-alive')
  headers.set('X-Accel-Buffering', 'no')

  return new Response(stream, {
    status: backendResponse.status,
    headers,
  })
}
