"use client";

import { useEffect, useRef } from "react";

export default function NewAd() {
  const containerRef = useRef<HTMLDivElement>(null);
  const loaded = useRef(false);

  useEffect(() => {
    const loadScript = () => {
      const script = document.createElement("script");
      script.src = "https://pl30597637.effectivecpmnetwork.com/08370281e563742f6dcb56530f5e8082/invoke.js";
      script.async = true;
      script.setAttribute("data-cfasync", "false");
      document.head.appendChild(script);
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
    <div ref={containerRef} style={{ textAlign: "center", margin: "20px auto", overflow: "hidden", maxWidth: "728px", minHeight: "90px", border: "1px dashed #333", padding: "10px" }}>
      <div id="container-08370281e563742f6dcb56530f5e8082"></div>
    </div>
  );
}
