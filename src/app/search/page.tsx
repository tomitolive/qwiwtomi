import fs from "fs";
import path from "path";
import { ContentIndexEntry } from "@/lib/content";
import { Metadata } from "next";
import Link from "next/link";
import NewAd from "@/components/NewAd";

interface SearchPageProps {
  searchParams: Promise<{ q?: string }>;
}

interface TMDBSearchResult {
  id: number;
  media_type: "movie" | "tv";
  title?: string;
  name?: string;
  poster_path?: string;
  release_date?: string;
  first_air_date?: string;
  vote_average?: number;
}

export async function generateMetadata({ searchParams }: SearchPageProps): Promise<Metadata> {
  const { q } = await searchParams;
  const query = q || "";
  return {
    title: query ? `بحث: ${query} - توميتو` : "بحث - توميتو",
    description: query ? `نتائج البحث عن: ${query} على توميتو` : "ابحث عن أفلام ومسلسلات على توميتو",
  };
}

async function getLocalContent(): Promise<ContentIndexEntry[]> {
  try {
    const indexPath = path.join(process.cwd(), "data", "content_index.json");
    if (!fs.existsSync(indexPath)) return [];
    const data = fs.readFileSync(indexPath, "utf-8");
    return JSON.parse(data) as ContentIndexEntry[];
  } catch {
    return [];
  }
}

async function searchTMDB(query: string): Promise<TMDBSearchResult[]> {
  try {
    const res = await fetch(
      `https://api.themoviedb.org/3/search/multi?api_key=882e741f7283dc9ba1654d4692ec30f6&query=${encodeURIComponent(query)}&language=ar&page=1`,
      { next: { revalidate: 300 } }
    );
    const data = await res.json();
    return (data.results || []).filter(
      (item: TMDBSearchResult) => item.media_type === "movie" || item.media_type === "tv"
    );
  } catch {
    return [];
  }
}

export default async function SearchPage({ searchParams }: SearchPageProps) {
  const { q } = await searchParams;
  const query = q || "";
  
  if (!query) {
    return (
      <div className="min-h-screen bg-[#000] text-white pt-20 px-6">
        <div className="max-w-6xl mx-auto text-center py-20">
          <h1 className="text-4xl font-bold mb-4">بحث</h1>
          <p className="text-gray-400">أدخل كلمة البحث في شريط البحث أعلاه</p>
        </div>
      </div>
    );
  }

  const localContent = await getLocalContent();
  const tmdbResults = await searchTMDB(query);

  // Search in local content
  const searchLower = query.toLowerCase();
  const localResults = localContent.filter(
    (item) =>
      item.title?.toLowerCase().includes(searchLower) ||
      item.title_ar?.toLowerCase().includes(searchLower) ||
      item.title_en?.toLowerCase().includes(searchLower)
  );

  // Filter TMDB results to exclude local content
  const localIds = new Set(localContent.map((item) => item.tmdb_id));
  const tmdbFiltered = tmdbResults
    .filter((item) => !localIds.has(item.id))
    .slice(0, 20);

  const getPoster = (item: ContentIndexEntry | TMDBSearchResult) => {
    if ("poster" in item && item.poster) {
      return item.poster.startsWith("http")
        ? item.poster.replace("https://image.tmdb.org/t/p/w500", "/t/p/w500")
        : item.poster;
    }
    if ("poster_path" in item && item.poster_path) {
      return `https://image.tmdb.org/t/p/w500${item.poster_path}`;
    }
    return "/favicon.ico";
  };

  const getTitle = (item: ContentIndexEntry | TMDBSearchResult) => {
    if ("title_ar" in item && item.title_ar) return item.title_ar;
    if ("title" in item && item.title) return item.title;
    if ("name" in item && item.name) return item.name;
    return "بدون عنوان";
  };

  const getYear = (item: ContentIndexEntry | TMDBSearchResult) => {
    if ("year" in item && item.year) return item.year;
    if ("release_date" in item && item.release_date) return item.release_date.substring(0, 4);
    if ("first_air_date" in item && item.first_air_date) return item.first_air_date.substring(0, 4);
    return "";
  };

  const getFolder = (item: ContentIndexEntry | TMDBSearchResult) => {
    if ("folder" in item) return item.folder;
    if ("media_type" in item) return item.media_type === "movie" ? "movie" : "tv";
    return "movie";
  };

  const isLocal = (item: ContentIndexEntry | TMDBSearchResult): item is ContentIndexEntry => {
    return "slug" in item;
  };

  return (
    <div className="min-h-screen bg-[#000] text-white pt-20 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">نتائج البحث: "{query}"</h1>
          <p className="text-gray-400">
            {localResults.length + tmdbFiltered.length} نتيجة
          </p>
        </div>

        {/* Ad 1 - بعد العنوان */}
        <NewAd ad="ad1" />

        {localResults.length > 0 && (
          <div className="mb-12">
            <h2 className="text-xl font-bold mb-4 text-primary">المحتوى المحلي</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {localResults.map((item) => (
                <Link
                  key={item.tmdb_id}
                  href={`/${item.folder}/${item.slug}`}
                  className="block"
                >
                  <div className="tc-small-box">
                    <div className="tc-poster">
                      <img
                        src={getPoster(item)}
                        alt={getTitle(item) || "صورة ملصق"}
                        loading="lazy"
                        className="w-full h-auto"
                      />
                    </div>
                    <div className="p-2">
                      <h3 className="text-sm font-bold truncate">{getTitle(item)}</h3>
                      <p className="text-xs text-gray-400">
                        {item.folder === "movie" ? "فيلم" : "مسلسل"} • {getYear(item)}
                      </p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Ad 2 - بين القسمين */}
        <NewAd ad="ad2" />

        {tmdbFiltered.length > 0 && (
          <div className="mb-12">
            <h2 className="text-xl font-bold mb-4 text-primary">من TMDB</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {tmdbFiltered.map((item) => (
                <a
                  key={item.id}
                  href={`https://tv.tomito.xyz/${item.media_type}/${item.id}/watch`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block"
                >
                  <div className="tc-small-box">
                    <div className="tc-poster">
                      <img
                        src={getPoster(item)}
                        alt={getTitle(item) || "صورة ملصق"}
                        loading="lazy"
                        className="w-full h-auto"
                      />
                    </div>
                    <div className="p-2">
                      <h3 className="text-sm font-bold truncate">{getTitle(item)}</h3>
                      <p className="text-xs text-gray-400">
                        {item.media_type === "movie" ? "فيلم" : "مسلسل"} • {getYear(item)}
                      </p>
                    </div>
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}

        {localResults.length === 0 && tmdbFiltered.length === 0 && (
          <div className="text-center py-20">
            <p className="text-gray-400 text-xl">لم يتم العثور على نتائج</p>
          </div>
        )}

        {/* Ad 3 - في الأسفل */}
        <NewAd ad="ad3" />
      </div>
    </div>
  );
}
