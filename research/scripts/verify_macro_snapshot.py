"""Verify frozen content and replay vegetation/water results without overwriting them."""
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import tempfile

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'research/reproducibility/macro_snapshot_20261026.json'


def verify(root, manifest):
    for entry in manifest['files']:
        path = root / entry['path']
        data = path.read_bytes()
        if entry['mode'] == 'text_lf':
            data = data.replace(b'\r\n', b'\n')
        actual = hashlib.sha256(data).hexdigest()
        if actual != entry['sha256']:
            raise ValueError('Snapshot mismatch: ' + entry['path'])
    print('Verified snapshot files:', len(manifest['files']), flush=True)


def replay():
    import pandas as pd
    jobs = [
        ('naamp_remote_vegetation_network', 'naamp_remote_vegetation_20261026',
         ['primary_site_landscape_context.csv.gz'],
         ['network_rank_coefficients.csv', 'one_km_sensitivity_coefficients.csv',
          'marginal_context_correlations.csv']),
        ('naamp_prior_water_associations', 'naamp_prior_water_20261026',
         ['prior_year_site_water_context.csv.gz'],
         ['fixed_pairs_joint_ecological_context.csv.gz', 'matched_water_differences.csv',
          'matched_water_coverage.csv', 'water_stratified_joint_differences.csv']),
    ]
    with tempfile.TemporaryDirectory(prefix='frogcs-replay-') as temp:
        for module_name, folder, inputs, outputs in jobs:
            saved = ROOT / 'research/results' / folder
            dest = Path(temp) / folder
            dest.mkdir()
            for name in inputs:
                shutil.copyfile(saved / name, dest / name)
            module = importlib.import_module(module_name)
            module.OUT = dest
            print('Replaying:', module_name, flush=True)
            module.main()
            for name in outputs:
                expected = pd.read_csv(saved / name)
                actual = pd.read_csv(dest / name)
                pd.testing.assert_frame_equal(actual, expected, check_exact=False,
                                              rtol=1e-10, atol=1e-12)
                print('PASS:', folder + '/' + name, len(actual), 'rows', flush=True)
    print('PASS: seven result tables replayed; frozen files were not overwritten.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay', action='store_true', help='Recompute all saved vegetation/water bootstrap tables offline')
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    verify(ROOT, manifest)
    if args.replay:
        replay()
        verify(ROOT, manifest)
