"""Matched species contrasts at NAAMP sites with similar local calling calendars."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
from naamp_shared_site_pair import get_panel
import sdm_flooded_omission as sdm

OUT=sdm.ROOT/"species_predator_correlations_20261111"
def association(data, weights):
    # Frequency weights replicate route clusters; recalculating midranks includes ties.
    route,cols=data
    w=weights[route]
    if w.sum()<2: return np.full(4,np.nan)
    ranked=[]
    for codes in cols:
        mass=np.bincount(codes,weights=w)
        z=(mass.cumsum()-.5*mass)[codes]
        # Routes enter as complete blocks so the route mean uses original site weights.
        z-= (np.bincount(route,weights=z)/np.maximum(1,np.bincount(route)))[route]
        ranked.append(z)
    x,a,b,c=ranked
    def cor(x,y):
        den=np.sqrt((w@x**2)*(w@y**2))
        return (w*x)@y/den if den>1e-12 else np.nan
    raw=[cor(x,a),cor(x,b)]
    cc=w@c**2
    if cc:
        x,a,b=(v-c*((w*c)@v/cc) for v in (x,a,b))
    return np.array(raw+[cor(x,a),cor(x,b)])

def run(raw):
    traits=pd.read_csv(OUT/"breeding_traits_44.csv").set_index("species")
    panel=traits[traits.strong_routes>=25]
    surface=panel.egg_position.str.contains("floating|surface film")
    # Include every named label in the call matrix. Ambiguous complex labels are
    # excluded from the common other-species chorus, to avoid focal contamination.
    sites=sdm.site.set_index("site")
    names=traits.index.tolist()
    v=get_panel(raw,sites,species=names)
    assert v.shape[0]==63180
    total=v[names].ge(2).sum(axis=1)
    sy=['site','year']
    dates=v.melt(id_vars=sy+['doy'],value_vars=panel.index,var_name='species')
    observed=dates[dates.value>0].groupby(sy+['species']).doy
    med=observed.median().unstack()
    n=observed.nunique().unstack()
    models=sdm.models.query("background=='uniform' and guild=='Caudata'")
    suit=np.mean([sdm.refit(m,sdm.base) for m in models.itertuples()],axis=0)
    sites=sites.assign(suit=suit)
    route_levels=sorted(sites.route.unique())
    rc={k:i for i,k in enumerate(route_levels)}
    rng=np.random.default_rng(20261111)
    R=len(rc)
    boots=rng.multinomial(R,np.ones(R)/R,size=1000)
    weights=np.ones(R)
    records=[]; draws={}
    for a in panel.index[surface]:
        for b in panel.index[~surface]:
            if panel.at[a,'hydroperiod']!=panel.at[b,'hydroperiod']:continue
            gap=(med[a]-med[b]).abs()
            flags=v[[a,b]].ge(2).astype(int)
            byyear=flags.assign(other=(total-flags.sum(axis=1)>0).astype(int),visits=1,
                                site=v.site,year=v.year).groupby(sy).sum()
            assert (byyear.other<=byyear.visits).all()
            for window,minimum,history in [(7,1,False),(14,1,False),(7,2,False),(7,1,True)]:
                eligible=gap[(gap<=window)&(n[a]>=minimum)&(n[b]>=minimum)].index
                z=byyear.reindex(eligible)
                if history:z=byyear[byyear.index.get_level_values('site').isin(eligible.get_level_values('site'))]
                z=z.groupby(level='site').sum()
                rates=z[[a,b,'other']].div(z.visits,axis=0).join(sites[['route','suit']])
                nr=rates.route.nunique(); multi=(rates.route.value_counts()>=2).sum()
                result=[np.nan]*4
                key=(a,b,window,minimum,history)
                if multi>0:
                    data=(rates.route.map(rc).to_numpy(),[np.unique(rates[k],return_inverse=True)[1] for k in ['suit',a,b,'other']])
                    result=association(data,weights)
                    if multi>=25 and np.isfinite(result).all():
                        sim=np.array([association(data,w) for w in boots])
                        draws[key]=sim[:,2]-sim[:,3]
                records.append([*key,panel.at[a,'hydroperiod'],len(eligible),len(z),nr,multi,z.visits.sum(),*result])
    df=pd.DataFrame(records,columns=['surface','other','window','dates_per_species','all_years','hydroperiod','site_years','sites','routes','multi_site_routes','visits','surface_r','other_r','surface_partial','other_partial'])
    df['delta']=df.surface_r-df.other_r
    df['adjusted_delta']=df.surface_partial-df.other_partial
    df.to_csv(OUT/'shared_site_year_pairs.csv',index=False)
    rows=[]
    for key,g in df.groupby(['window','dates_per_species','all_years']):
        for floor in [2,10,25]:
            q=g[(g.multi_site_routes>=floor)&g.adjusted_delta.notna()].copy()
            lo=hi=np.nan; valid=0
            if floor==25 and len(q):
                m=np.stack([draws[(r.surface,r.other,*key)] for r in q.itertuples()])
                good=np.isfinite(m).all(axis=0)
                valid=sum(good)
                if valid:lo,hi=np.quantile(m[:,good].mean(axis=0),[.025,.975])
            rows.append([*key,floor,len(q),q.surface.nunique(),q.other.nunique(),q.delta.mean(),q.adjusted_delta.mean(),sum(q.adjusted_delta>0),lo,hi,valid])
    s=pd.DataFrame(rows,columns=['window','dates_per_species','all_years','min_multi_site_routes','pairs','surface_species','other_species','delta','adjusted_delta','positive','low','high','valid_draws'])
    s.to_csv(OUT/'shared_site_year_summary.csv',index=False)
    print(s.round(4).to_string(index=False))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('raw',type=Path)
    with threadpool_limits(limits=1):run(parser.parse_args().raw)
