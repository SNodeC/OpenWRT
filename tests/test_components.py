"""Exercise real CPack component ownership and inferred ELF dependencies."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)


class DebianComponentsTest(unittest.TestCase):
    def test_dependency_closure_and_full_install_migration(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'base.c').write_text('int value(void) { return 42; }\n')
            (root / 'client.c').write_text('extern int value(void); int client(void) { return value(); }\n')
            (root / 'CMakeLists.txt').write_text('''
cmake_minimum_required(VERSION 3.25)
project(package_fixture VERSION 1.0 LANGUAGES C)
add_library(base SHARED base.c)
add_library(client SHARED client.c)
target_link_libraries(client PRIVATE base)
foreach(target base client)
    target_link_options(${target} PRIVATE -nostdlib)
    set_target_properties(${target} PROPERTIES SOVERSION 1)
    install(TARGETS ${target} LIBRARY DESTINATION lib COMPONENT ${target})
endforeach()
set(CPACK_PACKAGE_NAME fixture)
set(CPACK_PACKAGE_CONTACT "Test <test@example.invalid>")
set(CPACK_PACKAGING_INSTALL_PREFIX /usr)
set(CPACK_DEBIAN_FILE_NAME DEB-DEFAULT)
set(CPACK_DEBIAN_ENABLE_COMPONENT_DEPENDS ON)
set(CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON)
set(CPACK_COMPONENTS_ALL base client)
include(CPack)
''')
            build, packages = root / 'build', root / 'packages'
            run('cmake', '-S', str(root), '-B', str(build))
            run('cmake', '--build', str(build))
            run('cpack', '--config', str(build / 'CPackConfig.cmake'), '-G', 'DEB', '-B', str(packages),
                '-D', 'CPACK_PACKAGE_VERSION=1.0-2', '-D', f'COMPONENT_OUTPUT={packages}',
                '-D', f'CPACK_PROJECT_CONFIG_FILE={ROOT}/ci/components.cmake')
            self.assertEqual(len(list(packages.glob('*.deb'))), 3)
            architecture = run('dpkg', '--print-architecture').strip()
            client = packages / f'fixture-client_1.0-2_{architecture}.deb'
            meta = packages / f'fixture_1.0-2_{architecture}.deb'
            self.assertIn('fixture-base (= 1.0-2)', run('dpkg-deb', '-f', str(client), 'Depends'))
            for field in ['Breaks', 'Replaces']:
                self.assertEqual(run('dpkg-deb', '-f', str(client), field).strip(), 'fixture (<< 1.0-2)')
            self.assertIn('fixture-client (= 1.0-2)', run('dpkg-deb', '-f', str(meta), 'Depends'))
            self.assertEqual(set((packages / 'fixture.packages').read_text().splitlines()),
                             {'fixture', 'fixture-base', 'fixture-client'})
            self.assertNotIn('libclient', run('dpkg-deb', '-c', str(meta)))
            rpm_packages = root / 'rpm'
            run('cpack', '--config', str(build / 'CPackConfig.cmake'), '-G', 'RPM', '-B', str(rpm_packages),
                '-D', 'CPACK_RPM_PACKAGE_RELEASE=2', '-D', f'COMPONENT_OUTPUT={rpm_packages}',
                '-D', f'CPACK_PROJECT_CONFIG_FILE={ROOT}/ci/components.cmake')
            self.assertEqual(len(list(rpm_packages.glob('*.rpm'))), 3)
            rpm_client = next(rpm_packages.glob('fixture-client-*.rpm'))
            rpm_meta = next(rpm_packages.glob('fixture-1*.rpm'))
            self.assertIn('fixture-base = 1.0-2', run('rpm', '-qp', '--requires', str(rpm_client)))
            self.assertIn('fixture-client = 1.0-2', run('rpm', '-qp', '--requires', str(rpm_meta)))
            self.assertNotIn('/usr/', run('rpm', '-qpl', str(rpm_meta)))



if __name__ == '__main__':
    unittest.main()
