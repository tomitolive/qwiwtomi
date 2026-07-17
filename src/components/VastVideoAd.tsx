"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { usePathname } from "next/navigation";

const VAST_URL = "https://s.magsrv.com/v1/vast.php?idz=5979262";

interface VastAd {
  mediaUrl: string;
  clickThrough: string;
  duration: number;
  impressionUrls: string[];
  trackingEvents: Record<string, string[]>;
}

// Prefetch VAST XML immediately on module load for fastest first ad
let prefetchedVastPromise: Promise<string> | null = null;
function prefetchVast() {
  prefetchedVastPromise = fetch(VAST_URL)
    .then((res) => res.text())
    .catch(() => "");
  return prefetchedVastPromise;
}
// Start prefetching as soon as this module loads
if (typeof window !== "undefined") {
  prefetchVast();
}

export default function VastVideoAd() {
  const pathname = usePathname();
  const [showAd, setShowAd] = useState(false);
  const [adData, setAdData] = useState<VastAd | null>(null);
  const [countdown, setCountdown] = useState(0);
  const [canSkip, setCanSkip] = useState(false);
  const [videoReady, setVideoReady] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const prevPathRef = useRef<string>("");
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const preloadVideoRef = useRef<HTMLVideoElement | null>(null);
  const videoReadyRef = useRef(false);

  const parseVast = useCallback((xml: string): VastAd | null => {
    try {
      const parser = new DOMParser();
      const doc = parser.parseFromString(xml, "text/xml");

      const mediaFile = doc.querySelector("MediaFile");
      const mediaUrl = mediaFile?.textContent?.trim() || "";

      const clickThrough =
        doc.querySelector("ClickThrough")?.textContent?.trim() || "";

      const durationStr =
        doc.querySelector("Duration")?.textContent?.trim() || "00:00:15";
      const parts = durationStr.split(":");
      const duration =
        parseInt(parts[0]) * 3600 +
        parseInt(parts[1]) * 60 +
        parseInt(parts[2]);

      const impressionEls = doc.querySelectorAll("Impression");
      const impressionUrls: string[] = [];
      impressionEls.forEach((el) => {
        const url = el.textContent?.trim();
        if (url) impressionUrls.push(url);
      });

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
    setVideoReady(false);
    videoReadyRef.current = false;
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.src = "";
    }
    // Prefetch next ad immediately after closing
    prefetchVast();
  }, []);

  // Preload video file in background for instant playback
  const preloadVideo = useCallback((url: string) => {
    if (preloadVideoRef.current) {
      preloadVideoRef.current.src = "";
    }
    const video = document.createElement("video");
    video.preload = "auto";
    video.muted = true;
    video.src = url;
    video.load();
    preloadVideoRef.current = video;
  }, []);

  // Trigger ad on pathname change - NO DELAY
  useEffect(() => {
    if (pathname === prevPathRef.current) return;
    prevPathRef.current = pathname;

    const fetchVast = async () => {
      try {
        let xml: string;
        // Use prefetched data if available, otherwise fetch fresh
        if (prefetchedVastPromise) {
          xml = await prefetchedVastPromise;
          prefetchedVastPromise = null;
        } else {
          const res = await fetch(VAST_URL);
          xml = await res.text();
        }

        const parsed = parseVast(xml);
        if (parsed) {
          // Preload the video file
          preloadVideo(parsed.mediaUrl);

          setAdData(parsed);
          setShowAd(true);
          setCanSkip(false);
          setVideoReady(false);
          videoReadyRef.current = false;
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

          // Safety timeout: if video is not ready in 6 seconds, close it to avoid blocking the user
          setTimeout(() => {
            if (!videoReadyRef.current) {
              closeAd();
            }
          }, 6000);
        }
      } catch {
        // Silently fail - don't block user
      }
    };

    // No delay - show ad immediately
    fetchVast();
  }, [pathname, parseVast, firePixels, preloadVideo, closeAd]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (preloadVideoRef.current) {
        preloadVideoRef.current.src = "";
      }
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
      {/* Loading spinner while video loads */}
      {!videoReady && (
        <div
          style={{
            position: "absolute",
            zIndex: 5,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "12px",
          }}
        >
          <div
            style={{
              width: 40,
              height: 40,
              border: "3px solid rgba(255,255,255,0.2)",
              borderTopColor: "#fff",
              borderRadius: "50%",
              animation: "vastSpin 0.8s linear infinite",
            }}
          />
          <span style={{ color: "rgba(255,255,255,0.6)", fontSize: 13 }}>
            جاري التحميل...
          </span>
        </div>
      )}

      {/* Spinner keyframes */}
      <style>{`@keyframes vastSpin { to { transform: rotate(360deg); } }`}</style>

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
          opacity: videoReady ? 1 : 0,
          transition: "opacity 0.3s ease",
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
          muted
          preload="auto"
          onCanPlay={() => {
            setVideoReady(true);
            videoReadyRef.current = true;
          }}
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
