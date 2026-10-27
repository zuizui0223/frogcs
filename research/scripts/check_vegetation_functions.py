"""Matched sensitivity across every vegetation function at the prior reference stage."""
import pandas as pd
import argparse
ap=argparse.ArgumentParser();ap.add_argument("--d-duration",type=int,choices=[40,60],default=40);args=ap.parse_args()
prefix="reference" if args.d_duration==40 else "duration60"
from compare_vegetation_functions import FUNCTIONS,OUT,make_design,run
from audit_response_scales import compare
rows=[]
base=make_design(FUNCTIONS,wide=False)
base=base[(base.s_arrival==40)&(base.d_arrival==20)].reset_index(drop=True)
base["D_duration"]=args.d_duration
base["timing"]=f"S40_D20_dur45_40_{args.d_duration}"
for name,strength,kwargs in [('half_strength',.5,{}),('half_step',1.,{'dt':.125}),('rho25',1.,{}),('rho75',1.,{}),('conversion2',1.,{'conversion':(2,2,2)}),('conversion8',1.,{'conversion':(8,8,8)})]:
 des=base.copy()
 if name.startswith('rho'):des['rho']=int(name[3:])/100
 su,err=run(des,strength=strength,**kwargs);su.to_csv(OUT/(prefix+'_'+name+'_summary.csv'),index=False)
 for func,g in su.groupby('function'):rows+=compare(g,dict(function=func,timing=g.timing.iloc[0],check=name))
 print('Reference sensitivity',name,'complete',err,flush=True)
pd.DataFrame(rows).to_csv(OUT/(prefix+'_sensitivity.csv'),index=False)
