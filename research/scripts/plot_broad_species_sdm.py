"""Validation and matched-site diagnostics, never an occupancy-probability map."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--results',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    df=pd.read_csv(a.results/'species_matched_comparison.csv')
    order=df[df.background=='uniform'].sort_values(['guild','species']).species.tolist()
    fig, axes=plt.subplots(1,2,figsize=(13,10),sharey=True,gridspec_kw={'width_ratios':[1,1.1]})
    for kind,color,offset in [('uniform','#2076a4',-.13),('target_group','#d67a23',.13)]:
        part=df[df.background==kind].set_index('species').reindex(order)
        y=np.arange(len(order))+offset
        axes[0].scatter(part.mean_auc_2deg,y,c=color,s=28,label=kind.replace('_',' '))
        axes[0].scatter(part.mean_auc_4deg,y,facecolors='none',edgecolors=color,s=45,marker='s')
        x=part.route_mean_percentile_difference.to_numpy()*100
        lo=part.bootstrap_low.to_numpy()*100
        hi=part.bootstrap_high.to_numpy()*100
        axes[1].errorbar(x,y,xerr=np.array([x-lo,hi-x]),fmt='o',color=color,markersize=4,capsize=2,lw=1)
    axes[0].set_yticks(range(len(order)),[x.replace('Lithobates ','L. ').replace('Ambystoma ','A. ') for x in order])
    axes[0].invert_yaxis()
    axes[0].axvline(.5,c='gray',ls='--',lw=1)
    axes[1].axvline(0,c='gray',ls='--',lw=1)
    axes[0].set_xlabel('Spatially held-out presence/background AUC\nfilled circles: 2-degree blocks; open squares: 4-degree blocks')
    axes[1].set_xlabel('Strong-call minus silent site suitability percentile\npercentage points; equal-route mean and 95% bootstrap interval')
    axes[0].set_title('Can species suitability be predicted across space?')
    axes[1].set_title('Do matched calling sites differ in that suitability?')
    axes[0].legend(loc='lower left',fontsize=9)
    for ax in axes:
        ax.grid(axis='y',alpha=.15)
        ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Broad GBIF species models projected to NAAMP',fontsize=16,y=.98)
    fig.text(.02,.025,'Climate/landscape suitability, not calibrated occupancy or observed predator abundance.\nExploratory intervals are not corrected for multiple species; source-bias sensitivity is shown in orange.',fontsize=10)
    fig.tight_layout(rect=(0,.07,1,.96))
    fig.savefig(a.output,dpi=170)


if __name__=='__main__':
    main()
