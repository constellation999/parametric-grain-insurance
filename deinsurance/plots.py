import pandas as pd, numpy as np, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False,
                     'figure.facecolor': 'white', 'axes.grid': True, 'grid.alpha': 0.25})
C = {'malawi': '#B3421B', 'kenya': '#1B6CB3', 'ethiopia': '#2E7D32'}
summ = json.load(open('sim_summary.json'))
cal = json.load(open('calibration.json'))

# ---------- Fig 1: what the real data says ----------
fig, axes = plt.subplots(3, 1, figsize=(10, 7.5), sharex=False)
for ax, c in zip(axes, ['malawi', 'kenya', 'ethiopia']):
    df = pd.read_csv(f'series_{c}.csv', index_col=0, parse_dates=False)
    df.index = pd.PeriodIndex(df.index, freq='M').to_timestamp()
    r = df['excess_ratio']
    ax.plot(df.index, r, color=C[c], lw=1.1)
    ax.axhline(1.25, color='black', ls='--', lw=0.8)
    ax.fill_between(df.index, 1.25, r.where(r > 1.25), color=C[c], alpha=0.35)
    s = cal['stats'][c]
    ax.set_title(f"{c.capitalize()} maize — excess over trailing trend+season (WFP, {s['years']}y): "
                 f"{s['episodes']} episodes, mean {s['mean_dur_mo']}mo, mean peak {s['mean_peak']}x",
                 fontsize=9, loc='left')
    ax.set_ylabel('excess ratio')
    ax.set_ylim(0.5, min(6, r.max() * 1.1 if r.max() > 2 else 2.2))
axes[0].annotate('attachment 1.25 (payouts begin)', xy=(0.995, 0.93), xycoords='axes fraction',
                 ha='right', fontsize=8)
fig.suptitle('Real-data backtest: WFP retail maize prices, trigger episodes (shaded = payout months)', y=0.995)
fig.tight_layout()
fig.savefig('fig1_realdata_backtest.png', dpi=150)

# ---------- Fig 2: Monte Carlo — solvency ----------
fan = np.load('resfan.npy') / 1e6
lr = np.load('lossratio.npy'); lr_no = np.load('lossratio_no.npy')
fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.6))
yrs = np.arange(1, fan.shape[1] + 1)
for q, a, lab in [(5, .18, 'p5-p95'), (25, .32, 'p25-p75')]:
    axes[0].fill_between(yrs, np.percentile(fan, q, 0), np.percentile(fan, 100 - q, 0),
                         color='#1B6CB3', alpha=a, label=lab)
axes[0].plot(yrs, np.median(fan, 0), color='#0B3550', lw=1.6, label='median')
fac = 2.5 * summ['pool_annual_premium_$'] / 1e6
axes[0].axhline(0, color='black', lw=0.8)
axes[0].axhline(-fac, color='#B3421B', ls='--', lw=1, label='contingent credit exhausted')
axes[0].set_title('Pool reserves, 1,000 runs ($M)', loc='left'); axes[0].set_xlabel('year')
axes[0].legend(fontsize=7, loc='upper left')
axes[1].hist(lr, bins=30, color='#1B6CB3', alpha=0.8)
axes[1].axvline(1.0, color='black', ls='--', lw=0.9)
axes[1].set_title(f"25y avg loss ratio (median {summ['loss_ratio_median']}, p95 {summ['loss_ratio_p95']})", loc='left')
bars = [('full stack', summ['P_insolvency_25y_with_reins']),
        ('no reinsurance', summ['P_insolvency_25y_no_reins']),
        ('naive sim\n(single run)', np.nan)]
axes[2].bar([b[0] for b in bars[:2]], [b[1] * 100 for b in bars[:2]], color=['#2E7D32', '#B3421B'], width=0.55)
axes[2].set_title('P(insolvency within 25y), %', loc='left')
axes[2].text(0.02, 0.95, f"facility drawn in {summ['P_facility_drawn']*100:.0f}% of runs\n"
             f"(p95 draw ${summ['facility_draw_p95_$']/1e6:.2f}M of ${fac:.1f}M)",
             transform=axes[2].transAxes, va='top', fontsize=8)
fig.tight_layout(); fig.savefig('fig2_montecarlo_solvency.png', dpi=150)

# ---------- Fig 3: welfare, demand, funding composition ----------
fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.6))
axes[0].bar(['uninsured', 'insured'],
            [summ['distress_events_per_cty_yr_uninsured'], summ['distress_events_per_cty_yr_insured']],
            color=['#8A8578', '#2E7D32'], width=0.55)
axes[0].set_title(f"Distress events / cohort-year\n(3-mo excess cost >15% income): −{summ['distress_reduction_pct']}%", loc='left')
xs = np.linspace(0, 0.28, 200)
axes[1].plot(xs * 100, 72 / (1 + np.exp(28 * (xs - 0.085))), color='#0B3550')
for c in ['malawi', 'kenya', 'ethiopia']:
    axes[1].scatter(summ['net_share_of_spend'][c] * 100, summ['takeup'][c] * 100, color=C[c], zorder=5, label=c)
axes[1].scatter([24.5], [72 / (1 + np.exp(28 * (0.245 - 0.085)))], marker='x', color='black', label='naive sim premium')
axes[1].set_xlabel('net premium, % of staple spend'); axes[1].set_title('Endogenous take-up (lit-anchored)', loc='left')
axes[1].legend(fontsize=7)
p = summ['pool_annual_premium_$'] / 1e6
flows = {'household premiums (50%)': 0.5 * p, 'donor premium match (50%)': 0.5 * p,
         'reinsurance premium (cost)': -summ['reinsurance_premium_$'] / 1e6,
         'expected reins. recovery': summ['reinsurance_premium_$'] / 1.6 / 1e6}
axes[2].barh(list(flows.keys()), list(flows.values()),
             color=['#1B6CB3', '#C99700', '#B3421B', '#2E7D32'])
axes[2].axvline(0, color='black', lw=0.8)
axes[2].set_title('Annual funding flows ($M)\n+ donor seed 1.5x & contingent credit 2.5x premium', loc='left', fontsize=8.5)
fig.tight_layout(); fig.savefig('fig3_welfare_demand_funding.png', dpi=150)
print('figures written')
