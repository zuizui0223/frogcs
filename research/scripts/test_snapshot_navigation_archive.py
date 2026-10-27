"""Moving navigation must not weaken frozen-content verification."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from verify_macro_snapshot import verify

class SnapshotNavigationArchive(unittest.TestCase):
    def test_archived_original_is_checked_not_current_navigation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'research/reproducibility').mkdir(parents=True)
            (root / 'legacy').mkdir()
            (root / 'README.md').write_bytes(b'current navigation')
            original = root / 'legacy/README.md'
            original.write_bytes(b'frozen\r\n')
            manifest = {'files': [{'path': 'README.md', 'mode': 'text_lf',
                                  'sha256': hashlib.sha256(b'frozen\n').hexdigest()}]}
            mapping = root / 'research/reproducibility/snapshot_path_overrides_20261027.json'
            mapping.write_text(json.dumps({'README.md': 'legacy/README.md'}))
            verify(root, manifest)
            original.write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError, 'Snapshot mismatch'):
                verify(root, manifest)
            original.unlink()
            with self.assertRaises(FileNotFoundError):
                verify(root, manifest)

    def test_result_data_cannot_be_redirected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'research/reproducibility').mkdir(parents=True)
            mapping = root / 'research/reproducibility/snapshot_path_overrides_20261027.json'
            mapping.write_text(json.dumps({'research/results/data.csv': 'elsewhere.csv'}))
            with self.assertRaisesRegex(ValueError, 'Only archived navigation'):
                verify(root, {'files': []})

    def test_original_snapshot_without_overrides_still_works(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'README.md').write_bytes(b'frozen\n')
            verify(root, {'files': [{'path': 'README.md', 'mode': 'text_lf',
                                    'sha256': hashlib.sha256(b'frozen\n').hexdigest()}]})

if __name__ == '__main__':
    unittest.main()
