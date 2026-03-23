'use client'
import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { supabase, Campaign, Article } from '@/lib/supabase'
import { STATUS_LABELS, STATUS_COLORS, cn } from '@/lib/utils'

export default function CampaignDetail() {
  const { id } = useParams<{ id: string }>()
  const [campaign, setCampaign] = useState<Campaign | null>(null)
  const [articles, setArticles] = useState<Article[]>([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (id) { loadData() }
  }, [id])

  async function loadData() {
    setLoading(true)
    const [{ data: camp }, { data: arts }] = await Promise.all([
      supabase.from('campaigns').select('*').eq('id', id).single(),
      supabase.from('articles').select('*').eq('campaign_id', id).order('seq_no', { ascending: true })
    ])
    setCampaign(camp)
    setArticles(arts || [])
    setLoading(false)
  }

  const filtered = filter === 'all' ? articles : articles.filter(a => a.status === filter)

  if (loading) return <div className="flex items-center justify-center h-64 text-gray-400">加载中...</div>
  if (!campaign) return <div className="flex items-center justify-center h-64 text-gray-400">Campaign 不存在</div>

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      {/* 头部 */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 text-sm text-gray-400 mb-2">
            <a href="/" className="hover:text-gray-600">Campaigns</a>
            <span>/</span>
            <span className="text-gray-700">{campaign.name}</span>
          </div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">{campaign.name}</h1>
            <span className={cn('text-xs px-2 py-1 rounded-full font-medium', STATUS_COLORS[campaign.status])}>
              {STATUS_LABELS[campaign.status]}
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-1">{campaign.target_topic} · {campaign.language}</p>
        </div>
        <a href={'/review?campaign=' + id}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">
          进入审核台 →
        </a>
      </div>

      {/* KPI 卡片 */}
      <div className="grid grid-cols-5 gap-4 mb-8">
        {[
          { label: '总文章', value: campaign.total_articles, color: 'text-gray-900' },
          { label: '待审核', value: campaign.drafted_count, color: 'text-yellow-600' },
          { label: '已通过', value: campaign.approved_count, color: 'text-green-600' },
          { label: '已拒绝', value: campaign.rejected_count, color: 'text-red-500' },
          { label: '已发布', value: campaign.published_count, color: 'text-blue-600' },
        ].map(kpi => (
          <div key={kpi.label} className="bg-white border border-gray-200 rounded-xl p-4 text-center">
            <div className={cn('text-3xl font-bold', kpi.color)}>{kpi.value}</div>
            <div className="text-xs text-gray-400 mt-1">{kpi.label}</div>
          </div>
        ))}
      </div>

      {/* 文章列表 */}
      <div className="bg-white border border-gray-200 rounded-xl">
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <h2 className="font-semibold text-gray-900">文章列表</h2>
          <div className="flex gap-1">
            {['all', 'pending', 'draft', 'reviewing', 'approved', 'published', 'rejected'].map(s => (
              <button key={s} onClick={() => setFilter(s)}
                className={cn('px-3 py-1 rounded-lg text-xs font-medium transition-colors',
                  filter === s ? 'bg-blue-600 text-white' : 'text-gray-500 hover:bg-gray-100')}>
                {s === 'all' ? '全部' : STATUS_LABELS[s]}
              </button>
            ))}
          </div>
        </div>
        {filtered.length === 0 ? (
          <div className="py-12 text-center text-gray-400 text-sm">
            {articles.length === 0 ? '暂无文章，等待 Skill 写作完成后通过 webhook 同步' : '该状态下没有文章'}
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {filtered.map(a => (
              <a key={a.id} href={'/review?campaign=' + id + '&article=' + a.id}
                className="flex items-center justify-between px-5 py-3.5 hover:bg-gray-50 transition-colors">
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-400 w-8">#{a.seq_no ?? '—'}</span>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{a.title || '未命名文章'}</p>
                    {a.review_comment && (
                      <p className="text-xs text-red-500 mt-0.5">修改意见：{a.review_comment}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className={cn('text-xs px-2 py-0.5 rounded-full font-medium', STATUS_COLORS[a.status])}>
                    {STATUS_LABELS[a.status]}
                  </span>
                  <span className="text-xs text-gray-400">
                    {a.updated_at ? new Date(a.updated_at).toLocaleDateString('zh-CN') : '—'}
                  </span>
                </div>
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
