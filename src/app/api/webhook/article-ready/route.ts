import { createClient } from '@supabase/supabase-js'
import { NextRequest, NextResponse } from 'next/server'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

/**
 * 将 base64 封面图上传到 Supabase Storage
 * 返回公开访问 URL，失败则返回 null
 */
async function uploadCoverImage(
  b64: string,
  filename: string
): Promise<string | null> {
  try {
    // 解析 data URI：data:image/png;base64,<data>
    const match = b64.match(/^data:(image\/\w+);base64,(.+)$/)
    if (!match) return null

    const mime = match[1]                      // e.g. "image/png"
    const ext  = mime.split('/')[1] || 'png'   // e.g. "png"
    const buf  = Buffer.from(match[2], 'base64')

    const storagePath = `covers/${filename}.${ext}`

    const { error: upErr } = await supabase.storage
      .from('article-covers')
      .upload(storagePath, buf, {
        contentType: mime,
        upsert: true,          // 同名文件直接覆盖
      })

    if (upErr) {
      console.error('[upload-cover] storage error:', upErr.message)
      return null
    }

    // 获取公开 URL（bucket 需要设为 public，或使用 createSignedUrl）
    const { data: urlData } = supabase.storage
      .from('article-covers')
      .getPublicUrl(storagePath)

    return urlData?.publicUrl ?? null
  } catch (err: any) {
    console.error('[upload-cover] unexpected error:', err.message)
    return null
  }
}

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

      // ── 处理封面图 ──────────────────────────────────────
      let coverUrl: string | null = a.cover_image_url || null

      if (!coverUrl && a.cover_image_b64) {
        // 用 article_id 或序号作为文件名，避免冲突
        const fname = a.article_id
          ? `${campaign_id}-${a.article_id}`
          : `${campaign_id}-${String(i + 1).padStart(3, '0')}`
        coverUrl = await uploadCoverImage(a.cover_image_b64, fname)
      }
      // ─────────────────────────────────────────────────────

      const { data, error } = await supabase.from('articles').insert({
        campaign_id,
        seq_no:          a.seq_no || (i + 1),
        title:           a.title,
        content_md:      a.content_md,
        summary:         a.summary   || null,
        keywords:        a.keywords  || null,
        cover_image_url: coverUrl,
        status:          'reviewing',
      }).select().single()

      if (!error && data) inserted.push(data)
      else if (error) console.error(`[insert article ${i}]`, error.message)
    }

    // 更新 campaign 统计
    const { data: allArts } = await supabase
      .from('articles')
      .select('status')
      .eq('campaign_id', campaign_id)

    if (allArts) {
      await supabase.from('campaigns').update({
        total_articles: allArts.length,
        drafted_count:  allArts.filter(a => a.status === 'reviewing').length,
        status:         'reviewing',
      }).eq('id', campaign_id)
    }

    return NextResponse.json({ ok: true, inserted: inserted.length })
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 })
  }
}
