"""Static evidence figures; empirical and hypothetical panels kept in separate files."""
import argparse,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parents[1]/'results'
    d=json.loads((root/'naamp_three_guild_occurrence/observed_results.json').read_text(encoding='utf8'))
    x=next(x for x in d['overlap'] if x['radius_km']==25 and x['accuracy']=='strict')
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(11.8,4.6),gridspec_kw={'width_ratios':[1.35,1]})
    labels={'Anura':'Frogs','Caudata':'Salamanders','Odonata':'Odonates'}
    for r,c in zip(x['pairs'],['#28666e','#d37b24','#825d9e']):
        vals=[r[k]['jaccard'] for k in ('neighborhood','neighborhood_year','neighborhood_year_month')]
        axes[0].plot(range(3),vals,'o-',color=c,lw=2,label=labels[r['guild_a']]+' / '+labels[r['guild_b']])
    axes[0].set(xticks=range(3),xticklabels=['Neighborhood','+ same year','+ same month'],ylim=(0,.72),ylabel='Recorded-set overlap (Jaccard)',title='Spatial overlap shrinks with temporal alignment')
    axes[0].legend(frameon=False,fontsize=9)
    h=d['full_naamp_environment_matched_history'];v=h['equal_route_mean_prior_difference']*100;lo,hi=np.array(h['equal_route_bootstrap_interval'])*100
    axes[1].errorbar(v,0,xerr=[[v-lo],[hi-v]],fmt='o',color='#28666e',capsize=5,markersize=9)
    axes[1].axvline(0,color='#999999',lw=1);axes[1].set(xlim=(-3,40),ylim=(-.8,.8),yticks=[],xlabel='Prior strong-call frequency difference\n(strong now minus silent now, percentage points)',title='Past calling remains associated with current calling')
    axes[1].text(21,.42,f'{v:.1f} pp [{lo:.1f}, {hi:.1f}]',ha='center',fontsize=13)
    axes[1].text(21,-.40,'4,040 disjoint matches / 389 routes\nSame run; background, temperature and noise matched',ha='center',fontsize=9)
    fig.suptitle('Observed patterns — NAAMP recording sites and surrounding records',fontsize=14)
    fig.text(.5,.015,'25-km pilot, uncertainty ≤1 km; unknown life stage retained. Recording sites are not verified ponds. History association is not causal memory.',ha='center',fontsize=8)
    fig.tight_layout(rect=[0,.07,1,.92]);fig.savefig(a.out/'three_guild_observed_patterns.png',dpi=170);plt.close(fig)
    d=json.loads((root/'three_guild_delay_toy/synthetic_results.json').read_text(encoding='utf8'))
    fig,ax=plt.subplots(figsize=(8.5,5))
    for variant,label,color in [('two','F + S','#28666e'),('three_direct','F + S + D: direct predation only','#b35242'),('three_inhibition','F + S + D: direct + S suppression','#a1781b')]:
        rows=[r for r in d['illustrative_scenarios'] if r['variant']==variant]
        ax.plot([r['delay'] for r in rows],[r['completion'] for r in rows],'-o',markersize=3,color=color,label=label)
    ax.set(xlabel='Delay of frog cohort relative to its baseline (hypothetical days)',ylabel='Fraction completing aquatic development',ylim=(0,1),title='An assumed third pathway can reverse the cost of delay')
    ax.legend(frameon=False,loc='lower left');fig.suptitle('HYPOTHETICAL MODEL — not fitted to occurrence or calling data',fontsize=11,color='#9a501f')
    fig.text(.5,.02,'Illustration fixed in advance: water 120 days, refuge 0, D attack 0.002, inhibition 10.\n20 of 90 tested parameter settings reversed the 30-day delay contrast; not a probability in nature.',ha='center',fontsize=8)
    fig.tight_layout(rect=[0,.1,1,.94]);fig.savefig(a.out/'three_guild_hypothetical_delay.png',dpi=170);plt.close(fig)

if __name__=='__main__':main()
