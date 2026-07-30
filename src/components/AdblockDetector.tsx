"use client";

import { useState, useEffect } from "react";

export default function AdblockDetector() {
  const [isAdblockDetected, setIsAdblockDetected] = useState(false);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    let blockedCount = 0;
    const totalChecks = 8;

    // Method 1: Check if ad containers are blocked via CSS
    const checkAdContainers = () => {
      const adTest = document.createElement("div");
      adTest.innerHTML = "&nbsp;";
      adTest.className = "adsbox ad-banner ad-placement ad-sidebar ad-container ad-banner-top ad-banner-bottom ad-sidebar-ad ad-content";
      adTest.style.position = "absolute";
      adTest.style.left = "-999px";
      document.body.appendChild(adTest);

      setTimeout(() => {
        const computedStyle = window.getComputedStyle(adTest);
        const isBlocked = 
          adTest.offsetHeight === 0 ||
          adTest.style.display === "none" ||
          computedStyle.display === "none" ||
          adTest.style.visibility === "hidden" ||
          computedStyle.visibility === "hidden" ||
          computedStyle.opacity === "0" ||
          computedStyle.height === "0px";
        
        document.body.removeChild(adTest);
        if (isBlocked) blockedCount++;
        checkComplete();
      }, 100);
    };

    // Method 2: Check if common ad scripts are blocked
    const checkBlockedScripts = () => {
      const testScript = document.createElement("script");
      testScript.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js";
      testScript.async = true;
      testScript.onerror = () => {
        blockedCount++;
        checkComplete();
      };
      testScript.onload = () => {
        if (document.head.contains(testScript)) {
          document.head.removeChild(testScript);
        }
        checkComplete();
      };
      document.head.appendChild(testScript);
    };

    // Method 3: Check if adblock properties exist on window
    const checkWindowProperties = () => {
      const adblockProps = [
        'canRunAds',
        'canRunAdsense',
        '_ab_',
        'abp',
        'adblock',
        'adblockActive',
        'adblockEnabled',
        'adblockDetected',
        'isAdBlockActive',
        'isAdblockActive'
      ];
      
      for (const prop of adblockProps) {
        if (window[prop as keyof Window] !== undefined) {
          blockedCount++;
          break;
        }
      }
      checkComplete();
    };

    // Method 4: Check if ad elements are removed from DOM
    const checkElementRemoval = () => {
      const bait = document.createElement("div");
      bait.id = "ad-banner-test";
      bait.className = "ad-banner adsbox";
      bait.style.position = "absolute";
      bait.style.left = "-9999px";
      bait.innerHTML = "<ins class='adsbygoogle'></ins>";
      document.body.appendChild(bait);

      setTimeout(() => {
        const isRemoved = !document.body.contains(bait) || 
                          bait.innerHTML === "" ||
                          !bait.querySelector("ins");
        
        if (document.body.contains(bait)) {
          document.body.removeChild(bait);
        }
        
        if (isRemoved) blockedCount++;
        checkComplete();
      }, 200);
    };

    // Method 5: Check if specific ad URLs are blocked
    const checkBlockedUrls = () => {
      const testImg = new Image();
      testImg.src = "https://pagead2.googlesyndication.com/pagead/imgad?id=CICAgKDL7IjD9woEQqYQ4AII";
      testImg.onload = () => checkComplete();
      testImg.onerror = () => {
        blockedCount++;
        checkComplete();
      };
    };

    // Method 6: Check for adblock extension injection
    const checkExtensionInjection = () => {
      const adblockElements = document.querySelectorAll('[class*="adblock"], [id*="adblock"], [class*="block-ad"], [id*="block-ad"]');
      if (adblockElements.length > 0) {
        blockedCount++;
      }
      checkComplete();
    };

    // Method 7: Check if localStorage has adblock flags
    const checkLocalStorage = () => {
      try {
        const adblockKeys = Object.keys(localStorage).filter(key => 
          key.toLowerCase().includes('adblock') || 
          key.toLowerCase().includes('adblocker') ||
          key.toLowerCase().includes('blockad')
        );
        if (adblockKeys.length > 0) {
          blockedCount++;
        }
      } catch (e) {
        // Ignore localStorage errors
      }
      checkComplete();
    };

    // Method 8: Check if specific ad classes are hidden
    const checkHiddenClasses = () => {
      const testDiv = document.createElement("div");
      testDiv.className = "google-ad ad-ad advertisement banner-ad";
      testDiv.style.position = "absolute";
      testDiv.style.left = "-9999px";
      document.body.appendChild(testDiv);

      setTimeout(() => {
        const computedStyle = window.getComputedStyle(testDiv);
        const isHidden = computedStyle.display === "none" || 
                        computedStyle.visibility === "hidden" ||
                        computedStyle.opacity === "0";
        
        document.body.removeChild(testDiv);
        if (isHidden) blockedCount++;
        checkComplete();
      }, 100);
    };

    let checksCompleted = 0;
    const checkComplete = () => {
      checksCompleted++;
      if (checksCompleted >= totalChecks) {
        // If 2 or more checks detect adblock, consider it blocked
        setIsAdblockDetected(blockedCount >= 2);
        setIsChecking(false);
      }
    };

    // Run all checks
    checkAdContainers();
    checkBlockedScripts();
    checkWindowProperties();
    checkElementRemoval();
    checkBlockedUrls();
    checkExtensionInjection();
    checkLocalStorage();
    checkHiddenClasses();
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
