const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with:", deployer.address);

  const initialSupply = hre.ethers.parseEther("1000000"); // 1M tokens

  const LandBackDAO = await hre.ethers.getContractFactory("LandBackDAO");
  const dao = await LandBackDAO.deploy(initialSupply);

  await dao.waitForDeployment();
  console.log("LandBackDAO deployed to:", await dao.getAddress());

  // Verify on Etherscan (manual step)
  console.log("Verify on Sepolia Etherscan: https://sepolia.etherscan.io/address/" + await dao.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});