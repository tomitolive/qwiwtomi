import { getDataClient } from "./supabase";

/** TMDB genre entry as stored by the Python bot */
export interface ContentGenre {
  id: number;
  name: string;
}

/** FAQ item — bot writes {q,a}; legacy HTML may use question/answer */
export interface ContentFaqItem {
  q?: string;
  a?: string;
  question?: string;
  answer?: string;
  q_en?: string;
  a_en?: string;
}

/** AI-generated blocks written by mega_bot / ai_engine */
export interface ContentAiData {
  intro?: string;
  desc_ar?: string;
  desc_en?: string;
  seo_title_ar?: string;
  meta_desc?: string;
  outro?: string;
  opinion?: string;
  opinion_ar?: string;
  opinion_en?: string;
  faq?: ContentFaqItem[];
  keywords?: string;
}

/**
 * Shape of content data from Supabase.
 */
export interface ContentData {
  id: string | number;
  title: string;
  title_ar?: string;
  title_en?: string;
  slug?: string;
  overview: string;
  poster_path?: string;
  backdrop_path?: string;
  release_date?: string;
  first_air_date?: string;
  vote_average?: number;
  vote_count?: number;
  genres?: ContentGenre[];
  ai_content?: ContentAiData;
  fixed?: boolean;
  name?: string;
  poster?: string;
  number_of_seasons?: number;
  seasons?: any[];
  status?: string;
  number_of_episodes?: number;
  section?: string;
  quality?: string;
  duration?: string;
  language?: string;
  country?: string;
  cast?: string;
  imdb_id?: string;
}

/** Entry in content index (homepage / sitemap) */
export interface ContentIndexEntry {
  title: string;
  title_ar?: string;
  title_en?: string;
  slug: string;
  folder: "movie" | "tv";
  poster?: string;
  rating?: number;
  year?: string;
  type?: string;
  tmdb_id: number;
  genre_ids?: number[];
  /** Arabic genre names — used for homepage section filters */
  genres?: string[];
  timestamp?: number;
  fixed?: boolean;
}

/**
 * Convert a Supabase content row to ContentData.
 */
function rowToContentData(row: any): ContentData {
  return {
    id: row.tmdb_id,
    title: row.title || "",
    title_ar: row.title_ar || "",
    title_en: row.title_en || "",
    slug: row.slug || "",
    overview: row.overview || "",
    poster_path: row.poster_path || "",
    backdrop_path: row.backdrop_path || "",
    release_date: row.release_date || "",
    first_air_date: row.first_air_date || "",
    vote_average: row.vote_average ?? undefined,
    vote_count: row.vote_count ?? undefined,
    genres: row.genres || [],
    ai_content: row.ai_content || {},
    fixed: row.fixed ?? false,
    name: row.name || "",
    poster: row.poster || "",
    number_of_seasons: row.number_of_seasons ?? undefined,
    seasons: row.seasons || [],
    status: row.status || "",
    number_of_episodes: row.number_of_episodes ?? undefined,
    section: row.section || "",
    quality: row.quality || "",
    duration: row.duration || "",
    language: row.language || "",
    country: row.country || "",
    cast: row.cast_members || row.cast || "",
    imdb_id: row.imdb_id || "",
  };
}

/**
 * Convert a Supabase content row to ContentIndexEntry.
 */
function rowToIndexEntry(row: any): ContentIndexEntry {
  let genreNames: string[] = [];
  let genreIds: number[] = [];

  if (row.genres && Array.isArray(row.genres)) {
    if (typeof row.genres[0] === "string") {
      genreNames = row.genres;
    } else {
      genreNames = row.genres.map((g: any) => g.name).filter(Boolean);
      genreIds = row.genres.map((g: any) => g.id).filter((id: any) => id != null);
    }
  }

  const year = row.year || (row.release_date || "").substring(0, 4) || undefined;

  return {
    title: row.title || (row.title_ar && row.title_en ? `${row.title_ar} / ${row.title_en}` : row.title_ar || ""),
    title_ar: row.title_ar || "",
    title_en: row.title_en || "",
    slug: row.slug || `${row.tmdb_id}`,
    folder: row.folder || "movie",
    poster: row.poster || "",
    rating: row.vote_average ?? undefined,
    year,
    type: row.type || row.folder || "movie",
    tmdb_id: Number(row.tmdb_id),
    genre_ids: genreIds.length > 0 ? genreIds : (row.genre_ids || []),
    genres: genreNames.length > 0 ? genreNames : undefined,
    timestamp: row.timestamp ?? undefined,
    fixed: row.fixed ?? false,
  };
}

/**
 * Returns up to `limit` similar items from Supabase.
 * Uses random items from the same type to ensure carousels are always populated.
 */
export async function getLocalSimilar(
  currentId: number | string,
  genreIds: number[],
  folder: "movie" | "tv",
  limit = 12
): Promise<ContentIndexEntry[]> {
  const sb = getDataClient();
  const { data, error } = await sb
    .from("content")
    .select("tmdb_id, slug, title, title_ar, title_en, folder, poster, vote_average, release_date, genres, genre_ids, timestamp, fixed")
    .eq("folder", folder)
    .neq("tmdb_id", Number(currentId))
    .limit(500);

  if (error || !data || data.length === 0) return [];

  const entries = data.map(rowToIndexEntry);

  const uniqueMap = new Map<number, ContentIndexEntry>();
  for (const item of entries) {
    if (!uniqueMap.has(item.tmdb_id)) {
      uniqueMap.set(item.tmdb_id, item);
    }
  }
  const unique = Array.from(uniqueMap.values());

  for (let i = unique.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [unique[i], unique[j]] = [unique[j], unique[i]];
  }

  return unique.slice(0, limit);
}

/**
 * Fetches content from Supabase.
 */
export async function getLocalContent(id: string): Promise<ContentData | null> {
  const sb = getDataClient();
  const { data, error } = await sb
    .from("content")
    .select("*")
    .eq("tmdb_id", Number(id))
    .single();

  if (error || !data) return null;
  return rowToContentData(data);
}

/**
 * Get all items filtered by type (movie/tv) from Supabase.
 */
export async function getContentByType(type: "movie" | "tv"): Promise<ContentIndexEntry[]> {
  const sb = getDataClient();
  const { data, error } = await sb
    .from("content")
    .select("tmdb_id, slug, title, title_ar, title_en, folder, poster, vote_average, release_date, genres, genre_ids, timestamp, fixed")
    .eq("folder", type)
    .order("timestamp", { ascending: false })
    .limit(3000);

  if (error || !data || data.length === 0) return [];
  return data.map(rowToIndexEntry);
}
