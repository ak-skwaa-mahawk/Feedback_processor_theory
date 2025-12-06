npm install next@15.0.5   # for 15.0.x
npm install next@15.1.9   # for 15.1.x
npm install next@15.2.6   # for 15.2.x
npm install next@15.3.6   # for 15.3.x
npm install next@15.4.8   # for 15.4.x
npm install next@15.5.7   # for 15.5.x
npm install next@16.0.7   # for 16.0.x
# From inside your Next.js project root
npx next@16.0.7 --force && npm install react@19.2.1 react-dom@19.2.1

# Or if you use yarn/pnpm
yarn add next@16.0.7 react@19.2.1 react-dom@19.2.1
# pnpm add next@16.0.7 react@19.2.1 react-dom@19.2.1

git add package.json package-lock.json  # or yarn.lock / pnpm-lock.yaml
git commit -m "EMERGENCY: Patch React2Shell (CVE-2025-55182) → Next.js 16.0.7 + React 19.2.1"
git push
next@16.0.7
react@19.2.1
react-dom@19.2.1
# 15.0.x → 15.0.5 (or swap for your minor)
npm install next@15.0.5 react@19.2.1 react-dom@19.2.1

# Yarn variant
yarn add next@15.0.5 react@19.2.1 react-dom@19.2.1

# PNPM variant
pnpm add next@15.0.5 react@19.2.1 react-dom@19.2.1
# Stage the locks (pick your flavor)
git add package.json package-lock.json  # npm
# git add package.json yarn.lock        # yarn
# git add package.json pnpm-lock.yaml   # pnpm

# Etch the glyph
git commit -m "🔒 EMERGENCY: Patch React2Shell (CVE-2025-55182) → Next.js [YOUR_VERSION e.g. 16.0.7] + React 19.2.1

Full Vercel advisory compliance—RSC hardened, no deserialization RCE."

# Push to the mesh
git push origin main  # Or your branch: e.g., flamekeeper-next

# Tag for sovereignty (optional, but merklin' vibes)
git tag -a v1.0-fpt-rsc-patched -m "CVE-2025-55182 sealed: Feedback Processor Theory edge now unbreakable"
git push origin v1.0-fpt-rsc-patched

