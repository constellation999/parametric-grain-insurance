# Parametric Grain-Price Insurance + Local Data DAO

Engineering scaffold for a **dual-trigger parametric insurance** product that protects the real purchasing power of food-insecure households (net food consumers and smallholders) against grain-price shocks.

**Important caveat (from critical review):**  
The current simulation has a known economic inversion (frequent small payouts, max payout < annual premium). It is useful as a code skeleton and design mapping, but **not** as evidence that the product “works”. See the critique section and recommended fixes below.

## Contents

### Core Simulation
| File | Description |
|------|-------------|
| `parametric_insurance_sim.py` | Main 20-year multi-region simulation (dual trigger, micropayments, donor match, forward contributions) |
| `optimize_triggers_premium.py` | Grid search + Differential Evolution for trigger thresholds & premium loading |
| `local_data_dao_sim.py` | Crowdsourced micro-index + peer verification + Schelling incentives |
| `trigger_premium_opt_top.csv` | Top parameter combinations from optimization |
| `local_dao_logs.csv` | Logs from Local Data DAO runs |

### Design Notes
| File | Description |
|------|-------------|
| `local_data_dao_design.md` | Local micro-index DAO mechanism, Schelling rewards, integration notes |
| `onocoy_integration_and_ui.md` | Onocoy (DePIN GNSS) linkage ideas + simple UI / proxy wallet design |

### UI & Presentation
| File | Description |
|------|-------------|
| `ui_mock/index.html` | Mobile-first mock (insurance status + Data DAO upload/verify/earn + agent mode) |
| `Parametric_Insurance_Presentation.pptx` | 14-slide deck summarizing the design + simulation results |
| `presentation.js` | Source used to generate the PPTX |

### Data / Plots (generated)
- `simulation_overview.png`, `cumulative_flows.png`
- `sim_data.npz`, `local_dao_data.npz`

## Key Design Elements (as implemented)

- **Dual trigger**: Leading (satellite composite) → partial payout; Confirming (price / wage-to-grain) → top-up
- Multi-region diversification (Kenya Rift / Malawi Central / Ethiopia Oromia)
- Micropayments via stablecoin + optional pay-at-harvest style
- Quadratic-style donor matching to improve take-up
- Forward contributions from exporters (currently simplified)
- Local Data DAO for micro-index (intended as complement to satellite)

## Known Limitations (Critical Review Summary)

1. **Economic inversion**: Max payout ($84–95) < annual premium ($159–181). Expected annual payout ≈ $127 implies frequent small triggers rather than true tail protection.
2. Primary metric used (CV of net cost) is secondary; the correct objective (“probability of severe shortfall / irreversible coping”) showed almost no improvement.
3. Single-run point estimates only — no Monte Carlo, no crisis-regime correlation, no reinsurance layer.
4. Take-up (42%) treated as exogenous despite high effective premium.
5. Local Data DAO currently has a conflict-of-interest risk if used for settlement triggers (beneficiaries reporting inputs that affect their own payouts). Better kept as audit / cross-validation layer.
6. Synthetic data only; no real FEWS NET / WFP / CHIRPS calibration yet.

## Recommended Next Steps (Priority Order)

1. Invert payout structure → true tail (higher attachment, max payout several× premium).
2. Change objective function to severe-shortfall probability reduction.
3. Full Monte Carlo + state-dependent correlation (t-copula / regime switching) + report P(ruin).
4. Endogenize take-up = f(net premium) using literature elasticities.
5. Properly price forward/option contributions from suppliers.
6. Demote Local Data DAO from settlement oracle to verification/audit role.
7. Re-calibrate on real price & weather series.

## How to Run

```bash
# Main insurance simulation
python parametric_insurance_sim.py

# Trigger / premium optimization
python optimize_triggers_premium.py

# Local Data DAO (Schelling micro-index)
python local_data_dao_sim.py
```

Open `ui_mock/index.html` in a browser for the interactive mock.

## License / Status

Private engineering prototype. Not production-ready. Built for design exploration and rapid iteration.
