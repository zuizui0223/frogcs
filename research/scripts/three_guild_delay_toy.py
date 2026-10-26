"""ASSUMED mechanism illustration, not empirical parameter estimation."""
import argparse,csv,itertools,json,math
from pathlib import Path

def simulate(delay=0,third=True,cue=10,direct=.002,refuge=0,water=120,dt=.1,trace=False):
    arrival=10+delay;S=1.;D=0.;F=0.;started=False;introduced=False;completion=0.;history=[]
    for step in range(round(water/dt)+1):
        t=step*dt
        if third and t>=35-1e-9 and not introduced:D=1.;introduced=True
        if t>=arrival-1e-9 and not started:F=1.;started=True
        if t>=arrival+45-1e-9:completion=F;break
        if trace and step%max(1,round(1/dt))==0:history.append(dict(day=t,F=F,S=S,D=D))
        if t>=water-1e-9:break
        age=max(0,t-arrival);ssize=.15+.012*t;fsize=.15+.02*age
        vulnerability=1/(1+math.exp(-4*(ssize-fsize)))
        hs=.03*S*vulnerability*(1-refuge)/(1+cue*D)
        hd=direct*D*(1-refuge);hazard=hs+hd
        loss=F*(-math.expm1(-hazard*dt));fs=loss*hs/hazard if hazard else 0;fd=loss-fs
        F-=loss
        S=max(0,S+dt*.004*S*(1-S/2)+.05*fs)
        D=max(0,D+dt*.003*D*(1-D/2)+.05*fd)
    return dict(completion=completion,trajectories=history)

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    rows=[];contrasts=[]
    for cue,direct,refuge,water in itertools.product((0,1,3,10,30),(.002,.01,.03),(0,.5),(60,90,120)):
        vals={}
        for delay in range(0,61,5):
            for variant,third,q in (('two',False,0),('three_direct',True,0),('three_inhibition',True,cue)):
                value=simulate(delay,third,q,direct,refuge,water)['completion']
                vals[(variant,delay)]=value
                rows.append(dict(cue=cue,direct=direct,refuge=refuge,water=water,delay=delay,variant=variant,completion=value))
        # Same delay contrast (30 days), without selecting its sign.
        b=vals[('two',30)]-vals[('two',0)];c=vals[('three_inhibition',30)]-vals[('three_inhibition',0)]
        contrasts.append(dict(cue=cue,direct=direct,refuge=refuge,water=water,two_late_minus_early=b,three_late_minus_early=c,
                              rescued_direction=bool(b< -1e-9 and c>1e-9)))
    with (a.out/'all_synthetic_scenarios.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    illustration=[r for r in rows if r['cue']==10 and r['direct']==.002 and r['refuge']==0 and r['water']==120]
    numerical=max(abs(simulate(delay=d,dt=.1)['completion']-simulate(delay=d,dt=.05)['completion']) for d in range(0,61,5))
    result=dict(classification='SYNTHETIC_ASSUMPTIONS_NOT_EMPIRICAL',scenarios=len(rows),fixed_delay_contrasts=contrasts,
                hypothetical_sign_reversals=sum(r['rescued_direction'] for r in contrasts),parameter_settings=len(contrasts),
                illustrative_scenarios=illustration,step_halving_max_abs_difference_default= numerical,
                limits=['arbitrary coefficients, not calibrated','one-season aquatic completion, not mating success or coexistence',
                        'risk effect sign assumed; net delay effect not forced','no adult frog predation of emerging odonates',
                        'no inference that NAAMP frogs use these cues'])
    (a.out/'synthetic_results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:result[k] for k in ('scenarios','hypothetical_sign_reversals','parameter_settings','step_halving_max_abs_difference_default')}))

if __name__=='__main__':main()
