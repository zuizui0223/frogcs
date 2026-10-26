"""Exploratory source-center landcover contrasts, not measured pond functions."""
import argparse,csv,gzip,hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np

def main():
    p=argparse.ArgumentParser();p.add_argument('--surveys',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    with gzip.open(a.surveys,'rt',encoding='utf8') as f:raw=list(csv.DictReader(f))
    data=[]
    for r in raw:
        env=json.loads(r['env'])
        if any(v is None for v in env) or r['timeout'] not in ('0','0.0') or r['noise'] not in ('0','1') or not r['air']:continue
        data.append(dict(r,env=env,strong=float(r['strong']),air=float(r['air']),prior=float(r['prior']) if r['prior'] else None))
    result=[]
    for variable,index in (('source_center_flooded_vegetation',0),('source_center_open_water',1)):
        groups=defaultdict(list)
        for r in data:groups[(r['run'],r['noise'],int(r['env'][1-index]>0))].append(r)
        contrasts=[]
        for group,rows in groups.items():
            positive=[r for r in rows if r['env'][index]>0];zero=[r for r in rows if r['env'][index]==0]
            if not positive or not zero:continue
            contrasts.append(dict(route=rows[0]['route'],difference=np.mean([r['strong'] for r in positive])-np.mean([r['strong'] for r in zero]),
                air_difference=np.mean([r['air'] for r in positive])-np.mean([r['air'] for r in zero]),n_positive=len(positive),n_zero=len(zero)))
        byroute=defaultdict(list)
        for r in contrasts:byroute[r['route']].append(r['difference'])
        means=np.array([np.mean(v) for v in byroute.values()]);ci=None
        if len(means)>=10:
            rng=np.random.default_rng(20261026);ix=rng.integers(0,len(means),size=(2000,len(means)))
            ci=np.quantile(means[ix].mean(axis=1),[.025,.975]).tolist()
        result.append(dict(variable=variable,positive_means='EarthEnv consensus value >0; zero is not verified absence of pond habitat',
            matched_run_noise_other_landcover_groups=len(contrasts),routes=len(means),
            equal_route_mean_strong_call_difference=float(means.mean()) if len(means) else None,route_bootstrap_95ci=ci,
            mean_air_temperature_difference=float(np.mean([r['air_difference'] for r in contrasts])) if contrasts else None,
            source_positive_visits=sum(r['n_positive'] for r in contrasts),source_zero_visits=sum(r['n_zero'] for r in contrasts)))
    out=dict(classification='EXPLORATORY_OBSERVED_BACKGROUND_ASSOCIATION',input_sha256=hashlib.sha256(a.surveys.read_bytes()).hexdigest(),
       input_rows=len(raw),valid_rows=len(data),comparisons=result,
       design='Within same RunID, same noise impairment and same binary other landcover class; route equal weights. Not history-adjusted.',
       limits=['not pond vegetation cover or measured hydroperiod','no predator niche or refuge function inferred directly',
               'stable site suitability and species composition remain confounded','temperature not exactly matched; contrast reported',
               'posthoc descriptive contrasts, not independent confirmatory tests'])
    (a.out/'observed_results.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
