/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost', 'storage.routix.ai'],
  },
  experimental: {
    appDir: true,
  },
}

module.exports = nextConfig