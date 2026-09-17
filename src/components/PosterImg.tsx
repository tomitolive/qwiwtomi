"use client";

import Image from "next/image";

type PosterImgProps = {
  src: string;
  alt: string;
  className?: string;
  width?: number;
  height?: number;
  priority?: boolean;
};

export default function PosterImg({ src, alt, className, width = 500, height = 750, priority = false }: PosterImgProps) {
  // Use regular img tag for local images to avoid Next.js optimization issues
  const isLocalImage = src.startsWith('/t/p/') || src.startsWith('/');

  if (isLocalImage) {
    return (
      <img
        src={src}
        alt={alt || "صورة ملصق"}
        className={className}
        loading={priority ? "eager" : "lazy"}
        onError={(e) => {
          const img = e.currentTarget;
          if (img.dataset.fallback) return;
          img.dataset.fallback = "1";
          const next = img.src
            .replace("/t/p/w500", "https://image.tmdb.org/t/p/w500")
            .replace("/t/p/original", "https://image.tmdb.org/t/p/original");
          if (next !== img.src) img.src = next;
        }}
      />
    );
  }

  // Use Next.js Image for external images only
  return (
    <Image
      src={src}
      alt={alt || "صورة ملصق"}
      width={width}
      height={height}
      className={className}
      priority={priority}
      loading={priority ? "eager" : "lazy"}
      onError={(e) => {
        const img = e.currentTarget;
        if (img.dataset.fallback) return;
        img.dataset.fallback = "1";
        const next = img.src
          .replace("/t/p/w500", "https://image.tmdb.org/t/p/w500")
          .replace("/t/p/original", "https://image.tmdb.org/t/p/original");
        if (next !== img.src) (img as any).src = next;
      }}
    />
  );
}
