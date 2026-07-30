import React from 'react';

interface BreadcrumbItem {
  name: string;
  item: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ items }) => {
  return (
    <nav className="breadcrumb mb-6 flex items-center gap-2 text-sm text-gray-400">
      {items.map((item, index) => (
        <React.Fragment key={index}>
          {index > 0 && <span className="text-gray-500">/</span>}
          {index === items.length - 1 ? (
            <span className="text-white font-bold">{item.name}</span>
          ) : (
            <a href={item.item} className="text-gray-300 hover:text-orange-500 transition-colors">
              {item.name}
            </a>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};

export default Breadcrumbs;
