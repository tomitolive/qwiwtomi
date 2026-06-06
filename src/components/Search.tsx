"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

interface ContentIndexEntry {
  title: string;
  title_ar?: string;
  title_en?: string;
  slug: string;
  folder: "movie" | "tv";
  poster?: string;
  rating?: number;
  year?: string;
  tmdb_id: number;
  isLocal?: boolean;
}

export default function Search() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ContentIndexEntry[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [allContent, setAllContent] = useState<ContentIndexEntry[]>([]);
  const router = useRouter();
  const searchRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Load local content index on mount
    fetch("/api/content-index")
      .then(res => res.json())
      .then(data => setAllContent(data || []))
      .catch(err => console.error("Failed to load content index:", err));
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent | TouchEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("touchstart", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("touchstart", handleClickOutside);
    };
  }, []);

  const handleSearch = async (val: string) => {
    setQuery(val);
    if (val.length < 2) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    // Search against local content index
    const searchLower = val.toLowerCase();
    const localResults = allContent.filter(item => 
      item.title?.toLowerCase().includes(searchLower) ||
      item.title_ar?.toLowerCase().includes(searchLower) ||
      item.title_en?.toLowerCase().includes(searchLower)
    ).map(item => ({ ...item, isLocal: true }));

    // Also search TMDB API for content not in local database
    let tmdbResults: ContentIndexEntry[] = [];
    try {
      const res = await fetch(`https://api.themoviedb.org/3/search/multi?api_key=882e741f7283dc9ba1654d4692ec30f6&query=${encodeURIComponent(val)}&language=ar&page=1`);
      const data = await res.json();
      
      const localIds = new Set(allContent.map(item => item.tmdb_id));
      tmdbResults = (data.results || [])
        .filter((item: any) => 
          (item.media_type === 'movie' || item.media_type === 'tv') && 
          !localIds.has(item.id)
        )
        .slice(0, 8)
        .map((item: any) => ({
          tmdb_id: item.id,
          title: item.title || item.name,
          title_ar: item.title || item.name,
          title_en: item.title || item.name,
          folder: item.media_type === 'movie' ? 'movie' : 'tv',
          poster: item.poster_path,
          year: (item.release_date || item.first_air_date || '').substring(0, 4),
          rating: item.vote_average,
          slug: '', // Not used for TMDB results
          isLocal: false
        }));
    } catch (e) {
      console.error("TMDB search error", e);
    }

    // Combine results: local first, then TMDB
    const combined = [...localResults, ...tmdbResults].slice(0, 8);
    setResults(combined);
    setIsOpen(true);
  };

  const handleSelect = (item: ContentIndexEntry) => {
    console.log("Selected item:", item);
    console.log("isLocal:", item.isLocal);
    
    if (item.isLocal) {
      // Navigate to local page - use encoded path to prevent bot crawling
      const encodedPath = btoa(`/${item.folder}/${item.slug}`);
      console.log("Navigating to local (encoded):", encodedPath);
      router.push(`/${item.folder}/${item.slug}`);
    } else {
      // Navigate to watch domain - use encoded URL to prevent bot crawling
      const watchUrl = `https://tv.tomito.xyz/${item.folder}/${item.tmdb_id}/watch`;
      const encodedUrl = btoa(watchUrl);
      console.log("Navigating to watch (encoded):", encodedUrl);
      window.open(watchUrl, '_blank');
    }
    setIsOpen(false);
    setQuery("");
  };

  return (
    <div className="relative group w-full" ref={searchRef}>
      <input
        type="text"
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        placeholder="ابحث عن فيلم أو مسلسل..."
        className="w-full bg-input border-none rounded-lg py-2.5 px-10 text-sm focus:outline-none transition-all placeholder:text-gray-600"
        style={{ touchAction: 'manipulation' }}
      />
      <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
        <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>

      {isOpen && results.length > 0 && (
        <div className="absolute top-full mt-2 left-0 right-0 bg-card-bg rounded-xl overflow-hidden shadow-2xl z-[2000]">
          {results.map((item) => {
            // Encode navigation data to prevent bot crawling
            const navData = item.isLocal 
              ? JSON.stringify({ type: 'local', folder: item.folder, slug: item.slug })
              : JSON.stringify({ type: 'watch', folder: item.folder, id: item.tmdb_id });
            const encodedNav = btoa(navData);
            
            return (
              <button
                key={item.tmdb_id}
                onClick={() => handleSelect(item)}
                className="w-full flex items-center gap-3 p-3 hover:bg-primary/10 transition-colors"
                rel="nofollow"
                data-cy="search-result"
                data-nav={encodedNav}
                style={{ touchAction: 'manipulation' }}
              >
                <img
                  src={item.poster ? `https://image.tmdb.org/t/p/w500${item.poster}` : "/favicon.ico"}
                  alt={item.title_ar || item.title}
                  className="w-10 h-14 object-cover rounded shadow"
                  loading="lazy"
                />
                <div className="text-right">
                  <div className="text-sm font-bold text-white truncate max-w-[200px]">{item.title_ar || item.title}</div>
                  <div className="text-[10px] text-gray-500">
                    {item.folder === 'movie' ? 'فيلم' : 'مسلسل'} • {item.year}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
