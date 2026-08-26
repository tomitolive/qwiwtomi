import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  compress: true, // Enable gzip compression for all responses
  allowedDevOrigins: ['192.168.0.131'],
  async redirects() {
    return [
      // www → non-www redirect (fixes Bing "redirect URL" issue)
      {
        source: '/:path*',
        has: [{ type: 'host', value: 'www.tomit.click' }],
        destination: 'https://tomit.click/:path*',
        permanent: true,
      },
      // Genre slug fixes
      {
        source: '/genre/disney-plus',
        destination: '/genre/disney',
        permanent: true,
      },
      {
        source: '/genre/reality-tv',
        destination: '/genre/reality-talk',
        permanent: true,
      },
    ];
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "image.tmdb.org",
      },
    ],
  },
};

export default nextConfig;
