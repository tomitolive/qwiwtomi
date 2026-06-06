"use client";

import { useState, useEffect, useRef } from "react";
import GenreModal from "@/components/GenreModal";
import Search from "@/components/Search";

const navTranslations: Record<string, any> = {
  ar: { home: "الرئيسية", movies: "أفلام", series: "مسلسلات", genres: "التصنيفات" },
  en: { home: "Home", movies: "Movies", series: "Series", genres: "Genres" },
  fr: { home: "Accueil", movies: "Films", series: "Séries", genres: "Genres" },
  es: { home: "Inicio", movies: "Películas", series: "Series", genres: "Géneros" },
};

export default function Navbar() {
  const [locale, setLocale] = useState("ar");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const savedLocale = localStorage.getItem("NEXT_LOCALE") || "ar";
    setLocale(savedLocale);
  }, []);

  // Close mobile menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent | TouchEvent) => {
      if (navRef.current && !navRef.current.contains(event.target as Node)) {
        setMobileMenuOpen(false);
      }
    };

    if (mobileMenuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("touchstart", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("touchstart", handleClickOutside);
    };
  }, [mobileMenuOpen]);

  // Close mobile menu on route change
  useEffect(() => {
    const handleRouteChange = () => setMobileMenuOpen(false);
    window.addEventListener("popstate", handleRouteChange);
    return () => window.removeEventListener("popstate", handleRouteChange);
  }, []);

  const t = navTranslations[locale] || navTranslations.ar;

  return (
    <header className="navbar" ref={navRef}>
      <div className="flex items-center justify-between w-full gap-3">
        <div className="flex items-center gap-3 md:gap-6">
          <a href="/" className="logo-link" style={{ fontFamily: 'var(--font-outfit)' }}>
            <h1 className="logo-text-wrapper m-0">
              <span className="logo-text">TOMITO</span>
            </h1>
          </a>
          <nav className={`items-center gap-5 text-[13px] font-semibold ${mobileMenuOpen ? 'flex flex-col absolute top-full left-0 right-0 bg-[#000] p-4 z-50' : 'hidden md:flex'}`}>
            <a href="/" className="nav-link-active" onClick={() => setMobileMenuOpen(false)}>{t.home}</a>
            <a href="/movie" className="nav-link" onClick={() => setMobileMenuOpen(false)}>{t.movies}</a>
            <a href="/tv" className="nav-link" onClick={() => setMobileMenuOpen(false)}>{t.series}</a>

            {/* Genres Modal Trigger */}
            <GenreModal />
          </nav>
        </div>
        <div className="flex items-center gap-3 flex-1 max-w-[320px] md:max-w-md justify-end">
          <button
            className="md:hidden p-2 text-white active:scale-95"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
            style={{ touchAction: 'manipulation' }}
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              {mobileMenuOpen ? (
                <path d="M18 6L6 18M6 6l12 12" />
              ) : (
                <>
                  <path d="M3 12h18" />
                  <path d="M3 6h18" />
                  <path d="M3 18h18" />
                </>
              )}
            </svg>
          </button>
          <div className="flex-1">
            <Search />
          </div>
        </div>
      </div>
    </header>
  );
}
