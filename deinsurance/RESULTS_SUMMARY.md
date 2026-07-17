# Results Summary: Optimal Regions, Pricing, Parameters, Fund Structure & Blockchain Role

*Based on the real-data-calibrated Monte Carlo simulation (1,000 runs × 25 years) using WFP maize price series for Malawi, Kenya and Ethiopia. This replaces the earlier synthetic simulation that suffered from inverted payout economics and wrong objective metrics.*

---

## 1. Optimal Region Selection

| Region     | Risk Class                          | EL / hh / yr | Recommendation |
|------------|-------------------------------------|--------------|----------------|
| **Kenya**  | Horn cluster, moderate frequency    | $26.3       | Core inclusion – high take-up, low capital intensity |
| **Ethiopia** | Horn cluster, lower frequency     | $37.1       | Core inclusion – co-moves with Kenya (lift ≈ 3.3) |
| **Malawi** | Southern, long deep episodes        | $97.3       | Include with separate pricing + stronger backstop; ~3× more expensive |

**Key findings**
- Kenya–Ethiopia form a natural **Horn cluster** with strong tail dependence (joint crisis probability far above independence).
- Malawi is nearly independent of the Horn (lift 0.5–0.8) and belongs to a different climate system. Including it provides genuine diversification value for the pool’s p95 loss ratio.
- A Horn-only pool has near-zero insolvency risk and cheap premiums, but abandons the population that needs protection most (Malawi’s multi-year, high-peak episodes).
- **Recommended portfolio**: all three countries, with Malawi priced and capitalised separately inside the same multi-country facility.

---

## 2. Pricing

Premiums are set at **1.35 × calibrated expected loss** (loading for expenses + contingency). Donors match 50 % of the loaded premium.

| Country   | Gross premium / hh / yr | Net of subsidy | % of staple spend | Endogenous take-up |
|-----------|--------------------------|----------------|-------------------|--------------------|
| Malawi    | $131.3                  | $65.7         | 10.1 %           | 28 %              |
| Kenya     | $35.5                   | $17.7         | 2.7 %            | 60 %              |
| Ethiopia  | $50.0                   | $25.0         | 3.8 %            | 57 %              |

- Take-up is **endogenous**, anchored to field-experimental literature (Casaburi–Willis, Cole et al.).
- At the naïve simulation’s ~24.5 % of spend, take-up collapses to ~2 % — confirming that the earlier high-premium design was demand-infeasible.
- Aggregate annual premium volume for 30 000 eligible households: **≈ $865 000**.

**Product parameters that drive pricing**
- Attachment: excess ratio 1.25  
- Cap: excess ratio 2.25  
- Sum insured: 60 % of annual staple spend ≈ **$390 / household**  
- Early (satellite) stage: $35 partial payout, 70 % detection rate, 5 % false-positive rate per year  

This produces a true tail product: sum insured / net premium ranges from **6× (Malawi) to 22× (Kenya)**.

---

## 3. Key Simulation Parameters

```text
Attachment point          1.25 × trend
Cap ratio                 2.25 × trend
Sum insured               $390 / hh
Early payout              $35
Loading                   1.35
Donor subsidy             50 % of loaded premium
Reinsurance attachment    1.4 × annual premium income
Reinsurance exhaustion    6.5 × annual premium income
Reinsurance pricing       1.6 × expected ceded loss
Seed capital              1.5 × annual premium
Contingent facility       2.5 × annual premium (CAT-DDO style, 0.5 % p.a. fee)
Monte Carlo               1 000 runs × 25 years
Tail dependence           Horn-cluster driver + global food-crisis regime (~1-in-8 yr)
```

---

## 4. Fund / Capital Composition (Steady-State Annual View)

| Layer                              | Role                                      | Approx. annual amount | Notes |
|------------------------------------|-------------------------------------------|-----------------------|-------|
| Household premiums                 | Primary risk-bearing                      | ~$433 k (50 %)       | After take-up |
| Donor premium match                | Demand support                            | ~$433 k (50 %)       | Quadratic-funding style matching possible |
| Reinsurance premium (cost)         | Tail transfer                             | ~$110 k              | Expected recovery ≈ $69 k |
| Donor seed capital                 | First-loss buffer                         | $1.3 M (stock)       | 1.5 × premium |
| Contingent credit facility         | Multi-year episode backstop               | $2.2 M capacity      | Drawn in ~10 % of runs; p95 draw $0.60 M |
| Natural hedgers (Layer 1)          | Price caps sold by exporters / traders    | Folded into reinsurance pricing in current runs | Preferred long-term |

**25-year solvency results**
- P(insolvency) with full stack: **0.4 %**
- Without reinsurance: 3.5 %
- Without contingent facility: 18.7 % (Malawi multi-year episodes defeat annually-attaching cover)
- Median 25-year loss ratio: 0.74; p95: 1.02
- Distress-event reduction (3-month rolling excess cost > 15 % of income): **–55 %**

Funding mix over 25 years (households ~44 %, donors ~47 %, reinsurance net transfers ~9 %) is consistent with early-stage CCRIF / ARC benchmarks.

---

## 5. Role of Blockchain / Distributed Ledger

The design deliberately keeps blockchain **narrow and non-load-bearing** for insurance economics. Its justified uses are limited to three places where institutional distrust actually binds:

1. **Trigger-bound escrow (commitment device)**  
   Multiple donors, recipient governments and agencies pre-fund a common pool. Release is mechanical upon public index conditions. No official can discretionarily delay or divert funds (the Somalia 2011 failure mode).

2. **Low-friction composition of the multi-layer capital stack**  
   Household premiums, donor first-loss, natural-hedger caps, exchange options and contingent credit can sit on one auditable ledger, reducing reconciliation and custody friction.

3. **Compressed issuance costs for Layer-C tail securitisation**  
   Smaller regional pools become viable as fully-collateralised, index-triggered instruments (catastrophe-bond economics with lower fixed costs).

**What blockchain is not used for**
- Individual claims adjudication  
- Oracle data generation (satellites, market prices and entitlement ratios remain external and public)  
- Last-mile distribution (aggregators + mobile money)  
- Governance of payouts (fact, not preference)

Local Data DAO / crowdsourced micro-indices, if retained, are confined to **verification and audit** roles, never to settlement triggers, precisely to avoid the conflict of interest of beneficiaries reporting inputs that affect their own payouts.

---

## 6. Bottom Line

Under real WFP-calibrated dynamics and a properly inverted (tail-weighted) product:

- The scheme **clears the three feasibility bars** the naïve simulation failed:  
  (1) pays multiples of premium in the states that matter,  
  (2) cuts irreversibility-risk events by 55 %,  
  (3) survives the actual tail (P(ruin) 0.4 % with the contingent-credit layer whose necessity the simulation itself demonstrates).

- Binding remaining fragilities are exactly those predicted by the design analysis: Malawi-type macro-price entanglement (prefer wage-ratio or import-parity confirming triggers) and demand at unsubsidised prices (retain blended premium + collection-timing design).

The numbers now support a cautious “feasible, with the stated caveats” verdict rather than an inverted, high-friction savings scheme.
