'use client';

import { useState, useEffect } from 'react';
import { ContentIndexEntry } from '@/lib/content';

interface AdCarouselCardProps {
  item: ContentIndexEntry;
  index: number;
  pageSmartLink: string;
  prefix: string;
}

export default function AdCarouselCard({ item, index, pageSmartLink, prefix }: AdCarouselCardProps) {
  const [showAd, setShowAd] = useState(false);

  useEffect(() => {
    setShowAd(Math.random() < 0.7);
  }, []);

  const handleAdClick = (e: React.MouseEvent) => {
    e.preventDefault();
    window.open(pageSmartLink, '_blank');
    window.location.href = `/movie/${item.slug}`;
  };

  const handleDirectAdClick = (e: React.MouseEvent) => {
    e.preventDefault();
    window.open(pageSmartLink, '_blank');
  };

  return (
    <div className="flex-shrink-0 w-[120px]">
      <a 
        href={!showAd ? `/movie/${item.slug}` : '#'}
        onClick={showAd ? handleAdClick : undefined}
      >
        <div className="bg-zinc-800 border border-zinc-700 overflow-hidden">
          <img
            src={item.poster?.replace('https://image.tmdb.org/t/p/w500', '/t/p/w500') || `/t/p/w500${item.poster}`}
            alt={item.title_ar || item.title}
            loading="lazy"
            className="w-full aspect-[2/3] object-cover"
          />
          <div className="p-2">
            <h3 className="text-white text-[10px] font-bold truncate">{item.title_ar || item.title}</h3>
            <p className="text-gray-500 text-[9px]">{item.year} ⭐ {item.rating}</p>
          </div>
        </div>
      </a>
      {showAd && (
        <div className="flex gap-1 mt-1">
          <a
            href={pageSmartLink}
            target="_blank"
            rel="noopener noreferrer"
            onClick={handleDirectAdClick}
            className="flex-1 bg-orange-600 hover:bg-orange-700 text-white text-[9px] font-bold py-1 text-center transition-colors"
          >
            مشاهدة
          </a>
          <a
            href={pageSmartLink}
            target="_blank"
            rel="noopener noreferrer"
            onClick={handleDirectAdClick}
            className="flex-1 bg-green-600 hover:bg-green-700 text-white text-[9px] font-bold py-1 text-center transition-colors"
          >
            التحميل
          </a>
        </div>
      )}
    </div>
  );
}
