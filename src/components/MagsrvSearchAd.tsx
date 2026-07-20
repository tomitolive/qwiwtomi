"use client";

import { useEffect, useRef } from "react";

declare global {
  interface Window {
    AdProvider?: Array<{ serve?: Record<string, unknown> }>;
  }
}

export default function MagsrvSearchAd() {
  const pushed = useRef(false);

  useEffect(() => {
    if (!document.querySelector('script[src="https://a.magsrv.com/ad-provider.js"]')) {
      const script = document.createElement("script");
      script.src = "https://a.magsrv.com/ad-provider.js";
      script.async = true;
      script.type = "application/javascript";
      document.head.appendChild(script);
    }

    if (!pushed.current) {
      pushed.current = true;
      window.AdProvider = window.AdProvider || [];
      window.AdProvider.push({ serve: {} });
    }
  }, []);

  return (
    <div style={{ textAlign: "center", margin: "16px auto", overflow: "hidden" }}>
      <ins
        className="eas6a97888e37"
        data-zoneid="5980994"
        style={{ display: "inline-block", minWidth: "300px", minHeight: "90px" }}
      />
    </div>
  );
}
