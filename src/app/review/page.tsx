'use client'
import { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { supabase, Campaign, Article } from '@/lib/supabase'
import { STATUS_LABELS, STATUS_COLORS, cn } from '@/lib/utils'
import ReactMarkdown from 'react-markdown'

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
            {/* 操作按钮 */}
            <div className="space-y-2">
              <button onClick={() => submitReview('approved')} disabled={saving}
                className="w-full bg-green-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50">
                ✅ 通过发布
              </button>
              <button onClick={() => submitReview('rejected')} disabled={saving || !comment}
                className="w-full bg-red-500 text-white py-2 rounded-lg text-sm font-medium hover:bg-red-600 disabled:opacity-50">
                ❌ 拒绝（需填意见）
              </button>
            </div>
            {saved && <p className="text-xs text-green-600 text-center">✓ 已保存</p>}
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
