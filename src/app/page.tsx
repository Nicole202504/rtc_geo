'use client'
import { useEffect, useState } from 'react'
import { supabase, Campaign } from '@/lib/supabase'
import { STATUS_LABELS, STATUS_COLORS, cn } from '@/lib/utils'

export default function Home() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [loading, setLoading] = useState(true)
  const [showNew, setShowNew] = useState(false)
  const [form, setForm] = useState({ name: '', target_topic: '', language: 'English', target_count: 20, cms_category: '' })

  useEffect(() => {
    loadCampaigns()
  }, [])

  async function loadCampaigns() {
    setLoading(true)
    const { data } = await supabase.from('campaigns').select('*').order('created_at', { ascending: false })
    setCampaigns(data || [])
    setLoading(false)
  }

  async function createCampaign() {
    const slug = form.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
    const { error } = await supabase.from('campaigns').insert({
      name: form.name,
      slug: slug + '-' + Date.now(),
      target_topic: form.target_topic,
      language: form.language,
      target_count: form.target_count,
      cms_category: form.cms_category || null,
      status: 'draft',
    })
    if (!error) { setShowNew(false); loadCampaigns() }
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
          <p className="text-gray-500 text-sm mt-1">管理所有内容生产批次</p>
        </div>
        <button onClick={() => setShowNew(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">
          + 新建 Campaign
        </button>
      </div>

      {/* 新建表单 */}
      {showNew && (
        <div className="bg-white border border-gray-200 rounded-xl p-6 mb-6 shadow-sm">
          <h3 className="font-semibold text-gray-900 mb-4">新建 Campaign</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Campaign 名称 *</label>
              <input className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Chat SDK 2026 Q1" value={form.name} onChange={e => setForm({...form, name: e.target.value})} />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">主题方向</label>
              <input className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Best Chat SDKs" value={form.target_topic} onChange={e => setForm({...form, target_topic: e.target.value})} />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">语言</label>
              <select className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={form.language} onChange={e => setForm({...form, language: e.target.value})}>
                <option value="English">English</option>
                <option value="Chinese">Chinese</option>
                <option value="Japanese">Japanese</option>
                <option value="Korean">Korean</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">计划篇数</label>
              <input type="number" className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={form.target_count} onChange={e => setForm({...form, target_count: parseInt(e.target.value)})} />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">CMS 分类</label>
              <input className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Tutorial" value={form.cms_category} onChange={e => setForm({...form, cms_category: e.target.value})} />
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button onClick={createCampaign} disabled={!form.name}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
              创建
            </button>
            <button onClick={() => setShowNew(false)}
              className="border border-gray-200 text-gray-600 px-4 py-2 rounded-lg text-sm hover:bg-gray-50">
              取消
            </button>
          </div>
        </div>
      )}

      {/* Campaign 列表 */}
      {loading ? (
        <div className="text-center py-16 text-gray-400">加载中...</div>
      ) : campaigns.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
          <p className="text-gray-400 mb-3">还没有 Campaign</p>
          <button onClick={() => setShowNew(true)} className="text-blue-600 text-sm hover:underline">新建第一个 →</button>
        </div>
      ) : (
        <div className="grid gap-4">
          {campaigns.map(c => (
            <a key={c.id} href={'/campaigns/' + c.id}
              className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow block">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="font-semibold text-gray-900">{c.name}</h3>
                    <span className={cn('text-xs px-2 py-0.5 rounded-full font-medium', STATUS_COLORS[c.status])}>
                      {STATUS_LABELS[c.status]}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500">{c.target_topic || '—'} · {c.language} · 目标 {c.target_count} 篇</p>
                </div>
                <div className="flex items-center gap-6 text-sm text-right">
                  <div>
                    <div className="font-semibold text-gray-900">{c.total_articles}</div>
                    <div className="text-xs text-gray-400">总文章</div>
                  </div>
                  <div>
                    <div className="font-semibold text-yellow-600">{c.drafted_count}</div>
                    <div className="text-xs text-gray-400">待审核</div>
                  </div>
                  <div>
                    <div className="font-semibold text-green-600">{c.approved_count}</div>
                    <div className="text-xs text-gray-400">已通过</div>
                  </div>
                  <div>
                    <div className="font-semibold text-blue-600">{c.published_count}</div>
                    <div className="text-xs text-gray-400">已发布</div>
                  </div>
                </div>
              </div>
              {c.target_count > 0 && (
                <div className="mt-3">
                  <div className="w-full bg-gray-100 rounded-full h-1.5">
                    <div className="bg-blue-500 h-1.5 rounded-full transition-all"
                      style={{ width: Math.min(100, (c.published_count / c.target_count) * 100) + '%' }} />
                  </div>
                  <p className="text-xs text-gray-400 mt-1">{c.published_count}/{c.target_count} 已发布</p>
                </div>
              )}
            </a>
          ))}
        </div>
      )}
    </div>
  )
}
