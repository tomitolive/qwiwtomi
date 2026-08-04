"use client";

import { useState, useEffect } from "react";

const SMART_LINK_URL = "https://www.effectivecpmnetwork.com/j1d8z33zf?key=92cdcd507fcea47e994c87fc91d5269b";

export default function SocialBar() {
  const [isVisible, setIsVisible] = useState(false);
  const [hasTriggeredLink, setHasTriggeredLink] = useState(false);

  useEffect(() => {
    // Show the popup after a short delay
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  const handleHideClick = () => {
    // Trigger smart link only once per page load
    if (!hasTriggeredLink) {
      setHasTriggeredLink(true);
      window.open(SMART_LINK_URL, '_blank');
    }
    
    // Hide the popup
    setIsVisible(false);
  };

  if (!isVisible) return null;

  return (
    <div className="fixed top-20 right-4 z-[10000] max-w-sm">
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg shadow-2xl p-4 border border-blue-400/30">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <p className="text-white text-sm font-medium leading-relaxed">
              Don't worry, here's how to SAVE your FB account if it was hacked
            </p>
          </div>
          <button
            onClick={handleHideClick}
            className="px-3 py-1 bg-white/20 hover:bg-white/30 text-white text-xs font-bold rounded transition-colors whitespace-nowrap"
          >
            Hide
          </button>
        </div>
      </div>
    </div>
  );
}
