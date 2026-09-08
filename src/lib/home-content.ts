import fs from "fs";
import path from "path";
import type { ContentData, ContentIndexEntry } from "./content";

const DATA_DIR = path.join(process.cwd(), "data");
const INDEX_PATH = path.join(DATA_DIR, "content_index.json");
const CONTENT_DIR = path.join(DATA_DIR, "content");

function posterFromPath(posterPath?: string): string {
  if (!posterPath) return "";
  if (posterPath.startsWith("/t/p/")) return posterPath;
  if (posterPath.startsWith("http")) {
    return posterPath.replace("https://image.tmdb.org/t/p/w500", "/t/p/w500");
  }
  return `/t/p/w500${posterPath.startsWith("/") ? posterPath : `/${posterPath}`}`;
}

function jsonToIndexEntry(data: ContentData, folder: "movie" | "tv"): ContentIndexEntry {
  const titleAr = data.title_ar || data.title;
  const titleEn = data.title_en || "";
  const genreNames = data.genres?.map((g) => g.name).filter(Boolean) as string[] | undefined;
  const genreIds = data.genres?.map((g) => g.id).filter((id) => id != null) as number[] | undefined;

  return {
    title: titleEn ? `${titleAr} / ${titleEn}` : titleAr,
    title_ar: titleAr,
    title_en: titleEn || undefined,
    slug: data.slug || `${data.id}`,
    folder,
    poster: posterFromPath(data.poster_path),
    rating: data.vote_average,
    year: (data.release_date || data.first_air_date || "").slice(0, 4) || undefined,
    type: folder === "tv" ? "tv" : "movie",
    tmdb_id: Number(data.id),
    genre_ids: genreIds,
    genres: genreNames,
    timestamp: Math.floor(Date.now() / 1000),
    fixed: data.fixed,
  };
}

/**
 * Homepage catalog: content_index.json merged with any data/content/*.json
 * not yet in the index (e.g. while rebuild is running).
 */
export const getHomeContent = (): ContentIndexEntry[] => {
  let index: ContentIndexEntry[] = [];
  try {
    if (fs.existsSync(INDEX_PATH)) {
      index = JSON.parse(fs.readFileSync(INDEX_PATH, "utf8")) as ContentIndexEntry[];
    }
  } catch (e) {
    console.error("Error reading content_index.json:", e);
  }

  const byId = new Map<string, ContentIndexEntry>();
  for (const item of index) {
    if (item.tmdb_id != null) byId.set(String(item.tmdb_id), item);
  }

  if (!fs.existsSync(CONTENT_DIR)) {
    return [...byId.values()].sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
  }

  for (const file of fs.readdirSync(CONTENT_DIR)) {
    if (!file.endsWith(".json")) continue;
    const id = file.replace(".json", "");
    if (byId.has(id)) continue;

    try {
      const raw = JSON.parse(
        fs.readFileSync(path.join(CONTENT_DIR, file), "utf8")
      ) as ContentData & { folder?: string; media_type?: string };

      const folder =
        raw.folder === "tv" || raw.media_type === "tv"
          ? "tv"
          : raw.folder === "movie" || raw.media_type === "movie"
            ? "movie"
            : "movie";

      const entry = jsonToIndexEntry(raw, folder);
      // Use a very old timestamp for files not in index
      // This prevents them from appearing at the top
      entry.timestamp = 0;
      byId.set(id, entry);
    } catch {
      // skip corrupt files
    }
  }

  return [...byId.values()].sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
};