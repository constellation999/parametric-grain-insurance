const hre = require("hardhat");

/** Deploys the full GrainShield stack and wires the circular references:
 *  MockUSD -> PolicyRegistry -> TriggerOracle -> PayoutRouter -> EscrowVault -> PremiumStream
 */
async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deployer:", deployer.address);
  console.log("Balance:", (await hre.ethers.provider.getBalance(deployer.address)).toString());

  const MockUSD = await hre.ethers.deployContract("MockUSD");
  await MockUSD.waitForDeployment();
  console.log("MockUSD:        ", await MockUSD.getAddress());

  const Registry = await hre.ethers.deployContract("PolicyRegistry");
  await Registry.waitForDeployment();
  console.log("PolicyRegistry: ", await Registry.getAddress());

  const Oracle = await hre.ethers.deployContract("TriggerOracle");
  await Oracle.waitForDeployment();
  console.log("TriggerOracle:  ", await Oracle.getAddress());

  const Router = await hre.ethers.deployContract("PayoutRouter", [
    await MockUSD.getAddress(),
    await Registry.getAddress(),
    await Oracle.getAddress(),
  ]);
  await Router.waitForDeployment();
  console.log("PayoutRouter:   ", await Router.getAddress());

  const Escrow = await hre.ethers.deployContract("EscrowVault", [
    await MockUSD.getAddress(),
    await Oracle.getAddress(),
    await Router.getAddress(),
  ]);
  await Escrow.waitForDeployment();
  console.log("EscrowVault:    ", await Escrow.getAddress());

  const Stream = await hre.ethers.deployContract("PremiumStream", [
    await MockUSD.getAddress(),
    await Registry.getAddress(),
    await Oracle.getAddress(),
    await Router.getAddress(), // premiums flow into the router = reserve pool
  ]);
  await Stream.waitForDeployment();
  console.log("PremiumStream:  ", await Stream.getAddress());

  // wire circular references (one-shot setters)
  await (await Router.setEscrow(await Escrow.getAddress())).wait();
  await (await Registry.setPayoutRouter(await Router.getAddress())).wait();
  console.log("\nWiring complete. Save these addresses for demo.js / the report.");
}

main().catch((e) => { console.error(e); process.exit(1); });
