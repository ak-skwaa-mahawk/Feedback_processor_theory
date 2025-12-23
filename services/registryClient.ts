// 1. Get challenge
const { challenge_string } = await (await fetch(`${REGISTRY_URL}/pow-challenge`)).json();

// 2. Solve locally (simple loop)
let nonce = 0;
while (!verifyPow(challenge_string, nonce)) nonce++;

// 3. Submit with pow_nonce
await fetch(`${REGISTRY_URL}/aggregate`, {
  method: "POST",
  body: JSON.stringify({ ..., challenge_string, pow_nonce: nonce })
});
// In real version: POST to Soliton Registry API
export const mockLogAggregate = (packet: any) => {
  console.log("📜 Registry EEG_AGGREGATE (mock):", packet);
};

export const mockLogRevocation = (receipt: any) => {
  console.log("🔥 Registry EEG_REVOCATION (mock):", receipt);
};