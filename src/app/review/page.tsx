'use client'
import { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { supabase, Campaign, Article } from '@/lib/supabase'
import { STATUS_LABELS, STATUS_COLORS, cn } from '@/lib/utils'
import ReactMarkdown from 'react-markdown'

const CMS_API = '/api/cms-proxy'

/** 将标题转成 URL slug */
function titleToSlug(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .slice(0, 80)
}

/** 将图片 URL 转成 base64 字符串（不含 data: 前缀） */
async function urlToBase64(url: string): Promise<string | null> {
  try {
    const res = await fetch(url)
    if (!res.ok) return null
    const blob = await res.blob()
    return await new Promise<string>((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => {
        const result = reader.result as string
        // 去掉 "data:image/png;base64," 前缀，只保留 base64 数据
        resolve(result.split(',')[1] || '')
      }
      reader.onerror = reject
      reader.readAsDataURL(blob)
    })
  } catch {
    return null
  }
}

function ReviewContent() {
  const searchParams = useSearchParams()
  const campaignId = searchParams.get('campaign')
  const initialArticleId = searchParams.get('article')

  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [articles, setArticles] = useState<Article[]>([])
  const [selectedCampaign, setSelectedCampaign] = useState<string>(campaignId || '')
  const [selected, setSelected] = useState<Article | null>(null)
  const [comment, setComment] = useState('')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  // CMS 上传状态
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<{ ok: boolean; msg: string } | null>(null)

  useEffect(() => { loadCampaigns() }, [])
  useEffect(() => { if (selectedCampaign) loadArticles(selectedCampaign) }, [selectedCampaign])
  useEffect(() => {
    if (initialArticleId && articles.length > 0) {
      const a = articles.find(x => x.id === initialArticleId)
      if (a) selectArticle(a)
    }
  }, [articles, initialArticleId])

  async function loadCampaigns() {
    const { data } = await supabase.from('campaigns').select('id, name, status').order('created_at', { ascending: false })
    setCampaigns((data as any[]) || [])
    if (!campaignId && data && data.length > 0) setSelectedCampaign(data[0].id)
  }

  async function loadArticles(cid: string) {
    const { data } = await supabase.from('articles').select('*').eq('campaign_id', cid).order('seq_no', { ascending: true })
    setArticles(data || [])
  }

  function selectArticle(a: Article) {
    setSelected(a)
    setComment(a.review_comment || '')
    setSaved(false)
    setUploadResult(null)
  }

  async function submitReview(action: 'approved' | 'rejected') {
    if (!selected) return
    setSaving(true)
    const update = {
      status: action,
      reviewed_at: new Date().toISOString(),
      review_comment: comment || null,
    }
    await supabase.from('articles').update(update).eq('id', selected.id)
    // 更新 campaign 统计
    const { data: arts } = await supabase.from('articles').select('status').eq('campaign_id', selectedCampaign)
    if (arts) {
      const counts = { approved_count: 0, rejected_count: 0, drafted_count: 0, published_count: 0, total_articles: arts.length }
      arts.forEach(a => {
        if (a.status === 'approved') counts.approved_count++
        else if (a.status === 'rejected') counts.rejected_count++
        else if (a.status === 'draft' || a.status === 'reviewing') counts.drafted_count++
        else if (a.status === 'published') counts.published_count++
      })
      await supabase.from('campaigns').update(counts).eq('id', selectedCampaign)
    }
    setSelected({ ...selected, ...update })
    setArticles(prev => prev.map(a => a.id === selected.id ? { ...a, ...update } : a))
    setSaving(false)
    setSaved(true)
  }

  async function uploadToCms() {
    if (!selected) return
    setUploading(true)
    setUploadResult(null)

    try {
      // 构建 poster（封面图 base64）
      let poster: string | undefined
      if (selected.cover_image_url) {
        const b64 = await urlToBase64(selected.cover_image_url)
        if (b64) poster = b64
      }

      const payload: Record<string, any> = {
        title: selected.title || '',
        route_name: titleToSlug(selected.title || 'article'),
        rich_content: selected.content_md || '',
        language: 'English',
      }
      if (poster) payload.poster = poster

      const res = await fetch(CMS_API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const json = await res.json().catch(() => ({}))

      if (res.ok && (json.code === 200 || json.code === 0 || json.id || json.data?.id)) {
        const cmsId = json.data?.id || json.id || String(json.code)
        // 更新 Supabase 记录
        const update = {
          status: 'published' as const,
          cms_article_id: String(cmsId),
        }
        await supabase.from('articles').update(update).eq('id', selected.id)
        setSelected({ ...selected, ...update })
        setArticles(prev => prev.map(a => a.id === selected.id ? { ...a, ...update } : a))
        setUploadResult({ ok: true, msg: `✅ 已发布！CMS ID: ${cmsId}` })
      } else {
        const errMsg = json.message || json.msg || JSON.stringify(json).slice(0, 100)
        setUploadResult({ ok: false, msg: `❌ 发布失败：${errMsg}` })
      }
    } catch (e: any) {
      setUploadResult({ ok: false, msg: `❌ 网络错误：${e.message}` })
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="flex h-[calc(100vh-53px)]">
      {/* 左侧：文章列表 */}
      <div className="w-72 border-r border-gray-200 bg-white flex flex-col">
        <div className="p-3 border-b border-gray-100">
          <select className="w-full text-sm border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none"
            value={selectedCampaign} onChange={e => { setSelectedCampaign(e.target.value); setSelected(null) }}>
            {campaigns.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <div className="flex-1 overflow-y-auto divide-y divide-gray-50">
          {articles.map(a => (
            <button key={a.id} onClick={() => selectArticle(a)}
              className={cn('w-full text-left px-3 py-3 hover:bg-gray-50 transition-colors',
                selected?.id === a.id && 'bg-blue-50 border-l-2 border-blue-500')}>
              <div className="flex items-start justify-between gap-2">
                <p className="text-xs font-medium text-gray-900 leading-snug line-clamp-2">{a.title || '未命名'}</p>
                <span className={cn('shrink-0 text-xs px-1.5 py-0.5 rounded-full', STATUS_COLORS[a.status])}>
                  {STATUS_LABELS[a.status]}
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-1">#{a.seq_no ?? '—'}</p>
            </button>
          ))}
          {articles.length === 0 && (
            <div className="py-8 text-center text-xs text-gray-400">暂无文章</div>
          )}
        </div>
      </div>

      {/* 中间：文章内容 */}
      <div className="flex-1 overflow-y-auto">
        {selected ? (
          <div className="max-w-3xl mx-auto px-8 py-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">{selected.title}</h1>
            {selected.cover_image_url && (
              <img src={selected.cover_image_url} alt="封面" className="w-full max-w-sm rounded-lg mb-6 border" />
            )}
            <div className="text-gray-800 text-sm leading-relaxed">
              <ReactMarkdown
                components={{
                  h1: ({children}) => <h1 className="text-2xl font-bold mt-6 mb-3 text-gray-900">{children}</h1>,
                  h2: ({children}) => <h2 className="text-xl font-bold mt-5 mb-2 text-gray-900">{children}</h2>,
                  h3: ({children}) => <h3 className="text-lg font-semibold mt-4 mb-2 text-gray-800">{children}</h3>,
                  h4: ({children}) => <h4 className="text-base font-semibold mt-3 mb-1 text-gray-800">{children}</h4>,
                  p: ({children}) => <p className="mb-3 leading-7">{children}</p>,
                  ul: ({children}) => <ul className="list-disc pl-5 mb-3 space-y-1">{children}</ul>,
                  ol: ({children}) => <ol className="list-decimal pl-5 mb-3 space-y-1">{children}</ol>,
                  li: ({children}) => <li className="leading-6">{children}</li>,
                  strong: ({children}) => <strong className="font-semibold text-gray-900">{children}</strong>,
                  em: ({children}) => <em className="italic">{children}</em>,
                  blockquote: ({children}) => <blockquote className="border-l-4 border-blue-300 pl-4 my-3 text-gray-600 italic">{children}</blockquote>,
                  code: ({children, className}) => className
                    ? <code className="block bg-gray-100 rounded-lg p-3 text-xs font-mono overflow-x-auto my-3 whitespace-pre">{children}</code>
                    : <code className="bg-gray-100 rounded px-1.5 py-0.5 text-xs font-mono text-red-600">{children}</code>,
                  pre: ({children}) => <pre className="bg-gray-100 rounded-lg p-3 overflow-x-auto my-3 text-xs">{children}</pre>,
                  table: ({children}) => <div className="overflow-x-auto my-4"><table className="min-w-full border-collapse text-sm">{children}</table></div>,
                  thead: ({children}) => <thead className="bg-gray-100">{children}</thead>,
                  th: ({children}) => <th className="border border-gray-300 px-3 py-2 text-left font-semibold text-gray-700 text-xs">{children}</th>,
                  td: ({children}) => <td className="border border-gray-300 px-3 py-2 text-gray-700 text-xs">{children}</td>,
                  hr: () => <hr className="my-5 border-gray-200" />,
                  a: ({children, href}) => <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{children}</a>,
                }}
              >{selected.content_md || '*暂无内容*'}</ReactMarkdown>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400 text-sm">
            ← 从左侧选择一篇文章
          </div>
        )}
      </div>

      {/* 右侧：审核操作 */}
      {selected && (
        <div className="w-72 border-l border-gray-200 bg-white flex flex-col">
          <div className="p-4 border-b border-gray-100">
            <h3 className="font-semibold text-gray-900 text-sm">审核操作</h3>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* 当前状态 */}
            <div>
              <p className="text-xs text-gray-400 mb-1">当前状态</p>
              <span className={cn('text-xs px-2 py-1 rounded-full font-medium', STATUS_COLORS[selected.status])}>
                {STATUS_LABELS[selected.status]}
              </span>
            </div>
            {/* 审核意见 */}
            <div>
              <p className="text-xs text-gray-400 mb-1">审核意见</p>
              <textarea rows={4} value={comment} onChange={e => setComment(e.target.value)}
                placeholder="填写修改意见（拒绝时必填）..."
                className="w-full text-xs border border-gray-200 rounded-lg p-2 resize-none focus:outline-none focus:ring-1 focus:ring-blue-500" />
            </div>
            {/* 审核按钮 */}
            <div className="space-y-2">
              <button onClick={() => submitReview('approved')} disabled={saving}
                className="w-full bg-green-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50">
                ✅ 通过审核
              </button>
              <button onClick={() => submitReview('rejected')} disabled={saving || !comment}
                className="w-full bg-red-500 text-white py-2 rounded-lg text-sm font-medium hover:bg-red-600 disabled:opacity-50">
                ❌ 拒绝（需填意见）
              </button>
            </div>
            {saved && <p className="text-xs text-green-600 text-center">✓ 已保存</p>}

            {/* 发布到 CMS */}
            <div className="pt-3 border-t border-gray-100">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">发布到 CMS</p>
              {selected.status !== 'approved' && selected.status !== 'published' && (
                <p className="text-xs text-amber-600 mb-2">⚠️ 请先通过审核再发布</p>
              )}
              <button
                onClick={uploadToCms}
                disabled={uploading || selected.status === 'published' || (selected.status !== 'approved')}
                className={cn(
                  'w-full py-2 rounded-lg text-sm font-medium transition-colors',
                  selected.status === 'published'
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : selected.status === 'approved'
                      ? 'bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50'
                      : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                )}
              >
                {uploading ? '⏳ 上传中...' : selected.status === 'published' ? '✓ 已发布到 CMS' : '🚀 上传到 CMS'}
              </button>
              {uploadResult && (
                <p className={cn('text-xs mt-2 text-center', uploadResult.ok ? 'text-green-600' : 'text-red-500')}>
                  {uploadResult.msg}
                </p>
              )}
            </div>

            {/* 文章信息 */}
            <div className="pt-3 border-t border-gray-100 space-y-2">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">文章信息</p>
              {[
                ['序号', '#' + (selected.seq_no ?? '—')],
                ['创建时间', selected.created_at ? new Date(selected.created_at).toLocaleDateString('zh-CN') : '—'],
                ['审核时间', selected.reviewed_at ? new Date(selected.reviewed_at).toLocaleDateString('zh-CN') : '—'],
                ['CMS ID', selected.cms_article_id || '未发布'],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between text-xs">
                  <span className="text-gray-400">{k}</span>
                  <span className="text-gray-700 font-medium">{v}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default function ReviewPage() {
  return <Suspense><ReviewContent /></Suspense>
}
