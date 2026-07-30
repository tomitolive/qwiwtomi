import { Metadata } from "next";
import { getDetails } from "@/lib/tmdb";
import { getLocalContent, getLocalSimilar, ContentGenre, ContentFaqItem } from "@/lib/content";
import { buildMovieMetadata, formatBilingualTitle } from "@/lib/seo";
import { notFound } from "next/navigation";
import Breadcrumbs from "@/components/Breadcrumbs";
import Script from "next/script";
import ProtectedLink from "@/components/ProtectedLink";
import Navbar from "@/components/Navbar";
import NewAd from "@/components/NewAd";

interface TMDBVideo {
  id: string;
  key: string;
  name: string;
  site: string;
  type: string;
}

interface Props {
  params: Promise<{ slug: string }>;
}

function parseId(slug: string) {
  const match = slug.match(/^(\d+)/);
  return match ? match[1] : null;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const id = parseId(slug);
  if (!id) return { title: "فيلم غير موجود" };

  const local = await getLocalContent(id);

  if (!local) {
    return { title: "فيلم غير موجود" };
  }

  const data = local;
  const titleAr =
    local?.title_ar || local?.title || data?.title || "";
  const titleEn =
    local?.title_en || local?.title || "";
  const year = (data?.release_date || "2026").substring(0, 4);
  const genreLabel = data?.genres?.[0]?.name;

  return buildMovieMetadata({
    title: titleAr,
    titleEn,
    year,
    genreLabel,
    slug,
    local,
    posterPath: data?.poster_path,
    overview: local?.ai_content?.desc_ar || data?.overview,
  });
}

export default async function MoviePage({ params }: Props) {
  const { slug } = await params;
  const id = parseId(slug);
  if (!id) notFound();

  const local = await getLocalContent(id);

  if (!local) notFound();

  const data = local;
  const ai = local?.ai_content;
  const genreIds: number[] = data.genres?.map((g: ContentGenre) => g.id) || [];

  // Get trailer from TMDB safely
  let trailer = null;
  try {
    const tmdbDetails = await getDetails(id, "movie");
    const videos = tmdbDetails?.videos?.results || [];
    trailer = videos.find((v: TMDBVideo) => v.type === "Trailer" && v.site === "YouTube") || videos[0];
  } catch (error) {
    console.error(`Failed to fetch TMDB details for movie ${id}:`, error);
  }

  // Local similar movies from our own database (no TMDB external calls)
  const localSimilar = getLocalSimilar(id!, genreIds, "movie", 40);

  const titleAr =
    local?.title_ar ||
    local?.title ||
    data.title ||
    "";
  const titleEn =
    local?.title_en ||
    local?.title ||
    "";
  const displayTitle = formatBilingualTitle(titleAr, titleEn);
  const overview = data.overview || ai?.desc_ar || "";
  const extraDesc = ai?.desc_ar && data.overview && ai.desc_ar !== data.overview && ai.desc_ar.length > 30 && !ai.desc_ar.startsWith("مشاهدة وتحميل") ? ai.desc_ar : null;
  const year = (data.release_date || "2026").substring(0, 4);
  const rating = data.vote_average?.toFixed(1);
  const genres = data.genres?.map((g: ContentGenre) => g.name).join(" • ");
  const backdrop = data.backdrop_path ? `/t/p/original${data.backdrop_path}` : "";
  const poster = data.poster_path ? `/t/p/w500${data.poster_path}` : "";

  const movieSchema = {
    "@context": "https://schema.org",
    "@type": "Movie",
    "name": displayTitle,
    "alternateName": titleEn && titleEn !== titleAr ? titleEn : undefined,
    "image": `https://tomito.xyz${poster}`,
    "description": overview,
    "datePublished": data.release_date,
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": rating,
      "bestRating": "10",
      "worstRating": "1",
      "ratingCount": data.vote_count || "100"
    }
  };

  return (
    <div className="relative min-h-screen bg-background text-white">
      <Script
        id="movie-schema"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(movieSchema) }}
      />

      {/* Hero Section */}
      <div className="relative w-full bg-background py-8 md:py-12">
        
        {/* Layer 3: Transparent Header */}
        <div className="absolute top-0 left-0 w-full z-30 bg-transparent">
          <Navbar />
        </div>

        {/* Layer 4: Clear Content */}
        <div className="relative z-20 container mx-auto flex items-center px-4 md:px-6 pt-20 md:pt-24">
          <div className="flex flex-col md:flex-row gap-6 md:gap-8 items-center w-full">
            
            {/* Left: Poster */}
            {poster && (
              <div className="w-full md:w-[260px] flex-shrink-0 relative order-1">
                <img
                  src={poster}
                  alt={displayTitle}
                  className="w-full h-auto object-contain rounded-lg border-2 border-white/20 shadow-2xl"
                  loading="eager"
                />
              </div>
            )}

            {/* Right: Content */}
            <div className="flex-1 space-y-3 md:space-y-4 order-2 text-center md:text-left">
              {/* Title */}
              <h1 className="text-xl md:text-3xl lg:text-4xl font-extrabold tracking-wider text-white">
                {displayTitle} {year}
              </h1>

              {/* Rating */}
              {rating && (
                <div className="flex items-center gap-2 justify-center md:justify-start">
                  <span className="text-yellow-400 text-lg md:text-xl">⭐</span>
                  <span className="text-base md:text-lg font-extrabold tracking-wider" style={{
                    color: 'transparent',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    backgroundImage: 'linear-gradient(to right, #ef4444, #f97316, #dc2626)',
                    filter: 'drop-shadow(0 0 15px rgba(255, 80, 0, 0.8))'
                  }}>{rating}</span>
                </div>
              )}

              {/* Genres */}
              <div className="flex flex-wrap gap-2 justify-center md:justify-start">
                {data.genres?.map((g: ContentGenre) => (
                  <span key={g.id} className="px-2 md:px-3 py-1 md:py-1.5 bg-white/10 backdrop-blur-sm text-xs md:text-xs rounded-full border border-white/20 font-extrabold tracking-wider" style={{
                    color: 'transparent',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    backgroundImage: 'linear-gradient(to right, #ef4444, #f97316, #dc2626)',
                    filter: 'drop-shadow(0 0 15px rgba(255, 80, 0, 0.8))'
                  }}>
                    {g.name}
                  </span>
                ))}
              </div>

              {/* Overview */}
              {overview && (
                <p className="text-gray-300 text-sm md:text-base leading-relaxed max-w-3xl">
                  {overview}
                </p>
              )}

              {/* Watch Buttons */}
              <div className="flex flex-col md:flex-row gap-2 md:gap-3 pt-1 md:pt-2 justify-center md:justify-start">
                <ProtectedLink
                  encodedUrl={btoa(`https://tv.tomito.xyz/movie/${id}/watch`)}
                  className="px-5 md:px-6 py-2 md:py-2.5 bg-orange-500 hover:bg-orange-600 text-white font-bold rounded-lg transition-colors text-center text-sm md:text-base tracking-wider"
                >
                  مشاهدة الآن
                </ProtectedLink>
                {data.imdb_id && (
                  <a
                    href={`https://www.imdb.com/title/${data.imdb_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-5 md:px-6 py-2 md:py-2.5 bg-yellow-600 hover:bg-yellow-700 text-white font-bold rounded-lg transition-colors text-center text-sm md:text-base tracking-wider"
                  >
                    IMDb
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content below Hero Section */}
      <div className="px-4 md:px-8 pb-16 max-w-[1200px] mx-auto -mt-8">
        <div className="flex flex-col md:flex-row gap-6">

          {/* Right Column - Content (69%) */}
          <div className="w-full md:w-[69%] space-y-6">
            {/* Breadcrumbs */}
            <div className="h-[38px]">
              <Breadcrumbs items={[
                { name: "الرئيسية", item: "/" },
                { name: "أفلام", item: "/movie" },
                { name: displayTitle, item: `/movie/${slug}` }
              ]} />
            </div>

            {/* Ad 1 - بعد البريدكرامبس */}
            <NewAd ad="ad1" />

            {/* Full Content Section */}
            <div className="bg-transparent border border-zinc-800 p-4">
              <h2 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500">
                  <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                  <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
                </svg>
                المحتوى الكامل
              </h2>
              <div className="space-y-6">
                {/* SEO Title */}
                {ai?.seo_title_ar && (
                  <div className="mb-6">
                    <p className="text-orange-400 text-base font-semibold mb-2">العنوان:</p>
                    <p className="text-gray-300 text-base leading-relaxed">
                      {ai.seo_title_ar}
                    </p>
                  </div>
                )}
                
                {/* Intro */}
                {ai?.intro && (
                  <p className="text-gray-300 text-base leading-relaxed">
                    {ai.intro}
                  </p>
                )}
                
                {/* Arabic Description removed from here intentionally as it was moved upstairs */}
                {extraDesc && (
                  <p className="text-gray-300 text-base leading-relaxed">
                    {extraDesc}
                  </p>
                )}
                
                {/* Tomito Opinion Arabic */}
                {(ai?.opinion_ar || ai?.opinion) && (
                  <div className="mt-4 pt-4 border-t border-zinc-700">
                    <p className="text-orange-400 text-base font-semibold mb-1">رأي توميتو (عربي):</p>
                    <p className="text-gray-300 text-base leading-relaxed">
                      {ai.opinion_ar || ai.opinion}
                    </p>
                  </div>
                )}
                
                {/* Outro */}
                {ai?.outro && (
                  <div className="mt-4 pt-4 border-t border-zinc-700">
                    <p className="text-gray-500 italic text-sm">
                      {ai.outro}
                    </p>
                  </div>
                )}
                
                {/* Keywords */}
                {ai?.keywords && (
                  <div className="mt-4 pt-4 border-t border-zinc-700">
                    <p className="text-orange-400 text-base font-semibold mb-2">الكلمات المفتاحية:</p>
                    <div className="flex flex-wrap gap-2">
                      {ai.keywords.split(',').map((keyword: string, index: number) => (
                        <span key={index} className="px-3 py-1 bg-orange-500/20 text-orange-400 text-sm rounded-full border border-orange-500/30">
                          {keyword.trim()}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* English Description */}
                {ai?.desc_en && (
                  <div className="mt-4 pt-4 border-t border-zinc-700">
                    <p className="text-orange-400 text-base font-semibold mb-1">English Description:</p>
                    <p className="text-gray-300 text-base leading-relaxed">
                      {ai.desc_en}
                    </p>
                  </div>
                )}
                
                {/* Tomito Opinion English */}
                {ai?.opinion_en && (
                  <div className="mt-4 pt-4 border-t border-zinc-700">
                    <p className="text-orange-400 text-base font-semibold mb-1">رأي توميتو (English):</p>
                    <p className="text-gray-300 text-base leading-relaxed">
                      {ai.opinion_en}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Movie Details Table */}
            <div className="bg-transparent border border-zinc-800 p-4">
              <h2 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 6v6l4 2"/>
                </svg>
                تفاصيل الفيلم
              </h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-start gap-2">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500 mt-1 shrink-0">
                    <path d="M3 7v2a3 3 0 0 0 3 3 3 3 0 0 0-3 3v2a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-2a3 3 0 0 0-3-3 3 3 0 0 0 3-3V7a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2z"/>
                  </svg>
                  <div>
                    <p className="text-gray-400 text-sm mb-1">قسم الفيلم</p>
                    <p className="text-white font-medium">{local?.section || "أفلام أجنبية"}</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500 mt-1 shrink-0">
                    <path d="M7 4v16M17 4v16M3 8h4M10 8h4M17 8h4M3 16h4M10 16h4M17 16h4"/>
                  </svg>
                  <div>
                    <p className="text-gray-400 text-sm mb-1">نوع الفيلم</p>
                    <p className="text-white font-medium">{genres}</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500 mt-1 shrink-0">
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                  </svg>
                  <div>
                    <p className="text-gray-400 text-sm mb-1">جودة الفيلم</p>
                    <p className="text-white font-medium">{local?.quality || "1080p BluRay"}</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500 mt-1 shrink-0">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                  <div>
                    <p className="text-gray-400 text-sm mb-1">مدة الفيلم</p>
                    <p className="text-white font-medium">{local?.duration || "-"}</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500 mt-1 shrink-0">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/>
                    <line x1="8" y1="2" x2="8" y2="6"/>
                    <line x1="3" y1="10" x2="21" y2="10"/>
                  </svg>
                  <div>
                    <p className="text-gray-400 text-sm mb-1">تاريخ الصدور</p>
                    <p className="text-white font-medium">{year}</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500 mt-1 shrink-0">
                    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
                  </svg>
                  <div>
                    <p className="text-gray-400 text-sm mb-1">لغة الفيلم</p>
                    <p className="text-white font-medium">{local?.language || "الإنجليزية"}</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500 mt-1 shrink-0">
                    <path d="M3 21h18M5 21V7l8-4 8 4v14M8 21v-4h8v4"/>
                  </svg>
                  <div>
                    <p className="text-gray-400 text-sm mb-1">دولة الفيلم</p>
                    <p className="text-white font-medium">{local?.country || "الولايات المتحدة الأمريكية"}</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500 mt-1 shrink-0">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                  <div>
                    <p className="text-gray-400 text-sm mb-1">بطولة</p>
                    <p className="text-white font-medium">{local?.cast || "-"}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Ad 2 - بعد تفاصيل الفيلم */}
            <NewAd ad="ad2" />

            {/* Trailer Section */}
            {trailer && (
              <div className="bg-transparent border border-zinc-800 p-4">
                <h2 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                  </svg>
                  مقطع الدعائي
                </h2>
                <div className="aspect-video">
                  <iframe
                    src={`https://www.youtube.com/embed/${trailer.key}`}
                    title={trailer.name}
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    className="w-full h-full rounded"
                  />
                </div>
              </div>
            )}

            {/* FAQ Section */}
            {ai?.faq && ai.faq.length > 0 && (
              <div className="bg-transparent border border-zinc-800 p-4">
                <h2 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                    <line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                  الأسئلة الشائعة
                </h2>
                <div className="space-y-3">
                  {ai.faq.map((item: ContentFaqItem, index: number) => (
                    <div key={index} className="border-b border-zinc-700 pb-3 last:border-0">
                      {/* Arabic / Default FAQ */}
                      <h3 className="text-white font-semibold mb-2">{item.q || item.question}</h3>
                      <p className="text-gray-300 text-sm leading-relaxed mb-3">{item.a || item.answer}</p>
                      
                      {/* English FAQ (if exists) */}
                      {item.q_en && item.a_en && (
                        <div className="bg-zinc-800/30 rounded p-3 mt-2 border border-zinc-700/50" dir="ltr" style={{ fontFamily: 'var(--font-inter)' }}>
                          <h4 className="text-white text-sm font-semibold mb-1 flex items-center gap-2">
                             <span className="bg-orange-500/20 text-orange-400 text-[10px] px-1.5 py-0.5 rounded font-bold">EN</span>
                             {item.q_en}
                          </h4>
                          <p className="text-gray-400 text-xs leading-relaxed">{item.a_en}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>

        </div>

        {/* Suggested Movies List - 6 cards in one row */}
        {localSimilar.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <line x1="9" y1="3" x2="9" y2="21"/>
                <line x1="15" y1="3" x2="15" y2="21"/>
              </svg>
              أفلام مقترحة
            </h2>
            <div className="grid grid-cols-6 gap-0">
              {localSimilar.slice(0, 6).map((item, i) => (
                <a
                  key={`suggested-${item.tmdb_id}-${i}`}
                  href={`/movie/${item.slug}`}
                  className="group"
                >
                  <div className="bg-zinc-800 border border-zinc-700 overflow-hidden">
                    <img
                      src={item.poster?.replace('https://image.tmdb.org/t/p/w500', '/t/p/w500') || `/t/p/w500${item.poster}`}
                      alt={item.title_ar || item.title}
                      loading="lazy"
                      className="w-full aspect-[2/3] object-cover"
                    />
                    <div className="p-2">
                      <h3 className="text-white text-xs font-bold truncate">{item.title_ar || item.title}</h3>
                      <p className="text-gray-500 text-[10px]">{item.year} ⭐ {item.rating}</p>
                    </div>
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Ad 3 - بعد الأفلام المقترحة */}
        <NewAd ad="ad3" />

        {/* Footer Carousels - 4 sections with sliding cards */}
        <div className="mt-8 space-y-8">
          {/* Latest */}
          <div>
            <h2 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              الأحدث
            </h2>
            <div className="flex gap-3 overflow-x-auto pb-4 scrollbar-hide">
              {localSimilar.slice(0, 10).map((item, i) => (
                <a
                  key={`latest-${item.tmdb_id}-${i}`}
                  href={`/movie/${item.slug}`}
                  className="flex-shrink-0 w-[120px]"
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
              ))}
            </div>
          </div>

          {/* Most Viewed */}
          <div>
            <h2 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              الأكثر مشاهدة
            </h2>
            <div className="flex gap-3 overflow-x-auto pb-4 scrollbar-hide">
              {localSimilar.slice(10, 20).map((item, i) => (
                <a
                  key={`viewed-${item.tmdb_id}-${i}`}
                  href={`/movie/${item.slug}`}
                  className="flex-shrink-0 w-[120px]"
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
              ))}
            </div>
          </div>

          {/* Top Rated */}
          <div>
            <h2 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
              الأعلى تقييماً
            </h2>
            <div className="flex gap-3 overflow-x-auto pb-4 scrollbar-hide">
              {localSimilar.slice(20, 30).map((item, i) => (
                <a
                  key={`rated-${item.tmdb_id}-${i}`}
                  href={`/movie/${item.slug}`}
                  className="flex-shrink-0 w-[120px]"
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
              ))}
            </div>
          </div>

          {/* Random */}
          <div>
            <h2 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500">
                <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
                <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>
                <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>
              </svg>
              عشوائي
            </h2>
            <div className="flex gap-3 overflow-x-auto pb-4 scrollbar-hide">
              {localSimilar.slice(30, 40).map((item, i) => (
                <a
                  key={`random-${item.tmdb_id}-${i}`}
                  href={`/movie/${item.slug}`}
                  className="flex-shrink-0 w-[120px]"
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
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
