import { Metadata } from "next";
import fs from "fs";
import path from "path";
import { notFound } from "next/navigation";

interface Props {
  params: { slug: string };
}

interface GenreItem {
  id: number;
  title: string;
  title_ar?: string;
  poster_path: string;
  media_type: 'movie' | 'tv';
  vote_average: number;
  release_date?: string;
  first_air_date?: string;
}

interface GenreData {
  name: string;
  name_ar: string;
  description: string;
  items: GenreItem[];
}

const GENRE_AR: Record<string, string> = {
    "action": "أكشن",
    "adventure": "مغامرة",
    "animation": "أنمي",
    "comedy": "كوميديا",
    "crime": "جريمة",
    "documentary": "وثائقي",
    "drama": "دراما",
    "family": "عائلي",
    "fantasy": "خيال",
    "history": "تاريخي",
    "horror": "رعب",
    "music": "موسيقي",
    "mystery": "غموض",
    "romance": "رومانسية",
    "sci-fi": "خيال علمي",
    "tv-movie": "فيلم تلفزيوني",
    "thriller": "إثارة",
    "war": "حربي",
    "western": "غربي",
    "20th-century": "القرن العشرين",
    "20th-century-studios": "ستوديوهات القرن العشرين",
    "70s-cinema": "سينما السبعينات",
    "80s-cinema": "سينما الثمانينات",
    "90s-cinema": "سينما التسعينات",
    "2000s-cinema": "سينما الألفيات",
    "a24": "A24",
    "amazon": "أمازون",
    "amazon-studios": "ستوديوهات أمازون",
    "apple": "آبل",
    "apple-tv": "آبل تي في",
    "blumhouse": "بلومهاوس",
    "canal": "قناة",
    "classics": "كلاسيكيات",
    "columbia-pictures": "كولومبيا بيكتشرز",
    "disney": "ديزني",
    "dreamworks": "دريم ووركس",
    "hbo": "HBO",
    "hulu": "هولو",
    "legendary": "ليجندري",
    "lionsgate": "لايونزغيت",
    "lucasfilm": "لوكاس فيلم",
    "marvel": "مارفل",
    "marvel-studios": "ستوديوهات مارفل",
    "mbc": "MBC",
    "mbc-group-shahid": "MBC شاهد",
    "mbc-studios": "ستوديوهات MBC",
    "mini-series": "مسلسلات قصيرة",
    "miramax": "ميراماكس",
    "movie": "أفلام",
    "new-line": "نيو لاين",
    "new-line-cinema": "نيو لاين سينما",
    "new-releases": "إصدارات جديدة",
    "paramount": "باراماونت",
    "pixar": "بيكسار",
    "reality-talk": "برامج واقع",
    "sony": "سوني",
    "sony-pictures": "سوني بيكتشرز",
    "synergy": "سينرجي",
    "tv-show": "مسلسلات",
    "universal": "يونيفرسال",
    "universal-pictures": "يونيفرسال بيكتشرز",
    "warner-bros": "وارنر براذرز",
};

function getGenreData(slug: string): GenreData | null {
  try {
    const filePath = path.join(process.cwd(), "data", "genre", `${slug}.json`);
    if (!fs.existsSync(filePath)) return null;
    const data = fs.readFileSync(filePath, "utf-8");
    return JSON.parse(data);
  } catch {
    return null;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const genreData = getGenreData(slug);
  const genreName = genreData?.name_ar || GENRE_AR[slug] || slug;
  return {
    title: `أفلام ومسلسلات ${genreName} — توميتو`,
    description: genreData?.description || `مشاهدة وتحميل أفضل أفلام ومسلسلات ${genreName} مترجمة باحترافية وبدون إعلانات.`,
  };
}

export default async function GenrePage({ params }: Props) {
  const { slug } = await params;
  const genreData = getGenreData(slug);
  if (!genreData) notFound();

  const genreName = genreData.name_ar || GENRE_AR[slug] || slug;

  return (
    <div className="bg-background text-foreground min-h-screen pt-32 pb-24 relative overflow-hidden">
      {/* Background Image */}
      <div 
        className="absolute inset-0 z-0"
        style={{ 
          backgroundImage: 'url(\'/background.jpeg\')', 
          backgroundSize: 'cover', 
          backgroundPosition: 'center',
          filter: 'brightness(0.3) saturate(0.7) hue-rotate(220deg) contrast(1.2)',
          opacity: '1.2'
        }}
      />
      {/* Decorative Gradient */}
      <div className="absolute top-0 right-0 w-[50vw] h-[50vh] bg-primary/5 blur-[120px] rounded-full -z-10" />
      <div className="absolute bottom-0 left-0 w-[40vw] h-[40vh] bg-primary/3 blur-[100px] rounded-full -z-10" />

      <header className="px-6 md:px-12 lg:px-20 mb-16 fade-in">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-1.5 h-10 bg-primary rounded-full shadow-[0_0_15px_var(--primary)]" />
          <h1 className="text-4xl md:text-6xl font-black font-heading tracking-tighter">
             تصفح تصنيف: <span className="text-primary">{genreName}</span>
          </h1>
        </div>
        <p className="text-muted max-w-2xl text-lg font-medium leading-relaxed border-r-2 border-white/5 pr-6">
           {genreData.description || `اكتشف عالم ${genreName} مع أفضل الأفلام والمسلسلات المختارة بعناية. تجربة مشاهدة فريدة بجودة 4K وبدون إعلانات.`}
        </p>
      </header>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6 px-6 md:px-12 lg:px-20">
        {genreData.items.map((item: any, i: number) => {
          const type = item.media_type;
          const title = item.title_ar || item.title;
          const slug_raw = title.toLowerCase().replace(/[^a-z0-9 ]/g, '').replace(/\s+/g, '-');
          const itemSlug = `${item.id}-${slug_raw}`;

          return (
            <div key={`${type}-${item.id}`} style={{ animationDelay: `${i * 30}ms` }} className="fade-in-up">
              <a
                href={`/${type}/${itemSlug}`}
                className="movie-card"
              >
                <img
                  src={item.poster_path ? `/t/p/w500/${item.poster_path}` : ''}
                  alt={title}
                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                  loading="lazy"
                />
                <div className="card-info bg-gradient-to-t from-black via-black/60 to-transparent pt-12">
                   <h3 className="text-xs font-bold text-white leading-tight line-clamp-2 mb-1">{title}</h3>
                   <div className="flex items-center gap-2">
                      <span className="text-[9px] text-primary font-black">⭐ {item.vote_average?.toFixed(1)}</span>
                      <span className="text-[9px] text-white/40">{type === 'movie' ? 'فيلم' : 'مسلسل'} • {(item.release_date || item.first_air_date || '').substring(0, 4)}</span>
                   </div>
                </div>
              </a>
            </div>
          );
        })}
      </div>
    </div>
  );
}
