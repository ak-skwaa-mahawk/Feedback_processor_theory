/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverActions: true,  // Keep enabled, but hardened by the dep update
    allowedOrigins: process.env.NODE_ENV === 'production' ? ['your-fpt-backend-domain.com'] : undefined
  },
  // Your existing config (e.g., for Tailwind or custom webpack if bridging to quantum_bridge.py)
};

module.exports = nextConfig;