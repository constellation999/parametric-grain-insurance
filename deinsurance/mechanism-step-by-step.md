# How the Mechanism Works, Step by Step

*Companion explainer to the concept paper. Follows one full cycle — setup, monitoring, crisis, aftermath — and states, for each step, who acts, what happens, and why it is designed that way.*

---

## Phase I — Setup (before any crisis)

### Step 1. Enrollment through trusted local aggregators
Households do not interact with the protocol directly. Cooperatives, microfinance institutions, and similar local organizations enroll their members and collect small premiums. Two member classes are registered: **net food buyers** (protected against price *rises*) and **net food sellers / farmers** (protected against price *falls*).

*Why:* field evidence shows the poor buy insurance from people they trust, not from apps — uptake rises sharply when a trusted intermediary introduces the product, and "trustless" technology is meaningless to someone who cannot verify it. The aggregator is also needed later, at payout time (Step 10).

### Step 2. Internal netting of the two member classes
The pool adds up its promises. Because buyers are hurt by high prices and sellers by low prices, the two books partially cancel: in a high-price state the pool pays buyers while the sellers' coverage costs nothing, and vice versa. Only the **net** exposure must be financed externally.

*Why:* capital is the main cost driver. Netting means the pool needs capital proportional to net, not gross, coverage — the two-sided design turns an apparent conflict (opposite interests) into a subsidy each side gives the other.

### Step 3. Building the capital stack
The remaining net exposure is financed in order of cheapness:

1. **Natural hedgers sell price caps.** Grain traders and exporters — who *profit* when prices spike — sell the pool contracts that pay out in exactly those states, posting warehouse receipts (stored grain) as collateral. They accept low prices because they are giving up a slice of windfall profits, and their collateral appreciates precisely when they owe money.
2. **Exchange hedging.** The pool bundles remaining exposure into standard sizes and buys call options on global futures markets (CME). No goodwill needed — market makers sell for the premium.
3. **Donor capital as first-loss, locked in escrow.** Donor and development-bank money enters as the *most junior* tranche plus contingent credit lines, deposited into an on-chain escrow that releases **only** when public trigger conditions are met. No official — donor or recipient — can divert or delay it afterward.

*Why the escrow:* the historical failure mode of food-crisis finance is not missing information but discretionary delay — Somalia 2011 had eleven months of escalating warnings, no timely release of funds, and ~258,000 deaths. Hard-coding the release condition removes the political channel.

### Step 4. Forward procurement network
The pool signs option-style supply contracts with grain producers and warehousers across **multiple, climatically uncorrelated regions**, and pre-positions some physical stock. These partners will deliver food at payout time.

*Why diversified:* a local price spike usually means a local harvest failure — a single-region supplier would default exactly when delivery is owed. Suppliers are paid for capacity, and are **never** used as price oracles: an entity that both reports the index and profits from settlement would recreate the conflict of interest the design exists to remove.

### Step 5. Registering the oracles
Trigger data sources are fixed in advance and published: satellite vegetation/rainfall/soil-moisture indices (NDVI/VCI, CHIRPS, SMAP) for the early stage, and entitlement ratios — local wage ÷ staple price, livestock ÷ grain price, or import-parity price from FX and world markets — for the main stage. Payouts require **multiple independent indices** to agree.

*Why:* every index is external, publicly checkable, and expensive-to-impossible to manipulate; requiring conjunction means corrupting one feed is never enough. Committee judgments (official famine declarations) are deliberately excluded — they are systematically politicized and late.

---

## Phase II — Quiet years

### Step 6. Monitoring and premium recycling
Indices are checked continuously; in normal years nothing fires. Premium income pays option costs and hedger fees; a share flows into a **quadratic-funding round** where members' small contributions decide (with donor matching) which public goods get built — better local price indices, more weather stations, drought-resistant seed programs. The pool itself co-funds prevention, since lower expected losses come back to it as lower payouts.

*Why:* better measurement shrinks basis risk for everyone (a textbook public good), and the breadth of members' own contributions tells donors where demand is real.

---

## Phase III — Crisis

### Step 7. Stage-1 trigger: the satellites fire
Vegetation and soil-moisture indices cross their thresholds weeks-to-months before prices move. The contract automatically releases a **partial early payout** to aggregators.

*Why early money matters most:* it prevents the crisis spiral — families who receive support before prices peak do not have to sell their livestock and tools at fire-sale prices, which is the step that converts a bad season into a poverty trap.

### Step 8. Stage-2 trigger: entitlement ratios confirm
Local purchasing power (wage-to-grain ratio) collapses past its threshold. The **main payout** releases automatically. No claims are filed, no adjusters visit, no committee votes.

### Step 9. The capital waterfall pays, in order
Premium reserves are used first; then the natural hedgers' caps pay in (funded by their crisis windfalls, secured by now-appreciated grain collateral); then the CME options, deep in the money, are exercised; only the deepest losses touch donor first-loss capital and drawn credit lines.

*Why this order:* each layer is tapped in the state where its money is cheapest — the traders are paying out of windfalls, the options were priced by a global market, and scarce donor money is reserved for the tail no market will price.

### Step 10. Distribution through the aggregators
Aggregators receive the payout — part cash (stablecoin converted to mobile money), part **physical grain** delivered under the Step-4 forward contracts — and distribute to members using local knowledge of who was actually hurt.

*Why two-stage distribution:* the index can only approximate individual losses (basis risk). The cooperative can see which member lost everything and which was barely touched, so the last mile of accuracy is handled by the layer that has the information. In-kind delivery also protects members from crisis inflation and currency collapse.

---

## Phase IV — Aftermath

### Step 11. The track record compounds
Every payout is publicly verifiable, and every member either received one or watched neighbors receive one on time. Evidence shows payout experience is the strongest driver of future demand — trust is built by performance, then enrollment grows, netting improves, and capital gets cheaper.

### Step 12. Recalibration
Basis-risk gaps observed in the crisis feed the next QF round (Step 6): which index needs refining, which region needs a weather station, which supply contract failed. The measurement infrastructure — the system's real foundation — improves each cycle.

---

## The whole design in one sentence

**Fix the promise before the crisis, let satellites and markets — never committees — decide when it is kept, pay through the people the poor already trust, and fund each layer of risk with the money that is cheapest in exactly the state where it must pay.**
