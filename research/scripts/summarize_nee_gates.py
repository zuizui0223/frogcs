"""Summarize every declared G1 test and explicit unachieved G2/G3 gates."""
import json
from pathlib import Path
import pandas as pd
from nee_context_robustness import OUT,ROOT

def main():
    d=pd.read_csv(OUT/'coefficients.csv');s=pd.read_csv(OUT/'support_diagnostics.csv')
    assert len(s)==84 and len(d)==588
    assert set(s.status)=={'OK','LOW_BOOTSTRAP_SUPPORT'}
    assert d.loc[~d.inference_eligible,['p_centered_bootstrap','q_bh']].isna().all().all()
    focal=d.term.str.contains(':');key=d[(d.outcome=='strong_rate')&(d.subset=='all')&d.adjustment.isin(['none','space'])&focal]
    key.to_csv(OUT/'key_coefficients.csv',index=False)
    g=dict(G1=dict(status='PARTIAL_NOT_MET',reason='Uniform pooled O:S and O:V persist, but background/spatial/within-route and geographic support do not establish a transferable local mechanism'),G2=dict(status='NOT_MET',reason='No calibrated joint suitability-density-stage-abundance-calling observation bridge; current simulation three-way sign does not match frozen uniform macro term'),G3=dict(status='NOT_MET',reason='No independent discriminating three-guild experiment; density-dependent refuge response was already used to construct model and is not a new principle'),NEE_submission_ready=False,original_results_modified=False,models=84,coefficient_rows=588,route_bootstrap_draws=999,finite_focal_p_tests=int(d.loc[focal,'p_centered_bootstrap'].notna().sum()),unsupported_models=int((s.status!='OK').sum()))
    (OUT/'gate_status.json').write_text(json.dumps(g,indent=2)+'\n',encoding='utf-8')
    def table(frame):
        return '| '+' | '.join(frame.columns)+' |\n| '+' | '.join(['---']*len(frame.columns))+' |\n'+''.join('| '+' | '.join(f'{x:.4f}' if isinstance(x,float) else str(x) for x in row)+' |\n' for row in frame.itertuples(index=False,name=None))
    q=key[(key.adjustment=='space')&(key.bootstrap_cluster=='route')]
    text='# G1 quantitative readout — fixed 2026-10-29 design\n\n'+table(q[['background','mode','term','beta','low','high','q_bh']])+'\n\n## Geographic coverage\n\n'+table(pd.read_csv(OUT/'geographic_coverage.csv'))+'\n\n## Residual spatial diagnostic\n\n'+table(pd.read_csv(OUT/'residual_spatial_diagnostics.csv')[['background','adjustment','moran_I','permutation_p']])+'\n\n84 models; 588 coefficients. Four NW models have only 545/999 valid resamples; their p/q values are withheld. Intervals in these rows describe only the estimable resamples and are not adequate inferential intervals. BH uses 320 finite focal interaction p values; it does not correct prior research-wide selection. Fixed 2-degree bootstrap uses 56 geographic blocks.\n'
    (OUT/'quantitative_readout.md').write_text(text,encoding='utf-8')
    print(json.dumps(g,indent=2))

if __name__=='__main__':main()
