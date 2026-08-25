import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ['192.168.0.131'],
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "image.tmdb.org",
      },
    ],
  },
  async redirects() {
    return [
      {
        source: "/:path*",
        has: [
          {
            type: "host",
            value: "www.tomit.click",
          },
        ],
        destination: "https://tomit.click/:path*",
        permanent: true,
      },
      {
        source: "/:path*",
        has: [
          {
            type: "host",
            value: "tomito.xyz",
          },
        ],
        destination: "https://tomit.click/:path*",
        permanent: true,
      },
      {
        source: "/:path*",
        has: [
          {
            type: "host",
            value: "www.tomito.xyz",
          },
        ],
        destination: "https://tomit.click/:path*",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
