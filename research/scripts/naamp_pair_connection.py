"""Small live taxon/interaction bridge; never an NAAMP site-time or causal join."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

PAIRS = [
    ('Lithobates clamitans', 'Lithobates catesbeianus'),
    ('Hyla chrysoscelis', 'Hyla versicolor'),
]
ALIASES = {
    'Lithobates clamitans': ['Lithobates clamitans', 'Rana clamitans'],
    'Lithobates catesbeianus': ['Lithobates catesbeianus', 'Rana catesbeiana'],
    'Hyla chrysoscelis': ['Hyla chrysoscelis', 'Dryophytes chrysoscelis'],
    'Hyla versicolor': ['Hyla versicolor', 'Dryophytes versicolor'],
}
FIELDS = ['source_taxon_name', 'target_taxon_name', 'interaction_type',
          'source_specimen_life_stage', 'target_specimen_life_stage', 'study_citation']


def accepted_key(d):
    if d.get('matchType') != 'EXACT' or d.get('rank') != 'SPECIES':
        raise ValueError('Taxonomic bridge requires exact species-level match')
    if d.get('status') not in ('ACCEPTED', 'SYNONYM'):
        raise ValueError('Unaccepted/unsupported taxonomic status')
    key = d.get('acceptedUsageKey') if d.get('status') == 'SYNONYM' else d.get('usageKey')
    if not isinstance(key, int):
        raise ValueError('No accepted species key')
    return key


def fetch(url, out, label):
    receipt = {'url': url, 'queried_at_utc': datetime.now(timezone.utc).isoformat()}
    try:
        req = Request(url, headers={'User-Agent': 'FrogcsGlobalMacro/0.1 (source-cited noncommercial scientific audit)',
                                    'Accept': 'application/json'})
        with urlopen(req, timeout=35) as r:
            raw = r.read()
        data = json.loads(raw)
        receipt.update(status='SUCCESS', response_sha256=hashlib.sha256(raw).hexdigest(), response=data)
    except Exception as exc:
        receipt.update(status='REQUEST_FAILED', error=type(exc).__name__ + ': ' + str(exc))
    (out / (label + '.json')).write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    time.sleep(0.5)
    return receipt


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args(); a.out.mkdir(parents=True, exist_ok=True)
    taxonomy = {}; errors = []
    for focal, names in ALIASES.items():
        entries = []
        for name in names:
            url = 'https://api.gbif.org/v1/species/match?' + urlencode(
                {'name': name, 'verbose': 'true', 'kingdom': 'Animalia', 'class': 'Amphibia'})
            rec = fetch(url, a.out, 'gbif_' + name.replace(' ', '_'))
            entry = {'query_name': name, 'status': rec['status']}
            if rec['status'] == 'SUCCESS':
                d = rec['response']
                entry.update({k: d.get(k) for k in ['usageKey','acceptedUsageKey','canonicalName',
                                                   'rank','status','confidence','matchType','alternatives']})
                try:
                    entry['accepted_key'] = accepted_key(d)
                except ValueError as exc:
                    entry['bridge_error'] = str(exc); errors.append(name + ': ' + str(exc))
            else:
                errors.append(name + ': ' + rec['error'])
            entries.append(entry)
        keys = {e.get('accepted_key') for e in entries}
        valid = len(keys) == 1 and None not in keys
        taxonomy[focal] = {'aliases': entries, 'verified_alias_identity': valid}
        if not valid:
            errors.append(focal + ': alias identity not verified; GloBI pair query ineligible')
    queries = []
    for pair_id, (left, right) in enumerate(PAIRS, 1):
        if not all(taxonomy[t]['verified_alias_identity'] for t in [left, right]):
            continue
        for qid, (src, tar) in enumerate(itertools.chain(
                itertools.product(ALIASES[left], ALIASES[right]),
                itertools.product(ALIASES[right], ALIASES[left])), 1):
            params = dict(sourceTaxon=src, targetTaxon=tar, includeObservations='true',
                          fields=','.join(FIELDS), limit=1000, offset=0)
            url = 'https://api.globalbioticinteractions.org/interaction?' + urlencode(params)
            label = f'globi_pair{pair_id}_query{qid}'
            rec = fetch(url, a.out, label)
            info = dict(pair_id=pair_id, source_query=src, target_query=tar, receipt=label+'.json',
                        status=rec['status'], empty_response_is_no_interaction_evidence=False)
            if rec['status'] == 'SUCCESS':
                d = rec['response']
                if d.get('columns') != FIELDS or not isinstance(d.get('data'), list):
                    info['status'] = 'SCHEMA_FAILED'; errors.append(label + ': schema mismatch')
                else:
                    data = d['data']
                    if any(not isinstance(r, list) or len(r) != len(FIELDS) for r in data):
                        info['status'] = 'SCHEMA_FAILED'; errors.append(label + ': row mismatch')
                    else:
                        rows = [dict(zip(FIELDS, r)) for r in data]
                        exact = [r for r in rows if r['source_taxon_name'] in ALIASES[left]+ALIASES[right]
                                 and r['target_taxon_name'] in ALIASES[left]+ALIASES[right]
                                 and ((r['source_taxon_name'] in ALIASES[left]) != (r['target_taxon_name'] in ALIASES[left]))]
                        info.update(returned_rows=len(rows), target_pair_rows=len(exact),
                                    other_or_unverified_name_rows=len(rows)-len(exact),
                                    first_page_limit_reached=len(rows)>=1000,
                                    interaction_types=dict(Counter(r['interaction_type'] for r in exact)),
                                    citation_count=len({r['study_citation'] for r in exact if r['study_citation']}))
            else:
                errors.append(label + ': ' + rec['error'])
            queries.append(info)
            print(label, info['status'], info.get('returned_rows'), flush=True)
    control_params = dict(sourceTaxon='Lithobates catesbeianus', interactionType='eats',
                          includeObservations='true', fields=','.join(FIELDS), limit=5, offset=0)
    control = fetch('https://api.globalbioticinteractions.org/interaction?' + urlencode(control_params),
                    a.out, 'globi_positive_source_control')
    control_rows = len(control.get('response', {}).get('data', []))
    if control['status'] != 'SUCCESS' or not control_rows:
        errors.append('Positive source control failed or returned no rows; empty pair queries need caution')
    result = dict(date_utc=datetime.now(timezone.utc).isoformat(),
                  scope='Four prespecified NAAMP species labels and verified aliases; live exploratory bridge',
                  taxonomy=taxonomy, globi_queries=queries, errors=errors,
                  globi_source_control_rows=control_rows,
                  status='COMPLETE_NARROW_LIVE_QUERY' if not errors and len(queries)==16 else 'INCOMPLETE_EXPLICIT_FAILURES',
                  live_not_version_pinned=True, no_naamp_site_date_join=True,
                  no_competition_inference=True, missing_globi_edge_is_not_absence=True,
                  alias_query_rows_not_independent=True, raw_receipts_saved=True,
                  globi_guidance='https://www.globalbioticinteractions.org/data.html')
    (a.out/'observed_results.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf8')
    print(result['status'], flush=True)
    if errors:
        raise SystemExit(4)


if __name__ == '__main__':
    main()
