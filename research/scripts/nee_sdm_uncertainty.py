"""Spatial SDM refit stability; fixed observation model, no density calibration."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import argparse,json
import numpy as np
import pandas as pd
from broad_species_sdm import features as sdm,thin
from nee_context_robustness import ROOT,load,zrank
from nee_existing_strata import covariates
from common_scale_comparison import features
from naamp_site_use_associations import POND
OUT=ROOT/'research/results/nee_boundaries_20261029';SRC=ROOT/'research/results/interaction_species_sdm_20261026';COL=['bio1','bio4','bio12','bio15','flooded','water']

def blocks(d):return (np.floor(d.lat/2).astype(int).astype(str)+'_'+np.floor(d.lon/2).astype(int).astype(str)).to_numpy()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--replicates',type=int,default=49);args=ap.parse_args();OUT.mkdir(parents=True,exist_ok=True)
 d=load();c=covariates(d);y=zrank(d.strong_rate.to_numpy());v=zrank(d.flooded_3000m_mean.to_numpy())
 pr=pd.read_csv(SRC/'training_presence_environment.csv.gz',dtype={'species_key':str});bg=pd.read_csv(SRC/'background.csv.gz');sites=pd.read_csv(SRC/'naamp_site_environment.csv.gz').set_index('site').loc[d.site];saved=pd.read_csv(SRC/'naamp_species_suitability.csv.gz',dtype={'species_key':str})
 modeled=saved[(saved.guild=='Odonata')|saved.species.isin(POND)].species_key.unique();pr['block']=blocks(pr);bg['block']=blocks(bg)
 unique=sorted(set(pr.block)|set(bg.block));rng=np.random.default_rng(20261029);mult=rng.multinomial(len(unique),np.full(len(unique),1/len(unique)),size=args.replicates)
 counts=[None]+[dict(zip(unique,row)) for row in mult];rows=[];diagnostics=[];guildsaved=[];allguild=[]
 for rep,weights in enumerate(counts):
  for background in ['uniform','target_group']:
   values={'O':[],'S':[]}
   for sid in sorted(modeled):
    pp=pr[pr.species_key==sid];guild=pp.guild.iloc[0]
    if background=='uniform':bb=bg
    else:bb=pd.DataFrame(thin(pr[(pr.guild==guild)&(pr.species_key!=sid)].to_dict('records')))
    if weights is None:p=pp;b=bb
    else:
     p=pp.loc[pp.index.repeat(pp.block.map(weights).to_numpy())];b=bb.loc[bb.index.repeat(bb.block.map(weights).to_numpy())]
    if len(p)<10 or len(b)<20:raise ValueError('Insufficient bootstrap training rows')
    x=np.vstack([p[COL],b[COL]]);yy=np.r_[np.ones(len(p)),np.zeros(len(b))];m=sdm(x);m.fit(x,yy)
    reference=np.sort(m.decision_function(bg[COL].to_numpy()));pred=np.searchsorted(reference,m.decision_function(sites[COL].to_numpy()),side='right')/len(reference)
    if weights is None:
     old=saved[(saved.species_key==sid)&(saved.background==background)].set_index('site').loc[d.site].suitability_percentile.to_numpy()
     error=float(np.max(np.abs(pred-old)));diagnostics.append(dict(species_key=sid,background=background,max_replay_error=error));np.testing.assert_allclose(pred,old,atol=.000250001)
    values['O' if guild=='Odonata' else 'S'].append(pred)
   o=np.mean(values['O'],axis=0);s=np.mean(values['S'],axis=0);allguild.append(np.column_stack([o,s]));x=features(zrank(o),zrank(s),v);z=np.column_stack([x,c,np.ones(len(d))]);beta=np.linalg.lstsq(z,y,rcond=1e-10)[0][:7]
   for j,t in enumerate(['O','S','V','OS','OV','SV','OSV']):rows.append(dict(replicate=rep,background=background,term=t,beta=beta[j]))
   if rep in [0,1,2]:guildsaved.append(pd.DataFrame(dict(site=d.site,replicate=rep,background=background,O=o,S=s)))
  if rep%5==0:print('SDM replication',rep,flush=True);pd.DataFrame(rows).to_csv(OUT/'sdm_bootstrap_coefficients.csv',index=False)
 pd.DataFrame(rows).to_csv(OUT/'sdm_bootstrap_coefficients.csv',index=False);pd.DataFrame(diagnostics).to_csv(OUT/'sdm_replay.csv',index=False);pd.concat(guildsaved).to_csv(OUT/'sdm_example_guild_predictions.csv.gz',index=False,compression={'method':'gzip','mtime':0})
 np.save(OUT/'sdm_guild_draws.npy',np.asarray(allguild).reshape(len(counts),2,len(d),2))
 (OUT/'sdm_receipt.json').write_text(json.dumps(dict(replicates=args.replicates,seed=20261029,blocks=len(unique),species=len(modeled),resampling='same 2-degree geographic block weights across species and backgrounds',uncertainty='SDM training resampling only; observation model/site sample fixed',reference_background='original4000 points re-scored for each fit',interpretation='finite-replicate stability, not joint95percent confidence intervals'),indent=2)+'\n')
if __name__=='__main__':main()
