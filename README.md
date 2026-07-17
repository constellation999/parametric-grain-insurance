# Parametric Staple-Price Protection

**Corrected, real-data-calibrated design** for protecting food-insecure households against maize-price shocks in Malawi, Kenya and Ethiopia.

The earlier synthetic simulation (still present in the root for historical reference) had inverted economics and the wrong objective. All current results live in the **`deinsurance/`** folder.

## Start here

→ **[deinsurance/RESULTS_SUMMARY.md](deinsurance/RESULTS_SUMMARY.md)**  
Optimal regions · Pricing · Parameters · Fund composition · Blockchain role

→ **[deinsurance/README.md](deinsurance/README.md)**  
Quick results table and how to reproduce the Monte Carlo

→ **[deinsurance/simulation-report.md](deinsurance/simulation-report.md)** (full technical report)  
→ **[deinsurance/staple-price-protection-concept.md](deinsurance/staple-price-protection-concept.md)** (concept paper)

## Headline numbers (1 000 runs × 25 years, WFP-calibrated)

| Metric | Value |
|--------|-------|
| Expected loss / hh / yr | Malawi $97 · Kenya $26 · Ethiopia $37 |
| Net premium (50 % subsidy) | $66 / $18 / $25 |
| Take-up (endogenous) | 28 % / 60 % / 57 % |
| Distress-event reduction | **–55 %** |
| P(insolvency 25 y) with full stack | **0.4 %** |
| Without contingent credit | 18.7 % |

## Design principles now implemented

1. Tail-weighted payouts (attachment 1.25, cap 2.25, sum insured ≈ $390)
2. Correct objective: reduction in irreversibility-risk (distress) events
3. Full Monte Carlo with Horn-cluster tail dependence + global food-crisis regime
4. Endogenous take-up from literature price elasticities
5. Four-layer capital stack including CAT-DDO-style contingent credit
6. Blockchain used only as trigger-bound escrow and stack-composition substrate

## Legacy material (root)

The original synthetic simulation, Local Data DAO experiments, UI mock and Onocoy notes remain in the repository root for reference. They are superseded by the `deinsurance/` package for any feasibility claim.
