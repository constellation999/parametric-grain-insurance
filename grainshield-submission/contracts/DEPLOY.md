# GrainShield — Hedera PoC (DDiB 2026)
A PoC that implements the 5 components of a dual-trigger parametric insurance (Deck §3 Architecture) in Solidity and deploys them to the Hedera Testnet (EVM compatible).

```text
contracts/
  MockUSD.sol        Stablecoin for testing (will be replaced by Stablecoin Studio / HTS in production)
  PolicyRegistry.sol Enrollment via aggregator, 2 classes (Buyer/Seller), sum insured
  TriggerOracle.sol  Two-stage state machine (Satellite Stage 1 → Entitlement Median Stage 2)
  PremiumStream.sol  Income-linked 0.5% skim + automatic premium waiver during a crisis
  EscrowVault.sol    3 donor tranches, trigger-bound release (no admin withdrawal function)
  PayoutRouter.sol   pay = S·max(0, min(r,2.25)−1.25), waterfall allocation
scripts/
  deploy.js          Deployment of the 6 contracts + wiring of circular references
  demo.js            End-to-end demo: Enrollment → Skim → Stage 1 Early Payout → Waiver → Stage 2 Main Payout
```

## Deployment Steps (Hedera Testnet)

### 0. Prerequisites
- Node.js 18+
- Hedera Portal account: https://portal.hedera.com

### 1. Testnet Account Creation (Important: ECDSA)
1. Create a Testnet account in the Portal. **Select ECDSA for the key type** (ED25519 cannot be used with the EVM toolchain).
2. Copy the HEX Encoded Private Key.
3. The Portal automatically grants 1000 test HBAR (if you need more, use faucet.hedera.com — gas only requires a few HBAR).

### 2. Setup
```bash
npm install
cp .env.example .env   # Enter your OPERATOR_PRIVATE_KEY
npx hardhat compile
```

### 3. Deployment
```bash
npx hardhat run scripts/deploy.js --network hederaTestnet
```
Enter the 6 output addresses into `MOCKUSD`/`REGISTRY`/... in your `.env` file.

### 4. Verification (Demo for HashScan)
```bash
npx hardhat run scripts/demo.js --network hederaTestnet
```
Afterward, search for the deployer address on https://hashscan.io/testnet → The sequence of events (`EarlyPayoutTriggered` / `PremiumWaived` / `MainPayoutConfirmed` / `MainPayout`) can be used directly as screenshot material for your presentation.

### Troubleshooting
- **insufficient funds** → Insufficient HBAR balance. Use faucet.hedera.com.
- **nonce error / timeout** → Hashio is a public relay. Wait a few seconds and retry, or change the `HEDERA_RPC_URL` to an alternative relay like Arkhia.
- **Deployment fails with ED25519 key** → Recreate an ECDSA account (the most common pitfall).

## Design Mapping (For Report/Presentation)

| Claims in the Deck | Implementation in Code |
|---|---|
| "no admin function can divert funds" | `owner-withdraw` does not exist in EscrowVault. `release` is only routed to the immutable router + `oracle.isCrisisActive` is required. |
| "no single feed can fire a payout" | TriggerOracle: Median of `MIN_REPORTS=3`, and Stage 2 is not accepted unless Stage 1 is active (conjunction). |
| premium-waiver-by-code | `PremiumStream.onIncomeEvent` does not transfer during a crisis and emits `PremiumWaived`. |
| "no claims, no adjusters" | `execute*` in PayoutRouter is permissionless (keeper pattern that anyone can execute). |
| Waterfall | `_fund()`: Self-Reserves → Seed → PremiumMatch → ContingentCredit. |
| Reason for selecting Hedera | Fees are fixed in USD at sub-cents → A $0.03/day skim is viable (fee-floor argument). |

## Differences from Production (Include in report's limitations)
- MockUSD → Stablecoin Studio HTS token (KYC/freeze flags).
- Admin registration of Reporters → Ordered attestation using HCS topics.
- Manual `resetRegion` / `resetAnnual` → Epoch-based automation.
- Hedger caps and reinsurance recoveries are off-chain legs (substituted by escrow tranches).
