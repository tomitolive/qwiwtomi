import type { Metadata } from "next";
import type { ContentData } from "./content";

const SITE_URL = "https://tomit.click";

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
function buildOptimizedPageTitle(opts: {
  title: string;
  titleEn?: string;
  year: string;
  genreLabel?: string;
  mediaType: "movie" | "tv";
  aiSeoTitle?: string;
}): string {
  const typeLabel = opts.mediaType === "movie" ? "فيلم" : "مسلسل";
  const titleEn = opts.titleEn?.trim();
  const titleAr = opts.title.trim();

  // Helper 1: Build a target title structure
  const build = (name: string, useGenre: boolean, useEnglish: boolean) => {
    const formattedName = useEnglish && titleEn && titleEn !== name
      ? `${name} (${titleEn})`
      : name;
    const genre = useGenre && opts.genreLabel ? `${opts.genreLabel} ` : "";
    return `مشاهدة ${typeLabel} ${genre}${formattedName} ${opts.year} مترجم`;
  };

  // Helper 2: Clean and potentially inject EN into an existing AI title
  const cleanAndInjectAiTitle = (rawAiTitle: string, useEnglish: boolean): string => {
    let clean = rawAiTitle.trim();
    // Split by common delimiters if the title is long
    if (clean.length > 60) {
      for (const delimiter of [" - ", " | ", " – ", " — "]) {
        if (clean.includes(delimiter)) {
          const parts = clean.split(delimiter);
          if (parts[0].length >= 15) {
            clean = parts[0].trim();
            break;
          }
        }
      }
    }
    
    // If still > 60, try removing parenthesized content
    if (clean.length > 60 && clean.includes("(")) {
      clean = clean.replace(/\s*\([^)]*\)/g, "").trim();
    }

    // Inject English title if requested and not already present
    if (useEnglish && titleEn && titleEn !== titleAr) {
      if (!clean.includes(titleEn) && clean.includes(titleAr)) {
        clean = clean.replace(titleAr, `${titleAr} (${titleEn})`);
      }
    }

    // Remove trailing "- توميتو" or "توميتو" if it is still too long
    if (clean.length > 60) {
      clean = clean.replace(/\s*-\s*توميتو\s*$/, "").replace(/\s*توميتو\s*$/, "").trim();
    }

    // If too short and missing suffix elements, enrich it
    if (clean.length < 40 && !clean.includes("مترجم") && !clean.includes("تحميل")) {
      clean = `${clean} ${opts.year} مترجم`;
    }

    return clean;
  };

  // 1. Try AI SEO title if exists
  if (opts.aiSeoTitle?.trim()) {
    let t = cleanAndInjectAiTitle(opts.aiSeoTitle, true);
    if (t.length <= 60) return t;

    t = cleanAndInjectAiTitle(opts.aiSeoTitle, false);
    if (t.length <= 60) return t;
  }

  // 2. Try Default title with full details (genre + bilingual name)
  let t = build(titleAr, true, true);
  if (t.length <= 60) return t;

  // 3. Try Default title with bilingual name (no genre)
  t = build(titleAr, false, true);
  if (t.length <= 60) return t;

  // 4. Try Default title with Arabic name + genre (no English)
  t = build(titleAr, true, false);
  if (t.length <= 60) return t;

  // 5. Try Default title with Arabic name only (no English, no genre)
  t = build(titleAr, false, false);
  if (t.length <= 60) return t;

  // 6. Try splitting Arabic title by colon (if it has one) to drop the subtitle
  if (titleAr.includes(":")) {
    const mainPartAr = titleAr.split(":")[0].trim();
    if (mainPartAr.length >= 3) {
      t = build(mainPartAr, true, false);
      if (t.length <= 60) return t;

      t = build(mainPartAr, false, false);
      if (t.length <= 60) return t;
    }
  }

  // 7. Try splitting Arabic title by dash (if it has one)
  if (titleAr.includes("-")) {
    const mainPartAr = titleAr.split("-")[0].trim();
    if (mainPartAr.length >= 3) {
      t = build(mainPartAr, true, false);
      if (t.length <= 60) return t;

      t = build(mainPartAr, false, false);
      if (t.length <= 60) return t;
    }
  }

  // 8. If all else fails, hard truncate the Arabic title
  const suffix = ` ${opts.year} مترجم`;
  const basePrefix = `مشاهدة ${typeLabel} `;
  const allowedLength = 60 - basePrefix.length - suffix.length - (opts.genreLabel ? opts.genreLabel.length + 1 : 0);
  
  const truncatedAr = titleAr.length > allowedLength && allowedLength > 5
    ? titleAr.substring(0, allowedLength - 3).trim() + "..."
    : titleAr;
    
  const genre = opts.genreLabel ? `${opts.genreLabel} ` : "";
  return `${basePrefix}${genre}${truncatedAr}${suffix}`;
}

export function formatBilingualTitle(ar: string, en?: string): string {
  const enClean = en?.trim();
  if (!enClean || enClean === ar) return ar;
  return `${ar} (${enClean})`;
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
  const { title, year, genreLabel, slug, local, posterPath } = opts;
  const ai = local?.ai_content;

  const canonicalUrl = `${SITE_URL}/movie/${slug}`;

  const titleEn = opts.titleEn?.trim();
  const mergedName = formatBilingualTitle(title, titleEn);

  const pageTitle = buildOptimizedPageTitle({
    title,
    titleEn,
    year,
    genreLabel,
    mediaType: "movie",
    aiSeoTitle: ai?.seo_title_ar,
  });

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

  const nowISO = new Date().toISOString();

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
      site: "@tomito_xyz",
      creator: "@tomito_xyz",
      title: pageTitle,
      description,
      images: ogImage ? [ogImage] : undefined,
    },
    other: {
      "og:image:secure_url": ogImage || "",
      "og:image:type": "image/jpeg",
      "og:image:width": "500",
      "og:image:height": "750",
      "og:image:alt": `بوستر فيلم ${mergedName}`,
      "article:published_time": opts.local?.release_date ? `${opts.local.release_date}T00:00:00Z` : nowISO,
      "og:updated_time": nowISO,
      "article:section": genreLabel || "أفلام",
      "Content-Language": "ar",
      "rating": "General",
      "revisit-after": "3 days",
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
  const { title, year, genreLabel, slug, local, posterPath } = opts;
  const ai = local?.ai_content;
  const canonicalUrl = `${SITE_URL}/tv/${slug}`;
  const titleEn = opts.titleEn?.trim();
  const mergedName = formatBilingualTitle(title, titleEn);
  const pageTitle = buildOptimizedPageTitle({
    title,
    titleEn,
    year,
    genreLabel,
    mediaType: "tv",
    aiSeoTitle: ai?.seo_title_ar,
  });

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

  const nowISO = new Date().toISOString();

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
      site: "@tomito_xyz",
      creator: "@tomito_xyz",
      title: pageTitle,
      description,
      images: ogImage ? [ogImage] : undefined,
    },
    other: {
      "og:image:secure_url": ogImage || "",
      "og:image:type": "image/jpeg",
      "og:image:width": "500",
      "og:image:height": "750",
      "og:image:alt": `بوستر مسلسل ${mergedName}`,
      "article:published_time": opts.local?.release_date ? `${opts.local.release_date}T00:00:00Z` : nowISO,
      "og:updated_time": nowISO,
      "article:section": genreLabel || "مسلسلات",
      "Content-Language": "ar",
      "rating": "General",
      "revisit-after": "3 days",
    },
  };
}
