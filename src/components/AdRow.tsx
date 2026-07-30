"use client";

import NewAd from "./NewAd";

interface AdRowProps {
  ads: ("ad1" | "ad2" | "ad3")[];
}

export default function AdRow({ ads }: AdRowProps) {
  return (
    <div style={{ 
      display: "flex", 
      flexDirection: "row", 
      gap: "10px", 
      justifyContent: "center",
      alignItems: "center",
      margin: "20px auto",
      maxWidth: "100%"
    }}>
      {ads.map((ad, index) => (
        <div key={index} style={{ flex: 1, minWidth: 0 }}>
          <NewAd ad={ad} />
        </div>
      ))}
    </div>
  );
}
