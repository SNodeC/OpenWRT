#!/usr/bin/env python3
"""Exercise the installer boundary with isolated /etc and mocked system commands."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallerTest(unittest.TestCase):
    def run_installer(self, distribution, suite, arch, *args, missing=False):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            etc = root / 'etc'
            etc.mkdir()
            if distribution == 'openwrt':
                (etc / 'openwrt_release').write_text(
                    f'DISTRIB_RELEASE={suite}.5\nDISTRIB_ARCH={arch}\n')
                (etc / 'opkg').mkdir()
                (etc / 'opkg/customfeeds.conf').write_text('src/gz official https://example.test\n')
            else:
                ident = 'debian' if distribution == 'raspberrypios' else distribution
                (etc / 'os-release').write_text(
                    f'ID={ident}\nVERSION_ID={suite}\nVERSION_CODENAME={suite}\n')
                if distribution == 'raspberrypios':
                    (etc / 'rpi-issue').touch()
            binary = root / 'bin'
            binary.mkdir()
            mock = binary / 'mock'
            mock.write_text('''#!/usr/bin/env python3
import json, os, pathlib, sys
name = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
with open(os.environ['COMMAND_LOG'], 'a') as out:
    out.write(json.dumps([name, *args]) + '\\n')
if name == 'id': print('0')
elif name == 'dpkg' or (name == 'rpm' and '--eval' in args): print(os.environ['TEST_ARCH'])
elif name in ('curl', 'wget'):
    if os.environ['MISSING_FEED'] == '1': sys.exit(22)
    flag = '-o' if name == 'curl' else '-O'
    pathlib.Path(args[args.index(flag) + 1]).write_text('downloaded fixture')
''')
            mock.chmod(0o755)
            for name in ['id', 'dpkg', 'rpm', 'curl', 'wget', 'apt-get', 'dnf', 'opkg', 'opkg-key', 'apk']:
                (binary / name).symlink_to(mock)
            # Redirect fixed system paths in the test copy, without production test hooks.
            script = root / 'installer.sh'
            script.write_text((ROOT / 'ci/install-feed.sh').read_text().replace('/etc/', f'{etc}/'))
            log = root / 'commands.jsonl'
            env = dict(os.environ, PATH=f'{binary}:{os.environ["PATH"]}',
                       COMMAND_LOG=str(log), TEST_ARCH=arch, MISSING_FEED=str(int(missing)))
            result = subprocess.run(['sh', str(script), *args], env=env,
                                    text=True, capture_output=True)
            commands = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
            files = {str(p.relative_to(etc)): p.read_text() for p in etc.rglob('*') if p.is_file()}
            return result, commands, files

    def test_entire_matrix_prepare_and_full(self):
        targets = []
        for row in json.loads((ROOT / 'ci/linux.json').read_text()):
            targets.extend((row['distribution'], row['suite'], arch) for arch in row['architectures'])
        targets.extend(('raspberrypios', suite, 'arm64')
                       for suite in json.loads((ROOT / 'ci/raspberrypi.json').read_text()))
        platforms = json.loads((ROOT / 'ci/platforms.json').read_text())
        for release in platforms['releases']:
            series = '.'.join(release.split('.')[:2])
            for arch in platforms['targets']:
                if series == '24.10' and arch == 'riscv64_generic':
                    arch = 'riscv64_riscv64'
                targets.append(('openwrt', series, arch))
        self.assertEqual(len(targets), 76)
        for distribution, suite, arch in targets:
            for prepare in (True, False):
                with self.subTest(distribution=distribution, suite=suite, arch=arch, prepare=prepare):
                    result, commands, files = self.run_installer(
                        distribution, suite, arch, *(['--prepare'] if prepare else []))
                    self.assertEqual(result.returncode, 0, result.stderr)
                    installs = [c for c in commands if c[0] in ('apt-get', 'dnf', 'opkg', 'apk') and c[1] in ('install', 'add')]
                    self.assertEqual(len(installs), 0 if prepare else 1)
                    if distribution in ('debian', 'ubuntu', 'raspberrypios'):
                        config = files['apt/sources.list.d/snodec.list']
                        self.assertIn(f'/packages/{distribution} {suite} main', config)
                        self.assertIn(f'arch={arch} signed-by=', config)
                    elif distribution in ('rocky', 'fedora'):
                        config = files['yum.repos.d/snodec.repo']
                        self.assertIn(f'/packages/{distribution}/{suite}/{arch}/', config)
                        self.assertIn('gpgcheck=1\nrepo_gpgcheck=1', config)
                    elif suite == '24.10':
                        config = files['opkg/customfeeds.conf']
                        self.assertIn('src/gz official https://example.test', config)
                        self.assertIn(f'/openwrt/{suite}/{arch}', config)
                    else:
                        self.assertIn(f'/openwrt/{suite}/{arch}/packages.adb', files['apk/repositories.d/snodec.list'])
                    downloads = [c for c in commands if c[0] in ('curl', 'wget')]
                    self.assertEqual(len(downloads), 2)
                    self.assertIn(arch, ' '.join(downloads[0]))
                    if installs:
                        self.assertEqual(installs[0][-4:] if distribution == 'openwrt' else installs[0][-2:],
                                         ['mqttsuite-full', 'snode.c-full', 'snode.c-apps', 'snode.c-control']
                                         if distribution == 'openwrt' else ['snodec', 'mqttsuite'])

    def test_missing_feed_leaves_configuration_untouched(self):
        for dist, suite in [('debian', 'trixie'), ('raspberrypios', 'bookworm'), ('fedora', '44'), ('openwrt', '24.10')]:
            with self.subTest(distribution=dist):
                result, commands, files = self.run_installer(dist, suite, 'arm64', missing=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(any(c[0] in ('apt-get', 'dnf', 'opkg', 'apk', 'opkg-key') for c in commands))
                self.assertFalse(any('snodec' in name for name in files))

    def test_explicit_sid_and_unsupported_system(self):
        result, _, files = self.run_installer('debian', 'forky', 'amd64', '--suite', 'sid', '--prepare')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(' sid main', files['apt/sources.list.d/snodec.list'])
        for args in [('--unknown',), ('--suite',), ('--suite', '../sid')]:
            result, commands, _ = self.run_installer('debian', 'trixie', 'amd64', *args)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(any(c[0] in ('curl', 'apt-get') for c in commands))
        result, commands, _ = self.run_installer('unknown', '1', 'amd64')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(any(c[0] == 'curl' for c in commands))


if __name__ == '__main__':
    unittest.main()
