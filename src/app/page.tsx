import { getTMDBData, getDetails } from "@/lib/tmdb";
import { cookies } from "next/headers";
import { getHomeContent } from "@/lib/home-content";
import NewAd from "@/components/NewAd";
import { Metadata } from "next";
import Script from "next/script";
import fs from "fs";
import path from "path";
import HeroCarousel from "@/components/HeroCarousel";
import PosterImg from "@/components/PosterImg";


const pageTranslations: Record<string, any> = {
  ar: {
    newsBadge: "آخر الأخبار",
    newsText: "مرحباً بكم في توميتو — موقعكم الأول لمشاهدة وتحميل أحدث الأفلام والمسلسلات مترجمة بجودة عالية HD اون لاين بدون إعلانات",
    exploreBtn: "تصفح وإكتشف",
    allMovies: "جميع الأفلام",
    allSeries: "جميع المسلسلات",
    horror: "رعب وإثارة",
    action: "أكشن وإثارة",
    watchMore: "مشاهدة المزيد",
    sections: {
      "خيال علمي ومغامرة": "خيال علمي ومغامرة",
      "دراما": "دراما",
      "كوميديا": "كوميديا",
      "عائلي": "عائلي",
      "جريمة": "جريمة",
      "مغامرة": "مغامرة",
      "فانتازيا": "فانتازيا",
      "رسوم متحركة": "رسوم متحركة",
      "إثارة": "إثارة",
      "غموض": "غموض",
      "رومنسية": "رومنسية",
      "تاريخ وحرب": "تاريخ وحرب"
    }
  },
  en: {
    newsBadge: "Latest News",
    newsText: "Welcome to Tomito — Your premier site to watch and download the latest movies & series in HD without ads",
    exploreBtn: "Explore",
    allMovies: "All Movies",
    allSeries: "All Series",
    horror: "Horror & Thriller",
    action: "Action & Thriller",
    watchMore: "Watch More",
    sections: {
      "خيال علمي ومغامرة": "Sci-Fi & Adventure",
      "دراما": "Drama",
      "كوميديا": "Comedy",
      "عائلي": "Family",
      "جريمة": "Crime",
      "مغامرة": "Adventure",
      "فانتازيا": "Fantasy",
      "رسوم متحركة": "Animation",
      "إثارة": "Thriller",
      "غموض": "Mystery",
      "رومنسية": "Romance",
      "تاريخ وحرب": "History & War"
    }
  },
  fr: {
    newsBadge: "Dernières Nouvelles",
    newsText: "Bienvenue sur Tomito - Votre site principal pour regarder et télécharger les derniers films et séries en HD sans publicité",
    exploreBtn: "Explorer",
    allMovies: "Tous les films",
    allSeries: "Toutes les séries",
    horror: "Horreur et Thriller",
    action: "Action et Thriller",
    watchMore: "Voir plus",
    sections: {
      "خيال علمي ومغامرة": "Sci-Fi & Aventure",
      "دراما": "Drame",
      "كوميديا": "Comédie",
      "عائلي": "Famille",
      "جريمة": "Crime",
      "مغامرة": "Aventure",
      "فانتازيا": "Fantaisie",
      "رسوم متحركة": "Animation",
      "إثارة": "Thriller",
      "غموض": "Mystère",
      "رومنسية": "Romance",
      "تاريخ وحرب": "Histoire et Guerre"
    }
  },
  es: {
    newsBadge: "Últimas Noticias",
    newsText: "Bienvenido a Tomito: su sitio principal para ver y descargar las últimas películas y series HD sin anuncios",
    exploreBtn: "Explorar",
    allMovies: "Todas las películas",
    allSeries: "Todas las series",
    horror: "Horror y Suspenso",
    action: "Acción y Suspenso",
    watchMore: "Ver Más",
    sections: {
      "خيال علمي ومغامرة": "Ciencia Ficción y Avent.",
      "دراما": "Drama",
      "كوميديا": "Comedia",
      "عائلي": "Familia",
      "جريمة": "Crimen",
      "مغامرة": "Aventura",
      "فانتازيا": "Fantasía",
      "رسوم متحركة": "Animación",
      "إثارة": "Suspenso",
      "غموض": "Misterio",
      "رومنسية": "Romance",
      "تاريخ وحرب": "Historia y Guerra"
    }
  }
};

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: "Tomito |توميتو مشاهدة وتحميل الأفلام والمسلسلات مترجمة بجودة 4K بدون إعلانات",
    description: "توميتو هو موقعك الأول لمشاهدة وتحميل أحدث الأفلام والمسلسلات من جميع أنحاء العالم مترجمة بجودة عالية HD و 4K بدون إعلانات مزعجة. استمتع بمشاهدة أفلام الأكشن والدراما والكوميديا والرعب والخيال العلمي والمسلسلات الحصرية أون لاين مجاناً. مكتبة ضخمة تشمل الأفلام الأمريكية والهندية والآسيوية والتركية والعربية والأوروبية والفيتنامية والكورية والأنمي الياباني والكوري. جميع الأنواع متوفرة: أفلام رعب، أفلام أكشن، أفلام دراما، أفلام كوميديا، أفلام رومانسية، أفلام خيال علمي، أفلام مغامرة، أفلام جريمة، أفلام إثارة، أفلام فانتازيا، أفلام تاريخية، أفلام حرب، أفلام عائلية، أفلام رسوم متحركة، أفلام غموض، مسلسلات تركية، مسلسلات كورية، مسلسلات عربية، مسلسلات أمريكية، مسلسلات هندية، مسلسلات آسيوية، مسلسلات أوروبية، أنمي، أفلام فيتنامية. جودات متعددة للمشاهدة والتحميل: 480p, 720p, 1080p, 4K, BluRay, WEB-DL, HD, FHD, UHD, HDR, Dolby Vision, HDTV, DVDRip, BRRip, x264, x265, HEVC, 1080p BluRay, 720p WEB-DL, 480p HDTV.",
    keywords: "أفلام أون لاين, مسلسلات مترجمة, مشاهدة أفلام, تحميل مسلسلات, أفلام عربي, أفلام هوليود, مسلسلات تركية, أفلام بدون إعلانات, توميتو, tomito xyz, أفلام أمريكية, أفلام هندية, أفلام آسيوية, أفلام تركية, أفلام عربية, أفلام أوروبية, أفلام فيتنامية, أفلام كورية, أنمي, مسلسلات كورية, مسلسلات عربية, مسلسلات أمريكية, مسلسلات هندية, أفلام رعب, أفلام أكشن, أفلام دراما, أفلام كوميديا, أفلام رومانسية, أفلام خيال علمي, أفلام مغامرة, أفلام جريمة, أفلام إثارة, أفلام فانتازيا, 480p, 720p, 1080p, 4K, BluRay, WEB-DL, HD, FHD, UHD, HDR, Dolby Vision, HDTV, DVDRip, BRRip, x264, x265, HEVC",
    alternates: {
      canonical: "https://tomito.xyz",
    },
    openGraph: {
      title: "Tomito |توميتو مشاهدة وتحميل الأفلام والمسلسلات مترجمة بجودة 4K بدون إعلانات",
      description: "توميتو هو موقعك الأول لمشاهدة وتحميل أحدث الأفلام والمسلسلات من جميع أنحاء العالم مترجمة بجودة عالية HD و 4K بدون إعلانات مزعجة. مكتبة ضخمة تشمل الأفلام الأمريكية والهندية والآسيوية والتركية والعربية والأوروبية والفيتنامية والكورية والأنمي. جودات متعددة: 480p, 720p, 1080p, 4K, BluRay, WEB-DL.",
      url: "https://tomito.xyz",
      siteName: "توميتو",
      images: [
        {
          url: "https://tomito.xyz/background.jpeg",
          width: 1200,
          height: 630,
        },
      ],
      locale: "ar_AR",
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: "Tomito |توميتو مشاهدة وتحميل الأفلام والمسلسلات مترجمة بجودة 4K بدون إعلانات",
      description: "توميتو هو موقعك الأول لمشاهدة وتحميل أحدث الأفلام والمسلسلات من جميع أنحاء العالم مترجمة بجودة عالية HD و 4K بدون إعلانات مزعجة. مكتبة ضخمة تشمل الأفلام الأمريكية والهندية والآسيوية والتركية والعربية والأوروبية والفيتنامية والكورية والأنمي. جودات متعددة: 480p, 720p, 1080p, 4K, BluRay, WEB-DL.",
      images: ["https://tomito.xyz/background.jpeg"],
    },
  };
}


function CardItem({ item, getLink, getAlt, getPoster }: any) {
  const posterUrl = getPoster(item);
  return (
    <div className="tc-small-box">
      <a href={getLink(item)} title={getAlt(item)}>
        <div className="tc-poster">
          {posterUrl && <PosterImg src={posterUrl} alt={getAlt(item)} />}
        </div>
        <ul className="tc-li-list">
          {item.genres?.[0] && <li>{item.genres[0]}</li>}
          {item.rating && (
            <li className="tc-imdb-rating">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" /></svg>
              {item.rating?.toFixed?.(1) || item.rating}
            </li>
          )}
        </ul>
        <h3 className="tc-card-title">{item.title || item.title_ar}</h3>
      </a>
    </div>
  );
}

function SidebarItem({ item, getLink, getAlt, getPoster }: any) {
  const posterUrl = getPoster(item);
  return (
    <div className="tc-aside-post">
      <a href={getLink(item)}>
        <div className="tc-aside-poster">
          {posterUrl && <PosterImg src={posterUrl} alt={getAlt(item)} />}
        </div>
        <div className="tc-aside-info">
          <h3>{item.title || item.title_ar}</h3>
          {item.rating && (
            <span className="tc-aside-rating">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" /></svg>
              {item.rating?.toFixed?.(1) || item.rating}
            </span>
          )}
        </div>
      </a>
    </div>
  );
}

function getCarouselData() {
  try {
    const carouselFilePath = path.join(process.cwd(), "data", "carousel_data.json");
    if (fs.existsSync(carouselFilePath)) {
      const rawData = fs.readFileSync(carouselFilePath, "utf-8");
      return JSON.parse(rawData);
    }
    return [];
  } catch (error) {
    console.error("Error loading carousel data:", error);
    return [];
  }
}

async function enrichCarouselWithLiveRatings(carouselItems: any[]) {
  try {
    const enriched = await Promise.all(
      carouselItems.map(async (item) => {
        try {
          const tmdbDetails = await getDetails(String(item.tmdb_id), item.folder);
          const liveRating = tmdbDetails?.ar?.vote_average ?? tmdbDetails?.en?.vote_average;
          if (typeof liveRating === "number" && liveRating > 0) {
            return { ...item, vote_average: liveRating };
          }
          return item;
        } catch (error) {
          console.error(`Failed to fetch live rating for ${item.tmdb_id}:`, error);
          return item;
        }
      })
    );
    return enriched;
  } catch (error) {
    console.error("Error enriching carousel with live ratings:", error);
    return carouselItems;
  }
}

export default async function Home() {
  const cookieStore = await cookies();
  const locale = cookieStore.get("NEXT_LOCALE")?.value || "ar";
  const t = pageTranslations[locale] || pageTranslations.ar;

  const localContent = getHomeContent();
  const carouselData = getCarouselData();
  const enrichedCarouselData = await enrichCarouselWithLiveRatings(carouselData);

  console.log("First 5 carousel items in page.tsx:");
  localContent.slice(0, 5).forEach((item, i) => {
    console.log(`${i + 1}. ${item.title} - timestamp: ${item.timestamp}`);
  });

  const sortedAll = localContent; // Already sorted by timestamp in getHomeContent()

  const movies = sortedAll.filter((item: any) => item.folder === 'movie');
  const series = sortedAll.filter((item: any) => item.folder === 'tv');

  const carouselItems = sortedAll.slice(0, 20);

  // Hero carousel with specific IDs
  const heroIds = [1719380, 969681, 1368337, 1081003, 1212763, 30984, 1263532, 300480];
  const heroItems = sortedAll.filter((item: any) => heroIds.includes(item.tmdb_id));

  const getDynamicNewsText = (items: any[], loc: string) => {
    return items.slice(0, 10).map((item: any) => {
      const isTV = item.folder === 'tv';
      const title = item.title || item.title_ar;
      if (loc === 'ar') return `🔥 شاهد الآن ${isTV ? 'مسلسل' : 'فيلم'} "${title}" ترند جديد`;
      if (loc === 'en') return `🔥 Trending now: ${isTV ? 'Series' : 'Movie'} "${title}" - Watch in HD!`;
      if (loc === 'fr') return `🔥 Tendance: ${isTV ? 'Série' : 'Film'} "${title}" - Regardez en HD!`;
      if (loc === 'es') return `🔥 Tendencia: ${isTV ? 'Serie' : 'Película'} "${title}" - ¡Míralo en HD!`;
      return `🔥 شاهد الآن ${isTV ? 'مسلسل' : 'فيلم'} "${title}"`;
    }).join('  ✦  ');
  };
  const dynamicNewsText = getDynamicNewsText(carouselItems, locale);

  const WIDE_LIMIT = 10;
  const SIDEBAR_LIMIT = 7;
  const GRID_LIMIT = 18;

  // Custom user categories
  const allMovies = movies;
  const allSeries = series;
  // TMDB Genre IDs Mapping:
  // Action (حركة): 28 | Adventure (مغامرة): 12 | Animation (رسوم متحركة): 16 | Comedy (كوميديا): 35
  // Crime (جريمة): 80 | Drama (دراما): 18 | Family (عائلي): 10751 | Fantasy (فانتازيا): 14
  // History (تاريخ): 36 | Horror (رعب): 27 | Mystery (غموض): 9648 | Romance (رومنسية): 10749
  // Science Fiction (خيال علمي): 878 | Thriller (إثارة): 53 | War (حرب): 10752

  const actionMovies = [...movies, ...series].filter((m: any) => m.genres?.includes('حركة') || m.genre_ids?.includes(28));
  const horrorMovies = [...movies, ...series].filter((m: any) => m.genres?.includes('رعب') || m.genre_ids?.includes(27));

  const fullSections = [
    { title: "خيال علمي ومغامرة", items: movies.filter((m: any) => m.genres?.includes('خيال علمي') || m.genre_ids?.includes(878) || m.genre_ids?.includes(12)), link: "/movie" },
    { title: "دراما", items: movies.filter((m: any) => m.genres?.includes('دراما') || m.genre_ids?.includes(18)), link: "/movie" },
    { title: "كوميديا", items: movies.filter((m: any) => m.genres?.includes('كوميديا') || m.genre_ids?.includes(35)), link: "/movie" },
    { title: "عائلي", items: movies.filter((m: any) => m.genres?.includes('عائلي') || m.genre_ids?.includes(10751)), link: "/movie" },
    { title: "جريمة", items: movies.filter((m: any) => m.genres?.includes('جريمة') || m.genre_ids?.includes(80)), link: "/movie" },
    { title: "مغامرة", items: movies.filter((m: any) => m.genres?.includes('مغامرة') || m.genre_ids?.includes(12)), link: "/movie" },
    { title: "فانتازيا", items: movies.filter((m: any) => m.genres?.includes('فانتازيا') || m.genre_ids?.includes(14)), link: "/movie" },
    { title: "رسوم متحركة", items: movies.filter((m: any) => m.genres?.includes('رسوم متحركة') || m.genre_ids?.includes(16)), link: "/movie" },
    { title: "إثارة", items: [...movies, ...series].filter((m: any) => m.genres?.includes('إثارة') || m.genre_ids?.includes(53)), link: "/" },
    { title: "غموض", items: movies.filter((m: any) => m.genres?.includes('غموض') || m.genre_ids?.includes(9648)), link: "/movie" },
    { title: "رومنسية", items: movies.filter((m: any) => m.genres?.includes('رومنسية') || m.genre_ids?.includes(10749)), link: "/movie" },
    { title: "تاريخ وحرب", items: movies.filter((m: any) => m.genres?.includes('تاريخ') || m.genres?.includes('حرب') || m.genre_ids?.includes(36) || m.genre_ids?.includes(10752)), link: "/movie" },
  ].filter(s => s.items.length > 0);

  // Helpers
  const getPoster = (item: any) => {
    if (item.poster && item.poster !== '') return item.poster.replace('https://image.tmdb.org/t/p/w500', '/t/p/w500');
    if (item.poster_path) return `/t/p/w500${item.poster_path}`;
    return null;
  };
  const getAlt = (item: any) => {
    const prefix = item.folder === 'tv' ? 'مسلسل' : 'فيلم';
    return `${prefix} ${item.title || item.title_ar || ''} مترجم اون لاين`;
  };
  const getLink = (item: any) => `/${item.folder || 'movie'}/${item.slug}`;

  return (
    <div className="bg-background text-foreground min-h-screen" style={{ paddingTop: '64px' }}>

      {/* Schema.org JSON-LD for WebSite */}
      <Script
        id="website-schema"
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "توميتو",
            "alternateName": "توميتو | أكبر مكتبة أفلام ومسلسلات وأنمي مجاناً بدون إعلانات - Tomito",
            "url": "https://tomito.xyz",
            "description": "توميتو هو موقعك الأول لمشاهدة وتحميل أحدث الأفلام والمسلسلات من جميع أنحاء العالم مترجمة بجودة عالية مجانا HD و 4K بدون إعلانات مزعجة. مكتبة ضخمة تشمل أكثر من مليون إنتاج الأفلام والمسلسلات الأمريكية والهندية والآسيوية والتركية والعربية والأوروبية والفيتنامية والكورية والأنمي. جودات متعددة للمشاهدة والتحميل: 480p, 720p, 1080p, 4K, BluRay, WEB-DL.",
            "potentialAction": {
              "@type": "SearchAction",
              "target": {
                "@type": "EntryPoint",
                "urlTemplate": "https://tomito.xyz/search?q={search_term_string}"
              },
              "query-input": "required name=search_term_string"
            }
          })
        }}
      />


      {/* ═══════ HERO CAROUSEL (New Full-Screen with YouTube Trailer) ═══════ */}
      {enrichedCarouselData.length > 0 && (
        <HeroCarousel items={enrichedCarouselData} locale={locale} />
      )}

      {/* ═══════ NEWS BAR ═══════ */}
      <div className="tc-news-bar">
        <div className="tc-news-bar-inner">
          <div className="tc-news-content">
            <span className="tc-news-badge" style={{ zIndex: 10 }}>{t.newsBadge}</span>
            <div className="tc-news-ticker-container">
              <div className="tc-news-ticker-animated">
                {dynamicNewsText}
              </div>
            </div>
          </div>
          <div className="tc-news-links">
            <a href="/movie" className="tc-explore-btn">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" /></svg>
              {t.exploreBtn}
            </a>
          </div>
        </div>
      </div>


      {/* ═══════ SECTION 1: جميع الأفلام + جميع المسلسلات (Sidebar) ═══════ */}
      <section className="tc-two-section">
        <div className="tc-container">
          <div className="tc-wide">
            <div className="tc-title-box">
              <div className="tc-title-right">
                <h2>{t.allMovies}</h2>
              </div>
              <a href="/movie" className="tc-more-link">{t.watchMore}</a>
            </div>
            <div className="tc-grid-5">
              {allMovies.slice(0, WIDE_LIMIT).map((item: any, i: number) => (
                <CardItem key={`${item.slug || 'item'}-${i}`} item={item} getLink={getLink} getAlt={getAlt} getPoster={getPoster} />
              ))}
            </div>
          </div>

          <aside className="tc-sidebar">
            <div className="tc-title-box">
              <div className="tc-title-right">
                <h2>{t.allSeries}</h2>
              </div>
              <a href="/tv" className="tc-more-link">{t.watchMore}</a>
            </div>
            <div className="tc-aside-posts">
              {allSeries.slice(0, SIDEBAR_LIMIT).map((item: any, i: number) => (
                <SidebarItem key={`${item.slug || 'item'}-${i}`} item={item} getLink={getLink} getAlt={getAlt} getPoster={getPoster} />
              ))}
            </div>
          </aside>
        </div>
      </section>

      {/* ═══════ SECTION 2: أكشن وإثارة + رعب وإثارة (Reversed) ═══════ */}
      <section className="tc-two-section tc-reversed">
        <div className="tc-container">
          <aside className="tc-sidebar">
            <div className="tc-title-box">
              <div className="tc-title-right">
                <h2>{t.horror}</h2>
              </div>
              <a href="/movie" className="tc-more-link">{t.watchMore}</a>
            </div>
            <div className="tc-aside-posts">
              {horrorMovies.slice(0, SIDEBAR_LIMIT).map((item: any, i: number) => (
                <SidebarItem key={`${item.slug || 'item'}-${i}`} item={item} getLink={getLink} getAlt={getAlt} getPoster={getPoster} />
              ))}
            </div>
          </aside>

          <div className="tc-wide">
            <div className="tc-title-box">
              <div className="tc-title-right">
                <h2>{t.action}</h2>
              </div>
              <a href="/movie" className="tc-more-link">{t.watchMore}</a>
            </div>
            <div className="tc-grid-5">
              {actionMovies.slice(0, WIDE_LIMIT).map((item: any, i: number) => (
                <CardItem key={`${item.slug || 'item'}-${i}`} item={item} getLink={getLink} getAlt={getAlt} getPoster={getPoster} />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════ FULL-WIDTH SECTIONS (Dynamic mapped from original categories) ═══════ */}
      {fullSections.map((section, idx) => (
        <section key={idx} className="tc-full-section">
          <div className="tc-container">
            <div className="tc-title-box">
              <div className="tc-title-right">
                <h2>{t.sections[section.title] || section.title}</h2>
              </div>
              <a href={section.link} className="tc-more-link">{t.watchMore}</a>
            </div>
            <div className="tc-grid-6">
              {section.items.slice(0, GRID_LIMIT).map((item: any, i: number) => (
                <CardItem key={`${item.slug || 'item'}-${i}`} item={item} getLink={getLink} getAlt={getAlt} getPoster={getPoster} />
              ))}
            </div>
          </div>
        </section>
      ))}

    </div>
  );
}
