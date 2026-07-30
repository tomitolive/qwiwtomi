"use client";

import { useState, useEffect } from "react";

export default function AdblockDetector() {
  const [isAdblockDetected, setIsAdblockDetected] = useState(false);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Check for adblock by attempting to load a bait element
    const checkAdblock = () => {
      // Method 1: Check if ad containers are blocked
      const adTest = document.createElement("div");
      adTest.innerHTML = "&nbsp;";
      adTest.className = "adsbox ad-banner ad-placement ad-sidebar ad-container";
      adTest.style.position = "absolute";
      adTest.style.left = "-999px";
      document.body.appendChild(adTest);

      setTimeout(() => {
        const isBlocked = 
          adTest.offsetHeight === 0 ||
          adTest.style.display === "none" ||
          window.getComputedStyle(adTest).display === "none" ||
          adTest.style.visibility === "hidden" ||
          window.getComputedStyle(adTest).visibility === "hidden";
        
        document.body.removeChild(adTest);
        setIsAdblockDetected(isBlocked);
        setIsChecking(false);
      }, 100);
    };

    // Method 2: Check if common ad scripts are blocked
    const checkBlockedScripts = () => {
      const testScript = document.createElement("script");
      testScript.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js";
      testScript.async = true;
      testScript.onerror = () => {
        setIsAdblockDetected(true);
        setIsChecking(false);
      };
      document.head.appendChild(testScript);
      
      // Clean up after check
      setTimeout(() => {
        if (document.head.contains(testScript)) {
          document.head.removeChild(testScript);
        }
      }, 200);
    };

    // Run both checks
    checkAdblock();
    checkBlockedScripts();
  }, []);

  // Block page content if adblock is detected
  if (isAdblockDetected) {
    return (
      <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/95 backdrop-blur-md p-4">
        <div className="bg-zinc-900 border border-orange-500/50 rounded-xl max-w-md w-full p-6 text-center shadow-2xl">
          <div className="w-20 h-20 mx-auto mb-5 bg-orange-500/20 rounded-full flex items-center justify-center animate-pulse">
            <svg 
              width="40" 
              height="40" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2"
              className="text-orange-500"
            >
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
          </div>
          
          <h2 className="text-2xl font-bold text-white mb-4">
            ⚠️ تم اكتشاف مانع الإعلانات
          </h2>
          
          <p className="text-gray-300 mb-6 leading-relaxed text-base">
            نحن نعتمد على الإعلانات للحفاظ على الموقع مجاناً. يرجى تعطيل مانع الإعلانات لمواصلة التمتع بالمحتوى.
          </p>
          
          <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-4 mb-6">
            <p className="text-orange-400 text-sm font-semibold mb-2">خطوات التعطيل:</p>
            <ol className="text-gray-300 text-sm text-right space-y-1" dir="rtl">
              <li>1. اضغط على أيقونة مانع الإعلانات في المتصفح</li>
              <li>2. اختر "تعطيل على هذا الموقع"</li>
              <li>3. اضغط على زر التحديث أدناه</li>
            </ol>
          </div>
          
          <button
            onClick={() => window.location.reload()}
            className="w-full px-6 py-4 bg-orange-500 hover:bg-orange-600 text-white font-bold rounded-lg transition-colors text-lg"
          >
            🔄 قمت بتعطيله - تحديث الصفحة
          </button>
          
          <p className="text-gray-500 text-xs mt-6">
            شكراً لدعمك لنا ❤️
          </p>
        </div>
      </div>
    );
  }

  // Show loading state while checking
  if (isChecking) {
    return null;
  }

  // No adblock detected - allow content to load
  return null;
}
