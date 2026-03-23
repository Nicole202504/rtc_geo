import { createClient } from '@supabase/supabase-js'
import { NextRequest, NextResponse } from 'next/server'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const { campaign_id, articles } = body

    if (!campaign_id || !articles?.length) {
      return NextResponse.json({ error: 'Missing campaign_id or articles' }, { status: 400 })
    }

    const inserted = []
    for (let i = 0; i < articles.length; i++) {
      const a = articles[i]
      const { data, error } = await supabase.from('articles').insert({
        campaign_id,
        seq_no: a.seq_no || (i + 1),
        title: a.title,
        content_md: a.content_md,
        summary: a.summary || null,
        keywords: a.keywords || null,
        cover_image_url: a.cover_image_url || null,
        status: 'reviewing',
      }).select().single()
      if (!error && data) inserted.push(data)
    }

    // 更新 campaign 统计
    const { data: allArts } = await supabase.from('articles').select('status').eq('campaign_id', campaign_id)
    if (allArts) {
      await supabase.from('campaigns').update({
        total_articles: allArts.length,
        drafted_count: allArts.filter(a => a.status === 'reviewing').length,
        status: 'reviewing',
      }).eq('id', campaign_id)
    }

    return NextResponse.json({ ok: true, inserted: inserted.length })
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 })
  }
}
