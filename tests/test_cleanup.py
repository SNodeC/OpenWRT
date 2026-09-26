"""Retention at the filesystem boundary for opkg, APK and APT publications."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'ci'))
from cleanup import cleanup
from repository import digest


class RetentionTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.current, self.old = [], []
        for series, suffix, indexes in [('24.10', '.ipk', ['Packages', 'Packages.gz', 'Packages.sig']),
                                        ('25.12', '.apk', ['packages.adb'])]:
            base = self.root / 'openwrt' / series / 'arch'
            names = indexes + ['current' + suffix]
            self.manifest(base / 'build.json', base, names)
            self.old.append(self.write(base / ('old' + suffix)))
        base = self.root / 'raspberrypios'
        for suite in ['bookworm', 'trixie']:
            names = [f'pool/{suite}/current.deb'] + [f'dists/{suite}/{name}' for name in
                     ['Release', 'InRelease', 'Release.gpg', 'main/binary-arm64/Packages',
                      'main/binary-arm64/Packages.gz', 'main/binary-arm64/by-hash/SHA256/current']]
            self.manifest(base / 'dists' / suite / 'build.json', base, names)
            self.old.extend([self.write(base / 'pool' / suite / 'old.deb'),
                             self.write(base / 'dists' / suite / 'main/binary-arm64/by-hash/SHA256/old')])
        self.key = self.write(self.root / 'keys/public.key')
        self.readme = self.write(self.root / 'README.md')

    def write(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(path.name)
        return path

    def manifest(self, path, base, names):
        paths = [self.write(base / name) for name in names]
        self.current.extend(paths)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({'files': {name: digest(base / name) for name in names}}))

    def test_grace_period_and_both_platforms(self):
        self.assertEqual(cleanup(self.root, self.now), [])
        state = (self.root / 'retention.json').read_bytes()
        self.assertEqual(cleanup(self.root, self.now + timedelta(days=29)), [])
        self.assertEqual((self.root / 'retention.json').read_bytes(), state)
        self.assertEqual(set(cleanup(self.root, self.now + timedelta(days=30))), set(self.old))
        self.assertTrue(all(path.exists() for path in self.current + [self.key, self.readme]))
        self.assertEqual(json.loads((self.root / 'retention.json').read_text()), {})

    def test_referenced_again_resets_clock(self):
        cleanup(self.root, self.now)
        path = self.old[0]
        manifest = path.parent / 'build.json'
        info = json.loads(manifest.read_text())
        info['files'][path.name] = digest(path)
        manifest.write_text(json.dumps(info))
        cleanup(self.root, self.now + timedelta(days=31))
        self.assertTrue(path.exists())
        del info['files'][path.name]
        manifest.write_text(json.dumps(info))
        cleanup(self.root, self.now + timedelta(days=32))
        self.assertTrue(path.exists())
        cleanup(self.root, self.now + timedelta(days=62))
        self.assertFalse(path.exists())

    def test_changed_bytes_restart_grace_period(self):
        cleanup(self.root, self.now)
        self.old[0].write_text('replacement')
        cleanup(self.root, self.now + timedelta(days=30))
        self.assertTrue(self.old[0].exists())

    def test_bad_inventory_never_deletes(self):
        for fault in ['missing', 'corrupt', 'incomplete', 'unsafe']:
            with self.subTest(fault=fault):
                cleanup(self.root, self.now)
                manifest = self.root / 'raspberrypios/dists/trixie/build.json'
                original = manifest.read_text()
                info = json.loads(original)
                if fault == 'missing':
                    manifest.unlink()
                else:
                    if fault == 'corrupt':
                        info['files']['pool/trixie/current.deb'] = 'invalid'
                    elif fault == 'incomplete':
                        info['files'].pop('dists/trixie/InRelease')
                    else:
                        info['files']['../outside'] = 'invalid'
                    manifest.write_text(json.dumps(info))
                with self.assertRaises((RuntimeError, FileNotFoundError)):
                    cleanup(self.root, self.now + timedelta(days=90))
                self.assertTrue(all(path.exists() for path in self.old))
                manifest.write_text(original)

    def test_symlink_never_deleted(self):
        cleanup(self.root, self.now)
        self.old[0].unlink()
        self.old[0].symlink_to(self.key)
        with self.assertRaises(RuntimeError):
            cleanup(self.root, self.now + timedelta(days=30))
        self.assertTrue(self.key.exists())


class SnapshotTest(unittest.TestCase):
    def test_single_commit_noop_and_concurrent_update_rejection(self):
        def run(*args):
            return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo, remote, fresh = root / 'repo', root / 'remote', root / 'fresh'
            run('git', 'init', '--bare', str(remote))
            run('git', 'init', '-b', 'packages', str(repo))
            run('git', '-C', str(repo), 'config', 'user.name', 'Test')
            run('git', '-C', str(repo), 'config', 'user.email', 'test@example.invalid')
            run('git', '-C', str(repo), 'config', 'commit.gpgsign', 'false')
            (repo / 'package').write_text('original')
            run('git', '-C', str(repo), 'add', '.')
            run('git', '-C', str(repo), 'commit', '-m', 'original')
            original = run('git', '-C', str(repo), 'rev-parse', 'HEAD')
            run('git', '-C', str(repo), 'remote', 'add', 'origin', str(remote))
            run('git', '-C', str(repo), 'push', 'origin', 'packages')
            (repo / 'package').write_text('updated')
            script = Path(__file__).resolve().parents[1] / 'ci/push-packages.sh'
            run('bash', str(script), str(repo), original, 'maintenance')
            current = run('git', '--git-dir', str(remote), 'rev-parse', 'packages')
            self.assertEqual(run('git', '--git-dir', str(remote), 'rev-list', '--count', 'packages'), '1')
            run('git', 'clone', '-b', 'packages', str(remote), str(fresh))
            run('bash', str(script), str(fresh), current, 'unchanged maintenance')
            self.assertEqual(run('git', '--git-dir', str(remote), 'rev-parse', 'packages'), current)
            (repo / 'package').write_text('stale writer')
            with self.assertRaises(subprocess.CalledProcessError):
                run('bash', str(script), str(repo), original, 'stale maintenance')
            self.assertEqual(run('git', '--git-dir', str(remote), 'rev-parse', 'packages'), current)


if __name__ == '__main__':
    unittest.main()
