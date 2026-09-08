import { getDataClient } from "./supabase";
import type { ContentIndexEntry } from "./content";

/**
 * Convert a Supabase row to ContentIndexEntry.
 */
function rowToIndexEntry(row: any): ContentIndexEntry {
  let genreNames: string[] | undefined;
  let genreIds: number[] | undefined;

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
    genre_ids: genreIds || row.genre_ids || [],
    genres: genreNames,
    timestamp: row.timestamp ?? undefined,
    fixed: row.fixed ?? false,
  };
}

/**
 * Homepage catalog: content from Supabase.
 * Sorted by timestamp descending.
 */
export const getHomeContent = async (): Promise<ContentIndexEntry[]> => {
  const sb = getDataClient();
  const { data, error } = await sb
    .from("content")
    .select("tmdb_id, slug, title, title_ar, title_en, folder, poster, vote_average, release_date, genres, genre_ids, timestamp, fixed")
    .order("timestamp", { ascending: false })
    .limit(3000);

  if (error || !data || data.length === 0) return [];
  return data.map(rowToIndexEntry);
};
