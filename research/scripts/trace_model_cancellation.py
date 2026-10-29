"""Read-only tracing of the original kernel and exact hazard factor accounting.

Algebraic decomposition of existing simulated trajectories is not a field causal
effect. Replaying a season at mean starting cohorts is checked against the saved
annual summaries, not silently equated with them.
"""
import inspect
import json
import sys

import numpy as np
import pandas as pd

from final_mechanism_common import OUT as SOURCE
from stage_vegetation_network import DEFAULT, simulate

OUT = SOURCE.parent / 'model_failure_diagnosis_20261029'


def traced_season(rows):
    parameters = rows[[k for k in DEFAULT if k in rows]].to_dict('records')
    for row in parameters:
        row.update(roles=15, cue=0.)
    controls = {k: rows[k].to_numpy(float) for k in ['cover_SF', 'cover_DF',
        'cover_DS', 'cover_SD', 'support_DF', 'support_DS', 'edge_SD', 'edge_DS']}
    controls.update(cue_SD=0., emerge_survival=0., emerge_exposure=0.)
    lines, start = inspect.getsourcelines(simulate)
    positions = [start + i for i, line in enumerate(lines) if 'hf=hsf+hdf;loss=' in line]
    assert len(positions) == 1
    samples = []
    n = len(rows)

    def tracer(frame, event, arg):
        if frame.f_code is not simulate.__code__:
            return None
        if event == 'line' and frame.f_lineno == positions[0]:
            local = frame.f_locals
            f = local['f']; v = local['v']
            response = (1-v)*2/(1+f) + v*2*f/(1+f*f)
            k = .025*local['scale']*local['gdf']*local['df_cover']*local['c']['edge_DF']
            np.testing.assert_allclose(local['hdf'], k*local['d']*response, atol=1e-14)
            data = {name: local[name] for name in ['t', 'f', 's', 'd', 'fw', 'hsf', 'hdf', 'hds', 'hsd']}
            data.update(response=response, K=k)
            samples.append(np.column_stack([np.broadcast_to(value, (n,)).copy() for value in data.values()]))
        return tracer

    previous = sys.gettrace()
    try:
        sys.settrace(tracer)
        season = simulate(parameters, dt=.25, initial_cohorts=rows[['F_B', 'S_B', 'D_B']].to_numpy(),
            stage_durations=rows[['F_duration', 'S_duration', 'D_duration']].to_numpy(),
            pathway_controls=controls, diagnostics=True, functional_response='litter')
    finally:
        sys.settrace(previous)
    assert len(samples) == 480
    trace = pd.DataFrame(np.stack(samples).reshape(-1, 11),
        columns=['t', 'f', 's', 'd', 'fw', 'hsf', 'hdf', 'hds', 'hsd', 'response', 'K'])
    trace['cell'] = np.tile(np.arange(n), 480)
    for col in ['vegetation', 'S_source', 'D_source']:
        trace[col] = np.tile(rows[col].to_numpy(), 480)
    for short, full in [('hsf', 'audit_H_SF'), ('hdf', 'audit_H_DF')]:
        integrated = (trace[short]*trace.fw*.25).groupby(trace.cell).sum()
        np.testing.assert_allclose(integrated, season[full], atol=1e-12)
    return trace, season


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    diagnostics, attribution, contributions = [], [], []
    for mid, source in [(1479, 'validation_13_none_1_cells.csv.gz'),
                        (1455, 'reduced_None_cells.csv.gz')]:
        rows = pd.read_csv(SOURCE / source)
        rows = rows[(rows.model_id == mid) & (rows.block_id == 13)].reset_index(drop=True)
        assert len(rows) == 18
        trace, season = traced_season(rows)
        trace.to_csv(OUT / f'season_trace_{mid}.csv.gz', index=False,
            compression={'method': 'gzip', 'mtime': 0})
        error = float(np.max(abs(season[['audit_H_SF', 'audit_H_DF']].to_numpy()
                                 - rows[['audit_H_SF', 'audit_H_DF']].to_numpy())))
        diagnostics.append(dict(model_id=mid, trace_matches_kernel=True,
            max_mean_cohort_vs_saved_annual_hazard_difference=error,
            interpretation='Single-season replay at saved mean starting cohorts'))
        # Check closeness, but retain measured difference instead of claiming identity.
        assert error < 1e-4
        for vegetation in [0., 1.]:
            parts = []
            for density in [.25, 2.]:
                low = trace[(trace.vegetation == vegetation) & (trace.D_source == density)
                            & (trace.S_source == .25)].set_index('t')
                high = trace[(trace.vegetation == vegetation) & (trace.D_source == density)
                             & (trace.S_source == 2.)].set_index('t')
                np.testing.assert_allclose(low.K, high.K, atol=0.)
                np.testing.assert_array_equal(low.fw, high.fw)
                # Exact symmetric product decomposition of d*response(f).
                density_part = low.K*(high.d-low.d)*(high.response+low.response)/2
                response_part = low.K*(high.response-low.response)*(high.d+low.d)/2
                np.testing.assert_allclose(density_part+response_part, high.hdf-low.hdf, atol=1e-12)
                hdf = float(((high.hdf-low.hdf)*low.fw*.25).sum())
                hsf = float(((high.hsf-low.hsf)*low.fw*.25).sum())
                parts.append(dict(D_source=density, density_component=float((density_part*low.fw*.25).sum()),
                    response_component=float((response_part*low.fw*.25).sum()), H_DF_change_S=hdf, H_SF_change_S=hsf))
                contributions.append(dict(model_id=mid, vegetation=vegetation, **parts[-1]))
            diff = {k: parts[1][k]-parts[0][k] for k in parts[0] if k != 'D_source'}
            diff['net_H_SD'] = diff['H_DF_change_S'] + diff['H_SF_change_S']
            diff['opposing_SF_fraction_of_DF'] = -diff['H_SF_change_S']/diff['H_DF_change_S']
            attribution.append(dict(model_id=mid, vegetation=vegetation, **diff))
    pd.DataFrame(contributions).to_csv(OUT / 'season_trace_S_contributions.csv', index=False)
    pd.DataFrame(attribution).to_csv(OUT / 'season_trace_SD_decomposition.csv', index=False)
    (OUT / 'season_trace_validation.json').write_text(json.dumps(diagnostics, indent=2)+'\n')
    print(pd.DataFrame(attribution).to_string(index=False))
    print(json.dumps(diagnostics, indent=2))


if __name__ == '__main__':
    main()
