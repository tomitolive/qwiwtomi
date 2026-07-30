"use client";

import { useEffect, useRef } from "react";

export default function NewAd() {
  const loaded = useRef(false);

  useEffect(() => {
    const loadScript = () => {
      if (loaded.current) return;
      
      // Check if script is already loaded
      if (document.querySelector('script[src="https://pl29663723.effectivecpmnetwork.com/6e/78/14/6e781401b81579a741ac7074d6fe77eb.js"]')) {
        loaded.current = true;
        return;
      }

      const script = document.createElement("script");
      script.src = "https://pl29663723.effectivecpmnetwork.com/6e/78/14/6e781401b81579a741ac7074d6fe77eb.js";
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
