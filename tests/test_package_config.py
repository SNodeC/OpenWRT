"""Run branch-owned Kconfig cases without changing the SDK's active .config.

Usage: python3 tests/test_package_config.py SDK [CASE_FILE ...]
Without CASE_FILE arguments, run all project and integration cases in tests/.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SDK = Path(sys.argv[1]).resolve()
CASE_FILES = ([Path(arg) for arg in sys.argv[2:]] or
              sorted(Path(__file__).parent.glob('*/package_config.json')))


class PackageConfigTest(unittest.TestCase):
    def __init__(self, source, case):
        super().__init__()
        self.source, self.case = source, case

    def shortDescription(self):
        return f'{self.source.parent.name}: {self.case["name"]}'

    def runTest(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'config'
            config.write_text('# CONFIG_ALL is not set\n# CONFIG_ALL_KMODS is not set\n'
                              '# CONFIG_ALL_NONSHARED is not set\n' + ''.join(
                                  f'CONFIG_{key}={value}\n'
                                  for key, value in self.case['request'].items()))
            result = subprocess.run([str(SDK / 'scripts/config/conf'), '--defconfig',
                                     str(config), '-w', str(config), 'Config.in'],
                                    cwd=SDK, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            # The pinned SDK has an unrelated libcurl/LDAP recursion warning.
            for error in result.stderr.split('recursive dependency detected!')[1:]:
                error = error.split('For a resolution')[0]
                self.assertNotIn('snode', error)
                self.assertNotIn('mqttsuite', error)
            values = dict(line.split('=', 1) for line in config.read_text().splitlines()
                          if line.startswith('CONFIG_') and '=' in line)
        for key, value in self.case.get('expected', {}).items():
            self.assertEqual(values.get('CONFIG_' + key), value, key)
        for key in self.case.get('absent', []):
            self.assertNotIn('CONFIG_' + key, values)
        for prefix, count in self.case.get('packages', {}).items():
            packages = {key: value for key, value in values.items()
                        if key.startswith('CONFIG_PACKAGE_' + prefix)}
            self.assertEqual(len(packages), count, prefix)
            self.assertEqual(set(packages.values()), {'m'}, prefix)


suite = unittest.TestSuite(PackageConfigTest(source, case)
                           for source in CASE_FILES for case in json.loads(source.read_text()))
if not suite.countTestCases():
    raise SystemExit('No package configuration cases found')
sys.exit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
