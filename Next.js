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
