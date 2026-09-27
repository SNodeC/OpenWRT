"""Signed APT feeds, sharing source provenance and publication with OpenWrt."""
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from repository import ROOT, digest, run, unchanged, linux_matrix, signer


def suites(distribution='raspberrypios'):
    if distribution == 'raspberrypios':
        return json.loads((ROOT / 'ci/raspberrypi.json').read_text())
    return {row['suite']: row['image'] for row in linux_matrix() if row['distribution'] == distribution}


def architectures(distribution, suite):
    return ['arm64'] if distribution == 'raspberrypios' else sorted(
        row['arch'] for row in linux_matrix() if row['distribution'] == distribution and row['suite'] == suite)


def stage(suite, packages, bundle, output, distribution='raspberrypios'):
    image = suites(distribution)[suite]
    unchanged(bundle)
    apt = output / distribution
    pool = apt / 'pool' / suite
    pool.mkdir(parents=True)
    names = set()
    by_arch = {}
    for package in packages.glob('*.deb'):
        name, architecture = run('dpkg-deb', '-f', str(package), 'Package', 'Architecture').splitlines()
        name = name.removeprefix('Package: ')
        architecture = architecture.removeprefix('Architecture: ')
        if (name, architecture) in names:
            raise RuntimeError(f'Duplicate Debian package: {name}')
        names.add((name, architecture))
        by_arch.setdefault(architecture, set()).add(name)
        if architecture not in architectures(distribution, suite):
            raise RuntimeError(f'Unexpected architecture: {architecture}')
        shutil.copy2(package, pool / package.name)
    expected = {name for project in ('snodec', 'mqttsuite')
                for name in (packages / f'{project}.packages').read_text().splitlines()}
    if not by_arch or any(names != expected for names in by_arch.values()):
        raise RuntimeError(f'Incomplete Debian package set: {names}')
    dist = apt / 'dists' / suite
    records = run('apt-ftparchive', 'packages', f'pool/{suite}', cwd=apt).split('\n\n')
    for arch in sorted(by_arch):
        index = dist / f'main/binary-{arch}'
        index.mkdir(parents=True)
        contents = '\n\n'.join(record for record in records if f'Architecture: {arch}' in record.splitlines()) + '\n\n'
        (index / 'Packages').write_text(contents)
        (index / 'Packages.gz').write_bytes(gzip.compress(contents.encode(), mtime=0))
        for path in list(index.iterdir()):
            target = index / 'by-hash/SHA256' / digest(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    release = run('apt-ftparchive',
                  '-o', f'APT::FTPArchive::Release::Codename={suite}',
                  '-o', f'APT::FTPArchive::Release::Suite={suite}',
                  '-o', 'APT::FTPArchive::Release::Architectures=' + ' '.join(sorted(by_arch)),
                  '-o', 'APT::FTPArchive::Release::Components=main',
                  '-o', 'APT::FTPArchive::Release::Origin=SNodeC',
                  '-o', 'APT::FTPArchive::Release::Acquire-By-Hash=yes',
                  'release', f'dists/{suite}', cwd=apt)
    (dist / 'Release').write_text(release + '\n')
    with signer() as home:
        for option, filename in [('--clearsign', 'InRelease'), ('--detach-sign', 'Release.gpg')]:
            run('gpg', '--homedir', home, '--batch', '--yes', '--armor',
                '--output', str(dist / filename), option, str(dist / 'Release'))
    info = dict(suite=suite, distribution=distribution, image=image, architectures=sorted(by_arch), packages=sorted(expected),
                revision=os.environ['PACKAGE_RELEASE'],
                sources=json.loads((bundle / 'sources.json').read_text()),
                context=json.loads((bundle / 'context.json').read_text()),
                files={str(p.relative_to(apt)): digest(p) for p in apt.rglob('*') if p.is_file()})
    (dist / 'build.json').write_text(json.dumps(info, indent=2) + '\n')
    unchanged(bundle)


def publish(incoming, checkout, bundle, distribution='raspberrypios'):
    unchanged(bundle)
    apt = incoming / distribution
    expected = set(suites(distribution))
    if {p.parent.name for p in apt.glob('dists/*/build.json')} != expected:
        raise RuntimeError(f'Incomplete {distribution} matrix')
    inventories = []
    for suite in sorted(expected):
        dist = apt / 'dists' / suite
        info = json.loads((dist / 'build.json').read_text())
        if info['sources'] != json.loads((bundle / 'sources.json').read_text()):
            raise RuntimeError('Mixed source generations')
        for name, checksum in info['files'].items():
            path = Path(name)
            if path.is_absolute() or '..' in path.parts or digest(apt / path) != checksum:
                raise RuntimeError(f'APT checksum mismatch: {name}')
        names = sorted({run('dpkg-deb', '-f', str(apt / name), 'Package')
                        for name in info['files'] if name.endswith('.deb')})
        inventories.append(names)
        if (info['image'] != suites(distribution)[suite] or info['packages'] != names
                or info['architectures'] != architectures(distribution, suite)):
            raise RuntimeError('Unexpected image or package inventory')
        with tempfile.TemporaryDirectory() as home:
            run('gpg', '--homedir', home, '--batch', '--import', str(ROOT / 'ci/keys/snodec-apt.asc'))
            run('gpg', '--homedir', home, '--batch', '--verify', str(dist / 'InRelease'))
            run('gpg', '--homedir', home, '--batch', '--verify', str(dist / 'Release.gpg'), str(dist / 'Release'))
        previous = checkout / distribution / 'dists' / suite / 'build.json'
        if previous.exists() and int(json.loads(previous.read_text())['revision']) >= int(info['revision']):
            raise RuntimeError('Refusing older/equal APT publication')
    if any(names != inventories[0] for names in inventories):
        raise RuntimeError('Different component inventories across OS releases')
    # Retain old .debs and by-hash indexes for clients with cached metadata.
    shutil.copytree(apt, checkout / distribution, dirs_exist_ok=True)
    unchanged(bundle)


if __name__ == '__main__':
    command, *args = sys.argv[1:]
    if command == 'stage':
        stage(args[0], *(Path(p).resolve() for p in args[1:]))
    else:
        publish(*(Path(p).resolve() for p in args))
