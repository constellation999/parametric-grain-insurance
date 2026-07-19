"""Step 1: Calibrate price spike process from real WFP data.
Excess ratio r_t = P_t / trend_t where trend = trailing 36m log-linear fit + monthly seasonal factors.
This absorbs local inflation drift (MWK/ETB devaluations) and seasonality, isolating crisis spikes.
"""
import pandas as pd, numpy as np, json

CFG = {'malawi': ('MWK',), 'kenya': ('KES',), 'ethiopia': ('ETB',)}
series, episodes_all, stats = {}, {}, {}

def monthly_series(country, cur):
    df = pd.read_csv(f'wfp_{country}.csv', skiprows=[1], low_memory=False)
    m = df[df['commodity'].isin(['Maize', 'Maize (white)']) &
           (df['currency'] == cur) & (df['pricetype'] == 'Retail')].copy()
    if len(m) < 500:  # Ethiopia retail sparse -> allow wholesale
        m = df[df['commodity'].isin(['Maize', 'Maize (white)']) & (df['currency'] == cur)].copy()
    m['price'] = pd.to_numeric(m['price'], errors='coerce')
    m = m.dropna(subset=['price'])
    m['ym'] = pd.to_datetime(m['date']).dt.to_period('M')
    s = m.groupby('ym')['price'].median()
    s = s[~s.index.duplicated()].sort_index()
    s = s.reindex(pd.period_range(s.index.min(), s.index.max(), freq='M')).interpolate(limit=3)
    return s.dropna()

def excess_ratio(s, win=36):
    """r_t vs trailing log-linear trend + seasonal factors (both estimated on trailing window only -> no lookahead)."""
    logp, r = np.log(s.values), np.full(len(s), np.nan)
    months = s.index.month
    for t in range(win, len(s)):
        w = slice(t - win, t)
        x = np.arange(win)
        b, a = np.polyfit(x, logp[w], 1)
        resid = logp[w] - (a + b * x)
        seas = {mo: resid[months[w] == mo].mean() for mo in range(1, 13)}
        pred = a + b * win + seas.get(months[t], 0.0)
        r[t] = np.exp(logp[t] - pred)
    return pd.Series(r, index=s.index)

def find_episodes(r, attach=1.25):
    """Contiguous runs with r>attach; record duration, peak, mean excess."""
    ep, cur = [], None
    for t, v in r.items():
        if np.isnan(v):
            continue
        if v > attach:
            if cur is None:
                cur = {'start': t, 'peak': v, 'sum_ex': 0.0, 'dur': 0}
            cur['peak'] = max(cur['peak'], v)
            cur['sum_ex'] += v - 1.0
            cur['dur'] += 1
            cur['end'] = t
        elif cur is not None:
            ep.append(cur); cur = None
    if cur is not None:
        ep.append(cur)
    return ep

for c, (cur,) in CFG.items():
    s = monthly_series(c, cur)
    r = excess_ratio(s)
    series[c] = (s, r)
    ep = find_episodes(r)
    yrs = r.notna().sum() / 12
    # AR(1) of log r in normal regime
    lr = np.log(r.dropna().values)
    normal = lr[np.abs(lr) < np.log(1.25)]
    rho = np.corrcoef(normal[:-1], normal[1:])[0, 1] if len(normal) > 24 else 0.7
    stats[c] = {
        'years': round(yrs, 1),
        'episodes': len(ep),
        'freq_per_yr': round(len(ep) / yrs, 3),
        'mean_dur_mo': round(np.mean([e['dur'] for e in ep]), 1) if ep else 0,
        'mean_peak': round(np.mean([e['peak'] for e in ep]), 2) if ep else 0,
        'max_peak': round(max([e['peak'] for e in ep]), 2) if ep else 0,
        'sigma_normal': round(np.std(normal), 3),
        'rho_ar1': round(rho, 2),
    }
    episodes_all[c] = [{'start': str(e['start']), 'dur': e['dur'], 'peak': round(e['peak'], 2)} for e in ep]

# --- cross-country crisis co-occurrence (for tail dependence) ---
idx = None
for c in CFG:
    rr = series[c][1].dropna()
    idx = rr.index if idx is None else idx.intersection(rr.index)
crisis = pd.DataFrame({c: (series[c][1].reindex(idx) > 1.25) for c in CFG})
co = {}
n_any = int(crisis.any(axis=1).sum())
co['months_overlap'] = len(idx)
co['p_crisis_any'] = round(crisis.any(axis=1).mean(), 3)
co['p_co2_given_any'] = round((crisis.sum(axis=1) >= 2).sum() / max(n_any, 1), 3)
co['p_co3_given_any'] = round((crisis.sum(axis=1) >= 3).sum() / max(n_any, 1), 3)
pairs = {}
for a in CFG:
    for b in CFG:
        if a < b:
            pa, pb = crisis[a].mean(), crisis[b].mean()
            pab = (crisis[a] & crisis[b]).mean()
            pairs[f'{a}-{b}'] = {'p_joint': round(pab, 3), 'p_indep': round(pa * pb, 3),
                                 'lift': round(pab / (pa * pb), 1) if pa * pb > 0 else None}
co['pairs'] = pairs

out = {'stats': stats, 'co_occurrence': co, 'episodes': episodes_all}
with open('calibration.json', 'w') as f:
    json.dump(out, f, indent=1)
for c in CFG:
    series[c][0].to_frame('price').join(series[c][1].to_frame('excess_ratio')).to_csv(f'series_{c}.csv')
print(json.dumps({'stats': stats, 'co_occurrence': co}, indent=1))
