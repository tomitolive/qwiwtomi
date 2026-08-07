import type { Metadata } from "next";
import type { ContentData } from "./content";

const SITE_URL = "https://tomito.xyz";

/**
 * Ensures meta description is between 150-160 characters
 * If description is too short, appends additional descriptive text
 * If description is too long, truncates it
 */
function ensureMinimumDescriptionLength(description: string, title: string, mediaType: "movie" | "tv"): string {
  const minLength = 150;
  const maxLength = 160;
  
  // If description is already within range, return it as-is
  if (description.length >= minLength && description.length <= maxLength) {
    return description;
  }
  
  // If description is too long, truncate it to exactly maxLength
  if (description.length > maxLength) {
    console.log(`Truncating description from ${description.length} to ${maxLength} chars for: ${title}`);
    return description.slice(0, maxLength);
  }
  
  // If too short, append additional text
  const typeLabel = mediaType === "movie" ? "فيلم" : "مسلسل";
  const fallbackTexts = [
    `شاهد بجودة عالية وترجمة احترافية بدون إعلانات مزعجة.`,
    `استمتع بمشاهدة بجودة 4K وترجمة عربية احترافية مجاناً.`,
    `مشاهدة بترجمة احترافية وجودة عالية وبدون إعلانات.`,
    `تجربة مشاهدة فريدة بجودة عالية وترجمة دقيقة.`,
    `شاهد هذا ${typeLabel} بجودة عالية وترجمة احترافية على توميتو.`,
    `استمتع بمشاهدة هذا ${typeLabel} بجودة عالية وترجمة احترافية بدون إعلانات.`,
  ];
  
  // Try each fallback text until we reach the minimum length
  for (const fallback of fallbackTexts) {
    const extended = `${description} ${fallback}`;
    if (extended.length >= minLength) {
      // If extended is too long, truncate to exactly maxLength
      if (extended.length > maxLength) {
        return extended.slice(0, maxLength);
      }
      return extended;
    }
  }
  
  // If still too short, use a generic extended description
  const generic = `${description} شاهد بجودة عالية وترجمة احترافية على توميتو بدون إعلانات مزعجة.`;
  return generic.slice(0, maxLength);
}

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
    ? `مشاهدة فيلم ${genreLabel} ${title} ${year} على توميتو tomito`
    : `مشاهدة فيلم ${title} ${year} على توميتو tomito`;

  // Use AI meta_desc only if it's within acceptable range, otherwise use intentLead
  const aiDesc = ai?.meta_desc?.trim();
  const baseDescription = (aiDesc && aiDesc.length >= 140 && aiDesc.length <= 170) 
    ? aiDesc 
    : intentLead;

  const description = ensureMinimumDescriptionLength(
    baseDescription,
    title,
    "movie"
  );

  const keywords =
    ai?.keywords?.trim() ||
    [
      `مشاهدة ${title}`,
      `تحميل فيلم ${title}`,
      `فيلم ${title} ${year}`,
      `${title} مترجم`,
      `${title} اون لاين`,
      `توميتو ${title}`,
      // English keywords
      titleEn ? `watch ${titleEn} online` : `watch ${title} online`,
      titleEn ? `download ${titleEn}` : `download ${title}`,
      titleEn ? `${titleEn} movie ${year}` : `${title} movie ${year}`,
      titleEn ? `${titleEn} free` : `${title} free`,
      titleEn ? `${titleEn} streaming` : `${title} streaming`,
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
    ? `مشاهدة مسلسل ${genreLabel} ${title} ${year} على توميتو tomito`
    : `مشاهدة مسلسل ${title} ${year} على توميتو tomito`;

  // Use AI meta_desc only if it's within acceptable range, otherwise use intentLead
  const aiDesc = ai?.meta_desc?.trim();
  const baseDescription = (aiDesc && aiDesc.length >= 140 && aiDesc.length <= 170) 
    ? aiDesc 
    : intentLead;

  const description = ensureMinimumDescriptionLength(
    baseDescription,
    title,
    "tv"
  );

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
      // English keywords
      titleEn ? `watch ${titleEn} online` : `watch ${title} online`,
      titleEn ? `download ${titleEn}` : `download ${title}`,
      titleEn ? `${titleEn} series ${year}` : `${title} series ${year}`,
      titleEn ? `${titleEn} free` : `${title} free`,
      titleEn ? `${titleEn} streaming` : `${title} streaming`,
      titleEn ? `${titleEn} episodes` : `${title} episodes`,
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
