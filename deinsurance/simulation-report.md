# Consumer Staple-Price Protection: A Real-Data-Calibrated Feasibility Simulation

*Replaces the naive synthetic simulation. All price dynamics are calibrated to real WFP retail maize price series (HDX, 1998–2026); design follows the corrected principles: tail-weighted payouts, distress-reduction objective, full Monte Carlo with tail dependence, and the four-layer capital stack.*

## 1. Data and calibration (real, not synthetic)

Monthly national-median retail maize prices from WFP/HDX for **Malawi (18.4 usable years), Kenya (16.8y), Ethiopia (16.3y)**. For each month, the *excess ratio* is price over a trailing 36-month log-linear trend plus seasonal factors (no lookahead), which absorbs currency depreciation drift and seasonality and isolates crisis spikes. Episodes (excess > 1.25) found in the actual record:

| | episodes | freq (per yr) | mean duration | mean peak | max peak |
|---|---|---|---|---|---|
| Malawi | 8 | 0.43 (~1-in-2.3y) | 10.6 mo | 2.40× | 5.69× |
| Kenya | 6 | 0.36 (~1-in-2.8y) | 3.8 mo | 1.44× | 1.66× |
| Ethiopia | 4 | 0.25 (~1-in-4y) | 7.0 mo | 1.54× | 1.92× |

Two structural findings drive everything downstream. **(a) Malawi is a different risk class**: long, deep, partly macro-driven (kwacha devaluation pass-through) episodes make it ~3× as expensive to insure as the Horn countries. **(b) Tail dependence is real and cluster-shaped**: Kenya–Ethiopia crises co-occur far more than independence predicts (lift ≈ 3.3 — the Horn drought years 2011/2017/2022), while Malawi is broadly independent of both (lift 0.5–0.8, separate climate system). The Monte Carlo therefore uses a Horn-cluster common driver plus a global food-crisis regime (~1-in-8y, amplifying severities), not constant Gaussian correlation.

## 2. Corrected product design

Payouts begin at excess ratio 1.25 and scale with the excess up to 2.25, capped at 60% of annual staple spend (**sum insured $390/hh** against gross premiums of $35–131) — the tail-weighted inversion of the naive design, whose $84 cap sat *below* its $159 premium. A satellite-stage early payment ($35, detection 70%, false-positive 5%/yr) precedes the price-confirmed main payout. Premiums are priced per country at 1.35 × calibrated expected loss; donors match 50%. Take-up is **endogenous**, anchored to the field-experimental literature (Casaburi–Willis timing effects at the optimistic end; Cole et al. price sensitivity): ~62% at a net cost of 3% of staple spend, ~12% at 15%, ~2% at the naive sim's 24.5%.

## 3. Results (1,000 runs × 25 years)

**Pricing and demand.** Expected loss per household-year: Malawi $97, Kenya $26, Ethiopia $37. Net-of-subsidy premiums are 10.1% / 2.7% / 3.8% of staple spend, giving take-up of 28% / 60% / 57% and an insured pool of ~14,500 households per 30,000 eligible, with annual premium volume ≈ $0.86M.

**Solvency (the tail question the naive sim never asked).** With the full stack — donor seed 1.5× premium, aggregate stop-loss reinsurance attaching at 1.4× and exhausting at 6.5× premium (priced at 1.6× ceded EL ≈ $110K/yr), and a CAT-DDO-style contingent credit facility of 2.5× premium — **P(insolvency within 25y) = 0.4%**. Removing reinsurance raises it to 3.5%; removing the contingent facility (the first configuration tested) raised it to 18.7%, because Malawi's multi-year episodes defeat annually-attaching reinsurance — a direct quantitative vindication of the contingent-credit layer in the design. The facility is drawn in ~10% of runs (p95 draw $0.60M of $2.16M capacity). Median 25-year loss ratio 0.74, p95 1.02.

**Welfare (the correct objective).** Distress events — a 3-month rolling excess staple cost net of payouts exceeding 15% of annual income, the asset-fire-sale proxy motivated by the poverty-traps literature — fall from 0.058 to 0.026 per cohort-year: a **55% reduction in irreversibility-risk events**, achieved while median loss ratio stays below 1. (The naive sim's headline, cost-CV reduction, is not reported as a target: it is decoration.)

**Diversification, quantified.** A Horn-only pool (dropping Malawi) has P(insolvency) ≈ 0% and cheap premiums but abandons the population that needs protection most; including Malawi is affordable only because the stack prices it separately and backstops the multi-year tail. Portfolio spanning across climate systems (Southern Africa vs Horn) does real work: Malawi's near-independence from the Horn cluster is what keeps the pooled p95 loss ratio at 1.02.

**Funding composition (annual, steady state).** Household premiums 50% / donor match 50% of $0.86M premium flow; reinsurance premium $0.11M buys an expected recovery of $0.07M plus tail transfer; donor capital-at-risk consists of the $1.3M seed plus the $2.2M contingent commitment (fee 0.5%/yr), drawn with ~10% probability over 25 years. Over 25 years this is roughly: households 44%, donors 47% (match + seed + expected draws), reinsurance net transfers 9% — consistent with the CCRIF/ARC launch-phase benchmarks discussed previously.

## 4. Honest limitations

The Malawi excess ratio conflates real-purchasing-power crises with devaluation pass-through; a wage-deflated entitlement ratio (the design's actual confirming trigger) would require local wage series not in this dataset — the current trigger overstates payout frequency if wages partially track devaluation, so Malawi's EL is an upper bound. The satellite stage is stylized (detection probability, not actual CHIRPS/NDVI backtest). Take-up elasticity is literature-anchored but not estimated on this population. Basis risk within countries (household consumption heterogeneity, market-level dispersion around the national median) is not modeled and would degrade the distress-reduction figure; the aggregator-distribution layer exists precisely to absorb it. Hedger caps (Layer 1) are folded into reinsurance pricing rather than modeled as a separate counterparty. Twenty-five simulated years cannot capture climate-change nonstationarity in episode frequencies, which the calibration window (including 2022–25) partially and imperfectly reflects.

## 5. Verdict

Under real-data calibration, the corrected design clears the three feasibility bars the naive simulation failed: the product pays multiples of its premium in the states that matter (sum insured / net premium ≈ 6–22×), it measurably cuts irreversibility-risk events (−55%) rather than cosmetically smoothing costs, and the capital stack survives the actual tail (P(ruin) 0.4%, vs 18.7% without the contingent-credit layer whose necessity the simulation itself demonstrates). The binding fragilities are exactly where the earlier analysis predicted: Malawi-type macro-price entanglement (argues for import-parity or wage-ratio triggers), and demand at unsubsidized prices (argues for the blended premium and collection-timing design). Feasible, with the caveats stated — and now with the numbers attached.

## Files

`calibrate.py` (real-data calibration) · `sim.py` (Monte Carlo) · `plots.py` · `series_{country}.csv` (constructed monthly series) · `calibration.json` · `sim_summary.json` · figures 1–3.
