import { NextRequest, NextResponse } from 'next/server'

const CMS_API = 'http://9.135.146.68:8080/api/import/article'

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()

    const res = await fetch(CMS_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })

    const text = await res.text()
    let json: any = {}
    try { json = JSON.parse(text) } catch { json = { raw: text } }

    return NextResponse.json(json, { status: res.status })
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 })
  }
}
