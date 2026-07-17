# Local Micro-Index DAO – Design & Implementation Status

## Goal
Complement coarse satellite (macro) indices with crowdsourced, peer-verified local (micro) observations so that the parametric insurance dual-trigger has lower basis risk at village / grid level.

## Mechanism (implemented in simulation)

### 1. Crowdsourcing
- Agents (farmers, local investigators) upload:
  - Field photos
  - Rain-gauge readings
  - Crop-stress severity score (0–1)
- Each upload requires a PROTO stake.

### 2. Peer verification (Schelling)
- Other agents vote on the severity / accuracy of each upload.
- Consensus = median of votes (robust to outliers).
- Minimum votes + agreement threshold required for a valid consensus.
- **Schelling incentive**:
  - Voters whose vote is close to the eventual consensus receive full stake return + share of the verification reward pool.
  - Voters far from consensus lose most of their stake.
  - Uploaders are scored by how close their report was to the consensus; high-quality + high-stake uploads receive the larger share of the uploader reward pool.

### 3. Aggregation → Micro-index
- Per grid, stake- and quality-weighted consensus values form the micro-index for that window.
- Missing grids fall back to pure satellite.
- Final insurance trigger uses a blend:  
  `blended = 0.55 × micro + 0.45 × satellite` (when micro available).

### 4. Simulation results (80 agents, 24 windows, 6 grids)
| Metric | Value |
|--------|-------|
| Micro-index vs true state correlation | **0.991** |
| MAE (micro) | 0.025 |
| Coverage | 100% of grid-windows |
| Satellite-only MAE | 0.157 |
| Blended MAE | **0.073** (53% better) |
| Honest agent balance growth | **+86 PROTO** |
| Dishonest agent balance growth | **–16 PROTO** |

Honest reporting is strongly rewarded; random/strategic reporting is punished. The blended index materially reduces the basis-risk proxy.

## Token economics (PROTO)
- External reward pool per window (can be funded by insurance loading, donors, or mild inflation).
- 55% → accurate uploaders  
- 45% → correct verifiers  
- Stake is returned in full only on successful consensus participation.

## On-chain architecture (proposed)
- Solana (alignment with Onocoy) or cheap L2.
- Core accounts:
  - `Observation` (uploader, grid, hash of photo/IPFS, severity, stake, timestamp)
  - `Vote` (voter, observation, score, stake)
  - `Consensus` (final median, participants, rewards distributed)
- Off-chain: photo storage (IPFS / Arweave), lightweight reputation.
- Optional: Onocoy quality flags or precise location can be attached to an observation for extra weight.

## UI (implemented)
`ui_mock/index.html` now contains a full **Data DAO** tab with:
- Upload flow (photo, severity slider, stake)
- Verify flow (pending items, severity vote or agree/disagree)
- Earn / balance view + short Schelling explanation

## Integration with main insurance
- Micro-index becomes an additional input to the **leading stage**.
- Higher local confidence can lower the satellite threshold or increase the partial payout fraction for that grid.
- Participants who contribute high-quality data can receive premium discounts paid in PROTO or stablecoin.

## Important design note (from critical review)
If used as a *settlement* trigger, this creates a conflict of interest (beneficiaries reporting data that affects their own payouts). Recommended role: **verification / audit / cross-validation layer only**, not the primary settlement oracle.

## Next concrete steps
1. Wire the micro-index output into the main `parametric_insurance_sim.py` dual-trigger.
2. Write a minimal Solana/Anchor or Solidity interface for Observation → Vote → Consensus → Reward.
3. Add photo-hash + simple reputation score.
4. Pilot with 1–2 real villages (USSD fallback + agent-assisted uploads).
