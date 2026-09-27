"""Stage tested per-target feeds; assemble the complete Linux publication."""
import importlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

from repository import linux_matrix, unchanged

apt = importlib.import_module('apt-repository')
rpm = importlib.import_module('rpm-repository')


def stage(row, packages, bundle, output):
    if row not in linux_matrix():
        raise RuntimeError('Unknown Linux target')
    directory = output / 'linux' / row['distribution'] / row['suite'] / row['arch']
    if row['distribution'] in {'debian', 'ubuntu'}:
        apt.stage(row['suite'], packages, bundle, output / 'linux', row['distribution'])
    else:
        rpm.stage(row, packages, bundle, directory)


def publish(incoming, checkout, bundle):
    unchanged(bundle)
    rows = linux_matrix()
    expected = {(r['distribution'], r['suite'], r['arch']) for r in rows}
    found = {p.relative_to(incoming / 'linux').parts for p in (incoming / 'linux').glob('*/*/*') if p.is_dir()}
    if found != expected:
        raise RuntimeError(f'Incomplete Linux matrix: missing={expected - found}, unexpected={found - expected}')
    with tempfile.TemporaryDirectory() as temporary:
        staging = Path(temporary) / 'feeds'
        revisions = {json.loads(p.read_text())['revision'] for p in (incoming / 'linux').rglob('build.json')}
        if len(revisions) != 1:
            raise RuntimeError('Mixed publication revisions')
        rpm_rows = [row for row in rows if row['distribution'] in {'rocky', 'fedora'}]
        for row in rpm_rows:
            relative = Path(row['distribution']) / row['suite'] / row['arch']
            feed = incoming / 'linux' / relative / relative
            shutil.copytree(feed, staging / relative)
        for distribution in ['debian', 'ubuntu']:
            apt.publish(incoming / 'linux', checkout, bundle, distribution)
        rpm.publish(rpm_rows, staging, checkout, bundle)
    unchanged(bundle)


if __name__ == '__main__':
    command, *args = sys.argv[1:]
    if command == 'stage':
        stage(json.loads(args[0]), *(Path(p).resolve() for p in args[1:]))
    else:
        publish(*(Path(p).resolve() for p in args))
