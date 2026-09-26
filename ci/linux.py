"""Stage tested per-target feeds; assemble the complete Linux publication."""
import importlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

from repository import digest, linux_matrix, unchanged

apt = importlib.import_module('apt-repository')
rpm = importlib.import_module('rpm-repository')


def stage(row, packages, bundle, output):
    if row not in linux_matrix():
        raise RuntimeError('Unknown Linux target')
    directory = output / 'linux' / row['distribution'] / row['suite'] / row['arch']
    if row['distribution'] in {'debian', 'ubuntu'}:
        apt.stage(row['suite'], packages, bundle, directory, row['distribution'])
    else:
        rpm.stage(row, packages, bundle, directory)
    for inventory in packages.glob('*.packages'):
        shutil.copy2(inventory, directory / inventory.name)


def publish(incoming, checkout, bundle):
    unchanged(bundle)
    rows = linux_matrix()
    expected = {(r['distribution'], r['suite'], r['arch']) for r in rows}
    found = {p.relative_to(incoming / 'linux').parts for p in (incoming / 'linux').glob('*/*/*') if p.is_dir()}
    if found != expected:
        raise RuntimeError(f'Incomplete Linux matrix: missing={expected - found}, unexpected={found - expected}')
    with tempfile.TemporaryDirectory() as temporary:
        staging = Path(temporary) / 'feeds'
        revision = None
        for distribution in ['debian', 'ubuntu']:
            for suite in apt.suites(distribution):
                packages = Path(temporary) / distribution / suite
                packages.mkdir(parents=True)
                for arch in apt.architectures(distribution, suite):
                    target = incoming / 'linux' / distribution / suite / arch
                    feed = target / distribution
                    info = json.loads((feed / 'dists' / suite / 'build.json').read_text())
                    if info['sources'] != json.loads((bundle / 'sources.json').read_text()):
                        raise RuntimeError('Mixed source generations')
                    if info['architectures'] != [arch] or info['image'] != apt.suites(distribution)[suite]:
                        raise RuntimeError('Unexpected APT target')
                    if revision is not None and revision != info['revision']:
                        raise RuntimeError('Mixed publication revisions')
                    revision = info['revision']
                    for name, checksum in info['files'].items():
                        if Path(name).is_absolute() or '..' in Path(name).parts or digest(feed / name) != checksum:
                            raise RuntimeError(f'APT checksum mismatch: {name}')
                    for path in (feed / 'pool' / suite).glob('*.deb'):
                        shutil.copy2(path, packages / path.name)
                    for inventory in target.glob('*.packages'):
                        destination = packages / inventory.name
                        if destination.exists() and destination.read_bytes() != inventory.read_bytes():
                            raise RuntimeError('Different component inventories across architectures')
                        shutil.copy2(inventory, destination)
                os.environ['PACKAGE_RELEASE'] = revision
                apt.stage(suite, packages, bundle, staging, distribution)
        rpm_rows = [row for row in rows if row['distribution'] in {'rocky', 'fedora'}]
        for row in rpm_rows:
            relative = Path(row['distribution']) / row['suite'] / row['arch']
            feed = incoming / 'linux' / relative / relative
            if json.loads((feed / 'build.json').read_text())['revision'] != revision:
                raise RuntimeError('Mixed publication revisions')
            shutil.copytree(feed, staging / relative)
        for distribution in ['debian', 'ubuntu']:
            apt.publish(staging, checkout, bundle, distribution)
        rpm.publish(rpm_rows, staging, checkout, bundle)
    unchanged(bundle)


if __name__ == '__main__':
    command, *args = sys.argv[1:]
    if command == 'stage':
        stage(json.loads(args[0]), *(Path(p).resolve() for p in args[1:]))
    else:
        publish(*(Path(p).resolve() for p in args))
