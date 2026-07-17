# Staple-Price Protection — Real-Data Calibrated Design & Simulation

Corrected parametric insurance design for protecting the real purchasing power of food-insecure households against staple (maize) price shocks in Malawi, Kenya and Ethiopia.

This repository replaces an earlier synthetic simulation that had inverted economics (max payout < premium) and the wrong objective function. All price dynamics are now calibrated to real WFP retail maize series; the product is tail-weighted; solvency is evaluated with 1 000-run Monte Carlo that includes Horn-of-Africa cluster tail dependence and a global food-crisis regime.

## Quick Results

| Metric | Value |
|--------|-------|
| Expected loss / hh / yr | Malawi $97 · Kenya $26 · Ethiopia $37 |
| Net premium (50 % subsidy) | $66 / $18 / $25 |
| Take-up (endogenous) | 28 % / 60 % / 57 % |
| Distress-event reduction | **–55 %** |
| P(insolvency in 25 y) with full capital stack | **0.4 %** |
| Without contingent credit facility | 18.7 % |

Full numbers, region recommendations, pricing, fund composition and the narrow role of blockchain are in **[RESULTS_SUMMARY.md](RESULTS_SUMMARY.md)**.

## Repository Layout

```
├── README.md                          ← this file
├── RESULTS_SUMMARY.md                 ← optimal regions, pricing, parameters, fund, blockchain
├── simulation-report.md               ← full technical report
├── staple-price-protection-concept.md ← concept paper (architecture, incentives, theory)
├── mechanism-step-by-step.md          ← 12-step operational walkthrough
├── mechanism-brief.md                 ← one-page version of the mechanism
├── calibrate.py                       ← WFP data → excess-ratio episodes + co-occurrence
├── sim.py                             ← 1 000-run Monte Carlo (pricing + solvency + welfare)
├── plots.py                           ← figures
├── calibration.json                   ← calibrated frequencies, peaks, durations, lifts
├── sim_summary.json                   ← headline numbers
├── fig1_realdata_backtest.png
├── fig2_montecarlo_solvency.png
└── fig3_welfare_demand_funding.png
```

## How to Reproduce

```bash
# 1. Calibration (requires the original WFP CSVs; outputs calibration.json + series_*.csv)
python calibrate.py

# 2. Monte Carlo (reads calibration.json)
python sim.py
# → sim_summary.json, resfan.npy, lossratio*.npy

# 3. Figures
python plots.py
```

## Design Principles (Corrected)

1. **Tail-weighted payouts** — attachment 1.25, cap 2.25, sum insured ≈ $390 (several times net premium).
2. **Correct objective** — reduction in distress events (3-month rolling excess cost > 15 % of income), not cosmetic cost-CV.
3. **Full uncertainty** — 1 000 runs, state-dependent tail dependence, explicit P(insolvency), reinsurance + contingent credit.
4. **Endogenous take-up** — literature-anchored price elasticity.
5. **Four-layer capital stack** — internal netting → natural hedgers → exchange options → donor first-loss + CAT-DDO-style facility.
6. **Blockchain only where distrust binds** — trigger-bound escrow, stack composition, cheaper cat-bond issuance. Not for oracles, adjudication or last-mile delivery.

## Licence / Status

Research prototype. Not production software. Built for design validation and discussion.
