import { NextResponse } from 'next/server'

export function POST(req: Request) {
  return NextResponse.json({ hello: 'world' })
}

export default async function handler(req: any, res: any) {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
    const response = await fetch(`${backendUrl}/health`)
    const data = await response.json()
    res.status(response.status).json(data)
  } catch {
    res.status(502).json({ error: 'Backend unreachable' })
  }
}
