"""Post-pilot synthetic sensitivity: arbitrary reversal, mobility and third guild."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from dataclasses import replace
from pathlib import Path
import numpy as np
import pandas as pd
from multigeneration_reversal import (
    Rates, STAGES, initial_grid, simulate_abm, simulate_pde,
    OUT, FT, FA, DN, DA,
)

ATTACK = (0., .01, .04, .12)
MOVEMENT = ("stage_specific", "no_movement")
THIRD = ("D_to_S_on", "D_to_S_off")
SEEDS = (101, 102)
YEARS = (1, 2, 5, 10, 20)


def design(params=Rates()):
    all_parameters = []
    for motion, third, rate in itertools.product(MOVEMENT, THIRD, ATTACK):
        p = replace(params, a_fe=rate, a_ds=(params.a_ds if third == "D_to_S_on" else 0.),
                    diffusion=(params.diffusion if motion == "stage_specific" else (0.,)*7))
        all_parameters.append((motion,third,rate,p))
    return all_parameters


def run_sensitivity(years=20, dt=.025, seeds=SEEDS, out=OUT):
    if years < max(YEARS):
        raise ValueError("Sensitivity requires full 20-year horizon")
    init,v=initial_grid()
    rows=[]
    for motion,third,rate,p in design():
        for method,seed in [("pde",-1)]+[("abm",int(s)) for s in seeds]:
            if method=="pde":
                trajectory,_=simulate_pde(init,v,p,years,dt,reverse=rate>0)
            else:
                trajectory,_=simulate_abm(init,v,p,years,dt,reverse=rate>0,seed=seed)
            selected=trajectory[trajectory.year.isin(YEARS)]
            for r in selected.itertuples(index=False):
                rows.append(dict(method=method,seed=seed,mobility=motion,third_guild=third,
                                 a_fe=rate,year=int(r.year),
                                 F_adult=r.F_adult,F_tadpole=r.F_tadpole,
                                 D_adult=r.D_adult,D_nymph=r.D_nymph,
                                 D_occupied_cells=r.D_occupied_cells,
                                 kill_D_emerging=r.deaths_F_adult_to_D_emerging))
        print("Sensitivity",motion,third,"attack",rate,flush=True)
    table=pd.DataFrame(rows).sort_values(['method','seed','mobility','third_guild','a_fe','year'])
    pairs=[]
    for key,g in table.groupby(['method','seed','mobility','third_guild','year']):
        base=g[g.a_fe==0.]
        if len(base)!=1 or len(g)!=len(ATTACK):
            raise AssertionError("Unpaired reference")
        ref=base.iloc[0]
        for x in g.itertuples(index=False):
            for metric in ('F_adult','F_tadpole','D_adult','D_nymph','D_occupied_cells'):
                pairs.append(dict(method=x.method,seed=x.seed,mobility=x.mobility,
                                  third_guild=x.third_guild,a_fe=x.a_fe,year=x.year,
                                  measure=metric,baseline=float(ref[metric]),
                                  delta=float(getattr(x,metric)-ref[metric])))
    diff=pd.DataFrame(pairs)
    if not np.all(diff.loc[diff.a_fe==0.,'delta']==0):
        raise AssertionError("Zero-reversal control not exactly zero")
    if (table[['F_adult','F_tadpole','D_adult','D_nymph']]<0).any().any():
        raise AssertionError("Negative population")
    if not table.D_occupied_cells.between(0,len(v)).all():
        raise AssertionError("Invalid patch occupancy")
    out.mkdir(exist_ok=True,parents=True)
    table.to_csv(out/'post_pilot_sensitivity_endpoints.csv',index=False)
    diff.to_csv(out/'post_pilot_sensitivity_contrasts.csv',index=False)
    receipt=dict(status="POST_PILOT_SYNTHETIC_NOT_PREREGISTERED_OR_FIELD_FIT",
                 years=years,dt=dt,attack=list(ATTACK),mobility=list(MOVEMENT),
                 third_guild=list(THIRD),seeds=list(seeds),year_endpoints=list(YEARS),
                 design_scenarios=len(design()),data_rows=len(table),
                 contrast_rows=len(diff),zero_control_exact=True,
                 claim_limits=["Post hoc sensitivity after strong default extinction",
                               "PDE is deterministic and ABM extinction is stochastic",
                               "ABM paired seed labels are not matched random event streams",
                               "Rates not estimated from observed frog-dragonfly feeding",
                               "No field comparison or NAAMP acoustic validation"],
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'post_pilot_sensitivity_receipt.json').write_text(json.dumps(receipt,indent=2)+"\n")
    return table,diff,receipt


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--run',action='store_true')
    args=p.parse_args()
    if not args.run:p.error("Explicit --run required")
    a,b,r=run_sensitivity()
    print(json.dumps(r,indent=2))
    show=b[(b.measure.isin(['F_adult','D_adult','D_occupied_cells'])) &
           (b.a_fe.isin((.01,.04,.12))) &
           (b.year.isin((5,20)))]
    print(show.to_string(index=False))


if __name__=='__main__':
    main()
