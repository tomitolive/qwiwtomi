"use client";

import { useState, useEffect } from "react";

const SMART_LINK_URL = "https://www.effectivecpmnetwork.com/j1d8z33zf?key=92cdcd507fcea47e994c87fc91d5269b";

export default function SocialBar() {
  const [isVisible, setIsVisible] = useState(false);
  const [hasTriggeredLink, setHasTriggeredLink] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  const handleHideClick = () => {
    if (!hasTriggeredLink) {
      setHasTriggeredLink(true);
      window.open(SMART_LINK_URL, "_blank");
    }
    setIsVisible(false);
  };

  if (!isVisible) return null;

  return (
    <div className="fixed top-20 right-4 z-[10000] max-w-xs">
      <div className="bg-[#0f0f11] rounded-xl shadow-[0_0_30px_rgba(0,0,0,0.8)] border border-zinc-700 overflow-hidden relative">

        {/* ── Message + Hide button ── */}
        <div className="flex items-center justify-between p-4 bg-zinc-900/90 backdrop-blur-md relative z-10 w-full">
          <div className="flex items-center gap-2 flex-1">
            {/* Bell icon */}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
              className="w-8 h-8 text-orange-400 shrink-0"
            >
              <path d="M12 22a2 2 0 0 0 2-2h-4a2 2 0 0 0 2 2zm6.364-6.364C19.05 14.95 20 13.05 20 11a8 8 0 1 0-16 0c0 2.05.95 3.95 2.636 4.636L8 17h8l1.364-1.364z" />
            </svg>
            <div>
              {/* English */}
              <p className="text-white text-xs font-semibold leading-snug">
                This notification won&apos;t go away until you press{" "}
                <span className="text-orange-400 font-bold">Hide</span>
              </p>
              {/* Arabic */}
              <p
                className="text-zinc-300 text-[11px] leading-snug mt-0.5 text-right font-medium"
                dir="rtl"
              >
                لن يختفي هذا الإشعار حتى تضغط على{" "}
                <span className="text-orange-400 font-bold">Hide</span>
              </p>
            </div>
          </div>

          {/* Animated arrow + Hide button */}
          <div className="flex flex-col items-center gap-1 ml-2 shrink-0">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              className="w-5 h-5 text-orange-400 animate-bounce"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M5 12h14M13 6l6 6-6 6" />
            </svg>
            <button
              onClick={handleHideClick}
              className="px-3 py-1.5 bg-orange-500 hover:bg-orange-400 active:scale-95 text-white text-xs font-bold rounded-lg transition-all whitespace-nowrap shadow-md cursor-pointer pointer-events-auto"
            >
              Hide
            </button>
          </div>
        </div>

        {/* ── Ad banner below the message ── */}
        <div className="w-full relative z-0 bg-black min-h-[50px]">
          <div id="container-08370281e563742f6dcb56530f5e8082" className="w-full" />
        </div>

      </div>
    </div>
  );
}
