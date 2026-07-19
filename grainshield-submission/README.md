# GrainShield — Dual-Trigger Parametric Insurance
### DDiB 2026 Final Group Project · Group XX <!-- TODO: group number & member names -->

Protecting the purchasing power of food-insecure households against staple-price
shocks, with a dual-stage parametric trigger (satellite → entitlement-ratio),
income-linked micropremiums, and a trigger-bound donor escrow.

**Platforms:** UZH Ethereum (PoC) · **Hedera testnet (deployed)** — see [`contracts/`](contracts/)

---

## Repository map

| Path | What it is |
|---|---|
| [`simulation/`](simulation/) | Real-data calibration + Monte Carlo pricing engine (`calibrate.py`, `sim.py`, `plots.py`) on WFP/HDX monthly maize prices |
| [`contracts/`](contracts/) | Solidity implementation of the five on-chain components, deployable to Hedera testnet (Hardhat + Hashio JSON-RPC relay). Deploy guide: [`contracts/DEPLOY.md`](contracts/DEPLOY.md) |
| [`docs/`](docs/) | Concept paper, mechanism explainer (step-by-step + brief), full simulation report, results summary |
| [`ui_mock/`](ui_mock/) | UI mock — member mode + village-agent (aggregator) mode |

## The design in one paragraph

A two-sided mutual (consumer up-side / producer down-side books partially net out).
A **dual-stage trigger** fires payouts: satellite indices (NDVI/CHIRPS/soil moisture)
release an early partial payment weeks before prices peak; a multi-source-median
entitlement ratio (USD import-parity price) confirms the main payout. Premiums are
skimmed as ~0.5% of income events with an automatic **crisis waiver**. Capital is a
four-layer stack — internal netting → hedger caps → reinsurance → donor first-loss +
**trigger-bound escrow** with contingent credit — where the escrow's on-chain
commitment (no admin can divert funds) is the load-bearing blockchain component.

## Headline results (1,000 Monte Carlo runs × 25 years)

| Metric | Value |
|---|---|
| P(fund ruin, 25y), full capital stack | **0.0%** |
| … without contingent-credit facility | **18.7%** ← the ablation that justifies the escrow layer |
| Distress-event (fire-sale proxy) reduction | **−72.9%** |
| Loss ratio median / p95 | 0.74 / 0.97 |
| Contingent facility drawn | 3.9% of runs |
| Donor $ per prevented distress event (50% subsidy) | ≈ $1,438 |

> **Version note:** the numbers above are from the **v2-realdata-optimization**
> configuration (4-country pool MWI+KEN+ETH+SOM, USD-series triggers,
> `region_select.py` pool optimization) presented in the deck. The `simulation/`
> folder must contain the v2 files at submission time; the v1 (3-country) results —
> ruin 0.4%, distress −55% — are reproducible with the same commands and are
> documented in `docs/simulation-report.md`.
> <!-- TODO before submission: copy local v2 files (incl. region_select.py,
>      updated calibration.json / sim_summary.json) into simulation/ -->

## Reproduce the simulation

```bash
cd simulation
pip install numpy pandas matplotlib
python3 calibrate.py     # WFP series -> episode-process calibration -> calibration.json
python3 sim.py           # 1,000 x 25y Monte Carlo -> sim_summary.json
python3 plots.py         # figures
# v2 additionally: python3 region_select.py   # pool frontier optimization
```

Runs in ~1 minute on a laptop. All randomness is seeded (`rng = default_rng(7)`).

## Deploy & demo the contracts (Hedera testnet)

```bash
cd contracts
npm install
cp .env.example .env     # add ECDSA key from portal.hedera.com
npx hardhat compile
npx hardhat run scripts/deploy.js --network hederaTestnet
# paste printed addresses into .env, then:
npx hardhat run scripts/demo.js --network hederaTestnet
```

`demo.js` walks the full lifecycle — enrollment → premium skim → Stage-1 satellite
trigger → early payout + **automatic premium waiver** → three median reports →
Stage-2 confirmation → main payout under the sim's formula
`pay = S · max(0, min(r, 2.25) − 1.25)` — verifiable on
[HashScan](https://hashscan.io/testnet).

Deployed addresses (Hedera testnet): <!-- TODO: paste after deployment -->

| Contract | Address |
|---|---|
| MockUSD | `0x…` |
| PolicyRegistry | `0x…` |
| TriggerOracle | `0x…` |
| PremiumStream | `0x…` |
| EscrowVault | `0x…` |
| PayoutRouter | `0x…` |

## Design claims ↔ code

| Claim (deck / concept paper) | Where it is enforced |
|---|---|
| "No admin function can divert funds outside the payout router" | `EscrowVault.sol` — no owner-withdraw exists; `release()` requires `msg.sender == payoutRouter` (immutable) **and** an active oracle trigger |
| "No single feed can fire a payout" | `TriggerOracle.sol` — Stage 2 needs a median over ≥3 permissioned reporters, and only while Stage 1 is active (multi-index conjunction) |
| Premium-waiver-by-code | `PremiumStream.onIncomeEvent()` skips collection and emits `PremiumWaived` while the region is in crisis |
| "No claims, no adjusters, no committees" | `PayoutRouter.execute*Payout()` are permissionless keeper functions |
| Four-layer waterfall | `PayoutRouter._fund()`: premium reserves → Seed → PremiumMatch → ContingentCredit |
| Fee floor: $0.03 daily skims need sub-cent fixed USD fees | Platform choice — Hedera's USD-denominated fees; see `docs/` platform assessment and `contracts/DEPLOY.md` |

## Known PoC ↔ production gaps (honest limitations)

- `MockUSD` stands in for a Stablecoin Studio HTS token (KYC/freeze flags).
- Oracle reporters are admin-registered addresses; production reads HCS-ordered attestations.
- Season resets (`resetRegion`, `resetAnnual`) are manual; production is epoch-based.
- Hedger caps and reinsurance recovery are off-chain legs, represented by escrow tranches.
- Council-permissioned governance weakens credible neutrality — flagged in the report's
  conclusions as the design's deepest unresolved tension.

## Authors

All authors conceived and designed the project. X.X. built the simulation and data
pipeline. Y.Y. implemented the smart contracts. Z.Z. developed the economic and
legal analysis. <!-- TODO: adapt to real contributions -->
