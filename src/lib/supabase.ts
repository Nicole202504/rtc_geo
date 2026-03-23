import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export type Campaign = {
  id: string
  name: string
  slug: string
  description: string | null
  status: 'draft' | 'analyzing' | 'writing' | 'reviewing' | 'publishing' | 'completed' | 'paused'
  target_topic: string | null
  target_count: number
  language: string
  cms_category: string | null
  total_articles: number
  drafted_count: number
  approved_count: number
  rejected_count: number
  published_count: number
  created_by: string | null
  created_at: string
  updated_at: string
}

export type Article = {
  id: string
  campaign_id: string
  seq_no: number | null
  title: string | null
  content_md: string | null
  summary: string | null
  keywords: string[] | null
  cover_image_url: string | null
  status: 'pending' | 'generating' | 'draft' | 'reviewing' | 'approved' | 'rejected' | 'publishing' | 'published'
  reviewed_by: string | null
  reviewed_at: string | null
  review_comment: string | null
  cms_article_id: string | null
  cms_url: string | null
  published_at: string | null
  created_at: string
  updated_at: string
}
