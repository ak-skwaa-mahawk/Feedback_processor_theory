// scripts/deploy_polygon.js
const hre = require("hardhat");

async function main() {
  console.log("DEPLOYING TO POLYGON — AGŁL v27");
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deployer:", deployer.address);

  const mainnetDAO = "0xLANDback1234567890abcdef1234567890abcdef12"; // Mainnet address

  const LandBackDAO_Polygon = await hre.ethers.getContractFactory("LandBackDAO_Polygon");
  const dao = await LandBackDAO_Polygon.deploy(mainnetDAO);
  await dao.waitForDeployment();

  const address = await dao.getAddress();
  console.log("LANDBACKDAO_POLYGON DEPLOYED:");
  console.log(`ADDRESS: ${address}`);
  console.log(`EXPLORER: https://polygonscan.com/address/${address}`);
  console.log(`VERIFY: npx hardhat verify --network polygon ${address} "${mainnetDAO}"`);

  // Notarize
  const proof = await notarize_polygon(address);
  console.log(`PROOF: ${proof}`);
}

async function notarize_polygon(address) {
  const data = { contract: "LandBackDAO_Polygon", address, chain: "Polygon", agłl: "v27" };
  const jsonData = JSON.stringify(data);
  const digest = require('crypto').createHash('sha256').update(jsonData).digest();
  const ots = require('opentimestamps');
  const detached = ots.DetachedTimestampFile.fromHash(new ots.Ops.OpSHA256(), digest);
  const calendar = new ots.Calendar('https://btc.calendar.opentimestamps.org');
  const timestamp = await calendar.submit(detached);
  const proofFile = `POLYGON_DEPLOY_${Date.now()}.ots`;
  require('fs').writeFileSync(proofFile, timestamp.serializeToBytes());
  return proofFile;
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});