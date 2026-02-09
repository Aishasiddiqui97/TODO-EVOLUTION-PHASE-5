/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  images: {
    unoptimized: true,
  },

  // Enable Turbopack support while keeping legacy webpack config for dev
  turbopack: {},

  // Use webpack mode to avoid Turbopack WebSocket issues
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      // Use polling instead of WebSocket for file watching in some environments
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