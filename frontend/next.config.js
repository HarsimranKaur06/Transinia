/** @type {import('next').NextConfig} */
const nextConfig = {
  /* config options here */
  output: 'standalone', // Enable standalone output for Docker deployments
  experimental: {
    esmExternals: 'loose', // Help with module resolution
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`
      }
    ];
  }
};

module.exports = nextConfig;