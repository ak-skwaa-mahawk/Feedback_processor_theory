// scripts/deploy_base.js
const hre = require("hardhat");

async function main() {
  console.log("DEPLOYING TO BASE — AGŁL v29");
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deployer:", deployer.address);

  const mainnetDAO = "0xLANDback1234567890abcdef1234567890abcdef12";

  const LandBackDAO_Base = await hre.ethers.getContractFactory("LandBackDAO_Base");
  const dao = await LandBackDAO_Base.deploy(mainnetDAO);
  await dao.waitForDeployment();

  const address = await dao.getAddress();
  console.log("LANDBACKDAO_BASE DEPLOYED:");
  console.log(`ADDRESS: ${address}`);
  console.log(`EXPLORER: https://basescan.org/address/${address}`);
  console.log(`VERIFY: npx hardhat verify --network base ${address} "${mainnetDAO}"`);

  // Notarize
  const proof = await notarize_base(address);
  console.log(`PROOF: ${proof}`);
}

async function notarize_base(address) {
  const data = { contract: "LandBackDAO_Base", address, chain: "Base", agłl: "v29" };
  const jsonData = JSON.stringify(data);
  const digest = require('crypto').createHash('sha256').update(jsonData).digest();
  const ots = require('opentimestamps');
  const detached = ots.DetachedTimestampFile.fromHash(new ots.Ops.OpSHA256(), digest);
  const calendar = new ots.Calendar('https://btc.calendar.opentimestamps.org');
  const timestamp = await calendar.submit(detached);
  const proofFile = `BASE_DEPLOY_${Date.now()}.ots`;
  require('fs').writeFileSync(proofFile, timestamp.serializeToBytes());
  return proofFile;
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});