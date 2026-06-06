import fs from "fs";
import path from "path";

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
 * Shape of `data/content/{tmdb_id}.json` produced by mega_bot.create_page().
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

/** Entry in `data/content_index.json` (homepage / sitemap) */
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

const CONTENT_DIR = path.join(process.cwd(), "data", "content");
const INDEX_FILE = path.join(process.cwd(), "data", "content_index.json");

/**
 * Returns up to `limit` similar items from our local database,
 * matched by folder (movie/tv), excluding the current item.
 * Uses random items from the same type to ensure carousels are always populated.
 */
export function getLocalSimilar(
  currentId: number | string,
  genreIds: number[],
  folder: "movie" | "tv",
  limit = 12
): ContentIndexEntry[] {
  try {
    if (!fs.existsSync(INDEX_FILE)) return [];
    const raw = fs.readFileSync(INDEX_FILE, "utf-8");
    const all: ContentIndexEntry[] = JSON.parse(raw);

    // Filter by folder and exclude current item (no genre filtering to ensure enough items)
    const filtered = all.filter(
      (item) =>
        item.folder === folder &&
        String(item.tmdb_id) !== String(currentId)
    );

    // Remove duplicates by tmdb_id
    const uniqueMap = new Map<number, ContentIndexEntry>();
    for (const item of filtered) {
      if (!uniqueMap.has(item.tmdb_id)) {
        uniqueMap.set(item.tmdb_id, item);
      }
    }
    const unique = Array.from(uniqueMap.values());

    // Shuffle for freshness
    for (let i = unique.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [unique[i], unique[j]] = [unique[j], unique[i]];
    }

    return unique.slice(0, limit);
  } catch {
    return [];
  }
}

/**
 * Fetches content from local JSON store.
 * This is where the Python bot writes its results.
 */
export async function getLocalContent(id: string): Promise<ContentData | null> {
  const filePath = path.join(CONTENT_DIR, `${id}.json`);

  if (!fs.existsSync(filePath)) {
    return null;
  }

  try {
    const data = fs.readFileSync(filePath, "utf-8");
    return JSON.parse(data) as ContentData;
  } catch (error) {
    console.error(`Error reading local content for ${id}:`, error);
    return null;
  }
}

/**
 * Save content to local store.
 * Can be used by API routes if we want to bridge Python and Next.js.
 */
export async function saveLocalContent(id: string, data: ContentData) {
  if (!fs.existsSync(CONTENT_DIR)) {
    fs.mkdirSync(CONTENT_DIR, { recursive: true });
  }

  const filePath = path.join(CONTENT_DIR, `${id}.json`);
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}

/**
 * Get all items from content_index.json filtered by type (movie/tv)
 */
export function getContentByType(type: "movie" | "tv"): ContentIndexEntry[] {
  try {
    if (!fs.existsSync(INDEX_FILE)) return [];
    const raw = fs.readFileSync(INDEX_FILE, "utf-8");
    const all: ContentIndexEntry[] = JSON.parse(raw);

    return all.filter((item) => item.folder === type);
  } catch {
    return [];
  }
}
