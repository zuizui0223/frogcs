"""Fixed two-pond acoustic/visual calibration audit; see ANALYSIS_DESIGN.md."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'green_toad/SupplMat/Dataset1.xlsx'
d=pd.read_excel(SOURCE)
assert len(d)==44 and not d.duplicated(['Pond_ID','Date']).any() and not d.isna().any().any()
date=pd.to_datetime(d.Date);day=(date-date.min()).dt.days.to_numpy()/30
y=np.log1p(d.N_males.to_numpy());site=pd.get_dummies(d.Pond_ID,drop_first=True,dtype=float).to_numpy()
base=np.column_stack([np.ones(len(d)),day,site])
dates=date.unique();rng=np.random.default_rng(20261029)
draws=rng.choice(dates,(999,len(dates)),replace=True)
def fit(x,y):
    b,_,rank,_=np.linalg.lstsq(x,y,rcond=None)
    return b if rank==x.shape[1] else None
result=[];predictions=[]
for metric in ['N_call_sec_hour','N_call_night']:
    call=np.log1p(d[metric].to_numpy());x=np.column_stack([base,call]);b=fit(x,y)
    boot=[]
    for draw in draws:
        idx=np.concatenate([np.flatnonzero(date.to_numpy()==v) for v in draw]);bb=fit(x[idx],y[idx])
        if bb is not None:boot.append(bb[-1])
    correlations={'pooled':float(spearmanr(d[metric],d.N_males).statistic)}
    for pond in sorted(d.Pond_ID.unique()):
        m=(d.Pond_ID==pond).to_numpy();correlations[pond]=float(spearmanr(d.loc[m,metric],d.loc[m,'N_males']).statistic)
    r=dict(metric=metric,call_slope=float(b[-1]),call_slope_ci95=np.quantile(boot,[.025,.975]).tolist(),valid_bootstraps=len(boot),spearman=correlations)
    for mode in ['leave_date_out','leave_pond_out']:
        labels=date if mode=='leave_date_out' else d.Pond_ID
        xb=base if mode=='leave_date_out' else base[:,:2]
        xa=np.column_stack([xb,call]);pb=np.full(len(d),np.nan);pa=pb.copy()
        for group in labels.unique():
            test=(labels==group).to_numpy();train=~test
            bb=fit(xb[train],y[train]);ba=fit(xa[train],y[train]);assert bb is not None and ba is not None
            pb[test]=xb[test]@bb;pa[test]=xa[test]@ba
        assert np.isfinite(pb).all() and np.isfinite(pa).all()
        r[mode]=dict(n=len(d),groups=int(labels.nunique()),baseline_log_mse=float(np.mean((pb-y)**2)),with_calls_log_mse=float(np.mean((pa-y)**2)),delta_log_mse=float(np.mean((pa-y)**2-(pb-y)**2)))
        for i in range(len(d)):predictions.append(dict(metric=metric,validation=mode,pond=d.Pond_ID.iloc[i],date=date.iloc[i].strftime('%Y-%m-%d'),observed_log_count=y[i],baseline_prediction=pb[i],call_prediction=pa[i]))
    result.append(r)
out=dict(source_doi='10.1038/s41598-025-11706-3',source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),rows=len(d),ponds=int(d.Pond_ID.nunique()),dates=int(date.nunique()),date_min=str(date.min().date()),date_max=str(date.max().date()),missing_cells=int(d.isna().sum().sum()),duplicate_pond_date_rows=0,seed=20261029,models=result,limits=['Adult male visual counts, not detection-corrected population density','Automatic call counts, not calling-male counts or NAAMP index','Only two artificial ponds, one season, no developmental stages or predators','Same-date folds preserve pond context; only two leave-pond-out folds','Exploratory external measurement audit, not independent three-guild validation'])
(ROOT/'green_toad_calibration.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
pd.DataFrame(predictions).to_csv(ROOT/'green_toad_predictions.csv',index=False)
print(json.dumps(out,indent=2))
