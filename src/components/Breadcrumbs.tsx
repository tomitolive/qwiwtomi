import React from 'react';
import Link from 'next/link';

interface BreadcrumbItem {
  name: string;
  item: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ items }) => {
  return (
    <nav
      aria-label="breadcrumb"
      className="mt-5 mb-3 md:my-3 inline-flex items-center gap-1 rounded-full bg-white/5 px-4 py-2 md:py-1.5 text-base md:text-sm backdrop-blur-sm"
    >
      {items.map((item, index) => (
        <React.Fragment key={index}>
          {index > 0 && (
            <span className="text-gray-600 select-none text-xs mx-0.5">›</span>
          )}
          {index === items.length - 1 ? (
            <span className="text-gray-300 font-medium truncate max-w-[180px] sm:max-w-xs">
              {item.name}
            </span>
          ) : (
            <Link
              href={item.item}
              className="text-orange-400 hover:text-orange-300 transition-colors font-semibold shrink-0"
            >
              {item.name}
            </Link>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};

export default Breadcrumbs;
