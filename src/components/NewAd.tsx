"use client";

import { useEffect, useRef } from "react";

export default function NewAd() {
  const loaded = useRef(false);

  useEffect(() => {
    const loadScript = () => {
      if (loaded.current) return;
      
      // Check if script is already loaded
      if (document.querySelector('script[src="https://pl30597550.effectivecpmnetwork.com/e9/97/d5/e997d5de88469fe50e1f491bdebf4d3e.js"]')) {
        loaded.current = true;
        return;
      }

      const script = document.createElement("script");
      script.src = "https://pl30597550.effectivecpmnetwork.com/e9/97/d5/e997d5de88469fe50e1f491bdebf4d3e.js";
      script.async = true;
      document.head.appendChild(script);
      loaded.current = true;
    };

    // Load script after page is fully loaded
    if (document.readyState === 'complete') {
      loadScript();
    } else {
      window.addEventListener('load', loadScript);
    }

    return () => {
      window.removeEventListener('load', loadScript);
    };
  }, []);

  return (
    <div style={{ textAlign: "center", margin: "20px auto", overflow: "hidden", maxWidth: "728px", minHeight: "90px", border: "1px dashed #333", padding: "10px" }}>
      {/* Ad will be loaded here */}
    </div>
  );
}
