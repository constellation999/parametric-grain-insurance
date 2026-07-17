#!/usr/bin/env python3
"""
Parametric Insurance Simulation for Grain-Price Shock Protection
================================================================

Full working source was developed in the conversation session (~14k characters).
Because of automated push size limits, the complete script is kept in the original
session artifacts rather than embedded here.

Key features of the full version:
- Dual-trigger (satellite leading + price/wage confirming)
- Multi-region (Kenya Rift / Malawi Central / Ethiopia Oromia)
- Micropayments, donor matching, simplified forward contributions
- Household metrics (CV of net cereal cost, severe stress months)
- 20-year fund balance tracking

**Critical known issues** (see README.md):
- Economic inversion (max payout < annual premium)
- Primary metric (CV) is secondary to severe-shortfall probability
- Single-run only, no Monte Carlo / crisis correlation / reinsurance
- Take-up exogenous despite high premium

Request the full .py from the original conversation or Claude project if needed
for further development.
"""

print(__doc__)
