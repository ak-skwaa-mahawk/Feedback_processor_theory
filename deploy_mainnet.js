// scripts/deploy_mainnet.js
// AGŁL v26 — Deploy LandBackDAO to Ethereum Mainnet
const hre = require("hardhat");

async function main() {
  console.log("DEPLOYING TO ETHEREUM MAINNET — AGŁL v26");
  console.log("FLAMEHOLDER: John B. Carroll");
  console.log("ROOT: The Land Itself");
  console.log("=".repeat(70));

  const [deployer] = await hre.ethers.getSigners();
  console.log("Deployer:", deployer.address);
  console.log("Balance:", (await deployer.getBalance()).toString());

  const initialSupply = hre.ethers.parseEther("1000000"); // 1M DZHO

  const LandBackDAO = await hre.ethers.getContractFactory("LandBackDAO");
  console.log("Deploying contract...");
  
  const dao = await LandBackDAO.deploy(initialSupply);
  await dao.waitForDeployment();

  const address = await dao.getAddress();
  console.log("LANDBACKDAO DEPLOYED TO MAINNET:");
  console.log(`ADDRESS: ${address}`);
  console.log(`EXPLORER: https://etherscan.io/address/${address}`);
  console.log(`VERIFY: npx hardhat verify --network mainnet ${address} "${initialSupply}"`);

  // Notarize deployment
  const proof = await notarize_deployment(address);
  console.log(`PROOF: ${proof}`);
  console.log("=".repeat(70));
  console.log("THE ROOT IS LIVE.");
  console.log("THE LAND IS THE LEDGER.");
  console.log("THE FLAME IS ETERNAL.");
}

async function notarize_deployment(address) {
  const data = {
    "contract": "LandBackDAO",
    "address": address,
    "chain": "Ethereum Mainnet",
    "block": await hre.ethers.provider.getBlockNumber(),
    "timestamp": new Date().toISOString(),
    "flameholder": "John B. Carroll",
    "agłl": "v26"
  };
  const jsonData = JSON.stringify(data);
  const digest = require('crypto').createHash('sha256').update(jsonData).digest();
  const ots = require('opentimestamps');
  const detached = ots.DetachedTimestampFile.fromHash(new ots.Ops.OpSHA256(), digest);
  const calendar = new ots.Calendar('https://btc.calendar.opentimestamps.org');
  const timestamp = await calendar.submit(detached);
  const proofFile = `MAINNET_DEPLOY_${Date.now()}.ots`;
  require('fs').writeFileSync(proofFile, timestamp.serializeToBytes());
  return proofFile;
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});