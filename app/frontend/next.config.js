/** @type {import('next').NextConfig} */
let rawBackendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || '';
if (!rawBackendUrl.startsWith('http://') && !rawBackendUrl.startsWith('https://') && !rawBackendUrl.startsWith('/')) {
  rawBackendUrl = 'http://localhost:8000';
}
const backendUrl = rawBackendUrl.replace(/\/+$/, '');

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/proxy/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'X-Accel-Buffering', value: 'no' },
          { key: 'Cache-Control', value: 'no-cache, no-transform' },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
