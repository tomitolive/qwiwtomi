import re

def rewrite_page(filepath, type):
    with open(filepath, 'r') as f:
        content = f.read()

    # Find the return statement
    return_idx = content.find("  return (")
    if return_idx == -1:
        print(f"Could not find return statement in {filepath}")
        return

    header_code = content[:return_idx]
    
    # Watch and trailer URLs
    if type == 'movie':
        watch_btn_text = "مشاهدة الآن"
        title_var = "titleAr"
        episodes_info = ""
    else:
        watch_btn_text = "مشاهدة جميع الحلقات"
        title_var = "titleAr"
        episodes_info = """
            <div className="border border-white/10 bg-white/[0.01] p-6 lg:p-10">
              <div className="border-l-4 border-primary pl-4 mb-8">
                 <h2 className="text-2xl lg:text-3xl font-black">المواسم ({data.number_of_seasons})</h2>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {data.seasons?.map((season: any, i: number) => (
                  <div key={season.id} className="group border border-white/5 bg-black overflow-hidden relative" style={{ animationDelay: `${i * 50}ms` }}>
                    <div className="aspect-[2/3] w-full">
                      <img
                        src={season.poster_path ? `https://image.tmdb.org/t/p/w300${season.poster_path}` : poster}
                        alt={season.name}
                        className="w-full h-full object-cover grayscale opacity-80 group-hover:grayscale-0 group-hover:opacity-100 transition-all duration-500"
                      />
                    </div>
                    <div className="absolute bottom-0 inset-x-0 bg-background/90 p-3 border-t border-white/10 backdrop-blur-md">
                      <h4 className="text-xs font-bold text-white truncate mb-1">{season.name}</h4>
                      <p className="text-[10px] text-primary font-bold uppercase tracking-widest">{season.episode_count} حلقة</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
"""

    brutalist_return = """  return (
    <div className="min-h-screen bg-[#050505] text-white font-main selection:bg-primary selection:text-black">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(%sSchema) }}
      />
      
      {/* Brutalist Grid Layout */}
      <main className="max-w-[1600px] mx-auto p-4 md:p-8 pt-24 md:pt-32">
        <div className="mb-8 border-b border-white/10 pb-4">
          <Breadcrumbs items={[
            { name: "الرئيسية", item: "/" },
            { name: "%s", item: "/%s" },
            { name: displayTitle, item: `/%s/${slug}` }
          ]} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-12 auto-rows-auto gap-4 lg:gap-6">
          
          {/* Main Info Block */}
          <div className="md:col-span-8 lg:col-span-9 border border-white/10 bg-[#0a0a0a] relative overflow-hidden flex flex-col justify-between group p-6 lg:p-12 min-h-[50vh] md:min-h-[70vh]">
            <div className="absolute inset-0 opacity-20 group-hover:opacity-30 transition-opacity duration-700" 
                 style={{ backgroundImage: `url(${backdrop || poster})`, backgroundSize: 'cover', backgroundPosition: 'center', mixBlendMode: 'luminosity', filter: 'contrast(1.2)' }}></div>
            <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] via-[#0a0a0a]/80 to-transparent"></div>
            <div className="absolute inset-0 bg-gradient-to-r from-[#0a0a0a] via-[#0a0a0a]/50 to-transparent"></div>
            
            <div className="relative z-10">
              {ai?.intro && (
                <span className="inline-block border border-primary text-primary text-[10px] sm:text-xs font-bold uppercase tracking-[0.2em] px-3 py-1 mb-6 bg-primary/5">
                  {ai.intro}
                </span>
              )}
              <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-8xl font-black font-heading leading-[1.1] tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white to-white/60 mb-2">
                {titleAr}
              </h1>
              {titleEn && titleEn !== titleAr && (
                <h2 className="text-xl md:text-3xl font-black text-white/20 uppercase tracking-widest font-sans mb-8">
                  {titleEn}
                </h2>
              )}
              
              <div className="flex flex-wrap items-center gap-3 mb-10">
                <span className="border border-white/20 bg-white/5 px-4 py-1.5 text-xs font-bold uppercase tracking-wider">{year}</span>
                <span className="border border-white/20 bg-white/5 px-4 py-1.5 text-xs font-bold flex items-center gap-2">
                  <span className="text-primary">★</span> {rating}
                </span>
                <span className="border border-primary/50 text-primary px-4 py-1.5 text-xs font-black uppercase tracking-widest bg-primary/10">4K ULTRA HD</span>
              </div>
              
              <div className="flex flex-wrap gap-2 mb-12">
                {data.genres?.map((g: any) => (
                  <span key={g.id} className="border border-white/10 px-3 py-1 text-[10px] font-bold text-white/60 uppercase tracking-widest hover:bg-white hover:text-black transition-colors cursor-default">
                    {g.name}
                  </span>
                ))}
              </div>
            </div>

            <div className="relative z-10 flex flex-col sm:flex-row gap-4 border-t border-white/10 pt-8 mt-auto">
              <ProtectedLink encodedUrl={watchUrlEncoded} className="bg-primary hover:bg-white text-black font-black uppercase tracking-widest px-8 py-5 text-sm sm:text-base flex items-center justify-center gap-3 transition-colors duration-300">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg>
                {watchButton}
              </ProtectedLink>
              <button className="border border-white/20 hover:border-white bg-transparent text-white font-bold uppercase tracking-widest px-8 py-5 text-sm flex items-center justify-center gap-3 transition-colors duration-300">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>
                تحميل
              </button>
            </div>
          </div>
          
          {/* Poster Block */}
          <div className="md:col-span-4 lg:col-span-3 border border-white/10 bg-[#0a0a0a] p-4 hidden md:flex items-center justify-center relative overflow-hidden group">
            <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500 z-10 pointer-events-none"></div>
            <img 
              src={poster} 
              alt={displayTitle} 
              className="w-full h-full object-cover border border-white/5 grayscale saturate-50 contrast-125 group-hover:grayscale-0 group-hover:saturate-100 transition-all duration-700 aspect-[2/3]" 
            />
          </div>

          {/* Description Block */}
          <div className="md:col-span-12 lg:col-span-8 border border-white/10 bg-[#0a0a0a] p-6 lg:p-10">
            <div className="border-l-4 border-primary pl-4 mb-8">
              <h2 className="text-xl font-black uppercase tracking-widest text-white/50">قصة %s</h2>
            </div>
            <div className="prose prose-invert prose-p:leading-loose prose-p:text-white/70 prose-p:text-sm md:prose-p:text-base max-w-none text-justify">
              <p>{overview}</p>
              {extraDesc && <p className="text-primary/70 mt-6 font-medium">{extraDesc}</p>}
              {ai?.outro && <p className="text-white/40 italic mt-4 text-xs">{ai.outro}</p>}
            </div>
          </div>

          {/* Quick Stats Sidebar */}
          <div className="md:col-span-12 lg:col-span-4 border border-white/10 bg-[#0a0a0a] p-6 lg:p-10 grid grid-cols-2 gap-4 auto-rows-max">
            <div className="col-span-2 border-b border-primary w-fit pr-4 mb-4 pb-2">
               <h3 className="text-sm font-black uppercase tracking-widest text-primary">معلومات</h3>
            </div>
            
            <div className="border border-white/5 bg-white/[0.02] p-4 flex flex-col justify-center gap-2 hover:bg-white/5 transition-colors">
              <span className="text-white/30 text-[10px] uppercase font-bold tracking-widest">الإصدار</span>
              <span className="text-white font-black text-lg">{year}</span>
            </div>
            <div className="border border-white/5 bg-white/[0.02] p-4 flex flex-col justify-center gap-2 hover:bg-white/5 transition-colors">
              <span className="text-white/30 text-[10px] uppercase font-bold tracking-widest">اللغة</span>
              <span className="text-white font-black text-lg">العربية</span>
            </div>
            <div className="col-span-2 border border-white/5 bg-primary/10 p-4 flex flex-col justify-center gap-2 border-l-2 border-l-primary">
              <span className="text-primary/70 text-[10px] uppercase font-bold tracking-widest">تقييم توميتو</span>
              <span className="text-white font-black text-2xl">{rating} <span className="text-sm opacity-50 font-medium">/ 10</span></span>
            </div>
          </div>

          {/* Trailer Block */}
          {trailer ? (
            <div className="md:col-span-12 border border-white/10 bg-black relative overflow-hidden group min-h-[40vh] flex items-center justify-center p-4">
              <div className="w-full max-w-4xl border border-white/10 video-container shadow-2xl">
                <iframe
                  src={`https://www.youtube.com/embed/${trailer.key}?rel=0&showinfo=0&autoplay=0`}
                  title={`${displayTitle} Trailer`}
                  allowFullScreen
                  className="w-full aspect-video grayscale group-hover:grayscale-0 transition-all duration-700"
                ></iframe>
              </div>
            </div>
          ) : (
            <div className="md:col-span-12 border border-white/10 bg-white/[0.02] p-8 flex items-center justify-center">
               <ProtectedLink
                  encodedUrl={trailerSearchUrlEncoded}
                  className="flex items-center gap-6 p-6 border border-white/10 hover:bg-white hover:text-black transition-colors group w-full max-w-2xl justify-between"
                >
                  <div>
                    <h3 className="font-black text-xl mb-1 uppercase tracking-widest">التريلر الرسمي</h3>
                    <p className="text-sm opacity-50 font-mono">{titleAr || titleEn} {year} Trailer</p>
                  </div>
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor" className="text-red-500 group-hover:text-black transition-colors">
                    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                  </svg>
                </ProtectedLink>
            </div>
          )}

          %s

          {/* AI Opinion Block */}
          {ai?.opinion && (
            <div className="md:col-span-12 border-2 border-primary bg-primary/5 p-8 lg:p-12 relative overflow-hidden">
               <span className="absolute -right-8 -top-12 text-[200px] leading-none opacity-5 text-primary select-none font-serif">"</span>
               <div className="relative z-10 max-w-4xl mx-auto text-center">
                 <h3 className="text-primary font-black uppercase tracking-widest text-xs mb-6 inline-block border border-primary/20 px-4 py-2">رأي توميتو</h3>
                 <p className="text-xl md:text-3xl font-black italic text-white/90 leading-relaxed md:leading-relaxed">
                   {ai.opinion}
                 </p>
               </div>
            </div>
          )}

          {/* FAQ Block */}
          <div className="md:col-span-12 border border-white/10 bg-[#0a0a0a] p-6 lg:p-12">
            <div className="border-l-4 border-primary pl-4 mb-10">
              <h2 className="text-2xl font-black uppercase tracking-widest text-white/50">الأسئلة الشائعة</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8">
              {(ai?.faq && ai.faq.length > 0 ? ai.faq : [
                { q: `متى يتوفر %s على موقع توميتو؟`, a: `%s متاح الآن للمشاهدة والتحميل مباشرةً على موقع توميتو بجودة عالية مترجماً إلى العربية.` },
                { q: `هل يمكنني تحميله بجودة عالية؟`, a: `نعم، يمكنك التحميل وتتوفر جودات متعددة تصل إلى Full HD و 4K.` }
              ]).map((item: any, idx: number) => (
                <div key={idx} className="border border-white/5 bg-white/[0.01] p-6 hover:border-white/20 transition-colors">
                  <h3 className="text-base font-bold text-white mb-4 flex items-start gap-4">
                    <span className="text-primary font-black">/</span>
                    {item.q || item.question}
                  </h3>
                  <p className="text-white/50 text-sm leading-relaxed pr-6">
                    {item.a || item.answer}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Similar Content Block */}
          {localSimilar.length > 0 && (
            <div className="md:col-span-12 border border-white/10 bg-[#0a0a0a] p-6 lg:p-12">
              <div className="border-l-4 border-primary pl-4 mb-10 border-b border-b-white/5 pb-4 flex items-end justify-between">
                <h2 className="text-2xl font-black uppercase tracking-widest text-white/50">أعمال مشابهة</h2>
              </div>
              
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {localSimilar.map((item, i) => (
                  <a key={item.tmdb_id} href={`/%s/${item.slug}`} className="group block border border-white/10 bg-black overflow-hidden relative" style={{ animationDelay: `${i * 50}ms` }}>
                    <div className="aspect-[2/3] w-full">
                      <img
                        src={item.poster?.replace('https://image.tmdb.org/t/p/w500', '/t/p/w500') || `/t/p/w500${item.poster}`}
                        alt={item.title_ar || item.title}
                        loading="lazy"
                        className="w-full h-full object-cover grayscale opacity-70 group-hover:grayscale-0 group-hover:opacity-100 transition-all duration-700"
                      />
                    </div>
                    <div className="absolute inset-x-0 bottom-0 p-3 bg-gradient-to-t from-black via-black/80 to-transparent pt-12 transform translate-y-2 group-hover:translate-y-0 transition-transform duration-500">
                      <h3 className="text-xs font-bold text-white truncate mb-1">{item.title_ar || item.title}</h3>
                      <div className="flex items-center justify-between">
                         <span className="text-[9px] text-white/40 font-mono">{item.year}</span>
                         <span className="text-[9px] text-primary font-bold">{item.rating} ★</span>
                      </div>
                    </div>
                  </a>
                ))}
              </div>
            </div>
          )}

        </div>
      </main>
    </div>
  );
}
"""
    
    if type == "movie":
        format_args = (
            "movie", "أفلام", "movie", "movie", watch_btn_text, "الفيلم", 
            "فيلم", "الفيلم", "movie"
        )
    else:
        format_args = (
            "tv", "مسلسلات", "tv", "tv", watch_btn_text, "المسلسل", 
            "مسلسل", "المسلسل", "tv"
        )
        
    new_content = header_code + (brutalist_return % format_args).replace("%s", episodes_info, 1)

    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"Successfully rewritten {filepath}")

rewrite_page("src/app/movie/[slug]/page.tsx", "movie")
rewrite_page("src/app/tv/[slug]/page.tsx", "tv")
