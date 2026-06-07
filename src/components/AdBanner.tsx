'use client';

import { useEffect, useRef, useState } from 'react';

export default function AdBanner() {
  const [isLoaded, setIsLoaded] = useState(false);
  const adContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Load CPM script into the ad container
    const script = document.createElement('script');
    script.src = 'https://pl29663723.effectivecpmnetwork.com/6e/78/14/6e781401b81579a741ac7074d6fe77eb.js';
    script.async = true;
    
    script.onload = () => {
      setIsLoaded(true);
    };
    
    script.onerror = () => {
      console.error('Failed to load ad script');
    };
    
    if (adContainerRef.current) {
      adContainerRef.current.appendChild(script);
    }
    
    return () => {
      if (adContainerRef.current && script.parentNode) {
        script.parentNode.removeChild(script);
      }
    };
  }, []);

  return (
    <div className="w-full bg-gray-900/50 border border-gray-700/50 rounded-lg p-4 my-4">
      <div className="text-center text-xs text-gray-500 mb-2">إعلان</div>
      <div 
        ref={adContainerRef} 
        className="min-h-[250px] flex items-center justify-center bg-gray-800/30 rounded-lg"
      >
        {!isLoaded && (
          <div className="text-gray-600 text-sm">جاري تحميل الإعلان...</div>
        )}
      </div>
    </div>
  );
}
