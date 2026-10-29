"""Independent descriptive stage-count audit; not acoustic calibration or causal validation."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
from scipy.stats import rankdata,spearmanr

P=Path(__file__).resolve().parent
def zrank(x):
    x=rankdata(x);return (x-x.mean())/x.std()

def main():
    source=P/'alpine/data/N_73/TableAnalyse_RNN74_Odo_Amphi_Macrophytes_sitesOK.csv'
    d=pd.read_csv(source,sep=';');d.columns=d.columns.str.strip()
    assert len(d)==73 and d.Site.is_unique and d.columns.is_unique
    physical=[x for x in d if x.startswith(('Adult_','SubAdult_'))]
    values=d[physical].to_numpy()
    assert np.isfinite(values).all() and (values>=0).all() and np.equal(values,np.floor(values)).all()
    env=pd.read_csv(P/'alpine/data/N_73/occ.cov_2.csv',sep=';')
    assert set(env.Site)==set(d.Site) and env.Site.is_unique
    rows=[]
    for session in ['S01','S02']:
        q=pd.DataFrame({'Site':d.Site,'session':session})
        for stage in ['Adult','SubAdult']:
            q[stage+'_frog']=d[[f'{stage}_AmpRanatemporaria_{session}',f'{stage}_AmpBufobufo_{session}']].sum(axis=1)
            q[stage+'_newt']=d[f'{stage}_AmpIchthyosauraalpestris_{session}']
            q[stage+'_odonata']=d[[c for c in d if c.startswith(stage+'_Odo') and c.endswith(session)]].sum(axis=1)
        mac=[c for c in d if c.startswith('Adult_Mac') and c.endswith(session)]
        # Source duplicates physical plant observations across the two stage slots.
        for c in mac:np.testing.assert_array_equal(d[c],d[c.replace('Adult_','SubAdult_',1)])
        q['macrophyte_richness']=d[mac].gt(0).sum(axis=1)
        rows.append(q)
    c=pd.concat(rows,ignore_index=True).merge(env[['Site','Dry_Obs','TopoDist','NDVI_med_100']],on='Site',validate='many_to_one')
    assert len(c)==146 and not c.duplicated(['Site','session']).any() and not c.isna().any().any()
    c.to_csv(P/'alpine_keyed_stage_counts.csv',index=False)
    coverage=[]
    for stage in ['Adult','SubAdult']:
        for guild in ['frog','newt','odonata']:
            x=c[stage+'_'+guild]
            coverage.append(dict(stage=stage,guild=guild,total_count=int(x.sum()),positive_site_sessions=int((x>0).sum()),positive_sites=int(c.loc[x>0,'Site'].nunique())))
    pd.DataFrame(coverage).to_csv(P/'alpine_stage_coverage.csv',index=False)
    c['D_present']=c.SubAdult_odonata.gt(0);c['S_present']=c.SubAdult_newt.gt(0)
    c.groupby(['D_present','S_present']).agg(site_sessions=('Site','size'),sites=('Site','nunique'),frog_positive=('SubAdult_frog',lambda x:int((x>0).sum())),plant_richness_min=('macrophyte_richness','min'),plant_richness_max=('macrophyte_richness','max')).to_csv(P/'alpine_overlap_support.csv')
    # Fixed one-model-family exploratory check: all seven rank terms, then add
    # session, observed drying and rank-distance as common-habitat sensitivity.
    o=zrank(c.SubAdult_odonata);s=zrank(c.SubAdult_newt);v=zrank(c.macrophyte_richness);y=zrank(c.SubAdult_frog)
    terms=['O','S','V','O:S','O:V','S:V','O:S:V'];base=np.column_stack([o,s,v,o*s,o*v,s*v,o*s*v])
    ids=pd.factorize(c.Site,sort=True)[0];rng=np.random.default_rng(20261029);w=rng.multinomial(73,np.full(73,1/73),size=999)
    results=[]
    for adjustment in ['session','session_hydroperiod_connectivity']:
        controls=[np.ones(len(c)),(c.session=='S02').astype(int)]
        if adjustment!='session':controls += [zrank(c.Dry_Obs),zrank(c.TopoDist)]
        x=np.column_stack([base,*controls]);assert np.linalg.matrix_rank(x)==x.shape[1]
        b=np.linalg.lstsq(x,y,rcond=None)[0];boot=[]
        for weight in w:
            sw=np.sqrt(weight[ids]);xx=x*sw[:,None]
            bb,_,rank,_=np.linalg.lstsq(xx,y*sw,rcond=None)
            if rank==x.shape[1]:boot.append(bb[:7])
        boot=np.asarray(boot);lo,hi=np.quantile(boot,[.025,.975],axis=0)
        for j,t in enumerate(terms):results.append(dict(adjustment=adjustment,term=t,beta=float(b[j]),low=float(lo[j]),high=float(hi[j]),valid_bootstraps=len(boot)))
    pd.DataFrame(results).to_csv(P/'alpine_exploratory_rank_associations.csv',index=False)
    sums=dict(sites=73,site_sessions=146,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),seed=20261029,bootstrap=999,raw_odonata_total=int(c[['Adult_odonata','SubAdult_odonata']].sum().sum()),raw_amphibian_total=int(c[['Adult_frog','SubAdult_frog','Adult_newt','SubAdult_newt']].sum().sum()),paper_odonata_total=1108,paper_amphibian_total=1437,calling_available=False,density_calibrated=False,odonata_nonadult_mixes_larvae_exuviae_emergents=True,vegetation_structure_measured=False,claim='Exploratory stage-count association, not independent reproduction of the acoustic estimand or causal mechanism')
    (P/'alpine_audit_summary.json').write_text(json.dumps(sums,indent=2)+'\n')
    print(json.dumps(sums));print(pd.DataFrame(results).to_string(index=False))

if __name__=='__main__':main()
