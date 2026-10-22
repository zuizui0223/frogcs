#!/usr/bin/env python3
"""Synthetic design-only P×F×O (8 tanks/block) and P×F×O×C (16 tanks/block).

Primary outcome is focal tadpole survival probability, with fixed exposure
window, 20 larvae/tank, tank beta-binomial correlation and whole-block t tests.
Animal observations NEVER enter this script. Higher-order risk contrasts do NOT
identify causal mediation through fish predation of dragonflies.
"""
import argparse, json, math
from pathlib import Path
import numpy as np
from scipy.stats import t as td

B3=np.array([.80,.54,.64,.56,.82,.66,.70,.72])
B4=np.array([B3[i//2]-.06*(i%2) for i in range(16)])
ALPHA=.05/3
N_LARVAE=20
GRID_BLOCKS=(8,16,32,64,128)
RHO=(.05,.20)
DELTA=(0.,.20,.40,.60)

def signs(n):
    k=int(np.log2(n))
    return np.array([(-1.)**(k-bin(i).count('1')) for i in range(n)])

def contrast(prob,sign):return np.sum(np.asarray(prob)*sign,axis=-1)

def power(base,sign,b,rho,delta,iterations,seed,batch):
    cells=len(base)
    p0=base+sign*(delta/cells)
    assert abs(float(contrast(p0,sign))-delta)<1.e-12
    assert p0.min()>.15 and p0.max()<.95
    rng=np.random.default_rng(seed)
    crit=float(td.ppf(1-ALPHA/2,b-1))
    rejections=0
    for start in range(0,iterations,batch):
        m=min(batch,iterations-start)
        # A common block quality shift cancels in the alternating contrast.
        shifts=np.clip(rng.normal(0,.025,size=(m,b,1)),-.06,.06)
        p=p0.reshape(1,1,cells)+shifts
        assert np.all((p>0)&(p<1))
        if rho:
            conc=1/rho-1
            latent=rng.beta(p*conc,(1-p)*conc)
        else:latent=p
        success=rng.binomial(N_LARVAE,latent)/N_LARVAE
        d=(success*sign).sum(axis=-1)
        mu=d.mean(axis=1)
        se=d.std(axis=1,ddof=1)/math.sqrt(b)
        t=np.divide(mu,se,out=np.zeros_like(mu),where=se>0)
        rejections+=int(np.count_nonzero(np.abs(t)>crit))
    prob=rejections/iterations
    return {'blocks':b,'tanks':cells*b,'icc':rho,'delta_risk_contrast':delta,
            'rejections':rejections,'reps':iterations,'power':prob,
            'mc95_half_width':1.96*math.sqrt(prob*(1-prob)/iterations)}

def simulate(label,base,seed_root,batch,reps):
    sign=signs(len(base))
    assert abs(float(contrast(base,sign)))<1e-12
    rows=[]
    for ri,rho in enumerate(RHO):
        for di,delta in enumerate(DELTA):
            for b in GRID_BLOCKS:
                seed=seed_root+100000*ri+10000*di+10*b
                rows.append(power(base,sign,b,rho,delta,reps,seed,batch))
    minima=[]
    for rho in RHO:
        for d in DELTA[1:]:
            eligible=[x['blocks'] for x in rows if x['icc']==rho and x['delta_risk_contrast']==d and x['power']>=.8]
            minima.append({'icc':rho,'delta':d,'first_grid_blocks_ge80pct':min(eligible) if eligible else None})
    return {'label':label,'n_cells':len(base),'baseline_risks':base.tolist(),
            'baseline_null_contrast':float(contrast(base,sign)),'grid':rows,'grid80':minima}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--reps',type=int,default=3000)
    a=ap.parse_args()
    if a.reps<1000:raise SystemExit('At least 1000 simulations per scenario')
    assert all(abs(float(contrast(B3[4*p:4*p+4],signs(4)))-.18)<1e-12 for p in (0,1))
    logits=np.array([.1+.7*p-1.0*f-.7*o for p in (0,1) for f in (0,1) for o in (0,1)])
    probs=1/(1+np.exp(-logits))
    demo={'logit_PFO_contrast':float(contrast(logits,signs(8))),
          'risk_PFO_contrast':float(contrast(probs,signs(8)))}
    assert abs(demo['logit_PFO_contrast'])<1.e-10
    assert abs(demo['risk_PFO_contrast'])>1.e-3
    designs=[simulate('PFO',B3,2601023,300,a.reps),
             simulate('PFOC',B4,3101023,150,a.reps)]
    out={'status':'SYNTHETIC_power_calibration_not_observed_frogs','date':'2026-10-23',
         'mechanism':'fish x odonate larval predator effects with/without macrophyte structure; optional heterospecific tadpole competitor C',
         'risk_contrast':'alternating 2^k signed sum of survival probabilities (not single-cell difference)',
         'design':'full-factorial, randomized one tank per treatment within complete independent spatial block',
         'within_tank_20_tadpoles_not_20_replicates':True,
         'model':'beta-binomial tank ICC, common truncated-Normal (sd=.025) additive within-block hydrology shift',
         'alpha':ALPHA,'alpha_reason':'conservative Bonferroni for 3 distinct prospective tests PC, FO with mediator control, PFO; PFOC is exploratory extension',
         'monte_carlo_reps_per_scenario':a.reps,
         'mathematical_link_scale_caution':demo,
         'designs':designs,
         'source_mechanistic_frog_survival_data_used':False,
         'causal_mediation_identified':False,
         'no_live_animal_experiment_performed':True,
         'frozen_RC6_untouched':True,
         'scope_note':'Hypothetical baseline probabilities, effect contrasts and ICC values must be replaced with genuine pilot estimates before a confirmatory experiment.'}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('HIGHERORDER_POWER_RECEIPT_BEGIN')
    print(json.dumps({'status':out['status'],'grid80':{x['label']:x['grid80'] for x in designs},
      'spotcheck':{x['label']:[v for v in x['grid'] if v['blocks'] in (8,32) and v['delta_risk_contrast'] in (.2,.4)] for x in designs}},sort_keys=True))
    print('HIGHERORDER_POWER_RECEIPT_END')
if __name__=='__main__':main()
