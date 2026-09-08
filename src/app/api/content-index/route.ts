import { NextResponse } from "next/server";
import { ContentIndexEntry } from "@/lib/content";
import { getDataClient } from "@/lib/supabase";

export async function GET() {
  const sb = getDataClient();
  const { data, error } = await sb
    .from("content")
    .select("tmdb_id, slug, title, title_ar, title_en, folder, poster, vote_average, release_date, genres, genre_ids, timestamp, fixed")
    .order("timestamp", { ascending: false })
    .limit(3000);

  if (error || !data || data.length === 0) {
    return NextResponse.json([], { status: 200 });
  }

  const entries: ContentIndexEntry[] = data.map((row: any) => ({
    title: row.title || "",
    title_ar: row.title_ar || "",
    title_en: row.title_en || "",
    slug: row.slug || `${row.tmdb_id}`,
    folder: row.folder || "movie",
    poster: row.poster || "",
    rating: row.vote_average ?? undefined,
    year: (row.release_date || "").substring(0, 4) || undefined,
    type: row.type || row.folder || "movie",
    tmdb_id: Number(row.tmdb_id),
    genre_ids: row.genre_ids || [],
    genres: row.genres?.map((g: any) => typeof g === "string" ? g : g.name).filter(Boolean),
    timestamp: row.timestamp ?? undefined,
    fixed: row.fixed ?? false,
  }));

  return NextResponse.json(entries, { status: 200 });
}
