import type { Metadata } from "next";
import type { ContentData } from "./content";

const SITE_URL = "https://tomito.xyz";

/** Arabic + English in one label: هوس (Obsession) */
export function formatBilingualTitle(ar: string, en?: string): string {
  const enClean = en?.trim();
  if (!enClean || enClean === ar) return ar;
  return `${ar} (${enClean})`;
}

function injectEnglishIntoSeoTitle(seoTitle: string, ar: string, en?: string): string {
  const merged = formatBilingualTitle(ar, en);
  if (merged === ar || seoTitle.includes(merged) || seoTitle.includes(en || "")) {
    return seoTitle;
  }
  return seoTitle.replace(ar, merged);
}

export function absolutePosterUrl(posterPath?: string): string | undefined {
  if (!posterPath) return undefined;
  if (posterPath.startsWith("http")) return posterPath;
  const path = posterPath.startsWith("/t/p/")
    ? posterPath
    : `/t/p/w500${posterPath.startsWith("/") ? posterPath : `/${posterPath}`}`;
  return `${SITE_URL}${path}`;
}

export function buildMovieMetadata(opts: {
  title: string;
  titleEn?: string;
  year: string;
  genreLabel?: string;
  slug: string;
  local?: ContentData | null;
  posterPath?: string;
  overview?: string;
}): Metadata {
  const { title, year, genreLabel, slug, local, posterPath, overview } = opts;
  const ai = local?.ai_content;

  const canonicalUrl = `${SITE_URL}/movie/${slug}`;

  const titleEn = opts.titleEn?.trim();
  const mergedName = formatBilingualTitle(title, titleEn);

  const defaultTitle = genreLabel
    ? `مشاهدة وتحميل فيلم ${genreLabel} ${mergedName} ${year} مترجم اون لاين`
    : `مشاهدة وتحميل فيلم ${mergedName} ${year} مترجم اون لاين`;

  const pageTitle = ai?.seo_title_ar?.trim()
    ? injectEnglishIntoSeoTitle(ai.seo_title_ar.trim(), title, titleEn)
    : defaultTitle;

  const intentLead = genreLabel
    ? `مشاهدة وتحميل فيلم ${genreLabel} ${title} ${year} بجودة 4K مترجم اون لاين على توميتو.`
    : `مشاهدة وتحميل فيلم ${title} ${year} بجودة 4K مترجم اون لاين على توميتو.`;

  const description =
    ai?.meta_desc?.trim() ||
    `${intentLead} ${(overview || "").trim()}`.trim().slice(0, 160);

  const keywords =
    ai?.keywords?.trim() ||
    [
      `مشاهدة ${title}`,
      `تحميل فيلم ${title}`,
      `فيلم ${title} ${year}`,
      `${title} مترجم`,
      `${title} اون لاين`,
      `توميتو ${title}`,
    ].join(", ");

  const ogImage = absolutePosterUrl(posterPath || local?.poster_path);
  const ogImages = ogImage
    ? [{ url: ogImage, width: 500, height: 750, alt: `بوستر فيلم ${mergedName}` }]
    : undefined;

  return {
    title: pageTitle,
    description,
    keywords,
    alternates: { canonical: canonicalUrl },
    openGraph: {
      title: pageTitle,
      description,
      url: canonicalUrl,
      siteName: "TOMITO",
      locale: "ar_SA",
      type: "video.movie",
      images: ogImages,
    },
    twitter: {
      card: "summary_large_image",
      title: pageTitle,
      description,
      images: ogImage ? [ogImage] : undefined,
    },
  };
}

export function buildTvMetadata(opts: {
  title: string;
  titleEn?: string;
  year: string;
  genreLabel?: string;
  slug: string;
  local?: ContentData | null;
  posterPath?: string;
  overview?: string;
}): Metadata {
  const { title, year, genreLabel, slug, local, posterPath, overview } = opts;
  const ai = local?.ai_content;
  const canonicalUrl = `${SITE_URL}/tv/${slug}`;
  const titleEn = opts.titleEn?.trim();
  const mergedName = formatBilingualTitle(title, titleEn);

  const defaultTitle = genreLabel
    ? `مشاهدة وتحميل مسلسل ${genreLabel} ${mergedName} ${year} مترجم اون لاين`
    : `مشاهدة وتحميل مسلسل ${mergedName} ${year} مترجم اون لاين`;

  const pageTitle = ai?.seo_title_ar?.trim()
    ? injectEnglishIntoSeoTitle(ai.seo_title_ar.trim(), title, titleEn)
    : defaultTitle;

  const intentLead = genreLabel
    ? `مشاهدة وتحميل مسلسل ${genreLabel} ${title} ${year} بجودة 4K مترجم اون لاين على توميتو.`
    : `مشاهدة وتحميل مسلسل ${title} ${year} بجودة 4K مترجم اون لاين على توميتو.`;

  const description =
    ai?.meta_desc?.trim() ||
    `${intentLead} ${(overview || "").trim()}`.trim().slice(0, 160);

  const keywords =
    ai?.keywords?.trim() ||
    [
      `مشاهدة ${title}`,
      `تحميل مسلسل ${title}`,
      `مسلسل ${title} ${year}`,
      `${title} مترجم`,
      `${title} اون لاين`,
      `حلقات ${title}`,
      `توميتو ${title}`,
    ].join(", ");

  const ogImage = absolutePosterUrl(posterPath || local?.poster_path);
  const ogImages = ogImage
    ? [{ url: ogImage, width: 500, height: 750, alt: `بوستر مسلسل ${mergedName}` }]
    : undefined;

  return {
    title: pageTitle,
    description,
    keywords,
    alternates: { canonical: canonicalUrl },
    openGraph: {
      title: pageTitle,
      description,
      url: canonicalUrl,
      siteName: "TOMITO",
      locale: "ar_SA",
      type: "video.tv_show",
      images: ogImages,
    },
    twitter: {
      card: "summary_large_image",
      title: pageTitle,
      description,
      images: ogImage ? [ogImage] : undefined,
    },
  };
}
