"""Exercise real ELF normalization. Pass the SDK's host patchelf as argv[1]."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PATCHELF = str(Path(sys.argv.pop(1)).resolve())
SCRIPT = Path(__file__).resolve().parents[1] / 'net/mqttsuite/files/normalize-rpath.sh'

class RpathTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.stage = str(self.root / 'stage.[literal]')
        self.payload = self.root / 'payload with spaces'
        self.payload.mkdir()
        self.binary = self.payload / 'test library.so'
        subprocess.run(['cc', '-shared', '-x', 'c', '-o', str(self.binary), '-'],
                       input='int example(void) {return 0;}\n', text=True, check=True)
        (self.payload / 'ordinary.txt').write_text('not ELF')
        os.chmod(self.binary, 0o640)

    def tearDown(self):
        self.tmp.cleanup()

    def normalize(self, tool=PATCHELF):
        return subprocess.run(['bash', str(SCRIPT), tool, shutil.which('readelf'),
                               self.stage, str(self.payload)], capture_output=True, text=True)

    def test_preserves_paths_tag_and_permissions(self):
        for tag in ('RPATH', 'RUNPATH'):
            with self.subTest(tag=tag):
                old = f'{self.stage}/usr/lib/snode.c/iot/mqtt:$ORIGIN/../plugins:/opt/lib:{self.stage}-other/usr/lib::'
                args = ['--force-rpath'] if tag == 'RPATH' else []
                subprocess.run([PATCHELF, *args, '--set-rpath', old, str(self.binary)], check=True)
                result = self.normalize()
                self.assertEqual(result.returncode, 0, result.stderr)
                value = subprocess.check_output([PATCHELF, '--print-rpath', str(self.binary)], text=True).strip()
                self.assertEqual(value, old.replace(self.stage + '/usr/lib', '/usr/lib', 1))
                dynamic = subprocess.check_output(['readelf', '-d', str(self.binary)], text=True)
                self.assertIn('(' + tag + ')', dynamic)
                self.assertEqual(self.binary.stat().st_mode & 0o777, 0o640)
                self.assertEqual(self.normalize().returncode, 0)

    def test_missing_inputs_fail(self):
        missing = str(self.root / 'missing')
        for tool, reader, root in [(missing, 'readelf', str(self.payload)),
                                   (PATCHELF, missing, str(self.payload)),
                                   (PATCHELF, 'readelf', missing)]:
            result = subprocess.run(['bash', str(SCRIPT), tool, reader, self.stage, root],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)

    def test_patchelf_failure_is_fatal(self):
        subprocess.run([PATCHELF, '--set-rpath', self.stage + '/usr/lib', str(self.binary)], check=True)
        for failure in ('--print-rpath', '--set-rpath'):
            with self.subTest(failure=failure):
                tool = self.root / 'failing-patchelf'
                tool.write_text(f'#!/bin/sh\n[ "$1" != "{failure}" ] || exit 42\nexec "{PATCHELF}" "$@"\n')
                tool.chmod(0o755)
                self.assertNotEqual(self.normalize(str(tool)).returncode, 0)

unittest.main()
