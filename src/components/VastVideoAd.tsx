"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { usePathname } from "next/navigation";

const VAST_URL = "https://s.magsrv.com/v1/vast.php?idz=5979262";
const AD_CHANCE = 0.9; // 90% chance to show ad

interface VastAd {
  mediaUrl: string;
  clickThrough: string;
  duration: number;
  impressionUrls: string[];
  trackingEvents: Record<string, string[]>;
}

export default function VastVideoAd() {
  const pathname = usePathname();
  const [showAd, setShowAd] = useState(false);
  const [adData, setAdData] = useState<VastAd | null>(null);
  const [countdown, setCountdown] = useState(0);
  const [canSkip, setCanSkip] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const prevPathRef = useRef<string>("");
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const parseVast = useCallback((xml: string): VastAd | null => {
    try {
      const parser = new DOMParser();
      const doc = parser.parseFromString(xml, "text/xml");

      // Get media file URL
      const mediaFile = doc.querySelector("MediaFile");
      const mediaUrl = mediaFile?.textContent?.trim() || "";

      // Get click-through URL
      const clickThrough =
        doc.querySelector("ClickThrough")?.textContent?.trim() || "";

      // Get duration
      const durationStr =
        doc.querySelector("Duration")?.textContent?.trim() || "00:00:15";
      const parts = durationStr.split(":");
      const duration =
        parseInt(parts[0]) * 3600 +
        parseInt(parts[1]) * 60 +
        parseInt(parts[2]);

      // Get impression URLs
      const impressionEls = doc.querySelectorAll("Impression");
      const impressionUrls: string[] = [];
      impressionEls.forEach((el) => {
        const url = el.textContent?.trim();
        if (url) impressionUrls.push(url);
      });

      // Get tracking events
      const trackingEls = doc.querySelectorAll("Tracking");
      const trackingEvents: Record<string, string[]> = {};
      trackingEls.forEach((el) => {
        const event = el.getAttribute("event") || "";
        const url = el.textContent?.trim() || "";
        if (event && url) {
          if (!trackingEvents[event]) trackingEvents[event] = [];
          trackingEvents[event].push(url);
        }
      });

      if (!mediaUrl) return null;

      return { mediaUrl, clickThrough, duration, impressionUrls, trackingEvents };
    } catch {
      return null;
    }
  }, []);

  const firePixels = useCallback((urls: string[]) => {
    urls.forEach((url) => {
      const img = new Image();
      img.src = url;
    });
  }, []);

  const closeAd = useCallback(() => {
    setShowAd(false);
    setAdData(null);
    setCanSkip(false);
    setCountdown(0);
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.src = "";
    }
  }, []);

  // Trigger ad on pathname change
  useEffect(() => {
    if (pathname === prevPathRef.current) return;
    prevPathRef.current = pathname;

    // 90% random chance
    if (Math.random() > AD_CHANCE) return;

    // Fetch VAST XML
    const fetchVast = async () => {
      try {
        const res = await fetch(VAST_URL);
        const xml = await res.text();
        const parsed = parseVast(xml);
        if (parsed) {
          setAdData(parsed);
          setShowAd(true);
          setCanSkip(false);
          const skipDelay = Math.min(parsed.duration, 5);
          setCountdown(skipDelay);

          // Fire impression pixels
          firePixels(parsed.impressionUrls);

          // Start countdown timer
          if (timerRef.current) clearInterval(timerRef.current);
          let remaining = skipDelay;
          timerRef.current = setInterval(() => {
            remaining -= 1;
            setCountdown(remaining);
            if (remaining <= 0) {
              setCanSkip(true);
              if (timerRef.current) {
                clearInterval(timerRef.current);
                timerRef.current = null;
              }
            }
          }, 1000);
        }
      } catch {
        // Silently fail - don't block user
      }
    };

    // Small delay to ensure page transition feels smooth
    const timeout = setTimeout(fetchVast, 500);
    return () => clearTimeout(timeout);
  }, [pathname, parseVast, firePixels]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  if (!showAd || !adData) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 999999,
        background: "rgba(0, 0, 0, 0.92)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backdropFilter: "blur(8px)",
      }}
    >
      {/* Ad container */}
      <div
        style={{
          position: "relative",
          width: "min(90vw, 720px)",
          maxHeight: "80vh",
          borderRadius: "12px",
          overflow: "hidden",
          boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
          background: "#000",
        }}
      >
        {/* Ad label */}
        <div
          style={{
            position: "absolute",
            top: 12,
            left: 12,
            background: "rgba(255,255,255,0.15)",
            backdropFilter: "blur(4px)",
            color: "#fff",
            padding: "4px 12px",
            borderRadius: "6px",
            fontSize: "12px",
            fontWeight: 600,
            letterSpacing: "0.5px",
            zIndex: 10,
            pointerEvents: "none",
          }}
        >
          إعلان • AD
        </div>

        {/* Skip / Countdown button */}
        <button
          onClick={canSkip ? closeAd : undefined}
          style={{
            position: "absolute",
            top: 12,
            right: 12,
            zIndex: 10,
            background: canSkip
              ? "rgba(255,255,255,0.95)"
              : "rgba(255,255,255,0.2)",
            color: canSkip ? "#000" : "#fff",
            border: "none",
            padding: "8px 18px",
            borderRadius: "8px",
            fontSize: "14px",
            fontWeight: 700,
            cursor: canSkip ? "pointer" : "default",
            transition: "all 0.3s ease",
            backdropFilter: "blur(4px)",
          }}
        >
          {canSkip ? "تخطي ✕" : `تخطي بعد ${countdown}s`}
        </button>

        {/* Video player */}
        <video
          ref={videoRef}
          src={adData.mediaUrl}
          autoPlay
          playsInline
          muted={false}
          onClick={() => {
            if (adData.clickThrough) {
              window.open(adData.clickThrough, "_blank");
            }
          }}
          onEnded={closeAd}
          onError={closeAd}
          style={{
            width: "100%",
            maxHeight: "80vh",
            objectFit: "contain",
            cursor: adData.clickThrough ? "pointer" : "default",
            display: "block",
          }}
        />
      </div>
    </div>
  );
}
