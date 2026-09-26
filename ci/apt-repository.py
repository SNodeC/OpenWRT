"""Signed APT feeds, sharing source provenance and publication with OpenWrt."""
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from repository import ROOT, digest, run, unchanged


def suites():
    return json.loads((ROOT / 'ci/raspberrypi.json').read_text())


def stage(suite, packages, bundle, output):
    image = suites()[suite]
    unchanged(bundle)
    apt = output / 'apt'
    pool = apt / 'pool' / suite
    pool.mkdir(parents=True)
    names = set()
    for package in packages.glob('*.deb'):
        name, architecture = run('dpkg-deb', '-f', str(package), 'Package', 'Architecture').splitlines()
        names.add(name.removeprefix('Package: '))
        if architecture.removeprefix('Architecture: ') != 'arm64':
            raise RuntimeError('Non-ARM64 package')
        shutil.copy2(package, pool / package.name)
    if names != {'snodec', 'mqttsuite'}:
        raise RuntimeError(f'Incomplete Debian package set: {names}')
    dist = apt / 'dists' / suite
    index = dist / 'main/binary-arm64'
    index.mkdir(parents=True)
    contents = run('apt-ftparchive', 'packages', f'pool/{suite}', cwd=apt) + '\n'
    (index / 'Packages').write_text(contents)
    (index / 'Packages.gz').write_bytes(gzip.compress(contents.encode(), mtime=0))
    for path in list(index.iterdir()):
        target = index / 'by-hash/SHA256' / digest(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    release = run('apt-ftparchive',
                  '-o', f'APT::FTPArchive::Release::Codename={suite}',
                  '-o', f'APT::FTPArchive::Release::Suite={suite}',
                  '-o', 'APT::FTPArchive::Release::Architectures=arm64',
                  '-o', 'APT::FTPArchive::Release::Components=main',
                  '-o', 'APT::FTPArchive::Release::Origin=SNodeC',
                  '-o', 'APT::FTPArchive::Release::Acquire-By-Hash=yes',
                  'release', f'dists/{suite}', cwd=apt)
    (dist / 'Release').write_text(release + '\n')
    with tempfile.TemporaryDirectory() as home:
        subprocess.run(['gpg', '--homedir', home, '--batch', '--import'],
                       input=os.environ['APT_SIGNING_KEY'], text=True, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        for option, filename in [('--clearsign', 'InRelease'), ('--detach-sign', 'Release.gpg')]:
            run('gpg', '--homedir', home, '--batch', '--yes', '--armor',
                '--output', str(dist / filename), option, str(dist / 'Release'))
    info = dict(suite=suite, image=image, architecture='arm64', packages=sorted(names),
                revision=os.environ['PACKAGE_RELEASE'],
                sources=json.loads((bundle / 'sources.json').read_text()),
                context=json.loads((bundle / 'context.json').read_text()),
                files={str(p.relative_to(apt)): digest(p) for p in apt.rglob('*') if p.is_file()})
    (dist / 'build.json').write_text(json.dumps(info, indent=2) + '\n')
    unchanged(bundle)


def publish(incoming, checkout, bundle):
    unchanged(bundle)
    apt = incoming / 'apt'
    expected = set(suites())
    if {p.parent.name for p in apt.glob('dists/*/build.json')} != expected:
        raise RuntimeError('Incomplete Raspberry Pi OS matrix')
    for suite in sorted(expected):
        dist = apt / 'dists' / suite
        info = json.loads((dist / 'build.json').read_text())
        if info['sources'] != json.loads((bundle / 'sources.json').read_text()):
            raise RuntimeError('Mixed source generations')
        if info['image'] != suites()[suite] or info['packages'] != ['mqttsuite', 'snodec']:
            raise RuntimeError('Unexpected image or package inventory')
        for name, checksum in info['files'].items():
            path = Path(name)
            if path.is_absolute() or '..' in path.parts or digest(apt / path) != checksum:
                raise RuntimeError(f'APT checksum mismatch: {name}')
        with tempfile.TemporaryDirectory() as home:
            run('gpg', '--homedir', home, '--batch', '--import', str(ROOT / 'ci/keys/snodec-apt.asc'))
            run('gpg', '--homedir', home, '--batch', '--verify', str(dist / 'InRelease'))
            run('gpg', '--homedir', home, '--batch', '--verify', str(dist / 'Release.gpg'), str(dist / 'Release'))
        previous = checkout / 'apt/dists' / suite / 'build.json'
        if previous.exists() and int(json.loads(previous.read_text())['revision']) >= int(info['revision']):
            raise RuntimeError('Refusing older/equal APT publication')
    # Retain old .debs and by-hash indexes for clients with cached metadata.
    shutil.copytree(apt, checkout / 'apt', dirs_exist_ok=True)
    unchanged(bundle)


if __name__ == '__main__':
    command, *args = sys.argv[1:]
    if command == 'stage':
        stage(args[0], *(Path(p).resolve() for p in args[1:]))
    else:
        publish(*(Path(p).resolve() for p in args))
