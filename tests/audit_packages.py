"""Extract APKs and check ELF dependencies through each package's dependency closure.

Usage: python3 tests/audit_packages.py SDK OUTPUT_DIRECTORY [all|native|cli]
No target binaries or package installation scripts are executed.
"""
from pathlib import Path
import hashlib
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys

sdk, output = map(lambda p: Path(p).resolve(), sys.argv[1:3])
mode = sys.argv[3] if len(sys.argv) > 3 else 'all'
assert mode in {'all', 'native', 'cli'}
output.mkdir(parents=True, exist_ok=True)
apk = sdk / 'staging_dir/host/bin/apk'
archives = {}
for path in sdk.glob('bin/**/*.apk'):
    match = re.match(r'(.+)-(?=[0-9])', path.name)
    if match:
        archives[match[1]] = path
metadata = {}

def load(name):
    if name in metadata:
        return metadata[name]
    archive = archives[name]
    dump = subprocess.check_output([str(apk), 'adbdump', '--allow-untrusted', str(archive)], text=True)
    info = dump.split('info:\n', 1)[1].split('\npaths:', 1)[0]
    deps = re.search(r'^  depends:.*\n((?:    - .*\n)*)', info, re.M)
    dependencies = [re.split(r'[<>=~]', line.strip()[2:])[0]
                    for line in deps[1].splitlines()] if deps else []
    root = output / 'extracted' / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(apk), 'extract', '--allow-untrusted', '--no-chown',
                    '--destination', str(root), str(archive)], check=True, stdout=subprocess.DEVNULL)
    files = {'/' + str(p.relative_to(root)): p for p in root.rglob('*') if p.is_symlink() or p.is_file()}
    result = metadata[name] = {'dependencies': dependencies, 'files': files, 'root': root, 'archive': archive}
    for dep in dependencies:
        if not dep.startswith('!'):
            load(dep)
    return result

def closure(name, seen=None):
    seen = set() if seen is None else seen
    if name not in seen:
        seen.add(name)
        for dep in metadata[name]['dependencies']:
            if not dep.startswith('!'):
                closure(dep, seen)
    return seen

def resolve(path, files):
    for _ in range(20):
        host = files.get(path)
        if host is None:
            return False
        if not host.is_symlink():
            return True
        target = os.readlink(host)
        path = posixpath.normpath(target if target.startswith('/') else posixpath.join(posixpath.dirname(path), target))
    return False

selected = ['mqttsuite-cli'] if mode == 'cli' else sorted(name for name in archives if name.startswith(('snode.c', 'mqttsuite')))
assert len(selected) == (1 if mode == 'cli' else 76), f'Unexpected package count: {len(selected)}'
for name in selected:
    load(name)
report = {}
errors = []
for name in selected:
    package = metadata[name]
    available = {}
    for dependency in closure(name):
        for target, host in metadata[dependency]['files'].items():
            if target in available and available[target] != host:
                errors.append(f'{name}: conflicting ownership of {target}')
            available[target] = host
    elfs = []
    for target, host in package['files'].items():
        if host.is_symlink():
            if not resolve(target, available):
                errors.append(f'{name}: broken symlink {target}')
            continue
        with host.open('rb') as file:
            if file.read(4) != b'\x7fELF':
                continue
        dynamic = subprocess.check_output(['readelf', '-d', str(host)], text=True)
        header = subprocess.check_output(['readelf', '-h', str(host)], text=True)
        if 'AArch64' not in header:
            errors.append(f'{name}: incorrect architecture for {target}')
        needed = re.findall(r'\(NEEDED\).*\[(.*?)\]', dynamic)
        soname = re.findall(r'\(SONAME\).*\[(.*?)\]', dynamic)
        if '/usr/lib/' in target and '.so' in host.name:
            abi = '2' if host.name.startswith('libsnodec-') else '1'
            expected = host.name.split('.so')[0] + ('.so.' + abi if '.so.' in host.name else '.so')
            if soname != [expected]:
                errors.append(f'{name}: incorrect SONAME for {target}: {soname}, expected {expected}')
        rpath = re.findall(r'\((?:RUNPATH|RPATH)\).*\[(.*?)\]', dynamic)
        search = []
        for group in rpath:
            for item in group.split(':'):
                if '/staging_dir/' in item or '/build_dir/' in item or str(sdk) in item:
                    errors.append(f'{name}: host path leaked into {target}: {item}')
                search.append(item.replace('${ORIGIN}', posixpath.dirname(target)).replace('$ORIGIN', posixpath.dirname(target)))
        search += ['/lib', '/usr/lib']
        for library in needed:
            if not any(resolve(posixpath.normpath(directory + '/' + library), available) for directory in search):
                errors.append(f'{name}: {target} cannot resolve {library} using {search}')
        elfs.append({'path': target, 'needed': needed, 'soname': soname, 'rpath': rpath})
    report[name] = {'archive': str(package['archive']),
                    'sha256': hashlib.sha256(package['archive'].read_bytes()).hexdigest(),
                    'dependencies': package['dependencies'], 'elfs': elfs,
                    'files': sorted(package['files'])}

# These names are constructed by SNode.C's loaders, so DT_NEEDED cannot test them.
for app in ['broker', 'integrator', 'bridge', 'cli', 'store']:
    name = 'mqttsuite-' + app
    if name not in selected:
        continue
    if mode != 'all':
        if any('websocket' in path for path in metadata[name]['files']):
            errors.append(f'{name}: disabled WebSocket plugin still packaged')
        deps = closure(name)
        if any('websocket' in dep for dep in deps):
            errors.append(f'{name}: disabled WebSocket dependency still selected')
        if app in ['broker', 'cli', 'store'] and 'snode.c-core-socket-stream-tls' in deps:
            errors.append(f'{name}: disabled TLS transport dependency still selected')
        continue
    files = {p: f for dep in closure(name) for p, f in metadata[dep]['files'].items()}
    role = 'server' if app == 'broker' else 'client'
    for path in [f'/usr/lib/snode.c/web/http/upgrade/libsnodec-websocket-{role}.so.2',
                 f'/usr/lib/snode.c/web/http/upgrade/websocket/mqtt{app}/libsnodec-websocket-mqtt-{role}.so.2']:
        if not resolve(path, files):
            errors.append(f'{name}: missing dlopen library {path}')
(output / 'package-audit.json').write_text(json.dumps({'packages': report, 'errors': errors}, indent=2) + '\n')
print(f'Checked {len(selected)} packages, {sum(len(p["elfs"]) for p in report.values())} ELF files.')
print('\n'.join(errors) if errors else 'All dependency, architecture, symlink, RPATH and WebSocket plugin checks passed.')
sys.exit(bool(errors))
