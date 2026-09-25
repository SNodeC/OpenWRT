"""Publication boundary tests: complete matrix, integrity and source generation."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('repository', Path(__file__).resolve().parents[1] / 'ci/repository.py')
repo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(repo)
read_sources = repo.sources


class PublicationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bundle = self.root / 'bundle'
        self.bundle.mkdir()
        self.sources = {name: {'refs/tags/OpenWRT': name + '-tag'} for name in repo.REPOSITORIES}
        (self.bundle / 'sources.json').write_text(json.dumps(self.sources))
        self.incoming, self.checkout = self.root / 'incoming', self.root / 'checkout'
        self.checkout.mkdir()
        self.mock = patch.object(repo, 'sources', return_value=self.sources)
        self.mock.start()
        self.addCleanup(self.mock.stop)
        for row in repo.matrix():
            directory = self.incoming / 'releases' / row['series'] / row['arch']
            directory.mkdir(parents=True)
            (directory / 'sample.apk').write_bytes(b'package')
            info = dict(row, sources=self.sources, revision='2',
                        files={'sample.apk': repo.hashlib.sha256(b'package').hexdigest()})
            (directory / 'build.json').write_text(json.dumps(info))

    def publish(self):
        repo.publish(self.incoming, self.checkout, self.bundle)

    def test_same_platforms_in_both_releases(self):
        rows = repo.matrix()
        self.assertEqual(len(rows), 36)
        platforms = [{r['target'] for r in rows if r['series'] == version} for version in ['24.10', '25.12']]
        self.assertEqual(platforms[0], platforms[1])
        self.assertTrue({'mediatek/filogic', 'ipq40xx/generic', 'ramips/mt76x8', 'ath79/generic'} <= platforms[0])

    def test_complete_publication_preserves_cached_packages(self):
        old = self.checkout / 'releases/24.10/x86_64/old.ipk'
        old.parent.mkdir(parents=True)
        old.write_bytes(b'old')
        self.publish()
        self.assertTrue(old.exists())
        self.assertEqual(len(list(self.checkout.glob('releases/*/*/build.json'))), 36)

    def test_incomplete_matrix_rejected(self):
        next(self.incoming.glob('releases/*/*/build.json')).unlink()
        with self.assertRaisesRegex(RuntimeError, 'Incomplete matrix'):
            self.publish()
        self.assertEqual(list(self.checkout.iterdir()), [])

    def test_changed_tag_rejected(self):
        repo.sources.return_value = {'changed': {}}
        with self.assertRaisesRegex(RuntimeError, 'tags changed'):
            self.publish()

    def test_mixed_generation_rejected(self):
        path = next(self.incoming.glob('releases/*/*/build.json'))
        metadata = json.loads(path.read_text())
        metadata['sources'] = {'other': 'generation'}
        path.write_text(json.dumps(metadata))
        with self.assertRaisesRegex(RuntimeError, 'Mixed source'):
            self.publish()

    def test_corrupt_package_rejected(self):
        next(self.incoming.glob('releases/*/*/sample.apk')).write_bytes(b'corrupt')
        with self.assertRaisesRegex(RuntimeError, 'checksum mismatch'):
            self.publish()

    def test_older_and_equal_publications_rejected(self):
        self.publish()
        with self.assertRaisesRegex(RuntimeError, 'older/equal'):
            self.publish()
        path = self.checkout / 'releases/24.10/aarch64_cortex-a53/build.json'
        metadata = json.loads(path.read_text())
        metadata['revision'] = '3'
        path.write_text(json.dumps(metadata))
        with self.assertRaisesRegex(RuntimeError, 'older/equal'):
            self.publish()

    def test_missing_tag_rejected(self):
        with patch.object(repo, 'run', return_value=''):
            with self.assertRaisesRegex(RuntimeError, 'tag is missing'):
                read_sources()


if __name__ == '__main__':
    unittest.main()
