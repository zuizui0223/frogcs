"""Read-only audit of response rank geometry; no fitting of mechanisms."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
from scipy.stats import rankdata
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
src=ROOT/'research/results/final_mechanism_20261027/winner_rank_cells.csv.gz'
q=pd.read_csv(src);q=q[q.levels==21].copy()
assert len(q)==882
q['cdf']=(rankdata(q.F_B)-.5)/len(q)
q['rawz']=(q.F_B-q.F_B.mean())/q.F_B.std(ddof=0)
q['rankz']=(q.cdf-q.cdf.mean())/q.cdf.std(ddof=0)
c=q[q.S_source.isin([.25,2]) & q.D_source.isin([.25,2])].sort_values(['vegetation','S_source','D_source'])
c[['vegetation','S_source','D_source','F_B','cdf','rawz','rankz']].to_csv(OUT/'corners.csv',index=False)
rows=[]
for v,g in c.groupby('vegetation'):
 for scale in ['F_B','cdf','rawz','rankz']:
  z=g.set_index(['S_source','D_source'])[scale]
  low=z.loc[(.25,2)]-z.loc[(.25,.25)];high=z.loc[(2,2)]-z.loc[(2,.25)]
  rows.append(dict(vegetation=v,scale=scale,D_effect_lowS=low,D_effect_highS=high,DiD=high-low))
pd.DataFrame(rows).to_csv(OUT/'corner_contrasts.csv',index=False)
q.groupby('vegetation').F_B.agg(['min','max','mean','std']).to_csv(OUT/'distribution.csv')
z=lambda a:(a-np.mean(a))/np.std(a)
d,s,v=[z(rankdata(q[k])) for k in ['D_source','S_source','vegetation']]
X=np.column_stack([np.ones(len(q)),d,s,v,d*s,d*v,s*v,d*s*v]);names=['intercept','D','S','V','DS','DV','SV','DSV'];coefs=[]
for scale in ['rawz','rankz']:
 y=q[scale].to_numpy();b=np.linalg.lstsq(X,y,rcond=None)[0]
 coefs.append(dict(scale=scale,**dict(zip(names,b)),DS_lowV=b[4]-b[7],DS_highV=b[4]+b[7],main_effect_variance_share=float(np.var(X[:,1:4]@b[1:4])/np.var(y)),DS_variance_share=float(np.var(X[:,4]*b[4])/np.var(y))))
pd.DataFrame(coefs).to_csv(OUT/'regression.csv',index=False)
assert np.all(np.diff(q.sort_values('F_B').cdf)>=0)
(OUT/'receipt.json').write_text(json.dumps(dict(source=src.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),rows=len(q),mechanism_search=False),indent=2))
print(pd.DataFrame(coefs).to_string(index=False))
