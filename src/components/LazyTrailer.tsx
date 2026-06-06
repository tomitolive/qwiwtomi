"use client";

import React, { useState } from "react";

interface LazyTrailerProps {
  videoKey: string;
  title: string;
  year: string;
  runtimeOrType?: string;
}

export default function LazyTrailer({ videoKey, title, year, runtimeOrType = "Featured" }: LazyTrailerProps) {
  const [isPlaying, setIsPlaying] = useState(false);

  const handlePlay = () => {
    setIsPlaying(true);
  };

  return (
    <>
      <div className="video-container">
        {isPlaying ? (
          <iframe
            src={`https://www.youtube.com/embed/${videoKey}?rel=0&showinfo=0&autoplay=1`}
            title={`${title} Trailer`}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          ></iframe>
        ) : (
          <div 
            className="w-full h-full relative cursor-pointer group bg-black/50 aspect-video flex items-center justify-center rounded-2xl overflow-hidden border border-white/10"
            onClick={handlePlay}
            style={{
              backgroundImage: `url(https://img.youtube.com/vi/${videoKey}/hqdefault.jpg)`,
              backgroundSize: "cover",
              backgroundPosition: "center"
            }}
          >
            <div className="absolute inset-0 bg-black/40 group-hover:bg-black/20 transition-colors duration-300" />
            <div className="w-16 h-16 md:w-20 md:h-20 bg-red-600 rounded-full flex items-center justify-center z-10 shadow-[0_0_30px_rgba(220,38,38,0.5)] group-hover:scale-110 transition-transform duration-300">
               <svg width="24" height="24" viewBox="0 0 24 24" fill="white" className="ml-1"><path d="M8 5v14l11-7z" /></svg>
            </div>
          </div>
        )}
      </div>
      <div className="video-info">
        <h3 className="video-title">{title} - Trailer Official</h3>
        <div className="video-meta">
          <span>{year}</span>
          <span>•</span>
          <span>{runtimeOrType}</span>
        </div>
      </div>
    </>
  );
}
