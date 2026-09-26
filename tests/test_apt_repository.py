"""Real Debian archives and signatures at the APT publication boundary."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'ci'))
spec = importlib.util.spec_from_file_location('apt_repository', Path(sys.path[0]) / 'apt-repository.py')
apt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(apt)


class AptPublicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        home = cls.root / 'gnupg'
        home.mkdir(mode=0o700)
        apt.run('gpg', '--homedir', str(home), '--batch', '--pinentry-mode', 'loopback',
                '--passphrase', '', '--quick-generate-key', 'APT test <test@example.invalid>', 'rsa2048', 'sign', '0')
        cls.key = apt.run('gpg', '--homedir', str(home), '--batch', '--pinentry-mode', 'loopback',
                          '--passphrase', '', '--armor', '--export-secret-keys')
        cls.feed = cls.root / 'feed'
        (cls.feed / 'ci/keys').mkdir(parents=True)
        (cls.feed / 'ci/keys/snodec-apt.asc').write_text(apt.run('gpg', '--homedir', str(home), '--armor', '--export'))
        (cls.feed / 'ci/raspberrypi.json').write_text((apt.ROOT / 'ci/raspberrypi.json').read_text())

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.bundle = self.root / 'bundle'
        self.bundle.mkdir()
        (self.bundle / 'sources.json').write_text('{"tag": "generation"}')
        (self.bundle / 'context.json').write_text('{}')
        self.incoming, self.checkout = self.root / 'incoming', self.root / 'checkout'
        self.checkout.mkdir()
        for mock in [patch.object(apt, 'ROOT', self.feed), patch.object(apt, 'unchanged'),
                     patch.dict(os.environ, APT_SIGNING_KEY=self.key, PACKAGE_RELEASE='2')]:
            mock.start()
            self.addCleanup(mock.stop)
        for suite in apt.suites():
            packages = self.root / suite
            packages.mkdir()
            for project in ['snodec', 'mqttsuite']:
                (packages / f'{project}.packages').write_text(f'{project}\n{project}-component\n')
            for name in ['snodec', 'mqttsuite', 'snodec-component', 'mqttsuite-component']:
                control = self.root / 'deb/DEBIAN'
                control.mkdir(parents=True, exist_ok=True)
                (control / 'control').write_text(f'Package: {name}\nVersion: 1.0-2~{suite}\nArchitecture: arm64\n'
                                               'Maintainer: Test <test@example.invalid>\nDescription: Test\n')
                apt.run('dpkg-deb', '--build', '--root-owner-group', str(control.parent), str(packages / f'{name}.deb'))
            apt.stage(suite, packages, self.bundle, self.incoming / suite)
        import shutil
        self.merged = self.root / 'merged'
        for suite in apt.suites():
            shutil.copytree(self.incoming / suite, self.merged, dirs_exist_ok=True)

    def publish(self):
        apt.publish(self.merged, self.checkout, self.bundle)

    def test_complete_signed_publication_preserves_other_feeds(self):
        (self.checkout / 'openwrt').mkdir()
        old = self.checkout / 'openwrt/old.ipk'
        old.write_bytes(b'keep')
        self.publish()
        self.assertEqual(old.read_bytes(), b'keep')
        for suite in apt.suites():
            dist = self.checkout / 'raspberrypios/dists' / suite
            self.assertIn('Acquire-By-Hash: yes', (dist / 'Release').read_text())
            self.assertIn('Filename: pool/' + suite, (dist / 'main/binary-arm64/Packages').read_text())
            self.assertTrue((dist / 'InRelease').exists())

    def test_missing_component_rejected_before_signing(self):
        packages = self.root / 'bookworm'
        (packages / 'mqttsuite-component.deb').unlink()
        with self.assertRaisesRegex(RuntimeError, 'Incomplete Debian package set'):
            apt.stage('bookworm', packages, self.bundle, self.root / 'missing')

    def test_incomplete_matrix(self):
        (self.merged / 'raspberrypios/dists/bookworm/build.json').unlink()
        with self.assertRaisesRegex(RuntimeError, 'Incomplete'):
            self.publish()

    def test_corrupt_package(self):
        next((self.merged / 'raspberrypios/pool').rglob('*.deb')).write_bytes(b'broken')
        with self.assertRaisesRegex(RuntimeError, 'checksum'):
            self.publish()

    def test_mixed_sources(self):
        path = self.merged / 'raspberrypios/dists/bookworm/build.json'
        info = json.loads(path.read_text())
        info['sources'] = {}
        path.write_text(json.dumps(info))
        with self.assertRaisesRegex(RuntimeError, 'Mixed'):
            self.publish()

    def test_repeat_publication(self):
        self.publish()
        with self.assertRaisesRegex(RuntimeError, 'older/equal'):
            self.publish()

    def test_invalid_signature_even_with_updated_manifest(self):
        path = self.merged / 'raspberrypios/dists/bookworm/InRelease'
        path.write_text(path.read_text().replace('Origin: SNodeC', 'Origin: SomeoneElse'))
        manifest = path.parent / 'build.json'
        info = json.loads(manifest.read_text())
        info['files']['dists/bookworm/InRelease'] = apt.digest(path)
        manifest.write_text(json.dumps(info))
        with self.assertRaises(subprocess.CalledProcessError):
            self.publish()


if __name__ == '__main__':
    unittest.main()
