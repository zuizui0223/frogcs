#!/usr/bin/env python3
from __future__ import annotations
import json, math, hashlib, urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

URL_RAW='https://researchdata.jcu.edu.au/default/rdmp/pubrecord/6e808de0ddf811edb22c156e754c4bda/pubattach/76cdd0dc28f83c0dc4abc95bbed6dfcc?pubId=e28ccb6044a311eea020c9a81293027e'
URL_COMBINED='https://researchdata.jcu.edu.au/default/rdmp/pubrecord/6e808de0ddf811edb22c156e754c4bda/pubattach/2c7690372ace861161ba988732b4f9f4?pubId=e28ccb6044a311eea020c9a81293027e'
OUT=Path('external/BRODIE_2025_EXPANSION_WITHOUT_HOMOGENIZATION_RECEIPT_V0_1.json')
SEED=2840241
BOOT=10000
SPLIT=pd.Timestamp('2013-07-01')

def get(url,path):
    req=urllib.request.Request(url,headers={'User-Agent':'frogcs-brodie-validation/0.1'})
    with urllib.request.urlopen(req,timeout=120) as r:
        b=r.read()
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(b)
    return hashlib.sha256(b).hexdigest(),len(b)

rawp=Path('external_data/HerveyRange_frog_chorus_rawdata.csv')
combp=Path('external_data/HerveyRange_frogchorus_weather.csv')
sha_raw,size_raw=get(URL_RAW,rawp)
sha_comb,size_comb=get(URL_COMBINED,combp)

raw=pd.read_csv(rawp)
comb=pd.read_csv(combp)
raw['night']=pd.to_datetime(raw['night'],format='%d/%m/%Y',errors='raise')
comb['night']=pd.to_datetime(comb['night'],format='%d/%m/%Y',errors='raise')

extent_cols=[c for c in raw.columns if c.endswith('_extent')]
if len(extent_cols)!=17:
    raise ValueError(f'Expected 17 extent columns, found {len(extent_cols)}')

# Structural/effort audit before endpoint computation.
site_vals=sorted(raw['site'].dropna().astype(str).unique())
if len(site_vals)!=3:
    raise ValueError(f'Expected 3 sites, found {site_vals}')

# Each species-night is eligible only where all three site rows exist and have positive recording effort.
# Extent values are chorus minutes in the deposited data; blank/NA is treated as zero only when the
# site-night recording opportunity exists (positive mp3.length.mins).
raw['effort']=pd.to_numeric(raw['mp3.length.mins'],errors='coerce')
for c in extent_cols:
    raw[c]=pd.to_numeric(raw[c],errors='coerce')

night_groups=[]
for night,g in raw.groupby('night',sort=True):
    if len(g)!=3 or set(g['site'].astype(str))!=set(site_vals):
        continue
    if g['effort'].isna().any() or (g['effort']<=0).any():
        continue
    # If a valid recording exists and an extent is blank, interpret as no detected chorus for that species.
    z=g.copy()
    z[extent_cols]=z[extent_cols].fillna(0.0)
    night_groups.append(z)
if not night_groups:
    raise RuntimeError('No complete three-site nights')
dat=pd.concat(night_groups,ignore_index=True)

train=dat[dat['night']<SPLIT].copy()
valid=dat[dat['night']>=SPLIT].copy()

# Require training and validation observation at all three sites on >=5 active nights per species.
templates={}
elig_species=[]
for sp in extent_cols:
    # Active nights: positive total chorus minutes across three sites.
    trnight=train.groupby('night')[sp].sum(min_count=1)
    vanight=valid.groupby('night')[sp].sum(min_count=1)
    ntr=int((trnight>0).sum())
    nva=int((vanight>0).sum())
    if ntr<5 or nva<5:
        continue
    Y=train.groupby(train['site'].astype(str))[sp].sum().reindex(site_vals,fill_value=0.0).to_numpy(float)
    q=(Y+0.5)/(Y.sum()+1.5)
    templates[sp]=dict(zip(site_vals,q.tolist()))
    elig_species.append(sp)

rows=[]
for night,g in valid.groupby('night',sort=True):
    g=g.assign(site_s=g['site'].astype(str)).set_index('site_s').reindex(site_vals)
    for sp in elig_species:
        y=g[sp].to_numpy(float)
        if not np.all(np.isfinite(y)):
            continue
        T=float(y.sum())
        if T<=0:
            continue
        K=int((y>0).sum())
        if K<2:
            continue
        p=y/T
        q=np.array([templates[sp][s] for s in site_vals],float)
        A=float(np.sum((p-1/3)*(q-1/3)))
        rows.append({'night':night,'species':sp,'T':T,'K':K,'A':A})

v=pd.DataFrame(rows)
if v.empty:
    raise RuntimeError('No eligible K>=2 validation species-nights')

# Primary endpoint: median A > 0, hierarchical species-then-night bootstrap.
obs_median=float(v['A'].median())
rng=np.random.default_rng(SEED)
species=np.array(sorted(v['species'].unique()))
bysp={sp:v[v['species']==sp] for sp in species}
boots=np.empty(BOOT)
for b in range(BOOT):
    picks=rng.choice(species,size=len(species),replace=True)
    vals=[]
    for sp in picks:
        z=bysp[sp]
        idx=rng.integers(0,len(z),size=len(z))
        vals.extend(z.iloc[idx]['A'].tolist())
    boots[b]=np.median(vals)
ci_med=[float(np.quantile(boots,.025)),float(np.quantile(boots,.975))]
primary_pass=bool(ci_med[0]>0)

# Homogenization test: A ~ log1p(T) + species fixed effects, clustered by night/date.
v['logT']=np.log1p(v['T'])
v['night_cluster']=v['night'].astype(str)
fit=smf.ols('A ~ logT + C(species)',data=v).fit(cov_type='cluster',cov_kwds={'groups':v['night_cluster']})
b=float(fit.params['logT']); se=float(fit.bse['logT'])
ci_slope=[b-1.959963984540054*se,b+1.959963984540054*se]
homogenization_falsified=bool(ci_slope[1]<0)

# Rain-gated secondary, same-night rain variable from deposited combined file.
rain_col='rain.night.total'
rain_map=comb.groupby('night')[rain_col].first()
v['rain']=v['night'].map(rain_map)
vr=v[np.isfinite(pd.to_numeric(v['rain'],errors='coerce'))].copy()
vr['rain']=pd.to_numeric(vr['rain'])
if len(vr)>=10 and vr['night'].nunique()>=5:
    rfit=smf.ols('A ~ rain + C(species)',data=vr).fit(cov_type='cluster',cov_kwds={'groups':vr['night_cluster']})
    rb=float(rfit.params['rain']); rse=float(rfit.bse['rain'])
    rain_result={'n':int(len(vr)),'beta':rb,'ci95':[rb-1.959963984540054*rse,rb+1.959963984540054*rse]}
else:
    rain_result={'n':int(len(vr)),'status':'not_estimable'}

# Historical-best-site secondary for species with template range >= .20.
best_rows=[]
for sp in elig_species:
    q=np.array([templates[sp][s] for s in site_vals])
    if float(q.max()-q.min())<0.20:
        continue
    best=site_vals[int(np.argmax(q))]
    z=valid[['night','site',sp]].copy()
    z['site']=z['site'].astype(str)
    piv=z.pivot(index='night',columns='site',values=sp).reindex(columns=site_vals).fillna(0.0)
    T=piv.sum(axis=1)
    z2=piv[T>0].copy(); T=T[T>0]
    if len(z2)<2:
        continue
    share=z2[best]/T
    med=float(T.median())
    hi=share[T>=med]; lo=share[T<med]
    if len(hi) and len(lo):
        best_rows.append({'species':sp,'best_site':best,'high_mean':float(hi.mean()),'low_mean':float(lo.mean()),'difference':float(hi.mean()-lo.mean()),'n_high':int(len(hi)),'n_low':int(len(lo))})
best_df=pd.DataFrame(best_rows)
if len(best_df):
    diffs=best_df['difference'].to_numpy()
    best_summary={'species_n':int(len(best_df)),'mean_difference':float(diffs.mean()),'median_difference':float(np.median(diffs)),'positive_species':int((diffs>0).sum()),'zero_species':int((diffs==0).sum())}
else:
    best_summary={'species_n':0,'status':'not_estimable'}

classification = 'support' if primary_pass and not homogenization_falsified else ('falsified_homogenization' if homogenization_falsified else 'primary_non_support')
result={
  'analysis':'brodie_2025_expansion_without_homogenization_v0_1',
  'contract':'external/BRODIE_2025_EXPANSION_WITHOUT_HOMOGENIZATION_CONTRACT_V0_1.md',
  'source':{'raw_sha256':sha_raw,'raw_size':size_raw,'combined_sha256':sha_comb,'combined_size':size_comb},
  'split':{'training':'before 2013-07-01','validation':'2013-07-01 and later'},
  'structure':{'sites':site_vals,'complete_three_site_nights':int(dat['night'].nunique()),'training_nights':int(train['night'].nunique()),'validation_nights':int(valid['night'].nunique()),'extent_species_total':len(extent_cols),'eligible_species':len(elig_species)},
  'primary':{'eligible_species_nights':int(len(v)),'species':int(v['species'].nunique()),'median_A':obs_median,'bootstrap_ci95':ci_med,'pass':primary_pass},
  'homogenization_test':{'beta_log1p_total_activity':b,'ci95':ci_slope,'negative_ci_falsifies':homogenization_falsified},
  'rain_secondary':rain_result,
  'historical_best_site_secondary':best_summary,
  'classification':classification,
  'retuning_after_readback':False
}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
