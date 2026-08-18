"use client";

type PosterImgProps = {
  src: string;
  alt: string;
  className?: string;
};

export default function PosterImg({ src, alt, className }: PosterImgProps) {
  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      className={className}
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
