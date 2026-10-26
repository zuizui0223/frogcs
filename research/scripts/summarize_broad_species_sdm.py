"""Join independently trained species suitability to fixed NAAMP matched pairs."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--results', type=Path, required=True)
    args = p.parse_args()
    d = args.results
    models = json.loads((d/'models.json').read_text())
    predictions = pd.read_csv(d/'naamp_species_suitability.csv.gz', dtype={'species_key':str})
    pairs = pd.read_csv(ROOT/'research/results/naamp_three_guild_occurrence/full_naamp_history/matched_strong_silent_history.csv')
    rows = []
    for m in models:
        if m['status'] != 'fit':
            continue
        spec = str(m['species_key'])
        subset = predictions[(predictions.species_key==spec)&(predictions.background==m['background'])]
        if subset.site.duplicated().any():
            raise ValueError('Duplicate site/species/background prediction')
        lookup = subset.set_index('site')
        paired = pairs.copy()
        paired['chosen'] = paired.chosen_site.map(lookup.suitability_percentile)
        paired['silent'] = paired.silent_site.map(lookup.suitability_percentile)
        paired = paired.dropna(subset=['chosen','silent'])
        paired['difference'] = paired.chosen-paired.silent
        routes = paired.groupby('route').difference.mean().to_numpy()
        if not len(routes):
            rows.append(dict(species_key=spec, species=m['species'], guild=m['guild'],
                             background=m['background'], status='no_complete_matched_pairs'))
            continue
        rng = np.random.default_rng(20261026)
        boot = [rng.choice(routes,len(routes),replace=True).mean() for _ in range(2000)]
        ci = np.quantile(boot,[.025,.975])
        row = dict(species_key=spec, species=m['species'], guild=m['guild'], background=m['background'],
                   presence_cells=m['cells'], matched_pairs=len(paired), routes=len(routes),
                   route_mean_percentile_difference=float(routes.mean()),
                   bootstrap_low=float(ci[0]), bootstrap_high=float(ci[1]),
                   projected_sites=len(subset), extrapolated_sites=int(subset.environment_extrapolation.sum()))
        for size in (2,4):
            auc = [x['auc'] for x in m['cv'] if x['block_degrees']==size and x['auc'] is not None]
            row[f'valid_folds_{size}deg'] = len(auc)
            row[f'mean_auc_{size}deg'] = float(np.mean(auc)) if auc else None
            row[f'min_auc_{size}deg'] = float(min(auc)) if auc else None
        rows.append(row)
    pd.DataFrame(rows).to_csv(d/'species_matched_comparison.csv',index=False)
    # Attach actual normalized GloBI relationships, leaving unmatched pairs unasserted.
    source = ROOT/'research/results/three_guild_globi_live'
    crosswalk = json.loads((source/'taxon_crosswalk.json').read_text())['names']
    keys = {x['globi_name']:str(x['accepted_key']) for x in crosswalk if x['status']=='EXACT_ACCEPTED_SPECIES_BRIDGE'}
    edges = pd.read_csv(source/'direction_normalized_species_edges.csv')
    edges['source_species_key'] = edges.source_taxon_name.map(keys)
    edges['target_species_key'] = edges.target_taxon_name.map(keys)
    fitted = {r['species_key'] for r in rows}
    edges = edges[edges.source_species_key.isin(fitted)&edges.target_species_key.isin(fitted)]
    edges.to_csv(d/'globi_links_between_modeled_species.csv',index=False)
    summary = dict(modeled_species=len(fitted), globi_relations_between_modeled_species=len(edges),
                   comparison='Current strong-call minus protocol-silent site; fixed environment-matched pairs; equal-route mean',
                   uncertainty='2000 route bootstrap; exploratory intervals without multiplicity correction',
                   interpretation='Differences in modeled environmental suitability, not observed predators or causal competition',
                   rows=rows)
    (d/'matched_summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False),encoding='utf8')
    print(json.dumps({k:v for k,v in summary.items() if k!='rows'},indent=2))


if __name__=='__main__':
    main()
