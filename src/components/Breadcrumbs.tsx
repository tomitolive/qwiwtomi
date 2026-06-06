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
    <nav className="breadcrumb mb-6 flex items-center gap-2 text-sm text-muted">
      {items.map((item, index) => (
        <React.Fragment key={index}>
          {index > 0 && <span className="opacity-30">/</span>}
          {index === items.length - 1 ? (
            <span className="text-white font-bold">{item.name}</span>
          ) : (
            <a href={item.item} className="hover:text-primary transition-colors">
              {item.name}
            </a>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};

export default Breadcrumbs;
