"""Real RPM signatures and repository metadata at the publication boundary."""
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'ci'))
rpm = importlib.import_module('rpm-repository')


class RpmPublicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        home = cls.root / 'gpg'
        home.mkdir(mode=0o700)
        rpm.run('gpg', '--homedir', str(home), '--batch', '--pinentry-mode', 'loopback', '--passphrase', '',
                '--quick-generate-key', 'RPM test <test@example.invalid>', 'rsa2048', 'sign', '0')
        cls.key = rpm.run('gpg', '--homedir', str(home), '--armor', '--export-secret-keys')
        (cls.root / 'ci/keys').mkdir(parents=True)
        (cls.root / 'ci/keys/snodec-apt.asc').write_text(rpm.run('gpg', '--homedir', str(home), '--armor', '--export'))
        cls.packages = cls.root / 'packages'
        cls.packages.mkdir()
        for name in ['snodec', 'mqttsuite']:
            spec = cls.root / f'{name}.spec'
            spec.write_text(f'Name: {name}\nVersion: 1\nRelease: 2\nSummary: Test\nLicense: MIT\n%description\nTest\n%files\n')
            rpm.run('rpmbuild', '-bb', '--define', f'_topdir {cls.root}/build',
                    '--define', f'_rpmdir {cls.packages}', spec.as_posix())
            (cls.packages / f'{name}.packages').write_text(name + '\n')
        for path in list(cls.packages.rglob('*.rpm')):
            path.rename(cls.packages / path.name)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.work = Path(temp.name)
        self.bundle = self.work / 'bundle'
        self.bundle.mkdir()
        (self.bundle / 'sources.json').write_text('{"tag": "generation"}')
        (self.bundle / 'context.json').write_text('{}')
        self.row = dict(distribution='rocky', suite='9', arch=rpm.run('rpm', '--eval', '%{_arch}'))
        for mock in [patch.object(rpm, 'ROOT', self.root), patch.object(rpm, 'unchanged'),
                     patch.dict(os.environ, APT_SIGNING_KEY=self.key, PACKAGE_RELEASE='2')]:
            mock.start()
            self.addCleanup(mock.stop)
        self.incoming, self.checkout = self.work / 'incoming', self.work / 'checkout'
        rpm.stage(self.row, self.packages, self.bundle, self.incoming)

    def publish(self):
        rpm.publish([self.row], self.incoming, self.checkout, self.bundle)

    def test_signed_publication_and_stale_revision_rejection(self):
        self.publish()
        manifest = next(self.checkout.glob('rocky/*/*/build.json'))
        self.assertEqual(json.loads(manifest.read_text())['packages'], ['mqttsuite', 'snodec'])
        with self.assertRaisesRegex(RuntimeError, 'older/equal'):
            self.publish()

    def test_corrupt_package_rejected(self):
        next(self.incoming.rglob('*.rpm')).write_bytes(b'broken')
        with self.assertRaisesRegex(RuntimeError, 'checksum'):
            self.publish()
        self.assertFalse(self.checkout.exists())

    def test_unsigned_package_rejected_even_with_updated_manifest(self):
        package = next(self.incoming.rglob('*.rpm'))
        rpm.run('rpm', '--delsign', str(package))
        manifest = package.parent.parent / 'build.json'
        info = json.loads(manifest.read_text())
        info['files']['Packages/' + package.name] = rpm.digest(package)
        manifest.write_text(json.dumps(info))
        with self.assertRaisesRegex(RuntimeError, 'Unsigned RPM'):
            self.publish()
        self.assertFalse(self.checkout.exists())


if __name__ == '__main__':
    unittest.main()
