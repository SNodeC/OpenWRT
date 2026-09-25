"""Exercise IPK extraction and target-ELF checks through the audit CLI."""
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest

AUDIT = Path(__file__).with_name('audit_packages.py')


class IPKAuditTest(unittest.TestCase):
    def test_ipk_and_foreign_elf(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            binary = root / 'module'
            subprocess.run(['cc', '-nostdlib', '-shared', '-x', 'c', '-', '-o', str(binary)],
                           input='int value = 7;\n', text=True, check=True)
            reference = root / 'staging_dir/toolchain-test/lib/libc.so'
            reference.parent.mkdir(parents=True)
            reference.write_bytes(binary.read_bytes())
            package_dir = root / 'bin/packages/test/snodec'
            package_dir.mkdir(parents=True)

            def archive(entries):
                stream = io.BytesIO()
                with tarfile.open(fileobj=stream, mode='w:gz') as tar:
                    for name, data in entries.items():
                        info = tarfile.TarInfo(name)
                        info.size = len(data)
                        tar.addfile(info, io.BytesIO(data))
                return stream.getvalue()

            control = archive({'./control': b'Package: mqttsuite-cli\nVersion: 1.0.1-r1\nArchitecture: test\n'})
            data = archive({'./usr/bin/mqttcli': binary.read_bytes()})
            (package_dir / 'mqttsuite-cli_1.0.1-r1_test.ipk').write_bytes(
                archive({'./control.tar.gz': control, './data.tar.gz': data, './debian-binary': b'2.0\n'}))
            result = subprocess.run(['python3', str(AUDIT), str(root), str(root / 'audit'), 'cli'],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            header = bytearray(reference.read_bytes())
            header[18] ^= 1
            reference.write_bytes(header)
            result = subprocess.run(['python3', str(AUDIT), str(root), str(root / 'audit'), 'cli'],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            report = json.loads((root / 'audit/package-audit.json').read_text())
            self.assertTrue(any('incorrect architecture' in error for error in report['errors']))


if __name__ == '__main__':
    unittest.main()
