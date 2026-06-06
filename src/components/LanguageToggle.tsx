"use client";

import { useState, useEffect, useRef } from "react";

const languages = [
  { code: "ar", label: "العربية" },
  { code: "en", label: "English" },
  { code: "fr", label: "Français" },
  { code: "es", label: "Español" },
];

export function LanguageToggle() {
  const [isOpen, setIsOpen] = useState(false);
  const [currentLang, setCurrentLang] = useState("ar");
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Read current lang from cookie
    const cookies = document.cookie.split("; ");
    const localeCookie = cookies.find((c) => c.startsWith("NEXT_LOCALE="));
    if (localeCookie) {
      setCurrentLang(localeCookie.split("=")[1]);
    }

    const handleClickOutside = (event: MouseEvent | TouchEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("touchstart", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("touchstart", handleClickOutside);
    };
  }, []);

  const changeLanguage = (code: string) => {
    document.cookie = `NEXT_LOCALE=${code}; path=/; max-age=31536000`; // 1 year
    window.location.reload();
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-center cursor-pointer transition-all hover:text-primary hover:scale-110 active:scale-95"
        style={{ width: '36px', height: '36px', background: 'transparent', border: 'none', color: 'inherit', touchAction: 'manipulation' }}
        title="تغيير اللغة / Change Language"
        aria-label="تغيير اللغة"
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="2" y1="12" x2="22" y2="12"></line>
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
        </svg>
      </button>

      {isOpen && (
        <div className="absolute top-full mt-2 left-0 md:left-auto md:right-0 w-36 bg-[#0a1024] dark:bg-[#0a1024] bg-bg-elevated border border-[rgba(255,255,255,0.1)] rounded-lg shadow-2xl overflow-hidden z-[9999]" style={{ backgroundColor: "var(--bg-elevated)" }}>
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => changeLanguage(lang.code)}
              className={`w-full text-left px-4 py-3 text-sm hover:!bg-primary transition-colors flex items-center justify-between ${
                currentLang === lang.code ? "text-primary font-bold hover:!text-white" : "text-text hover:!text-white"
              }`}
              dir={lang.code === "ar" ? "rtl" : "ltr"}
            >
              <span className="flex-1 text-center font-semibold">{lang.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
