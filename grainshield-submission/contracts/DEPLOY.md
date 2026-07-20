contracts/
  MockUSD.sol        Test stablecoin (replaced by Stablecoin Studio / HTS in production)
  PolicyRegistry.sol Aggregator-mediated enrollment, Buyer/Seller classes, sum insured
  TriggerOracle.sol  Two-stage state machine (satellite Stage 1 → entitlement-median Stage 2)
  PremiumStream.sol  Income-linked 0.5% skim + automatic premium waiver during crises
  EscrowVault.sol    Three donor tranches, trigger-bound release (no admin withdrawal function)
  PayoutRouter.sol   pay = S·max(0, min(r, 2.25) − 1.25), waterfall funding
scripts/
  deploy.js          Deploys all six contracts + wires circular references
  demo.js            End-to-end demo: enroll → skim → Stage-1 early payout → waiver → Stage-2 main payout
Deployment Guide (Hedera Testnet)
0. Prerequisites

Node.js 18+
Hedera Portal account: https://portal.hedera.com

1. Create a testnet account (important: ECDSA)

Create a Testnet account on the Portal. Select ECDSA as the key type (ED25519 does not work with the EVM toolchain)
Copy the HEX Encoded Private Key
The Portal automatically grants 1,000 test HBAR (top up at faucet.hedera.com if needed — a few HBAR covers all gas)

2. Setup
bashnpm install
cp .env.example .env   # fill in OPERATOR_PRIVATE_KEY
npx hardhat compile
3. Deploy
bashnpx hardhat run scripts/deploy.js --network hederaTestnet
Copy the six printed addresses into MOCKUSD/REGISTRY/... in .env.
4. Verification (a demo you can show on HashScan)
bashnpx hardhat run scripts/demo.js --network hederaTestnet
Then search for the deployer address at https://hashscan.io/testnet →
the event sequence EarlyPayoutTriggered / PremiumWaived / MainPayoutConfirmed / MainPayout serves directly as screenshot material for the presentation.
Troubleshooting

insufficient funds → HBAR balance too low; use faucet.hedera.com
Nonce errors / timeouts → Hashio is a public relay; wait a few seconds and retry, or switch HEDERA_RPC_URL to an alternative relay such as Arkhia
Deployment fails with an ED25519 key → recreate the account with ECDSA (the most common pitfall)

Design-to-Code Mapping (for the report / presentation)
Design claimImplementation in code"No admin function can divert funds"EscrowVault has no owner-withdraw; release sends only to the immutable router address and requires oracle.isCrisisActive"No single feed can fire a payout"TriggerOracle: median over MIN_REPORTS = 3, and Stage 2 is only accepted while Stage 1 is active (conjunction)Premium waiver by codeDuring a crisis, PremiumStream.onIncomeEvent transfers nothing and emits PremiumWaived"No claims, no adjusters"PayoutRouter's execute* functions are permissionless (anyone-can-call keeper pattern)Waterfall_fund(): own reserves → Seed → PremiumMatch → ContingentCreditWhy HederaUSD-denominated fixed sub-cent fees make the $0.03/day skim economically viable (the fee-floor argument)
Gaps vs. Production (for the report's limitations section)

MockUSD → an HTS token issued via Stablecoin Studio (KYC / freeze flags)
Admin-registered reporters → ordered attestations on an HCS topic
Manual resetRegion / resetAnnual → epoch-based automation
Hedger caps and reinsurance recovery are off-chain legs (represented by escrow tranches in the PoC)
