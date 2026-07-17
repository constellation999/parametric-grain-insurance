# Onocoy Linkage + Simple UI / Proxy Wallet Design

## 1. Onocoy Integration Opportunities

Onocoy is a Solana-based DePIN for high-precision GNSS correction data (RTK). Key relevant features:
- Decentralized reference stations (miners) rewarded with ONO based on **data quality, uptime, location value** (under-served areas earn more).
- Validators detect spoofing / low-quality signals.
- **Square-root voting** (modified quadratic) for governance — directly aligns with the project’s planned Quadratic voting / AAM.
- Loopback: station operators get free high-quality RTK for their own devices (useful for precision ag).
- Pay-per-use Data Credits (fiat-pegged, non-transferable).

### Concrete integration points for the parametric insurance

| Layer | Use of Onocoy | Benefit |
|-------|---------------|---------|
| **Oracle / Index quality** | High-precision position + atmospheric / multipath metrics from nearby stations can validate or enrich satellite (NDVI, soil moisture) triggers | Lower basis risk; independent cross-check of “leading stage” |
| **Geo-fencing** | cm-level location for field-level or village-level parametric products | Product can move from regional to more granular (reduces basis risk further) |
| **Coverage incentive** | Encourage / subsidize reference stations in target rural corridors (Kenya Rift, Malawi, Ethiopia) via insurance-pool partnership or joint grants | Better GNSS coverage exactly where food-insecure populations live; dual revenue (ONO + insurance value) |
| **Governance** | Adopt (or bridge to) Onocoy-style square-root voting for insurance DAO parameter changes (triggers, premium loading, region weights) | Proven anti-whale mechanism already live; shared community of operators |
| **Farmer dual-use** | Smallholders who host a station get free Loopback RTK + discounted or free insurance coverage | Strong adoption incentive; turns infrastructure into both precision-ag tool and risk-management asset |
| **Data marketplace** | Insurance smart contracts pay Data Credits for verified station streams used in trigger calculation | Sustainable demand for Onocoy data in agriculture / climate vertical |

### Recommended first steps
1. Map existing Onocoy stations vs target insurance regions (public explorer).
2. Pilot: partner with 5–10 existing or new miners in one corridor; feed quality-assured position / integrity flags into the leading-stage oracle.
3. Governance bridge: insurance DAO can hold ONO and participate in Onocoy votes on data standards relevant to climate indices.
4. Token design: explore whether insurance participants can earn small ONO rewards for contributing ground-truth (e.g., local price reports, rainfall gauges) that improve the dual-trigger model.

## 2. Simple UI & Proxy / Agent Wallet

### Design principles (digital divide)
- Feature-phone / USSD path must work (majority of rural users).
- Smartphone path is progressive enhancement.
- No seed-phrase management for end users.
- Premium collection & payouts via existing mobile money (M-Pesa, Airtel Money, etc.) wherever possible.
- Local language + voice prompts later.

### Architecture options

**A. Account Abstraction (AA) smart wallet (preferred long-term)**
- ERC-4337 / Solana equivalent smart accounts.
- Login via phone number + OTP or social recovery (trusted contacts / village agent).
- Gas sponsorship by the insurance protocol or donor.
- Daily / monthly spending limits, session keys for micropayments.
- Bridge: deposit from mobile money → stablecoin balance inside the AA wallet.

**B. Proxy / Agent model (fastest to pilot)**
- Village agent, cooperative, or NGO staff holds a multi-sig or custodial wallet that covers 20–100 households.
- Agent enrolls members via simple paper + photo ID or existing social registry.
- Premiums collected in cash or mobile money by agent → bulk on-ramp.
- Payouts push to agent’s mobile money or distributed in cash / grain stock.
- On-chain: one proxy address per agent group; internal ledger (off-chain or cheap L2) tracks individual entitlements.
- Transparency: monthly SMS / USSD statement to each member (“Your group received X, your share Y”).

**C. Hybrid (recommended)**
- Early adopters / urban-adjacent: personal AA wallet + mobile-money bridge.
- Deep rural: agent proxy model.
- Both feed the same smart-contract pool and use the same dual-trigger oracle.

### Minimal viable UI flows

1. **Enrollment**
   - USSD: *123# → Insurance → Join → Select region / crop → Confirm premium schedule.
   - Smartphone: 3-screen flow (location confirm → household size → accept terms).

2. **Premium**
   - Auto-deduct from mobile money on payday or harvest window (pay-at-harvest style).
   - Or daily micro-deduction of ~$0.25–0.40.

3. **Status**
   - USSD “Check my cover” → current trigger status (green / amber / red) + last payout.
   - Push SMS when leading trigger fires (“Early support of $XX arriving”).

4. **Payout**
   - Automatic to mobile money or agent for distribution.
   - Option for in-kind grain voucher at partner warehouse.

### Tech stack suggestion for prototype
- Frontend: React Native or lightweight PWA (works offline-first with service worker).
- Backend / contracts: Solana (aligns with Onocoy) or cheap L2 (Base / Optimism) for lower fees.
- Mobile money: Africa’s Talking / Flutterwave / local aggregators.
- Identity: phone number + optional national ID hash (privacy-preserving).

## 3. Immediate next actions (code / design)
- [x] Trigger & premium numerical optimization (see `optimize_triggers_premium.py` and recommended params).
- [ ] Update main simulation with optimized LEAD_TH ≈ –1.23, CONF_TH ≈ 1.08, MAX_PAYOUT ≈ 84, LOADING ≈ 1.35–1.40 and re-run full 20-yr visualization.
- [ ] Draft smart-contract interface for dual-trigger oracle that can accept Onocoy quality flags.
- [ ] Build static HTML / simple React mock of the enrollment + status screens (proxy vs personal wallet toggle).
- [ ] One-pager partnership brief for Onocoy team (station coverage map + joint value prop).
