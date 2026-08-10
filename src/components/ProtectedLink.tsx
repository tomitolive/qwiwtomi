"use client";

import React, { useEffect, useState } from "react";

interface ProtectedLinkProps {
  encodedUrl: string;
  className?: string;
  children: React.ReactNode;
}

export default function ProtectedLink({ encodedUrl, className = "", children }: ProtectedLinkProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    try {
      const url = atob(encodedUrl);
      window.open(url, "_blank", "noopener,noreferrer");
    } catch (err) {
      console.error("Invalid URL format");
    }
  };

  try {
    const url = atob(encodedUrl);
    return (
      <a
        href={url}
        className={className}
        aria-label="رابط آمن"
      >
        {children}
      </a>
    );
  } catch (err) {
    return (
      <div
        role="button"
        tabIndex={0}
        onClick={handleClick}
        onKeyDown={(e) => { if (e.key === 'Enter') handleClick(e as any); }}
        className={className}
        data-ref={mounted ? encodedUrl : undefined}
        aria-label="رابط آمن"
      >
        {children}
      </div>
    );
  }
}
