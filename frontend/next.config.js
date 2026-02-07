/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  images: {
    unoptimized: true,
  },

  // Use webpack mode to avoid Turbopack WebSocket issues
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      // Use polling instead of WebSocket for file watching
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
        ignored: /node_modules/,
      };
    }
    return config;
  },
};

module.exports = nextConfig;