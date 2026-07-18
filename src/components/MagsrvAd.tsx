"use client";

import { useEffect, useRef } from "react";

declare global {
  interface Window {
    AdProvider?: Array<{ serve?: Record<string, unknown> }>;
  }
}

export default function MagsrvAd() {
  const pushed = useRef(false);

  useEffect(() => {
    // Load ad-provider script once
    if (!document.querySelector('script[src="https://a.magsrv.com/ad-provider.js"]')) {
      const script = document.createElement("script");
      script.src = "https://a.magsrv.com/ad-provider.js";
      script.async = true;
      script.type = "application/javascript";
      document.head.appendChild(script);
    }

    // Push serve only once per mount
    if (!pushed.current) {
      pushed.current = true;
      window.AdProvider = window.AdProvider || [];
      window.AdProvider.push({ serve: {} });
    }
  }, []);

  return (
    <div style={{ textAlign: "center", margin: "20px auto", overflow: "hidden", maxWidth: "728px", minHeight: "90px", border: "1px dashed #333", padding: "10px" }}>
      <ins
        className="eas6a97888e37"
        data-zoneid="5979910"
        style={{ display: "inline-block", minWidth: "300px", minHeight: "90px" }}
      />
    </div>
  );
}
