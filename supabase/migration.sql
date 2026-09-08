-- ============================================
-- Supabase Migration: Tomito Content Tables
-- ============================================
-- Execute this SQL in Supabase SQL Editor
-- https://supabase.com/dashboard/project/_/sql/new
-- ============================================

-- 1. جدول المحتوى الرئيسي (يجمع content_index + content detail)
CREATE TABLE IF NOT EXISTS content (
  tmdb_id BIGINT PRIMARY KEY,
  slug TEXT NOT NULL,
  title TEXT,
  title_ar TEXT,
  title_en TEXT,
  type TEXT NOT NULL DEFAULT 'movie',
  poster TEXT,
  poster_path TEXT,
  backdrop_path TEXT,
  release_date TEXT,
  first_air_date TEXT,
  vote_average NUMERIC,
  vote_count BIGINT,
  genres JSONB DEFAULT '[]'::jsonb,
  genre_ids JSONB DEFAULT '[]'::jsonb,
  ai_content JSONB DEFAULT '{}'::jsonb,
  overview TEXT,
  overview_en TEXT,
  section TEXT,
  quality TEXT,
  duration TEXT,
  language TEXT,
  country TEXT,
  cast_members TEXT,
  imdb_id TEXT,
  status TEXT,
  number_of_seasons BIGINT,
  seasons JSONB DEFAULT '[]'::jsonb,
  number_of_episodes BIGINT,
  timestamp BIGINT,
  fixed BOOLEAN DEFAULT false,
  name TEXT,
  folder TEXT NOT NULL DEFAULT 'movie',
  media_type TEXT
);

-- 2. جدول التصنيفات (genres/studios/collections)
CREATE TABLE IF NOT EXISTS genres (
  slug TEXT PRIMARY KEY,
  name TEXT,
  name_ar TEXT,
  description TEXT,
  items JSONB DEFAULT '[]'::jsonb
);

-- 3. جدول الـ Carousel (homepage hero)
CREATE TABLE IF NOT EXISTS carousel (
  id SERIAL PRIMARY KEY,
  tmdb_id BIGINT,
  title TEXT,
  title_en TEXT,
  overview TEXT,
  overview_en TEXT,
  poster_path TEXT,
  backdrop_path TEXT,
  release_date TEXT,
  vote_average NUMERIC,
  genre_ids JSONB DEFAULT '[]'::jsonb,
  genres JSONB DEFAULT '[]'::jsonb,
  youtube_key TEXT,
  youtube_url TEXT,
  local_video_path TEXT,
  age_rating TEXT,
  folder TEXT DEFAULT 'movie'
);

-- ============================================
-- الفهارس (Indexes) للسرعة
-- ============================================

-- فهرس للبحث حسب النوع (movie/tv)
CREATE INDEX IF NOT EXISTS idx_content_type ON content(type);

-- فهرس للبحث حسب المجلد
CREATE INDEX IF NOT EXISTS idx_content_folder ON content(folder);

-- فهرس للترتيب حسب التوقيت
CREATE INDEX IF NOT EXISTS idx_content_timestamp ON content(timestamp DESC);

-- فهرس للبحث بالـ slug
CREATE INDEX IF NOT EXISTS idx_content_slug ON content(slug);

-- فهرس للبحث في content_index (للصفحة الرئيسية)
CREATE INDEX IF NOT EXISTS idx_content_rating ON content(vote_average DESC NULLS LAST);

-- فهرس للـ genres
CREATE INDEX IF NOT EXISTS idx_genres_slug ON genres(slug);

-- فهرس للـ carousel
CREATE INDEX IF NOT EXISTS idx_carousel_tmdb_id ON carousel(tmdb_id);

-- ============================================
-- Full-Text Search للبحث
-- ============================================

-- إضافة حقل search_vector للبحث النصي
ALTER TABLE content ADD COLUMN IF NOT EXISTS search_vector tsvector;

-- إنشاء الفهرس
CREATE INDEX IF NOT EXISTS idx_content_search ON content USING gin(search_vector);

-- دالة تحديث search_vector
CREATE OR REPLACE FUNCTION update_content_search_vector()
RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('arabic', COALESCE(NEW.title_ar, '')), 'A') ||
    setweight(to_tsvector('simple', COALESCE(NEW.title_en, '')), 'A') ||
    setweight(to_tsvector('arabic', COALESCE(NEW.overview, '')), 'B') ||
    setweight(to_tsvector('simple', COALESCE(NEW.title, '')), 'B');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger لتحديث search_vector تلقائياً
DROP TRIGGER IF EXISTS update_content_search ON content;
CREATE TRIGGER update_content_search
  BEFORE INSERT OR UPDATE ON content
  FOR EACH ROW
  EXECUTE FUNCTION update_content_search_vector();

-- ============================================
-- RLS (Row Level Security) - للقراءة فقط
-- ============================================

ALTER TABLE content ENABLE ROW LEVEL SECURITY;
ALTER TABLE genres ENABLE ROW LEVEL SECURITY;
ALTER TABLE carousel ENABLE ROW LEVEL SECURITY;

-- سياسة القراءة للجميع (public)
CREATE POLICY "Allow public read access on content"
  ON content FOR SELECT
  USING (true);

CREATE POLICY "Allow public read access on genres"
  ON genres FOR SELECT
  USING (true);

CREATE POLICY "Allow public read access on carousel"
  ON carousel FOR SELECT
  USING (true);

-- سياسة الكتابة للـ service_role فقط (للبوت)
CREATE POLICY "Allow service role insert on content"
  ON content FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow service role update on content"
  ON content FOR UPDATE
  USING (true);

CREATE POLICY "Allow service role insert on genres"
  ON genres FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow service role update on genres"
  ON genres FOR UPDATE
  USING (true);

CREATE POLICY "Allow service role insert on carousel"
  ON carousel FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow service role update on carousel"
  ON carousel FOR UPDATE
  USING (true);
