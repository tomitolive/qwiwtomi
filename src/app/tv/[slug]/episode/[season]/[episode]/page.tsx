import { Metadata } from "next";
import { notFound } from "next/navigation";
import Script from "next/script";
import Breadcrumbs from "@/components/Breadcrumbs";
import Navbar from "@/components/Navbar";

interface Props {
  params: Promise<{
    slug: string;
    season: string;
    episode: string;
  }>;
}

function parseId(slug: string) {
  if (!slug) return null;
  const match = slug.match(/^(\d+)/);
  return match ? match[1] : null;
}

async function getEpisodeData(seriesId: string, season: string, episode: string) {
  const fs = require('fs').promises;
  const path = require('path');
  
  const episodeDir = path.join(process.cwd(), 'data', 'episodes');
  const filename = `${seriesId}_s${season}_e${episode}.json`;
  const filepath = path.join(episodeDir, filename);
  
  try {
    const data = await fs.readFile(filepath, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    return null;
  }
}

async function getSeriesData(seriesId: string) {
  const fs = require('fs').promises;
  const path = require('path');
  
  const seriesPath = path.join(process.cwd(), 'data', 'content', `${seriesId}.json`);
  
  try {
    const data = await fs.readFile(seriesPath, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    return null;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug, season, episode } = await params;
  const id = parseId(slug);
  if (!id) return { title: "حلقة غير موجودة" };

  const episodeData = await getEpisodeData(id, season, episode);
  if (!episodeData) return { title: "حلقة غير موجودة" };

  const ai = episodeData.ai_content;
  const titleAr = ai?.seo_title_ar || `الحلقة ${episode} الموسم ${season}`;
  const titleEn = ai?.seo_title_en || `Episode ${episode} Season ${season}`;
  const desc = ai?.meta_desc || episodeData.overview || "";

  return {
    title: titleAr,
    description: desc,
    openGraph: {
      title: titleAr,
      description: desc,
      type: "website",
    },
  };
}

export default async function EpisodePage({ params }: Props) {
  const { slug, season, episode } = await params;
  const id = parseId(slug);
  if (!id) notFound();

  const episodeData = await getEpisodeData(id, season, episode);
  if (!episodeData) notFound();

  const seriesData = await getSeriesData(id);
  const ai = episodeData.ai_content;

  const seriesTitle = episodeData.series_title;
  const episodeTitle = episodeData.episode_title;
  const displayTitle = `${seriesTitle} - S${season}E${episode} - ${episodeTitle}`;
  
  const poster = seriesData?.poster_path ? `/t/p/w500${seriesData.poster_path}` : "";
  const backdrop = seriesData?.backdrop_path ? `/t/p/original${seriesData.backdrop_path}` : "";
  const still = episodeData.still_path ? `/t/p/w780${episodeData.still_path}` : poster;

  const episodeSchema = {
    "@context": "https://schema.org",
    "@type": "TVEpisode",
    "name": episodeTitle,
    "episodeNumber": parseInt(episode),
    "seasonNumber": parseInt(season),
    "partOfSeries": {
      "@type": "TVSeries",
      "name": seriesTitle
    },
    "description": ai?.desc_ar || episodeData.overview,
    "image": still ? `https://tomito.xyz${still}` : undefined
  };

  return (
    <div className="relative min-h-screen bg-background text-white">
      <Script
        id="episode-schema"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(episodeSchema) }}
      />

      {/* Header */}
      <div className="relative w-full">
        <Navbar />
      </div>

      {/* Hero Section */}
      <div className="relative w-full h-[60vh] md:h-[50vh] bg-background overflow-hidden">
        {backdrop && (
          <div className="absolute inset-0">
            <img
              src={backdrop}
              alt={seriesTitle}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-background via-background/80 to-transparent" />
          </div>
        )}
        
        <div className="relative z-10 container mx-auto h-full flex items-end pb-8 px-4 md:px-6">
          <div className="w-full">
            <h1 className="text-2xl md:text-4xl font-extrabold tracking-wider text-white mb-2">
              {displayTitle}
            </h1>
            <p className="text-gray-300 text-sm md:text-base">
              {episodeData.air_date && `تاريخ العرض: ${episodeData.air_date}`}
            </p>
          </div>
        </div>
      </div>

      {/* Content Section */}
      <div className="px-4 md:px-8 pb-16 max-w-[1200px] mx-auto">
        {/* Breadcrumbs */}
        <div className="h-[38px]">
          <Breadcrumbs items={[
            { name: "الرئيسية", item: "/" },
            { name: "مسلسلات", item: "/tv" },
            { name: seriesTitle, item: `/tv/${slug}` },
            { name: `S${season}E${episode}`, item: `/tv/${slug}/episode/${season}/${episode}` }
          ]} />
        </div>

        {/* Episode Still Image */}
        {still && (
          <div className="mb-6">
            <img
              src={still}
              alt={episodeTitle}
              className="w-full rounded-lg border border-zinc-800"
            />
          </div>
        )}

        {/* Full Content Section */}
        <div className="bg-zinc-900 border border-zinc-800 p-4 mb-6">
          <h2 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500">
              <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
              <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
            </svg>
            محتوى الحلقة
          </h2>
          
          <div className="space-y-6">
            {/* Intro */}
            {ai?.intro && (
              <p className="text-gray-300 text-base leading-relaxed">
                {ai.intro}
              </p>
            )}
            
            {/* Arabic Description */}
            {ai?.desc_ar && (
              <div>
                <p className="text-orange-400 text-base font-semibold mb-2">الوصف بالعربية:</p>
                <p className="text-gray-300 text-base leading-relaxed">
                  {ai.desc_ar}
                </p>
              </div>
            )}
            
            {/* English Description */}
            {ai?.desc_en && (
              <div className="mt-4 pt-4 border-t border-zinc-700">
                <p className="text-orange-400 text-base font-semibold mb-2">English Description:</p>
                <p className="text-gray-300 text-base leading-relaxed" dir="ltr">
                  {ai.desc_en}
                </p>
              </div>
            )}
            
            {/* Opinion Arabic */}
            {ai?.opinion_ar && (
              <div className="mt-4 pt-4 border-t border-zinc-700">
                <p className="text-orange-400 text-base font-semibold mb-1">رأي توميتو (عربي):</p>
                <p className="text-gray-300 text-base leading-relaxed">
                  {ai.opinion_ar}
                </p>
              </div>
            )}
            
            {/* Opinion English */}
            {ai?.opinion_en && (
              <div className="mt-4 pt-4 border-t border-zinc-700">
                <p className="text-orange-400 text-base font-semibold mb-1">رأي توميتو (English):</p>
                <p className="text-gray-300 text-base leading-relaxed" dir="ltr">
                  {ai.opinion_en}
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
          </div>
        </div>

        {/* FAQ Section */}
        {ai?.faq && ai.faq.length > 0 && (
          <div className="bg-zinc-900 border border-zinc-800 p-4 mb-6">
            <h2 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500">
                <circle cx="12" cy="12" r="10"/>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
              الأسئلة الشائعة
            </h2>
            <div className="space-y-3">
              {ai.faq.map((item: any, index: number) => (
                <div key={index} className="border-b border-zinc-700 pb-3 last:border-0">
                  {/* Arabic FAQ */}
                  <h3 className="text-white font-semibold mb-2">{item.q}</h3>
                  <p className="text-gray-300 text-sm leading-relaxed mb-3">{item.a}</p>
                  
                  {/* English FAQ */}
                  {item.q_en && item.a_en && (
                    <div className="bg-zinc-800/30 rounded p-3 mt-2 border border-zinc-700/50" dir="ltr">
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
  );
}
