const REGISTRY_URL = process.env.REGISTRY_URL || 'http://localhost:8000'; // your Python REPL endpoint

export async function getRegistryHash(resourceType: string, resourceId?: string): Promise<string> {
  const query = `SHOW HASH FOR ${resourceType} ${resourceId || ''}`.trim();
  
  const res = await fetch(`${REGISTRY_URL}/sql`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
    next: { revalidate: 30 } // soft cache
  });

  const data = await res.json();
  return data.hash || '0000000000000000000000000000000000000000000000000000000000000000';
}

import { getRegistryHash } from '@/lib/registry-hash';

export default async function LicensesPage() {
  const currentHash = await getRegistryHash('LICENSE', 'GTC001');

  // Use hash as cache key
  const licenses = await fetch('/api/licenses', {
    headers: { 'x-registry-hash': currentHash },
    next: { tags: ['licenses'], revalidate: false } // revalidate only on hash change
  }).then(r => r.json());

  return <LicenseList licenses={licenses} />;
}