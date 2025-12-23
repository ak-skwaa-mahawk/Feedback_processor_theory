// In real version: POST to Soliton Registry API
export const mockLogAggregate = (packet: any) => {
  console.log("📜 Registry EEG_AGGREGATE (mock):", packet);
};

export const mockLogRevocation = (receipt: any) => {
  console.log("🔥 Registry EEG_REVOCATION (mock):", receipt);
};