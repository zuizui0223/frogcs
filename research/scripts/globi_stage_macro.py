#!/usr/bin/env python3
"""Stage-aware macro food-web QA for versioned GloBI observations.

Usage: python globi_stage_macro.py interactions.tsv.gz --output-dir outputs
       python globi_stage_macro.py --self-test

Descriptive evidence coverage and potential stage-specific reciprocal links,
NOT evidence for a population-level predation-rate reversal.
"""
import argparse
import csv
import gzip
import hashlib
import itertools
import json
import re
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

ALIASES = {
    'predator': ('source_taxon_name', 'sourceTaxonName'),
    'prey': ('target_taxon_name', 'targetTaxonName'),
    'predator_stage': ('source_specimen_life_stage', 'sourceLifeStageName', 'sourceSpecimenLifeStage'),
    'prey_stage': ('target_specimen_life_stage', 'targetLifeStageName', 'targetSpecimenLifeStage'),
    'interaction': ('interaction_type', 'interactionTypeName'),
    'citation': ('study_citation', 'studyCitation', 'study_source_citation', 'studySourceCitation'),
    'predator_path': ('source_taxon_path', 'sourceTaxonPath', 'sourceTaxonPathNames'),
}
FOCAL = ('Anura', 'Caudata', 'Odonata', 'Dytiscidae', 'Nepomorpha',
         'Trichoptera', 'Diptera', 'Actinopterygii', 'Decapoda', 'Gastropoda')
FOOD = {'eats', 'preysOn'}
SPECIES = re.compile(r'^[A-Z][a-z]+ [a-z][a-z-]+$')


def stage(value):
    s = (value or '').strip().lower()
    if not s or s in {'-999', 'na', 'n/a', 'unknown', 'unreported',
                      'none', 'null', 'unspecified'}:
        return None
    if re.search(r'egg|embryo|ovum', s):
        return 'egg'
    if re.search(r'tadpol|larv|nymph|instar|fry', s):
        return 'larva'
    if re.search(r'pupa|pupal', s):
        return 'pupa'
    if re.search(r'metamorph', s):
        return 'metamorph'
    if re.search(r'adult|imago|post-juvenile', s):
        return 'adult'
    if re.search(r'juvenil|immature|young|subadult|hatchling', s):
        return 'juvenile'
    return None


def get(row, key):
    for alias in ALIASES[key]:
        if alias in row and row[alias] not in (None, ''):
            return str(row[alias])
    return ''


def focal_group(path, taxon):
    names = {i.strip() for i in (path or '').split('|')}
    for group in FOCAL:
        if group in names or taxon == group:
            return group
    return 'other_or_unresolved'


def write_csv(path, fields, data):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def analyze(input_path, output_dir):
    src = Path(input_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if src.suffix == '.gz' else open
    delimiter = '\t' if '.tsv' in src.name or '.txt' in src.name else ','
    n_read, n_food, n_species = 0, 0, 0
    coverage = defaultdict(Counter)
    stage_diets = defaultdict(lambda: {'prey': set(), 'studies': set()})
    pair_directions = defaultdict(lambda: defaultdict(
        lambda: {'stages': set(), 'studies': set(), 'rows': 0}))
    with opener(src, 'rt', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        names = set(reader.fieldnames or [])
        for required in ('predator', 'prey', 'interaction'):
            if not any(alias in names for alias in ALIASES[required]):
                raise ValueError(f'Missing required input column: {required}')
        for row in reader:
            n_read += 1
            if get(row, 'interaction') not in FOOD:
                continue
            n_food += 1
            a, b = get(row, 'predator').strip(), get(row, 'prey').strip()
            sa, sb = stage(get(row, 'predator_stage')), stage(get(row, 'prey_stage'))
            cite = get(row, 'citation').strip()
            grp = focal_group(get(row, 'predator_path'), a)
            co = coverage[grp]
            co['food_rows'] += 1
            if sa or sb: co['stage_either'] += 1
            if sa and sb: co['stage_both'] += 1
            if cite: co['cited_rows'] += 1
            if not SPECIES.fullmatch(a) or not SPECIES.fullmatch(b) or a == b:
                continue
            n_species += 1
            if sa:
                d = stage_diets[(a, sa)]
                d['prey'].add(b)
                if cite: d['studies'].add(cite)
            key = tuple(sorted((a, b)))
            d = pair_directions[key][(a, b)]
            d['rows'] += 1
            if sa and sb:
                d['stages'].add((sa, sb))
                if cite: d['studies'].add(cite)
    coverage_rows = [dict(group=g, **{k: c.get(k, 0) for k in
                     ('food_rows', 'stage_either', 'stage_both', 'cited_rows')})
                     for g, c in sorted(coverage.items())]
    write_csv(out/'stage_coverage.csv',
              ['group', 'food_rows', 'stage_either', 'stage_both', 'cited_rows'],
              coverage_rows)
    candidates = []
    for (a, b), dirs in sorted(pair_directions.items()):
        ab, ba = dirs.get((a, b)), dirs.get((b, a))
        if not ab or not ba:
            continue
        candidates.append(dict(
            taxon_a=a, taxon_b=b,
            a_eats_b_rows=ab['rows'], b_eats_a_rows=ba['rows'],
            a_eats_b_stage_pairs=len(ab['stages']),
            b_eats_a_stage_pairs=len(ba['stages']),
            a_eats_b_source_count=len(ab['studies']),
            b_eats_a_source_count=len(ba['studies']),
            shared_source_count=len(ab['studies'] & ba['studies']),
            stage_complete_both_directions=bool(ab['stages'] and ba['stages']),
            interpretation='database_candidate_not_confirmed_reversal'))
    write_csv(out/'reciprocal_candidates.csv', [
        'taxon_a', 'taxon_b', 'a_eats_b_rows', 'b_eats_a_rows',
        'a_eats_b_stage_pairs', 'b_eats_a_stage_pairs',
        'a_eats_b_source_count', 'b_eats_a_source_count', 'shared_source_count',
        'stage_complete_both_directions', 'interpretation'], candidates)
    diet_rows = []
    by_taxon = defaultdict(dict)
    for (taxon, s), value in stage_diets.items():
        by_taxon[taxon][s] = value
    for taxon, d in sorted(by_taxon.items()):
        for sa, sb in itertools.combinations(sorted(d), 2):
            va, vb = d[sa], d[sb]
            union = len(va['prey'] | vb['prey'])
            diet_rows.append(dict(
                taxon=taxon, stage_a=sa, stage_b=sb,
                prey_a=len(va['prey']), prey_b=len(vb['prey']),
                jaccard=round(len(va['prey'] & vb['prey']) / union, 6) if union else '',
                studies_a=len(va['studies']), studies_b=len(vb['studies']),
                warning='descriptive_not_effort_standardized'))
    write_csv(out/'stage_prey_overlap.csv', [
        'taxon', 'stage_a', 'stage_b', 'prey_a', 'prey_b',
        'jaccard', 'studies_a', 'studies_b', 'warning'], diet_rows)
    digest = hashlib.sha256()
    with open(src, 'rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''):
            digest.update(chunk)
    receipt = dict(
        input_file=str(src), sha256=digest.hexdigest(), raw_rows=n_read,
        direct_feeding_rows=n_food, species_binomial_rows=n_species,
        reciprocal_pair_candidates=len(candidates),
        reciprocal_stage_complete_candidates=sum(
            item['stage_complete_both_directions'] for item in candidates),
        predator_two_stage_prey_overlap_rows=len(diet_rows),
        caveats=[
            'Stage association does not establish predation flux or directional dominance.',
            'Mixed evidence: sources may report observation, literature or inference.',
            'Live GloBI API head samples are not representative; use pinned stable release.',
            'No silent imputation for life stage; source-study effort is not standardized.',
            'A study citation alone is not an independent observed event.'])
    (out/'audit.json').write_text(
        json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    return receipt


def self_test():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)/'fixture.tsv'
        fields = ['source_taxon_name', 'target_taxon_name',
                  'source_specimen_life_stage', 'target_specimen_life_stage',
                  'interaction_type', 'study_citation',
                  'source_taxon_path', 'target_taxon_path']
        records = [
            ('Anax junius', 'Anaxyrus boreas', 'larva', 'tadpole',
             'eats', 'study_A', 'Odonata | Anax', 'Anura | Anaxyrus'),
            ('Anaxyrus boreas', 'Anax junius', 'adult', 'adult',
             'preysOn', 'study_B', 'Anura | Anaxyrus', 'Odonata | Anax'),
            ('Anaxyrus boreas', 'Anax junius', 'adult', 'larva',
             'eats', 'study_C', 'Anura | Anaxyrus', 'Odonata | Anax'),
            ('Anax junius', 'Pseudacris regilla', '-999', 'larva',
             'eats', 'study_A', 'Odonata | Anax', 'Anura | Pseudacris'),
            ('Anax junius', 'Pseudacris regilla', 'larva', 'larva',
             'parasiteOf', 'study_C', 'Odonata | Anax', 'Anura | Pseudacris'),
            ('Anax junius', 'Culex pipiens', 'adult', 'larva',
             'eats', 'study_D', 'Odonata | Anax', 'Diptera | Culex'),
        ]
        with p.open('w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(fields)
            writer.writerows(records)
        result = analyze(p, Path(td)/'out')
        assert result['direct_feeding_rows'] == 5, result
        assert result['reciprocal_pair_candidates'] == 1, result
        assert result['reciprocal_stage_complete_candidates'] == 1, result
        assert result['predator_two_stage_prey_overlap_rows'] == 1, result
        print('SELF TEST PASS')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', nargs='?')
    parser.add_argument('--output-dir', default='stage_macro_results')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif not args.input:
        parser.error('Provide pinned GloBI .csv/.tsv/.gz or --self-test')
    else:
        print(json.dumps(analyze(args.input, args.output_dir), indent=2))
