"""Map potential richness of the explicitly modeled interaction-associated pool."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--results',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    env=pd.read_csv(a.results/'naamp_site_environment.csv.gz')
    data=pd.read_csv(a.results/'ssdm/naamp_group_potential_richness.csv.gz')
    meta=json.loads((a.results/'ssdm/observed_results.json').read_text(encoding='utf8'))
    domain=json.loads((a.results/'us_domain.geojson').read_text(encoding='utf8'))['geometry']
    polygons=domain['coordinates'] if domain['type']=='MultiPolygon' else [domain['coordinates']]
    fig,axes=plt.subplots(2,3,figsize=(14,10),sharex=True,sharey=True)
    for row,background in enumerate(('uniform','target_group')):
        for col,guild in enumerate(('Anura','Caudata','Odonata')):
            ax=axes[row,col]
            q=data[(data.background==background)&(data.group==guild)&(data.omission==.1)].merge(env[['site','lon','lat']],on='site',validate='one_to_one')
            for poly in polygons:
                x,y=zip(*poly[0]); ax.plot(x,y,color='#777777',lw=.6,zorder=0)
            n=meta['species_pool'][guild]
            points=ax.scatter(q.lon,q.lat,c=q.potential_richness,vmin=0,vmax=n,s=4,cmap='viridis',rasterized=True)
            ax.set_title(f'{guild}: {n} modeled species\n{background.replace("_"," ")} background')
            ax.set_xlim(-101,-65); ax.set_ylim(24,50)
            ax.set_aspect(1.3)
            fig.colorbar(points,ax=ax,shrink=.7,label='Potential suitable species')
            if row==1: ax.set_xlabel('Longitude')
            if col==0: ax.set_ylabel('Latitude')
    fig.suptitle('Predicted potential diversity at NAAMP survey locations',fontsize=16,y=.98)
    fig.text(.04,.025,'GloBI-evidence-selected species pool only; not total regional diversity or observed richness.\nSpecies-specific 10% training-omission thresholds. Rows show sensitivity to background choice.',fontsize=11)
    fig.tight_layout(rect=(0,.075,1,.96))
    fig.savefig(a.output,dpi=170)


if __name__=='__main__':
    main()
