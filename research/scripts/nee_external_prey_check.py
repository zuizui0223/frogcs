"""Descriptive matched-treatment check of retrieved primary experimental rows.
Not an independent three-guild test; publication already informed hypotheses.
"""
import hashlib
import json
import pandas as pd
from nee_context_robustness import ROOT

SOURCE=ROOT/'research/results/nee_external_followup_20261029'
OUT=ROOT/'research/results/nee_external_prey_check_20261029'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    l=pd.read_csv(SOURCE/'multiprey_L_1h.csv');t=pd.read_csv(SOURCE/'multiprey_T_1h.csv')
    key=['Trial','Time','LeopStart','ToadStart','numPredators']
    assert len(l)==len(t)==144
    assert not l.duplicated(key).any() and not t.duplicated(key).any()
    overlap=l[key].merge(t[key],on=key,validate='one_to_one');assert len(overlap)==120
    print(t.columns.tolist())
    rows=[];cellrows=[]
    for label,data,focal,alt,killed in [('leopard',l,'LeopStart','ToadStart','L_killed'),('toad',t,'ToadStart','LeopStart','T_killed')]:
        assert (data[focal]>0).all()
        assert data[killed].between(0,data[focal]).all()
        for (n,pred),g in data.groupby([focal,'numPredators']):
            values=sorted(g[alt].unique())
            for a,q in g.groupby(alt):
                cellrows.append(dict(prey=label,focal_start=n,predators=pred,alternative_start=a,n=len(q),mean_killed=q[killed].mean(),mean_fraction=(q[killed]/q[focal]).mean()))
            if len(values)<2:continue
            low=g[g[alt]==values[0]];high=g[g[alt]==values[-1]]
            delta=(high[killed].mean()-low[killed].mean())/n
            rows.append(dict(prey=label,focal_start=n,predators=pred,alt_low=values[0],alt_high=values[-1],n_low=len(low),n_high=len(high),low_killed=low[killed].mean(),high_killed=high[killed].mean(),fraction_difference=delta,
                status='descriptive_matched_treatment_not_randomization_test'))
    r=pd.DataFrame(rows);r.to_csv(OUT/'matched_alternative_prey_contrasts.csv',index=False)
    pd.DataFrame(cellrows).to_csv(OUT/'treatment_means.csv',index=False)
    summary=[]
    for prey,g in r.groupby('prey'):
        summary.append(dict(prey=prey,matched_strata=len(g),positive=int((g.fraction_difference>1e-12).sum()),negative=int((g.fraction_difference< -1e-12).sum()),ties=int((abs(g.fraction_difference)<=1e-12).sum()),equal_stratum_mean=g.fraction_difference.mean(),median=g.fraction_difference.median()))
    pd.DataFrame(summary).to_csv(OUT/'summary.csv',index=False)
    (OUT/'receipt.json').write_text(json.dumps(dict(unique_experimental_trials=168,duplicated_mixed_prey_outcome_rows=120,endpoint='prey killed after1h; Time code2 not elapsed2h',day_and_tank_ids_available=False,independent_new_hypothesis_test=False,contains_salamanders=False,
        file_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE/'multiprey_L_1h.csv',SOURCE/'multiprey_T_1h.csv']}),indent=2)+'\n')
    print(pd.DataFrame(summary).to_string(index=False))


if __name__=='__main__':main()
