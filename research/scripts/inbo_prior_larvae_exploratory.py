"""Exploratory temporal associations; exact source IDs stay in memory only."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import date
import hashlib
from io import BytesIO
import json
from pathlib import Path
import zipfile
from xml.etree import ElementTree as ET
import numpy as np
from inbo_stage_taxon_g0 import SOURCES, part_rows
from part2_published_source_g0 import fetch
from gbif_inbo_event_g3_blind import ANURA_NAMES, CAUDATA_NAMES, stage

HYLA = 'Hyla arborea'

def load_source(name):
    spec = SOURCES[name]
    blob, _ = fetch(spec['url'])
    if hashlib.sha256(blob).hexdigest() != spec['sha256']:
        raise ValueError('Pinned source changed')
    events, aliases, records = {}, defaultdict(set), defaultdict(list)
    audit = Counter()
    with zipfile.ZipFile(BytesIO(blob)) as z:
        root = ET.fromstring(z.read('meta.xml'))
        core = next(n for n in root if n.tag.rsplit('}', 1)[-1] == 'core')
        for r in part_rows(z, core):
            eid = r.get('eventID') or r.get('sourceCoreID')
            site = r.get('locationID')
            try: dt = date.fromisoformat(r.get('eventDate', '')[:10])
            except ValueError: continue
            if not eid or not site: continue
            if eid in events: raise ValueError('Duplicate event')
            events[eid] = (site, dt)
            aliases[site].add(r.get('locality', '').strip().casefold())
        for ext in root:
            if ext.tag.rsplit('}', 1)[-1] != 'extension': continue
            for r in part_rows(z, ext):
                if 'scientificName' not in r: continue
                sp = r['scientificName']
                if sp not in ANURA_NAMES | CAUDATA_NAMES: continue
                ont = stage(r.get('lifeStage', ''))
                required = 'adult' if name == 'adult_chorus' else 'aquatic_immature'
                if ont != required: continue
                eid = r.get('eventID') or r.get('linkedCoreID')
                if eid not in events: continue
                status = r.get('occurrenceStatus', '').casefold()
                audit[f'{sp}|{status}'] += 1
                if status in ('present', 'absent'):
                    records[(eid, sp)].append(int(status == 'present'))
    annual = defaultdict(list)
    conflicts = 0
    for (eid, sp), values in records.items():
        if len(set(values)) != 1:
            conflicts += 1
            continue
        site, dt = events[eid]
        annual[(site, dt.year, sp)].append((dt, eid, values[0]))
    for values in annual.values(): values.sort()
    return annual, aliases, {'source_sha256': spec['sha256'], 'events': len(events),
                             'source_event_years': dict(Counter(dt.year for site, dt in events.values())),
                             'status_counts': dict(audit), 'conflicting_event_species': conflicts}

def construct(adult, larvae, safe, species, lag, first=False):
    rows = []
    # Same-day subsamples have no defensible order; pool the earliest date.
    def val(v): return max(t[2] for t in v if not first or t[0] == v[0][0])
    for (site, year, sp), surveys in sorted(adult.items()):
        if sp != HYLA or site not in safe: continue
        prior = larvae.get((site, year-lag, species))
        if not prior: continue
        history = adult.get((site, year-lag, HYLA))
        rows.append({'site': site, 'year': year, 'x': val(prior), 'y': val(surveys),
                     'history': val(history) if history else None,
                     'adult_surveys': len({t[0] for t in surveys}),
                     'larval_surveys': len({t[0] for t in prior}),
                     'adult_events': len(surveys), 'larval_events': len(prior),
                     'gap_days': (surveys[0][0]-prior[-1][0]).days})
    return rows

def contrast(rows, reps=4000):
    table = [[0, 0], [0, 0]]
    for r in rows: table[r['x']][r['y']] += 1
    n = [sum(t) for t in table]
    rates = [table[x][1]/n[x] if n[x] else None for x in (0, 1)]
    sites = sorted({r['site'] for r in rows})
    out = {'site_years': len(rows), 'sites': len(sites), 'cells_x_rows_y_columns': table,
           'chorus_rate_after_absence': rates[0], 'chorus_rate_after_presence': rates[1],
           'difference_presence_minus_absence': None, 'site_bootstrap_ci95': None,
           'bootstrap_valid': 0, 'bootstrap_replicates': reps,
           'years': sorted({r['year'] for r in rows}),
           'within_site_exposure_switchers': sum(len({r['x'] for r in rows if r['site']==s}) > 1 for s in sites)}
    if rows:
        out['survey_counts_by_exposure'] = {
            str(x): {k: dict(Counter(r[k] for r in rows if r['x']==x))
                     for k in ('adult_surveys', 'larval_surveys')}
            for x in (0, 1)}
        out['gap_days_range'] = [min(r['gap_days'] for r in rows), max(r['gap_days'] for r in rows)]
    if not all(n): return out
    out['difference_presence_minus_absence'] = rates[1]-rates[0]
    # Cluster resampling retains all years from each sampled site.
    cells = np.zeros((len(sites), 2, 2))
    index = {s:i for i,s in enumerate(sites)}
    for r in rows: cells[index[r['site']],r['x'],r['y']] += 1
    rng = np.random.default_rng(20261026)
    total = cells[rng.integers(0, len(sites), size=(reps, len(sites)))].sum(axis=1)
    den = total.sum(axis=2)
    ok = (den > 0).all(axis=1)
    dif = total[ok,1,1]/den[ok,1]-total[ok,0,1]/den[ok,0]
    out['bootstrap_valid'] = int(ok.sum())
    if len(dif): out['site_bootstrap_ci95'] = np.quantile(dif, [.025,.975]).tolist()
    out['bootstrap_degenerate'] = bool(len(dif) and np.ptp(dif) == 0)
    return out

def within_site(rows):
    """Post-result sensitivity: equal weight per site with both exposure states."""
    differences = []
    for site in sorted({r['site'] for r in rows}):
        groups = [[r['y'] for r in rows if r['site']==site and r['x']==x] for x in (0,1)]
        if all(groups): differences.append(float(np.mean(groups[1])-np.mean(groups[0])))
    out = {'post_result_sensitivity': True, 'switcher_sites': len(differences),
           'mean_within_site_difference': None, 'ci95': None,
           'warning': 'Different calendar years; site control is not time-varying confounder control.'}
    if differences:
        values=np.array(differences)
        draws=np.random.default_rng(20261026).choice(values,size=(4000,len(values))).mean(axis=1)
        out.update(mean_within_site_difference=float(values.mean()),
                   ci95=np.quantile(draws,[.025,.975]).tolist(),
                   bootstrap_degenerate=bool(np.ptp(draws)==0))
    return out

def run():
    adult, aa, aq = load_source('adult_chorus')
    larvae, la, lq = load_source('larval_census')
    shared = set(aa) & set(la)
    for site in shared:
        a, b = aa[site]-{''}, la[site]-{''}
        if len(a)>1 or len(b)>1 or (a and b and not a&b):
            raise ValueError('Conflicting exact-site locality')
    results = []
    species = sorted({sp for site, year, sp in larvae})
    for sp in species:
        for lag in (1, 2, 3):
            rows = construct(adult, larvae, shared, sp, lag)
            item = {'species': sp, 'lag_calendar_years': lag, 'annual_any': contrast(rows),
                    'within_site_post_result': within_site(rows),
                    'first_survey': contrast(construct(adult, larvae, shared, sp, lag, True)),
                    'two_or_more_adult_surveys': contrast([r for r in rows if r['adult_surveys']>=2]),
                    'history_strata': {str(h): contrast([r for r in rows if r['history']==h]) for h in (0,1)},
                    'history_missing_rows': sum(r['history'] is None for r in rows)}
            results.append(item)
    return {'analysis': 'Exploratory prior larvae to later chorus; not causal or recruitment',
            'sources': {'adult': aq, 'larvae': lq}, 'shared_exact_sites': len(shared),
            'source_identifiers_exported': False, 'results': results}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    output = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for r in output['results']:
        if r['lag_calendar_years']==1:
            print(r['species'], json.dumps(r['annual_any'], ensure_ascii=False))
