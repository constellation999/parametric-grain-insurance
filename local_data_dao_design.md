# Local Micro-Index DAO – Design Notes (Legacy / Complementary)

> **Status note (July 2026):** This document describes an experimental crowdsourced micro-index layer explored earlier. In the corrected design (`deinsurance/`), local crowdsourced data is **explicitly limited to verification and audit**. It is **not** used as a settlement trigger, precisely to avoid the conflict of interest of beneficiaries reporting inputs that affect their own payouts. The primary feasibility results and capital-stack analysis live in `deinsurance/`.

## Goal
Complement coarse satellite (macro) indices with crowdsourced, peer-verified local (micro) observations for cross-validation and basis-risk diagnostics at village / grid level.

## Mechanism (implemented in earlier simulation)

### 1. Crowdsourcing
- Agents (farmers, local investigators) upload field photos, rain-gauge readings, or crop-stress severity scores.
- Each upload requires a PROTO stake.

### 2. Peer verification (Schelling)
- Other agents vote; consensus = median.
- Voters / uploaders who match consensus are rewarded; dissenters lose stake.

### 3. Aggregation
- Per-grid quality-weighted consensus forms a micro-index used only for **audit / cross-check**, never for automatic settlement.

### 4. Simulation results (illustrative)
Micro-index correlated highly with synthetic truth and reduced a basis-risk proxy when blended, but this was under an honesty-rate assumption. The incentive problem remains if the same agents are also insurance beneficiaries.

## Recommended role in the corrected architecture
- **Allowed:** post-event audit, index quality monitoring, input to quadratic-funding rounds for better measurement infrastructure.
- **Forbidden for settlement:** any direct input into the trigger that releases payouts.

See `deinsurance/RESULTS_SUMMARY.md` and `deinsurance/staple-price-protection-concept.md` for the current design stance on oracles and blockchain.
