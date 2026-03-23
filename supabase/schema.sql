-- campaigns 表
CREATE TABLE IF NOT EXISTS campaigns (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name            TEXT NOT NULL,
  slug            TEXT UNIQUE NOT NULL,
  description     TEXT,
  status          TEXT NOT NULL DEFAULT 'draft',
  target_topic    TEXT,
  target_count    INT DEFAULT 20,
  language        TEXT DEFAULT 'English',
  cms_category    TEXT,
  total_articles  INT DEFAULT 0,
  drafted_count   INT DEFAULT 0,
  approved_count  INT DEFAULT 0,
  rejected_count  INT DEFAULT 0,
  published_count INT DEFAULT 0,
  created_by      TEXT,
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now()
);

-- articles 表
CREATE TABLE IF NOT EXISTS articles (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id     UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  seq_no          INT,
  title           TEXT,
  content_md      TEXT,
  summary         TEXT,
  keywords        TEXT[],
  meta_description TEXT,
  cover_image_url TEXT,
  status          TEXT NOT NULL DEFAULT 'pending',
  reviewed_by     TEXT,
  reviewed_at     TIMESTAMPTZ,
  review_comment  TEXT,
  cms_article_id  TEXT,
  cms_url         TEXT,
  published_at    TIMESTAMPTZ,
  model_used      TEXT,
  token_count     INT,
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now()
);

-- audit_logs 表
CREATE TABLE IF NOT EXISTS audit_logs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id     UUID REFERENCES campaigns(id),
  article_id      UUID REFERENCES articles(id),
  action          TEXT NOT NULL,
  from_status     TEXT,
  to_status       TEXT,
  operator        TEXT,
  note            TEXT,
  metadata        JSONB,
  created_at      TIMESTAMPTZ DEFAULT now()
);

-- task_runs 表
CREATE TABLE IF NOT EXISTS task_runs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id     UUID NOT NULL REFERENCES campaigns(id),
  task_type       TEXT NOT NULL,
  status          TEXT DEFAULT 'queued',
  started_at      TIMESTAMPTZ,
  finished_at     TIMESTAMPTZ,
  progress        INT DEFAULT 0,
  error_message   TEXT,
  result_summary  JSONB,
  triggered_by    TEXT,
  created_at      TIMESTAMPTZ DEFAULT now()
);

-- updated_at 自动更新触发器
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER campaigns_updated_at BEFORE UPDATE ON campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER articles_updated_at  BEFORE UPDATE ON articles  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- RLS 先关掉（内部工具，后续按需开启）
ALTER TABLE campaigns  DISABLE ROW LEVEL SECURITY;
ALTER TABLE articles   DISABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;
ALTER TABLE task_runs  DISABLE ROW LEVEL SECURITY;
