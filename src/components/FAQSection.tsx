"use client";

import { useState } from "react";

interface FAQSectionProps {
  faq: any[];
}

export default function FAQSection({ faq }: FAQSectionProps) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="bg-transparent border border-zinc-800 p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-orange-500">
            <circle cx="12" cy="12" r="10"/>
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          الأسئلة الشائعة
        </h2>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="text-orange-500 hover:text-orange-400 transition-colors"
        >
          <svg 
            width="24" 
            height="24" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2"
            className={`transform transition-transform ${isOpen ? 'rotate-180' : ''}`}
          >
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </button>
      </div>
      {isOpen && (
        <div className="space-y-3">
          {faq.map((item: any, index: number) => (
            <div key={index} className="border-b border-zinc-700 pb-3 last:border-0">
              {/* Arabic / Default FAQ */}
              <h3 className="text-white font-semibold mb-2">{item.q || item.question}</h3>
              <p className="text-gray-300 text-sm leading-relaxed mb-3">{item.a || item.answer}</p>
              
              {/* English FAQ (if exists) */}
              {item.q_en && item.a_en && (
                <div className="bg-zinc-800/30 rounded p-3 mt-2 border border-zinc-700/50" dir="ltr" style={{ fontFamily: 'var(--font-inter)' }}>
                  <h4 className="text-white text-sm font-semibold mb-1 flex items-center gap-2">
                     <span className="bg-orange-500/20 text-orange-400 text-[10px] px-1.5 py-0.5 rounded font-bold">EN</span>
                     {item.q_en}
                  </h4>
                  <p className="text-gray-400 text-xs leading-relaxed">{item.a_en}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
