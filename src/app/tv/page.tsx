import { Metadata } from "next";
import { getContentByType, ContentIndexEntry } from "@/lib/content";

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: "مسلسلات — توميتو",
    description: "مشاهدة وتحميل أفضل المسلسلات مترجمة باحترافية وبدون إعلانات.",
  };
}

export default async function TVPage() {
  const items = getContentByType("tv");

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
             جميع <span className="text-primary">المسلسلات</span>
          </h1>
        </div>
        <p className="text-muted max-w-2xl text-lg font-medium leading-relaxed border-r-2 border-white/5 pr-6">
           اكتشف عالم المسلسلات مع أفضل المسلسلات المختارة بعناية. تجربة مشاهدة فريدة بجودة 4K وبدون إعلانات.
        </p>
      </header>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6 px-6 md:px-12 lg:px-20">
        {items.map((item: ContentIndexEntry, i: number) => {
          const title = item.title_ar || item.title;
          
          return (
            <div key={`tv-${item.tmdb_id}`} style={{ animationDelay: `${i * 30}ms` }} className="fade-in-up">
              <a 
                href={`/tv/${item.slug}`}
                className="movie-card"
              >
                <img 
                  src={item.poster || ''} 
                  alt={title} 
                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" 
                  loading="lazy"
                />
                <div className="card-info bg-gradient-to-t from-black via-black/60 to-transparent pt-12">
                   <h3 className="text-xs font-bold text-white leading-tight line-clamp-2 mb-1">{title}</h3>
                   <div className="flex items-center gap-2">
                      <span className="text-[9px] text-primary font-black">⭐ {item.rating?.toFixed(1)}</span>
                      <span className="text-[9px] text-white/40">مسلسل • {item.year}</span>
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
