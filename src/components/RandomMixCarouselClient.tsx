'use client';

import { useEffect, useState, useRef, useCallback } from 'react';

interface CarouselItem {
  tmdb_id: number;
  title: string;
  title_ar?: string;
  poster?: string;
  rating?: number;
  year?: string;
  folder: 'movie' | 'tv';
  slug: string;
}

interface Props {
  items: CarouselItem[];
}

export default function RandomMixCarouselClient({ items }: Props) {
  const [shuffled, setShuffled] = useState<CarouselItem[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const arr = [...items];
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    setShuffled(arr);
  }, [items]);

  // Auto-scroll every 3 seconds — RTL (right to left)
  useEffect(() => {
    if (!shuffled.length) return;
    const interval = setInterval(() => {
      const el = scrollRef.current;
      if (!el) return;
      const cardWidth = 110 + 12; // w-[110px] + gap-3
      if (el.scrollLeft <= 5) {
        el.scrollTo({ left: el.scrollWidth - el.clientWidth, behavior: 'smooth' });
      } else {
        el.scrollBy({ left: -cardWidth * 2, behavior: 'smooth' });
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [shuffled]);

  const scrollLeft = useCallback(() => {
    scrollRef.current?.scrollBy({ left: -(110 + 12) * 2, behavior: 'smooth' });
  }, []);

  const scrollRight = useCallback(() => {
    scrollRef.current?.scrollBy({ left: (110 + 12) * 2, behavior: 'smooth' });
  }, []);

  if (!shuffled.length) return null;

  return (
    <div className="mt-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500">
            <polyline points="16 3 21 3 21 8"/>
            <line x1="4" y1="20" x2="21" y2="3"/>
            <polyline points="21 16 21 21 16 21"/>
            <line x1="15" y1="15" x2="21" y2="21"/>
          </svg>
          قد يعجبك أيضاً
        </h2>
        {/* Nav buttons */}
        <div className="flex gap-2">
          <button
            onClick={scrollLeft}
            className="w-8 h-8 flex items-center justify-center rounded-full bg-zinc-800 hover:bg-orange-500 border border-zinc-700 hover:border-orange-500 text-white transition-colors"
            aria-label="يسار"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
          </button>
          <button
            onClick={scrollRight}
            className="w-8 h-8 flex items-center justify-center rounded-full bg-zinc-800 hover:bg-orange-500 border border-zinc-700 hover:border-orange-500 text-white transition-colors"
            aria-label="يمين"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </button>
        </div>
      </div>

      <div ref={scrollRef} className="flex gap-3 overflow-x-auto pb-3 scrollbar-hide scroll-smooth">
        {shuffled.map((item, i) => (
          <a
            key={`mix-${item.tmdb_id}-${i}`}
            href={`/${item.folder}/${item.slug}`}
            className="flex-shrink-0 w-[110px] group"
          >
            <div className="bg-zinc-800 border border-zinc-700 overflow-hidden rounded group-hover:border-orange-500/50 transition-colors">
              <div className="relative">
                <img
                  src={item.poster?.replace('https://image.tmdb.org/t/p/w500', '/t/p/w500') || `/t/p/w500${item.poster}`}
                  alt={item.title_ar || item.title || "صورة ملصق"}
                  loading="lazy"
                  className="w-full aspect-[2/3] object-cover"
                />
                <span className={`absolute top-1 right-1 text-[9px] font-bold px-1.5 py-0.5 rounded ${item.folder === 'movie' ? 'bg-red-600' : 'bg-blue-600'} text-white`}>
                  {item.folder === 'movie' ? '🎬' : '📺'}
                </span>
              </div>
              <div className="p-1.5">
                <h3 className="text-white text-[10px] font-bold truncate">{item.title_ar || item.title}</h3>
                <p className="text-gray-500 text-[9px]">{item.year} ⭐ {item.rating?.toFixed(1)}</p>
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
