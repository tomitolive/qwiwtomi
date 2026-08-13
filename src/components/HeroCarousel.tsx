'use client';

import { useState, useEffect, useRef } from 'react';
import CarouselCardRow from './CarouselCardRow';

interface CarouselItem {
  tmdb_id: number;
  title: string;
  title_en: string;
  overview: string;
  overview_en: string;
  poster_path: string;
  backdrop_path: string;
  release_date: string;
  vote_average: number;
  genre_ids: number[];
  genres: string[];
  youtube_key: string;
  youtube_url: string;
  local_video_path: string;
  age_rating: string;
  folder: 'movie' | 'tv';
}

interface HeroCarouselProps {
  items: CarouselItem[];
  locale: string;
  onSlideChange?: (index: number) => void;
}

export default function HeroCarousel({ items, locale, onSlideChange }: HeroCarouselProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [isMuted, setIsMuted] = useState(true);
  const videoRef = useRef<HTMLVideoElement>(null);

  const activeItem = items[activeIndex];

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleSlideChange = (index: number) => {
    if (index !== activeIndex) {
      setIsTransitioning(true);
      setTimeout(() => {
        setActiveIndex(index);
        setIsTransitioning(false);
      }, 300);
    }
  };

  useEffect(() => {
    if (onSlideChange) {
      onSlideChange(activeIndex);
    }
  }, [activeIndex, onSlideChange]);

  if (!activeItem) return null;

  const title = activeItem.title_en || activeItem.title;
  const titleAr = activeItem.title;
  const overview = locale === 'ar' ? activeItem.overview : activeItem.overview_en;
  const year = activeItem.release_date?.split('-')[0] || '';
  const rating = activeItem.vote_average?.toFixed(1) || '0.0';
  const backdropUrl = activeItem.backdrop_path 
    ? `https://image.tmdb.org/t/p/original${activeItem.backdrop_path}`
    : '';
  const posterUrl = activeItem.poster_path
    ? `https://image.tmdb.org/t/p/w500${activeItem.poster_path}`
    : '';
  
  // Use local video if available, otherwise use YouTube
  const localVideoPath = activeItem.local_video_path;
  let youtubeKey = "";
  let youtubeUrl = "";
  
  if (!localVideoPath) {
    // Use youtube_url if provided, otherwise use youtube_key
    youtubeKey = activeItem.youtube_key;
    if (!youtubeKey && activeItem.youtube_url) {
      // Extract key from manual URL
      const match = activeItem.youtube_url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/);
      if (match) {
        youtubeKey = match[1];
      }
    }
    
    youtubeUrl = youtubeKey
      ? `https://www.youtube.com/embed/${youtubeKey}?autoplay=1&mute=1&controls=0&loop=1&playlist=${youtubeKey}&showinfo=0&rel=0&modestbranding=1`
      : '';
  }
  
  const itemLink = `/${activeItem.folder}/${activeItem.tmdb_id}`;

  const isRTL = locale === 'ar';

  return (
    <div className="hero-carousel-full" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Background Video/Image */}
      <div className="hero-backdrop">
        {localVideoPath ? (
          <video
            ref={videoRef}
            className="hero-trailer-video"
            src={localVideoPath}
            autoPlay
            muted
            loop
            playsInline
          />
        ) : youtubeUrl ? (
          <iframe
            className="hero-trailer-iframe"
            src={youtubeUrl}
            title={`${title} Trailer`}
            allow="autoplay; encrypted-media"
            allowFullScreen
          />
        ) : backdropUrl ? (
          <img
            src={backdropUrl}
            alt={title}
            className="hero-backdrop-image"
          />
        ) : null}
        
        {/* Mobile Mute Button */}
        {localVideoPath && (
          <button 
            className="hero-mobile-mute-button"
            onClick={toggleMute}
            aria-label={isMuted ? 'Unmute' : 'Mute'}
          >
            {isMuted ? (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M11 5L6 9H2v6h4l5 4V5z"/>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/>
              </svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M11 5L6 9H2v6h4l5 4V5z"/>
              </svg>
            )}
          </button>
        )}
        
        <div 
          className="hero-mobile-play-button"
          onClick={() => window.location.href = itemLink}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M8 5v14l11-7z"/>
          </svg>
        </div>
      </div>

      {/* Content */}
      <div className="hero-content">
        <div className="hero-content-inner">
          {/* Year + Rating */}
          <div className="hero-year-rating-row">
            {year && <span className="hero-year">{year}</span>}
            {rating && (
              <div className="hero-rating-badge">
                <span>{rating}/10</span>
                <div className="hero-rating-stars">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <svg 
                      key={star} 
                      width="12" 
                      height="12" 
                      viewBox="0 0 24 24" 
                      fill={star <= Math.round(parseFloat(rating) / 2) ? "currentColor" : "rgba(255,255,255,0.3)"}
                    >
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                    </svg>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Title */}
          <h1 className="hero-title">{title}</h1>
          
          {/* Arabic Title */}
          {titleAr && <h2 className="hero-title-arabic">{titleAr}</h2>}

          {/* Type */}
          <div className="hero-type-info">
            {activeItem.folder === 'tv' ? 'TV Show' : 'Movie'}
          </div>

          {/* Genres */}
          {activeItem.genres && activeItem.genres.length > 0 && (
            <div className="hero-genres">
              {activeItem.genres.slice(0, 3).map((genre, idx) => (
                <span key={idx} className="hero-genre-tag">{genre}</span>
              ))}
            </div>
          )}

          {/* Synopsis */}
          <p className="hero-synopsis">{overview}</p>

          {/* Action Buttons */}
          <div className="hero-actions">
            <a href={itemLink} className="btn-primary hero-btn-watch">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
              </svg>
              {locale === 'ar' ? 'شاهد الآن' : 'Watch Now'}
            </a>
            <a href={itemLink} className="btn-secondary hero-btn-download">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4 a2 2 0 0 1-2 2H5 a2 2 0 0 1-2-2 v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              {locale === 'ar' ? 'تحميل' : 'Download'}
            </a>
          </div>

          {/* Mini Carousel - Mobile Only */}
          <div className="hero-mini-carousel">
            {items.slice(0, 5).map((item, idx) => (
              <button
                key={item.tmdb_id}
                className={`mini-poster-card ${activeIndex === idx ? 'active' : ''}`}
                aria-label={`Switch to video ${idx + 1}`}
                onClick={() => handleSlideChange(idx)}
              >
                <img
                  src={item.poster_path ? `https://image.tmdb.org/t/p/w200${item.poster_path.replace('/t/p/w500', '')}` : ''}
                  alt={`Video ${idx + 1}`}
                  loading="lazy"
                />
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
