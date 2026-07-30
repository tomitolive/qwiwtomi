"use client";

import { useEffect } from "react";

const ADS = {
  ad1: {
    id: "container-08370281e563742f6dcb56530f5e8082",
    src: "https://pl30597637.effectivecpmnetwork.com/08370281e563742f6dcb56530f5e8082/invoke.js"
  },
  ad2: {
    id: "container-7853b06f071ef8a725aee4957098eae1",
    src: "https://pl30598106.effectivecpmnetwork.com/7853b06f071ef8a725aee4957098eae1/invoke.js"
  },
  ad3: {
    id: "container-74473a481e12f32fea68225a3cc97eed",
    src: "https://pl30598123.effectivecpmnetwork.com/74473a481e12f32fea68225a3cc97eed/invoke.js"
  }
};

interface NewAdProps {
  ad?: "ad1" | "ad2" | "ad3";
}

export default function NewAd({ ad = "ad1" }: NewAdProps) {
  const adConfig = ADS[ad];

  useEffect(() => {
    // Only inject script once per ad type
    if (!document.querySelector(`script[src="${adConfig.src}"]`)) {
      const script = document.createElement("script");
      script.src = adConfig.src;
      script.async = true;
      script.setAttribute("data-cfasync", "false");
      document.head.appendChild(script);
    }
  }, [adConfig.src]);

  return (
    <div style={{ 
      textAlign: "center", 
      margin: "20px auto", 
      overflow: "hidden", 
      maxWidth: "728px", 
      minHeight: "90px",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      gap: "10px"
    }}>
      <div id={adConfig.id} style={{ flex: 1, minWidth: 0 }}></div>
    </div>
  );
}
