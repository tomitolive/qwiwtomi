import { MetadataRoute } from 'next';
import fs from 'fs';
import path from 'path';

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://tomito.xyz';
  
  // Base URLs
  const routes = ['', '/genre/action', '/genre/adventure', '/genre/animation'].map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: 'daily' as const,
    priority: 1,
  }));

  try {
    const indexPath = path.join(process.cwd(), 'data', 'content_index.json');
    if (fs.existsSync(indexPath)) {
      const contentIndex = JSON.parse(fs.readFileSync(indexPath, 'utf8'));
      const contentRoutes = contentIndex.map((item: any) => ({
        url: `${baseUrl}/${item.folder}/${item.slug}`,
        lastModified: new Date(),
        changeFrequency: 'weekly' as const,
        priority: 0.8,
      }));
      return [...routes, ...contentRoutes];
    }
  } catch (error) {
    console.error('Error generating sitemap:', error);
  }

  return routes;
}
