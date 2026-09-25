"""Extract OpenWrt packages and check ELF dependencies through their closure.

Usage: python3 tests/audit_packages.py SDK OUTPUT_DIRECTORY [all|native|cli]
No target binaries or package installation scripts are executed.
"""
from pathlib import Path
import hashlib
import io
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tarfile

sdk, output = map(lambda p: Path(p).resolve(), sys.argv[1:3])
mode = sys.argv[3] if len(sys.argv) > 3 else 'all'
assert mode in {'all', 'native', 'cli'}
output.mkdir(parents=True, exist_ok=True)
apk = sdk / 'staging_dir/host/bin/apk'
metadata = {}

# Package identity and virtual names belong to control metadata, not filenames.
for path in sorted(sdk.glob('bin/**/*')):
    if path.suffix == '.apk':
        dump = subprocess.check_output([str(apk), 'adbdump', '--allow-untrusted', str(path)], text=True)
        info = dump.split('info:\n', 1)[1].split('\npaths:', 1)[0]
        name = re.search(r'^  name: (.+)$', info, re.M)[1]
        relations = {}
        for field in ('depends', 'provides'):
            entries = re.search(r'^  ' + field + r':.*\n((?:    - .*\n)*)', info, re.M)
            relations[field] = [line.strip()[2:] for line in entries[1].splitlines()] if entries else []
    elif path.suffix == '.ipk':
        with tarfile.open(path) as package:
            control_member = next(m for m in package.getmembers() if Path(m.name).name == 'control.tar.gz')
            with tarfile.open(fileobj=io.BytesIO(package.extractfile(control_member).read())) as control:
                entry = next(m for m in control.getmembers() if Path(m.name).name == 'control')
                info = control.extractfile(entry).read().decode()
        name = re.search(r'^Package: (.+)$', info, re.M)[1]
        relations = {}
        for field in ('depends', 'provides'):
            entries = re.search(r'^' + field.capitalize() + r': (.*)$', info, re.M)
            relations[field] = entries[1].split(',') if entries else []
    else:
        continue
    metadata[name] = {'archive': path, **{
        field: [re.split(r'[\s(<>=~]', entry.strip(), maxsplit=1)[0] for entry in entries if entry.strip()]
        for field, entries in relations.items()}}


def canonical(name):
    if name in metadata:
        return name
    providers = [package for package, info in metadata.items() if name in info['provides']]
    if len(providers) != 1:
        raise RuntimeError(f'Expected one provider for {name!r}, found {providers}')
    return providers[0]


def load(name):
    name = canonical(name)
    package = metadata[name]
    if 'files' in package:
        return package
    archive = package['archive']
    root = output / 'extracted' / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    if archive.suffix == '.apk':
        subprocess.run([str(apk), 'extract', '--allow-untrusted', '--no-chown',
                        '--destination', str(root), str(archive)], check=True, stdout=subprocess.DEVNULL)
    else:
        with tarfile.open(archive) as archive_file:
            member = next(m for m in archive_file.getmembers() if Path(m.name).name == 'data.tar.gz')
            data = archive_file.extractfile(member).read()
        subprocess.run(['tar', '-xz', '--no-same-owner', '-C', str(root)], input=data, check=True)
    files = {'/' + str(p.relative_to(root)): p for p in root.rglob('*') if p.is_symlink() or p.is_file()}
    package.update(files=files, root=root)
    for dep in package['depends']:
        if not dep.startswith('!'):
            load(dep)
    return package


def closure(name, seen=None):
    name = canonical(name)
    seen = set() if seen is None else seen
    if name not in seen:
        seen.add(name)
        for dep in metadata[name]['depends']:
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

selected = ['mqttsuite-cli'] if mode == 'cli' else sorted(name for name in metadata if name.startswith(('snode.c', 'mqttsuite')))
assert len(selected) == (1 if mode == 'cli' else 76), f'Unexpected package count: {len(selected)}'
for name in selected:
    load(name)
report = {}
errors = []
reference_elf = next(sdk.glob('staging_dir/toolchain-*/lib/libc.so')).read_bytes()[:20]
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
        header = host.read_bytes()[:20]
        if (header[4:6], header[18:20]) != (reference_elf[4:6], reference_elf[18:20]):
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
                    'dependencies': package['depends'], 'elfs': elfs,
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
