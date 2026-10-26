"""Exploratory three-guild associations, using existing calling-site data only.

Fixed before execution: all 4,248 primary sites; mean suitability, both SDM
backgrounds, all and pond-breeding Caudata; predictor-only tertiles; 1,000
route bootstrap draws. No model selection or prediction-gain criterion.
"""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
from scipy.stats import rankdata
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from naamp_site_use_associations import rank_association

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/results/naamp_odonata_caudata_associations_20261026'


def tertiles(values):
    cuts = np.quantile(values, [1/3, 2/3])
    if cuts[0] >= cuts[1]:
        raise ValueError('Cannot define distinct predictor tertiles')
    return np.searchsorted(cuts, values, side='left'), cuts


def interaction(d, xcol, scol, within=False):
    # Rank-scale interaction, standardized by full-sample rank SD in each draw.
    x = rankdata(d[xcol]); s = rankdata(d[scol]); y = rankdata(d.strong_rate)
    x = (x-x.mean())/x.std(); s = (s-s.mean())/s.std(); y = (y-y.mean())/y.std()
    design = np.column_stack([x,s,x*s])
    if within:
        groups = d.route.to_numpy()
        for g in np.unique(groups):
            mask = groups == g
            design[mask] -= design[mask].mean(axis=0)
            y[mask] -= y[mask].mean()
    design = np.column_stack([np.ones(len(y)), design])
    return np.linalg.lstsq(design,y,rcond=None)[0][-1]


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source = ROOT/'research/results/naamp_site_use_associations_20261026/primary_site_characteristics.csv.gz'
    d = pd.read_csv(source)
    assert len(d)==4248 and d.site.is_unique
    strata=[]; contrasts=[]; grids=[]; interactions=[]; config=[]
    rng=np.random.default_rng(20261027)
    blocks=[np.flatnonzero(d.route.to_numpy()==r) for r in sorted(d.route.unique())]
    indices=[np.concatenate([blocks[k] for k in rng.integers(0,len(blocks),len(blocks))]) for _ in range(1000)]
    for bg in ['uniform','target_group']:
        for group in ['Caudata','pond_breeding_Caudata']:
            xcol='mean_suitability_Odonata_'+bg; scol='mean_suitability_'+group+'_'+bg
            xbin,xcuts=tertiles(d[xcol]); sbin,scuts=tertiles(d[scol])
            config.append(dict(background=bg,group=group,odonata_cuts=xcuts.tolist(),caudata_cuts=scuts.tolist(),
                               predictor_spearman=rank_association(d[xcol],d[scol],d.route,False)))
            for sb in range(3):
                for xb in range(3):
                    sub=d[(sbin==sb)&(xbin==xb)]
                    grids.append(dict(background=bg,group=group,caudata_tertile=sb,odonata_tertile=xb,
                                      sites=len(sub),routes=sub.route.nunique(),mean_strong_rate=sub.strong_rate.mean()))
            for within in [False,True]:
                points=[]; draws=np.full((1000,3),np.nan)
                for sb in range(3):
                    sub=d[sbin==sb]
                    points.append(rank_association(sub[xcol],sub.strong_rate,sub.route,within))
                for b,idx in enumerate(indices):
                    for sb in range(3):
                        sub=d.iloc[idx[sbin[idx]==sb]]
                        val=rank_association(sub[xcol],sub.strong_rate,sub.route,within)
                        if val is not None: draws[b,sb]=val
                for sb in range(3):
                    sub=d[sbin==sb]; lo,hi=np.nanquantile(draws[:,sb],[.025,.975])
                    strata.append(dict(background=bg,group=group,within_route=within,caudata_tertile=sb,
                                       sites=len(sub),routes=sub.route.nunique(),rho=points[sb],low=lo,high=hi))
                diff=draws[:,2]-draws[:,0];lo,hi=np.nanquantile(diff,[.025,.975])
                contrasts.append(dict(background=bg,group=group,within_route=within,
                                      high_minus_low_rho=points[2]-points[0],low=lo,high=hi))
                # Continuous model is complementary to fixed-tertile visualization.
                beta=interaction(d,xcol,scol,within)
                betas=[interaction(d.iloc[idx].copy(),xcol,scol,within) for idx in indices]
                lo,hi=np.quantile(betas,[.025,.975])
                interactions.append(dict(background=bg,group=group,within_route=within,
                                         rank_interaction_beta=beta,low=lo,high=hi))
            print('completed',bg,group,flush=True)
    for name,rows in [('stratified_correlations',strata),('high_low_contrasts',contrasts),
                      ('binned_site_patterns',grids),('continuous_rank_interactions',interactions),('predictor_config',config)]:
        pd.DataFrame(rows).to_csv(OUT/(name+'.csv'),index=False)
    metadata=dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),sites=len(d),routes=len(blocks),
                  bootstrap=1000,seed=20261027,tertiles='Fixed full-cohort predictor cutpoints; ties not split',
                  interpretation='Exploratory associations; no causal trophic inference or independent replication',
                  uncertainty='Route resampling conditional on fitted SDM scores; no multiplicity correction')
    (OUT/'observed_results.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    g=pd.DataFrame(grids)
    fig,axes=plt.subplots(2,2,figsize=(11,9),sharex=True,sharey=True)
    vmin=g.mean_strong_rate.min();vmax=g.mean_strong_rate.max()
    for row,bg in enumerate(['uniform','target_group']):
        for col,group in enumerate(['Caudata','pond_breeding_Caudata']):
            ax=axes[row,col]; q=g[(g.background==bg)&(g.group==group)]
            mat=q.pivot(index='caudata_tertile',columns='odonata_tertile',values='mean_strong_rate')
            im=ax.imshow(mat,origin='lower',vmin=vmin,vmax=vmax,cmap='YlGnBu',aspect='auto')
            for z in q.itertuples():
                color='white' if z.mean_strong_rate>(vmin+vmax)/2 else '#111111'
                ax.text(z.odonata_tertile,z.caudata_tertile,f'{z.mean_strong_rate:.3f}\nn={z.sites}',ha='center',va='center',color=color,fontsize=11)
            ax.set_title(('All Caudata' if col==0 else 'Pond-breeding Caudata')+' | '+bg,fontsize=12)
            ax.set_xticks([0,1,2],['Low','Middle','High']);ax.set_yticks([0,1,2],['Low','Middle','High'])
            ax.set_xlabel('Odonata mean suitability tertile')
            ax.set_ylabel('Caudata mean suitability tertile')
    fig.suptitle('Calling frequency across Odonata and Caudata niches',fontsize=16)
    fig.subplots_adjust(left=.09,right=.87,top=.90,bottom=.12,hspace=.30,wspace=.28)
    cb=fig.colorbar(im,cax=fig.add_axes([.90,.25,.02,.5]));cb.set_label('Mean strong-call visit fraction')
    fig.text(.08,.025,'4,248 acoustic sites; each site weighted equally. Cells show means and site counts.\n'
             'Descriptive whole-area pattern, not pond preference or observed predation. SDM backgrounds shown separately.',fontsize=10)
    fig.savefig(OUT/'three_guild_niche_pattern.png',dpi=160)
    plt.close(fig)
    print(pd.DataFrame(contrasts).to_string(index=False))


if __name__=='__main__': main()
