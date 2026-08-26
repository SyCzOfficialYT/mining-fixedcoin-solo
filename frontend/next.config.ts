import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  async rewrites() {
    return [{ source: '/api/:path*', destination: 'http://fixedcoin-solo:5051/api/:path*' }];
  },
};

export default nextConfig;
