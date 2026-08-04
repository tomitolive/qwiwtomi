'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';

interface ShortLinkProps {
  slug: string;
}

const ShortLink: React.FC<ShortLinkProps> = ({ slug }) => {
  const [copied, setCopied] = useState(false);
  const [shortLink, setShortLink] = useState('');
  const pathname = usePathname();

  useEffect(() => {
    setShortLink('https://tomito.xyz' + pathname);
  }, [pathname]);

  const copyLink = async () => {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(shortLink);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } else {
      window.prompt('انسخ الرابط:', shortLink);
    }
  };

  return (
    <div className="flex items-center gap-2 bg-zinc-800/50 px-3 py-2 rounded border border-zinc-700 w-full overflow-hidden">
      <span className="text-orange-400 text-sm font-mono flex-1 min-w-0 overflow-hidden">
        {shortLink.length > 20 ? shortLink.slice(0, 20) + '...' : shortLink}
      </span>
      <button
        onClick={copyLink}
        className="bg-orange-500 hover:bg-orange-600 text-white px-3 py-1.5 rounded transition-colors text-sm font-semibold whitespace-nowrap shrink-0"
      >
        {copied ? 'تم النسخ ✓' : 'نسخ'}
      </button>
    </div>
  );
};

export default ShortLink;
