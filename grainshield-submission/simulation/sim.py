"""Step 2: Monte Carlo simulation of the consumer staple-price protection scheme.
Calibrated to real WFP maize data (calibrate.py). Fixes the three fatal flaws of the naive sim:
 (1) payout structure: tail-weighted (cap >> premium), attachment at real 1-in-2..4yr episodes
 (2) objective: distress-event reduction (irreversibility proxy), not cost-CV
 (3) uncertainty: 1000 runs, cluster-based tail dependence (Horn of Africa joint crises), P(insolvency)
"""
import numpy as np, json, pandas as pd

rng = np.random.default_rng(7)
cal = json.load(open('calibration.json'))['stats']
CTY = ['malawi', 'kenya', 'ethiopia']

# ---------- calibrated episode process ----------
# arrivals: Poisson(freq); duration: geometric(mean_dur); peak: lognormal fit to (mean_peak, max_peak)
P = {}
for c in CTY:
    s = cal[c]
    mu_pk = np.log(max(s['mean_peak'] - 1.0, 0.15))          # peak excess (r-1) lognormal
    sd_pk = 0.75 if c == 'malawi' else 0.45
    P[c] = dict(lam=s['freq_per_yr'] / 12, pdur=1 / s['mean_dur_mo'], mu=mu_pk, sd=sd_pk)

# tail dependence: Horn cluster (ken, eth) share driver; Malawi separate; global factor hits all
CLUSTER = {'kenya': 'horn', 'ethiopia': 'horn', 'malawi': 'south'}
P_GLOBAL = 1 / (12 * 8.0)        # world food crisis regime ~1-in-8yr (2008, 2011, 2022)
HORN_SHARE = 0.55                # given a horn-cluster event, both countries affected w.p. .55 (lift~3)
GLOBAL_AMP = 1.35                # severities amplified in global-crisis months

def simulate_excess(T):
    """monthly excess ratio r>=1 for each country; returns (T,3) array."""
    r = np.ones((T, len(CTY)))
    state = [None] * len(CTY)                     # (months_left, path)
    glob = False
    for t in range(T):
        if glob:
            glob = rng.random() > 1 / 10          # global regime persists ~10mo
        elif rng.random() < P_GLOBAL:
            glob = True
        horn_evt = rng.random() < P['kenya']['lam'] * 1.35   # cluster driver
        for i, c in enumerate(CTY):
            if state[i] is None:
                p_start = P[c]['lam'] * (2.2 if glob else 1.0)
                if CLUSTER[c] == 'horn' and horn_evt and rng.random() < HORN_SHARE:
                    p_start = 1.0
                if rng.random() < p_start:
                    dur = 1 + rng.geometric(P[c]['pdur'])
                    peak = 1 + rng.lognormal(P[c]['mu'], P[c]['sd']) * (GLOBAL_AMP if glob else 1)
                    peak = min(peak, 6.0)
                    ramp = np.concatenate([np.linspace(1.05, peak, max(dur // 2, 1)),
                                           np.linspace(peak, 1.02, dur - max(dur // 2, 1))])
                    state[i] = [dur, ramp]
            if state[i] is not None:
                dur, ramp = state[i]
                r[t, i] = ramp[len(ramp) - dur]
                state[i][0] -= 1
                if state[i][0] <= 0:
                    state[i] = None
    return r

# ---------- product (corrected design) ----------
ATTACH, CAPR = 1.25, 2.25          # pay excess above +25%, up to +100pp
SPEND_M = 650 / 12                 # monthly staple spend $
SUMINS = 0.6 * 650                 # annual payout cap $390/hh
INCOME = 1500
EARLY_PAY, EARLY_DETECT, EARLY_FP = 35.0, 0.70, 0.05   # satellite stage: $, sensitivity, false-pos/yr
LOAD = 1.35
SUBSIDY = 0.50                     # donor pays 50% of loaded premium
N_ELIG = 10_000                    # eligible hh per country

def hh_payout_year(r_yr, early_hit):
    ex = np.clip(np.minimum(r_yr, CAPR) - ATTACH, 0, None)
    main = min(ex.sum() * SPEND_M, SUMINS)
    return main + (EARLY_PAY if early_hit else 0.0)

def takeup(net_share):
    """anchored: 3%->.62 (income-linked auto-skim, C&W-style), 8.5%->.36, 15%->.12, 25%->.02"""
    return 0.72 / (1 + np.exp(28 * (net_share - 0.085)))

def distress_events(r_path, payout_stream):
    """distress = rolling 3m excess cost net of payouts > 15% of annual income (asset-sale proxy)"""
    exc = np.clip(r_path - 1, 0, None) * SPEND_M
    net = exc - payout_stream
    roll = np.convolve(net, np.ones(3), 'valid')
    return int((roll > 0.15 * INCOME).sum() > 0)   # any distress this year

# ---------- two-pass Monte Carlo ----------
def run(NRUN=1000, YRS=25, reinsurance=True, pool=CTY, el=None, ceded_el=None, seed=7):
    global rng
    rng = np.random.default_rng(seed)
    T = YRS * 12
    ncty = len(pool)
    idx = [CTY.index(c) for c in pool]
    # pricing pass supplies el (per-country expected loss per hh)
    if el is not None:
        prem_g = {c: LOAD * el[c] for c in pool}
        tu = {c: takeup((1 - SUBSIDY) * prem_g[c] / 650) for c in pool}
        nins = {c: int(N_ELIG * tu[c]) for c in pool}
        prem_inc = sum(prem_g[c] * nins[c] for c in pool)
        RE_ATT, RE_EXH = 1.4 * prem_inc, 6.5 * prem_inc
        re_prem = 1.6 * ceded_el if (reinsurance and ceded_el) else 0.0
        seed_cap = 1.5 * prem_inc
        FACILITY = 2.5 * prem_inc   # contingent credit (CAT-DDO style), fee 0.5%/yr
    out = dict(el={c: [] for c in pool}, lossratio=[], insolvent=0, minres=[],
               ceded=[], distress_u=[], distress_i=[], resfan=[], drawn=[])
    for run_i in range(NRUN):
        r_all = simulate_excess(T)
        res, res_path, dead = (seed_cap, [], False) if el is not None else (0, [], False)
        du = di = 0
        for y in range(YRS):
            sl = slice(y * 12, (y + 1) * 12)
            agg = 0.0
            for c in pool:
                i = CTY.index(c)
                r_yr = r_all[sl, i]
                epi = (r_yr > ATTACH).any()
                early = (rng.random() < EARLY_DETECT) if epi else (rng.random() < EARLY_FP)
                pay = hh_payout_year(r_yr, early)
                out['el'][c].append(pay)
                if el is not None:
                    agg += pay * nins[c]
                    # welfare on a representative insured hh
                    pstream = np.clip(np.minimum(r_yr, CAPR) - ATTACH, 0, None) * SPEND_M
                    scale = min(1.0, SUMINS / max(pstream.sum(), 1e-9))
                    pstream = pstream * scale
                    if early:
                        pstream[max(np.argmax(r_yr > ATTACH) - 2, 0)] += EARLY_PAY
                    du += distress_events(r_yr, np.zeros(12))
                    di += distress_events(r_yr, pstream)
            if el is not None:
                ceded = np.clip(min(agg, RE_EXH) - RE_ATT, 0, None) if reinsurance else 0.0
                out['ceded'].append(ceded)
                res += prem_inc - re_prem - 0.005 * FACILITY - (agg - ceded)
                res_path.append(res)
                if res < -FACILITY:
                    dead = True
        if el is not None:
            out['lossratio'].append(sum(out['el'][c][-YRS:][j] * nins[c] for c in pool for j in range(YRS))
                                    / (prem_inc * YRS))
            out['insolvent'] += dead
            out['minres'].append(min(res_path))
            out['drawn'].append(max(0.0, -min(res_path)))
            out['resfan'].append(res_path)
            out['distress_u'].append(du / (YRS * ncty))
            out['distress_i'].append(di / (YRS * ncty))
    if el is None:
        return {c: float(np.mean(out['el'][c])) for c in pool}
    out['nins'], out['prem_g'], out['tu'] = nins, prem_g, tu
    out['prem_inc'], out['re_prem'], out['seed'] = prem_inc, re_prem, seed_cap
    return out

# pass 1: expected losses
el = run(NRUN=400, el=None)
print('EL per hh/yr:', {k: round(v, 1) for k, v in el.items()})
# pass 1b: ceded EL estimate
pre = run(NRUN=400, el=el, ceded_el=0.0, reinsurance=True, seed=11)
ceded_el = float(np.mean(np.array(pre['ceded']).reshape(-1)))* 1.0
print('ceded EL/yr:', round(ceded_el, 0))
# pass 2: priced runs
res_re  = run(NRUN=1000, el=el, ceded_el=ceded_el, reinsurance=True,  seed=21)
res_no  = run(NRUN=1000, el=el, ceded_el=ceded_el, reinsurance=False, seed=21)
res_nom = run(NRUN=1000, el={c: el[c] for c in ['kenya', 'ethiopia']}, ceded_el=ceded_el * .5,
              reinsurance=True, pool=['kenya', 'ethiopia'], seed=21)

summ = {
 'EL_hh': {c: round(el[c], 1) for c in CTY},
 'premium_gross_hh': {c: round(res_re['prem_g'][c], 1) for c in CTY},
 'premium_net_hh': {c: round((1 - SUBSIDY) * res_re['prem_g'][c], 1) for c in CTY},
 'net_share_of_spend': {c: round((1 - SUBSIDY) * res_re['prem_g'][c] / 650, 3) for c in CTY},
 'takeup': {c: round(res_re['tu'][c], 2) for c in CTY},
 'insured_hh': res_re['nins'],
 'pool_annual_premium_$': round(res_re['prem_inc'], 0),
 'reinsurance_premium_$': round(res_re['re_prem'], 0),
 'loss_ratio_median': round(float(np.median(res_re['lossratio'])), 2),
 'loss_ratio_p95': round(float(np.quantile(res_re['lossratio'], .95)), 2),
 'P_insolvency_25y_with_reins': round(res_re['insolvent'] / 1000, 3),
 'P_insolvency_25y_no_reins': round(res_no['insolvent'] / 1000, 3),
 'P_insolvency_horn_only_pool': round(res_nom['insolvent'] / 1000, 3),
 'P_facility_drawn': round(float(np.mean(np.array(res_re['drawn']) > 0)), 3),
 'facility_draw_p95_$': round(float(np.quantile(res_re['drawn'], .95)), 0),
 'distress_events_per_cty_yr_uninsured': round(float(np.mean(res_re['distress_u'])), 3),
 'distress_events_per_cty_yr_insured': round(float(np.mean(res_re['distress_i'])), 3),
 'distress_reduction_pct': round(100 * (1 - np.mean(res_re['distress_i']) / np.mean(res_re['distress_u'])), 1),
}
json.dump(summ, open('sim_summary.json', 'w'), indent=1)
np.save('resfan.npy', np.array(res_re['resfan']))
np.save('lossratio.npy', np.array(res_re['lossratio']))
np.save('lossratio_no.npy', np.array(res_no['lossratio']))
print(json.dumps(summ, indent=1))
