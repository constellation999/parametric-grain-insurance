const hre = require("hardhat");

/** End-to-end demo on one deployer key (simulating all roles):
 *  1. Fund donor escrow (seed + match + contingent tranches)
 *  2. Register an aggregator; enroll a member (MWI, $54/mo spend, $390 cap)
 *  3. Skim a premium on an income event (0.5%)
 *  4. Fire Stage 1 (satellite) -> early payout $35; premium waiver kicks in
 *  5. Post 3 entitlement reports -> median >= 1.25 confirms Stage 2 -> main payout
 *  Numbers match Simulation_Summary.pdf: pay = S*max(0, min(r,2.25)-1.25).
 *
 *  Usage: ADDRESSES from deploy.js output ->
 *  npx hardhat run scripts/demo.js --network hederaTestnet
 */
const ADDR = {
  usd:      process.env.MOCKUSD,
  registry: process.env.REGISTRY,
  oracle:   process.env.ORACLE,
  router:   process.env.ROUTER,
  escrow:   process.env.ESCROW,
  stream:   process.env.STREAM,
};

const USD = (x) => BigInt(Math.round(x * 1e6)); // 6 decimals

async function main() {
  const [op] = await hre.ethers.getSigners();
  const usd = await hre.ethers.getContractAt("MockUSD", ADDR.usd);
  const reg = await hre.ethers.getContractAt("PolicyRegistry", ADDR.registry);
  const orc = await hre.ethers.getContractAt("TriggerOracle", ADDR.oracle);
  const rtr = await hre.ethers.getContractAt("PayoutRouter", ADDR.router);
  const esc = await hre.ethers.getContractAt("EscrowVault", ADDR.escrow);
  const stm = await hre.ethers.getContractAt("PremiumStream", ADDR.stream);

  const member = op.address;      // PoC: operator plays every role
  const MWI = 1;

  console.log("— 1. donor funds escrow tranches —");
  await (await usd.mint(op.address, USD(10_000))).wait();
  await (await usd.approve(ADDR.escrow, USD(3_000))).wait();
  await (await esc.deposit(0, USD(1_000))).wait(); // Seed
  await (await esc.deposit(1, USD(1_000))).wait(); // PremiumMatch
  await (await esc.deposit(2, USD(1_000))).wait(); // ContingentCredit
  console.log("escrow total:", (await esc.totalEscrowed()).toString());

  console.log("— 2. aggregator + member enrollment —");
  await (await reg.setAggregator(op.address, true)).wait();
  await (await reg.enroll(member, 1 /*Buyer*/, MWI, USD(54), USD(390))).wait();

  console.log("— 3. income event -> 0.5% skim —");
  await (await usd.approve(ADDR.stream, USD(100))).wait();
  await (await stm.onIncomeEvent(member, USD(20))).wait(); // skims $0.10
  console.log("router reserve:", (await usd.balanceOf(ADDR.router)).toString());

  console.log("— 4. Stage 1: satellite crossing -> early payout —");
  await (await orc.setReporter(op.address, true)).wait();
  await (await orc.postSatellite(MWI, 10_500)).wait(); // >= threshold
  await (await rtr.executeEarlyPayout(member)).wait();
  console.log("crisis active (waiver on):", await orc.isCrisisActive(MWI));
  await (await stm.onIncomeEvent(member, USD(20))).wait(); // -> PremiumWaived event

  console.log("— 5. Stage 2: three median reports at r=1.60 -> main payout —");
  // PoC has one reporter key; register two throwaway reporters via new wallets
  const r2 = hre.ethers.Wallet.createRandom().connect(hre.ethers.provider);
  const r3 = hre.ethers.Wallet.createRandom().connect(hre.ethers.provider);
  for (const w of [r2, r3]) {
    await (await op.sendTransaction({ to: w.address, value: hre.ethers.parseEther("2") })).wait();
    await (await orc.setReporter(w.address, true)).wait();
  }
  await (await orc.postEntitlement(MWI, 16_000)).wait();
  await (await orc.connect(r2).postEntitlement(MWI, 15_800)).wait();
  await (await orc.connect(r3).postEntitlement(MWI, 16_200)).wait(); // median 16000 -> confirm
  await (await rtr.executeMainPayout(member)).wait();
  // pay = 54 * (1.60 - 1.25) = $18.90; total with early = $53.90 <= $390 cap
  const m = await reg.getMember(member);
  console.log("paid out this year (6dp):", m.paidOutThisYear.toString());

  console.log("\nDemo complete — check HashScan for the event log.");
}

main().catch((e) => { console.error(e); process.exit(1); });
