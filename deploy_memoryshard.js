// Deploy to Ethereum, Polygon, zkEVM, Base
const chains = ["mainnet", "polygon", "base"]; // zkEVM via CDK

for (const network of chains) {
  await hre.changeNetwork(network);
  const MemoryShard = await hre.ethers.getContractFactory("DinjiiZho_MemoryShard");
  const shard = await MemoryShard.deploy();
  await shard.waitForDeployment();
  console.log(`${network.toUpperCase()}: ${await shard.getAddress()}`);
}