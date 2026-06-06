"use client";
import { useState, useEffect } from "react";

const genresList = [
  // Main genres
  { slug: "action", label: "أكشن", icon: "💥" },
  { slug: "adventure", label: "مغامرة", icon: "🗺️" },
  { slug: "animation", label: "رسوم متحركة", icon: "🎨" },
  { slug: "comedy", label: "كوميدي", icon: "😂" },
  { slug: "crime", label: "جريمة", icon: "🔫" },
  { slug: "documentary", label: "وثائقي", icon: "📽️" },
  { slug: "drama", label: "دراما", icon: "🎭" },
  { slug: "family", label: "عائلي", icon: "👨‍👩‍👧" },
  { slug: "fantasy", label: "خيال", icon: "🧙" },
  { slug: "history", label: "تاريخي", icon: "🏛️" },
  { slug: "horror", label: "رعب", icon: "👻" },
  { slug: "music", label: "موسيقى", icon: "🎵" },
  { slug: "mystery", label: "غموض", icon: "🔍" },
  { slug: "romance", label: "رومانسي", icon: "❤️" },
  { slug: "sci-fi", label: "خيال علمي", icon: "🚀" },
  { slug: "thriller", label: "إثارة", icon: "⚡" },
  { slug: "war", label: "حرب", icon: "⚔️" },
  { slug: "western", label: "غربي", icon: "🤠" },
];

const studiosList = [
  { slug: "netflix", label: "Netflix", icon: "🔴" },
  { slug: "disney-plus", label: "Disney+", icon: "✨" },
  { slug: "hbo", label: "HBO", icon: "🎬" },
  { slug: "amazon", label: "Amazon", icon: "📦" },
  { slug: "apple-tv", label: "Apple TV+", icon: "🍎" },
  { slug: "hulu", label: "Hulu", icon: "🟢" },
  { slug: "marvel", label: "Marvel", icon: "🦸" },
  { slug: "pixar", label: "Pixar", icon: "💡" },
  { slug: "a24", label: "A24", icon: "🎞️" },
  { slug: "dreamworks", label: "DreamWorks", icon: "🌙" },
  { slug: "warner-bros", label: "Warner Bros", icon: "🛡️" },
  { slug: "universal", label: "Universal", icon: "🌍" },
  { slug: "paramount", label: "Paramount", icon: "⛰️" },
  { slug: "sony", label: "Sony", icon: "📺" },
  { slug: "mbc", label: "شاهد MBC", icon: "📡" },
  { slug: "canal", label: "Canal+", icon: "🔵" },
];

const erasList = [
  { slug: "classics", label: "كلاسيكيات", icon: "🎩" },
  { slug: "70s-cinema", label: "سينما الـ 70", icon: "🕺" },
  { slug: "80s-cinema", label: "سينما الـ 80", icon: "🎸" },
  { slug: "90s-cinema", label: "سينما الـ 90", icon: "💿" },
  { slug: "2000s-cinema", label: "سينما الألفية", icon: "💾" },
  { slug: "new-releases", label: "إصدارات جديدة", icon: "🆕" },
  { slug: "mini-series", label: "مسلسلات قصيرة", icon: "⏱️" },
  { slug: "reality-tv", label: "برامج واقعية", icon: "🎤" },
];

export default function GenreModal() {
  const [open, setOpen] = useState(false);

  // Close on Escape key
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  // Prevent body scroll when open
  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  return (
    <>
      {/* Trigger Button */}
      <button
        onClick={() => setOpen(true)}
        className="nav-link flex items-center gap-1.5 active:scale-95"
        style={{ touchAction: 'manipulation' }}
        aria-label="فتح التصنيفات"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <rect x="3" y="3" width="7" height="7" rx="1" />
          <rect x="14" y="3" width="7" height="7" rx="1" />
          <rect x="3" y="14" width="7" height="7" rx="1" />
          <rect x="14" y="14" width="7" height="7" rx="1" />
        </svg>
        التصنيفات
      </button>

      {/* Backdrop */}
      <div
        onClick={() => setOpen(false)}
        className={`fixed inset-0 bg-black/70 backdrop-blur-sm z-[300] transition-opacity duration-300 ${open ? "opacity-100" : "opacity-0 pointer-events-none"}`}
      />

      {/* Drawer — slides in from the right */}
      <div
        className={`fixed top-0 right-0 h-full w-full max-w-sm bg-[#000000] border-l border-white/10 z-[400] flex flex-col shadow-2xl transition-transform duration-300 ease-in-out ${open ? "translate-x-0" : "translate-x-full"}`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-white/10">
          <span className="text-lg font-black text-white">التصنيفات</span>
          <button
            onClick={() => setOpen(false)}
            className="w-8 h-8 flex items-center justify-center rounded-full bg-white/10 hover:bg-white/20 transition-colors"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto px-5 py-6 space-y-8">

          {/* Genres */}
          <section>
            <p className="text-[10px] font-bold uppercase tracking-widest text-white/30 mb-3">تصنيفات</p>
            <div className="grid grid-cols-3 gap-2">
              {genresList.map((g) => (
                <a
                  key={g.slug}
                  href={`/genre/${g.slug}`}
                  onClick={() => setOpen(false)}
                  className="flex flex-col items-center gap-1 px-2 py-3 rounded-xl bg-white/[0.04] border border-white/[0.06] hover:bg-primary/15 hover:border-primary/30 transition-all text-center group"
                >
                  {/* <span className="text-lg">{g.icon}</span> */}
                  <span className="text-[11px] font-bold text-white/70 group-hover:text-white transition-colors leading-tight">{g.label}</span>
                </a>
              ))}
            </div>
          </section>

          {/* Studios */}
          <section>
            <p className="text-[10px] font-bold uppercase tracking-widest text-white/30 mb-3">استديوهات ومنصات</p>
            <div className="grid grid-cols-3 gap-2">
              {studiosList.map((g) => (
                <a
                  key={g.slug}
                  href={`/genre/${g.slug}`}
                  onClick={() => setOpen(false)}
                  className="flex flex-col items-center gap-1 px-2 py-3 rounded-xl bg-white/[0.04] border border-white/[0.06] hover:bg-primary/15 hover:border-primary/30 transition-all text-center group"
                >
                  {/* <span className="text-lg">{g.icon}</span> */}
                  <span className="text-[11px] font-bold text-white/70 group-hover:text-white transition-colors leading-tight">{g.label}</span>
                </a>
              ))}
            </div>
          </section>

          {/* Eras */}
          <section>
            <p className="text-[10px] font-bold uppercase tracking-widest text-white/30 mb-3">حقب زمنية</p>
            <div className="grid grid-cols-3 gap-2">
              {erasList.map((g) => (
                <a
                  key={g.slug}
                  href={`/genre/${g.slug}`}
                  onClick={() => setOpen(false)}
                  className="flex flex-col items-center gap-1 px-2 py-3 rounded-xl bg-white/[0.04] border border-white/[0.06] hover:bg-primary/15 hover:border-primary/30 transition-all text-center group"
                >
                  {/* <span className="text-lg">{g.icon}</span> */}
                  <span className="text-[11px] font-bold text-white/70 group-hover:text-white transition-colors leading-tight">{g.label}</span>
                </a>
              ))}
            </div>
          </section>
        </div>
      </div>
    </>
  );
}
