#!/usr/bin/env python3
"""Post-hoc fixed environmental contrasts; no changes to JAE submission.
Reuses archived ERA5+NAAMP extraction, caches run-level values once, and
separates a mean soil association from context moderation / layer specificity.
Wetter/drier labels reflect rain recency, NOT a chronological before/after.
Three primary two-sided tests, Holm adjustment, unchanged <=2008/>=2009
non-overlapping-pair temporal validation. No outcome-dependent thresholds.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

OLD_SOIL_SHA='80ef351a96abfc56b1dd52dd5ea7ba6eb21cd543'
OLD_WEATHER_SHA='ece570314de06bdee036920251ecb53c0556c4d609bc1ca72568581467cf1d02'
BASE='rain_contrast + rain72_z + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber) + vpd_relief_z + vpd_mid_z + air_mid_z'
ADDITIVE='strong_new_score ~ '+BASE+' + soil_delta_z + soil_mid_z'
INTERACTION=ADDITIVE+' + soil_delta_z:soil_mid_z + soil_delta_z:vpd_mid_z'
LAYER='strong_new_score ~ '+BASE+' + soil_mid_z + layer_common_z + surface_excess_z'
PRIMARY=[{'name':'soil_state_moderation','formula':INTERACTION,'term':'soil_delta_z:soil_mid_z'},
 {'name':'atmospheric_dryness_moderation','formula':INTERACTION,'term':'soil_delta_z:vpd_mid_z'},
 {'name':'surface_vs_deeper_change','formula':LAYER,'term':'surface_excess_z'}]

def raw_features(d):
 a=d.copy(); a['soil_delta']=d.soil1_w-d.soil1_d;a['soil_mid']=(d.soil1_w+d.soil1_d)/2
 a['vpd_mid']=(d.vpd_w+d.vpd_d)/2;a['vpd_relief']=d.vpd_d-d.vpd_w
 a['rain72']=np.log1p(d.rain72_w)-np.log1p(d.rain72_d)
 a['layer_common']=((d.soil1_w-d.soil1_d)+(d.soil2_w-d.soil2_d))/2
 a['surface_excess']=(d.soil1_w-d.soil1_d)-(d.soil2_w-d.soil2_d)
 a['air_mid']=(d.air_w+d.air_d)/2 if 'air_w' in d else 0.
 return a

def features(d,scaler=None):
 a=raw_features(d); names=['soil_delta','soil_mid','vpd_mid','vpd_relief','rain72','layer_common','surface_excess','air_mid']
 if not np.isfinite(a[names].to_numpy()).all():raise ValueError('Missing environment is not zero')
 if scaler is None:scaler={n:[float(a[n].mean()),float(a[n].std(ddof=0)) or 1.] for n in names}
 for n in names:a[n+'_z']=(a[n]-scaler[n][0])/scaler[n][1]
 return a,scaler

def holm(p):
 p=np.asarray(p,float);o=np.argsort(p);v=np.maximum.accumulate((len(p)-np.arange(len(p)))*p[o]);out=np.zeros(len(p));out[o]=np.minimum(1,v);return out

def fit_model(d,formula,route_fe=False):
 if route_fe:formula=formula.replace('C(State)','C(route_cluster)')
 return smf.ols(formula,data=d).fit(cov_type='cluster',cov_kwds={'groups':d.route_cluster})

def term(f,name):
 lo,hi=f.conf_int().loc[name]
 return {'beta':float(f.params[name]),'se_route_cluster':float(f.bse[name]),'ci95':[float(lo),float(hi)],'p':float(f.pvalues[name])}

def coverage(d):
 return {'pairs':len(d),'routes':int(d.route_cluster.nunique()),'states':int(d.State.nunique())}

def effects(d,route_fe=False,response='strong_new_score'):
 fits={};rows=[]
 for s in PRIMARY:
  formula=s['formula'].replace('strong_new_score',response)
  if formula not in fits:fits[formula]=fit_model(d,formula,route_fe)
  f=fits[formula];rows.append({'contrast':s['name'],**term(f,s['term'])})
 for r,p in zip(rows,holm([r['p'] for r in rows])):r['p_holm_three']=float(p)
 return {'coverage':coverage(d),'response':response,'route_fixed_effects':route_fe,'effects':rows}

def transfer(d):
 train=d[d.year_later<=2008].copy();test=d[d.year_earlier>=2009].copy()
 if len(train)<200 or len(test)<200:return {'status':'insufficient_unchanged_2008_split','train':coverage(train),'test':coverage(test)}
 train,sc=features(train);test,_=features(test,sc)
 keep=test.State.isin(train.State.unique())&test.RunNumber.isin(train.RunNumber.unique());excluded=int((~keep).sum());test=test[keep].copy()
 forms={'base_no_soil':'strong_new_score ~ '+BASE,'soil_additive':ADDITIVE,'soil_context':INTERACTION,'layer_partition':LAYER}
 pred={};fits={}
 for name,formula in forms.items():
  f=fit_model(train,formula);fits[name]=f;pred[name]=np.asarray(f.predict(test))
 y=test.strong_new_score.to_numpy();rng=np.random.default_rng(20261019);comparisons={}
 for name,ref in [('soil_additive','base_no_soil'),('soil_context','soil_additive'),('layer_partition','soil_additive')]:
  gain=(y-pred[ref])**2-(y-pred[name])**2
  a=pd.DataFrame({'route':test.route_cluster.to_numpy(),'gain':gain}).groupby('route').gain.mean().to_numpy()
  boots=a[rng.integers(0,len(a),size=(2000,len(a)))].mean(axis=1)
  comparisons[name+'_over_'+ref]={'route_equal_mse_reduction':float(a.mean()),'ci95_test_route_bootstrap':np.quantile(boots,[.025,.975]).tolist()}
 return {'train':coverage(train),'test':coverage(test),'training_scaler':sc,'unknown_source_categories_excluded_pairs':excluded,'comparisons':comparisons,'coefficient_refit_on_test':False,'training_uncertainty_in_ci':False}

def load_old(root):
 p=Path(root)/'exploration/run_naamp_soil_moisture_cue.py';s=importlib.util.spec_from_file_location('old_soil',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def extract_air(old,mid):
 import icechunk,xarray as xr
 store=icechunk.s3_storage(bucket='earthmover-icechunk-era5',prefix='icechunkV2',region='us-east-1',anonymous=True)
 repo=icechunk.Repository.open(store);session=repo.readonly_session('main');ds=xr.open_zarr(session.store,group='single/temporal',consolidated=False,chunks=None)
 ids=sorted(mid);t=ds[old.hydric.find_grib_var(ds,167,['2m temperature'])];td=ds[old.hydric.find_grib_var(ds,168,['2m dewpoint'])]
 for x in (t,td):
  if str(x.attrs.get('units')).lower() not in ('k','kelvin'):raise ValueError('Kelvin units drift')
 out={}
 for st in range(0,len(ids),200):
  bs=ids[st:st+200];lat=xr.DataArray([mid[r]['lat'] for r in bs],dims='run');lon=xr.DataArray([mid[r]['lon']%360 for r in bs],dims='run');times=xr.DataArray(np.array([np.datetime64(pd.Timestamp(mid[r]['midpoint'].astimezone(ZoneInfo('UTC')).replace(tzinfo=None)).floor('h'),'ns') for r in bs]),dims='run')
  vals=[np.asarray(x.sel(latitude=lat,longitude=lon,valid_time=times,method='nearest').values,float)-273.15 for x in (t,td)]
  if not all(np.isfinite(x).all() for x in vals):raise ValueError('Nonfinite air fields')
  vpd=np.maximum(old.hydric.es_kpa(vals[0])-old.hydric.es_kpa(vals[1]),0)
  for i,r in enumerate(bs):out[r]={'air_c':float(vals[0][i]),'dew_c':float(vals[1][i]),'vpd_kpa':float(vpd[i])}
  print('AIR_RUNS',min(st+200,len(ids)),flush=True)
 return out

def build_pair_cache(old,outdir):
 raw=old.hydric.retry(old.base.load,'NAAMP');runs,sets=old.base.build_runs(raw);mid=old.hydric.build_midpoints(raw,runs)
 weather,audit=old.extract(mid)
 if audit['weather_sha256']!=OLD_WEATHER_SHA:raise ValueError('Archived soil/rain values drift: '+audit['weather_sha256'])
 air=extract_air(old,mid);weather={r:{**weather[r],**air[r]} for r in weather}
 pd.DataFrame.from_dict(weather,orient='index').rename_axis('RunID').to_csv(outdir/'environment_by_run.csv.gz',compression='gzip')
 eligible=set(runs.RunID.astype(str));sampled,_=old.spatial.stop_matrix(raw,eligible);by=old.hydric.build_ci(raw,eligible,sampled);site=old.hydric.site_map(raw,eligible)
 pairs=old.base.pair_runs(runs,sets).reset_index(drop=True);_,same=old.sameobs.same_observer_pairs(raw,runs,sets);samekeys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}
 rows=[]
 for p in pairs.itertuples(index=False):
  w,d=str(p.wet_RunID),str(p.dry_RunID)
  if w not in weather or d not in weather:continue
  r=p._asdict();score,count,full=old.hydric.metrics(p,sampled,by);r.update(strong_new_score=score,strong_new_count=count,new_ci3_count=full,stable_sites=old.hydric.stable_pair(p,sampled,site),same_observer=(w,d) in samekeys)
  for label,rid in [('w',w),('d',d)]:
   for key,col in [('swvl1','soil1'),('swvl2','soil2'),('vpd_kpa','vpd'),('rain72_mm','rain72'),('air_c','air')]:r[col+'_'+label]=weather[rid][key]
  rows.append(r)
 df=pd.DataFrame(rows);z,_=features(df);z['soil1_gain_difference_z']=z.soil_delta_z;z['rain72_amount_difference_z']=z.rain72_z
 reproduced=old.fit(z,'strong_new_score','soil1_gain_difference_z')
 if len(df)!=4108 or abs(reproduced['soil_moisture']['beta']-1.572793534002266)>1e-7:raise ValueError('Original soil association did not reproduce')
 df.to_csv(outdir/'paired_environment_and_chorus.csv.gz',index=False,compression='gzip')
 return df,{'weather':audit,'reproduced_original':reproduced,'original_source_commit':OLD_SOIL_SHA,'air_is_reanalysis_not_direct_satellite':True}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-root',default='_soil_original');ap.add_argument('--output',default='research/output/environment_context_20261019');ap.add_argument('--reuse-cache',action='store_true');a=ap.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 if a.reuse_cache:df=pd.read_csv(out/'paired_environment_and_chorus.csv.gz');audit=json.loads((out/'source_audit.json').read_text())
 else:df,audit=build_pair_cache(load_old(a.source_root),out);(out/'source_audit.json').write_text(json.dumps(audit,indent=2))
 stable=df[df.stable_sites].copy();z,sc=features(stable)
 result={'analysis':'existing_era5_environmental_state_moderation_2026_10_19','status':'executed_post_hoc','source':audit,'eligible':coverage(stable),'standardization':sc,'primary_three_contrasts':effects(z),'same_observer_sensitivity':effects(z[z.same_observer]),'route_fixed_effect_sensitivity':effects(z,True),'full_chorus_secondary':effects(z,response='new_ci3_count'),'temporal_transfer':transfer(stable),'soil_layer_delta_correlation':float(np.corrcoef(stable.soil1_w-stable.soil1_d,stable.soil2_w-stable.soil2_d)[0,1]),'not_environment_matched_causal_test':True,'not_JAE_conditional_concentration':True,'wet_dry_not_chronological':True,'main_unchanged':True}
 f=fit_model(z,INTERACTION);evaluations=[]
 for axis,tname in [('soil_mid_z','soil_delta_z:soil_mid_z'),('vpd_mid_z','soil_delta_z:vpd_mid_z')]:
  for q in [.25,.75]:
   value=float(z[axis].quantile(q));v=np.zeros(len(f.params));v[f.params.index.get_loc('soil_delta_z')]=1;v[f.params.index.get_loc(tname)]=value;b=float(v@f.params);se=float(np.sqrt(v@f.cov_params()@v));evaluations.append({'moderator':axis,'quantile':q,'moderator_z':value,'soil_delta_slope':b,'ci95':[b-1.959964*se,b+1.959964*se]})
 result['conditional_soil_slopes_other_moderator_at_mean']=evaluations
 (out/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print('RESULT_BEGIN\n'+json.dumps(result,indent=2,sort_keys=True)+'\nRESULT_END',flush=True)
 manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file() and p.name!='SHA256.json'};(out/'SHA256.json').write_text(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
