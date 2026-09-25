"""Build/publish one complete OpenWRT-tag generation; SHAs are evidence, not refs."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
REPOSITORIES = ('snode.c', 'mqttsuite')


def run(*args, **kwargs):
    return subprocess.check_output(args, text=True, **kwargs).strip()


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def matrix():
    config = json.loads((ROOT / 'ci/platforms.json').read_text())
    return [dict(release=release, series=release.rsplit('.', 1)[0], target=target,
                 arch='riscv64_riscv64' if arch == 'riscv64_generic' and release.startswith('24.') else arch)
            for release in config['releases'] for arch, target in config['targets'].items()]


def sources():
    result = {}
    for repo in REPOSITORIES:
        refs = run('git', 'ls-remote', f'https://github.com/SNodeC/{repo}.git',
                   'refs/tags/OpenWRT', 'refs/tags/OpenWRT^{}').splitlines()
        if not refs:
            raise RuntimeError(f'{repo}: OpenWRT tag is missing')
        result[repo] = dict(line.split()[::-1] for line in refs)
    return result


def unchanged(bundle):
    if sources() != json.loads((bundle / 'sources.json').read_text()):
        raise RuntimeError('OpenWRT tags changed: refusing superseded build')


def prepare(source_dir, bundle):
    bundle.mkdir(parents=True)
    observed = sources()
    for repo in REPOSITORIES:
        ref = observed[repo].get('refs/tags/OpenWRT^{}', observed[repo]['refs/tags/OpenWRT'])
        if run('git', '-C', str(source_dir / repo), 'rev-parse', 'HEAD') != ref:
            raise RuntimeError(f'{repo}: checkout no longer matches OpenWRT')
        recipe = (ROOT / 'net' / repo / 'Makefile').read_text()
        version = re.search(r'^PKG_VERSION:=(.+)$', recipe, re.M)[1]
        assert re.search(r'^PKG_SOURCE_VERSION:=OpenWRT$', recipe, re.M)
        name = f'{repo}-{version}'
        run('tar', '-czf', str(bundle / f'{name}.tar.gz'), '--exclude=.git',
            f'--transform=s,^,{name}/,', '-C', str(source_dir / repo), '.')
    (bundle / 'sources.json').write_text(json.dumps(observed, indent=2) + '\n')
    (bundle / 'context.json').write_text(json.dumps({
        'recipe_ref': 'main', 'recipe_commit': run('git', '-C', str(ROOT), 'rev-parse', 'HEAD'),
        'run_url': f'https://github.com/SNodeC/OpenWRT/actions/runs/{os.environ.get("GITHUB_RUN_ID", "local")}'
    }))
    run('tar', '-czf', str(bundle / 'feed.tar.gz'), '--exclude=.git', '--exclude=__pycache__', '-C', str(ROOT), '.')
    unchanged(bundle)


def fetch(url):
    with urllib.request.urlopen(url, timeout=120) as response:
        return response.read()


def download_sdk(row, destination):
    base = f'https://downloads.openwrt.org/releases/{row["release"]}/targets/{row["target"]}/'
    profile = json.loads(fetch(base + 'profiles.json'))
    if profile['arch_packages'] != row['arch']:
        raise RuntimeError(f'Wrong SDK architecture: {profile["arch_packages"]}')
    entries = [line.split() for line in fetch(base + 'sha256sums').decode().splitlines()
               if 'openwrt-sdk-' in line]
    if len(entries) != 1:
        raise RuntimeError(f'Expected one SDK in {base}')
    checksum, filename = entries[0]
    filename = filename.lstrip('*')
    archive = destination.parent / filename
    urllib.request.urlretrieve(base + filename, archive)
    if digest(archive) != checksum:
        raise RuntimeError('SDK checksum mismatch')
    destination.mkdir()
    run('tar', '-xf', str(archive), '--strip-components=1', '-C', str(destination))
    archive.unlink()
    (destination / 'ci-sdk.json').write_text(json.dumps(dict(row, sdk_url=base + filename, sha256=checksum)))


def stage(sdk, bundle, output):
    """Stage only audited project packages; official feeds supply other dependencies."""
    info = json.loads((sdk / 'ci-sdk.json').read_text())
    feed = sdk / 'bin/packages' / info['arch'] / 'snodec'
    extension = '.ipk' if info['series'] == '24.10' else '.apk'
    packages = sorted(feed.glob('*' + extension))
    audit = json.loads((sdk / 'audit/package-audit.json').read_text())
    if audit['errors'] or len(packages) != len(audit['packages']):
        raise RuntimeError('Package inventory does not match successful audit')
    destination = output / 'releases' / info['series'] / info['arch']
    destination.mkdir(parents=True)
    indexes = ['Packages', 'Packages.gz', 'Packages.sig'] if extension == '.ipk' else ['packages.adb']
    for path in packages + [feed / name for name in indexes]:
        shutil.copy2(path, destination / path.name)
    files = {p.name: digest(p)
             for p in destination.iterdir()}
    info.update(sources=json.loads((bundle / 'sources.json').read_text()), files=files,
                packages=sorted(audit['packages']), revision=os.environ['PACKAGE_RELEASE'],
                context=json.loads((bundle / 'context.json').read_text()))
    (destination / 'build.json').write_text(json.dumps(info, indent=2) + '\n')


def publish(incoming, checkout, bundle):
    unchanged(bundle)
    expected = {(r['series'], r['arch']) for r in matrix()}
    found = {(p.parent.parent.name, p.parent.name) for p in incoming.glob('releases/*/*/build.json')}
    if found != expected:
        raise RuntimeError(f'Incomplete matrix: missing={expected - found}, unexpected={found - expected}')
    for series, arch in sorted(expected):
        directory = incoming / 'releases' / series / arch
        metadata = json.loads((directory / 'build.json').read_text())
        if metadata['sources'] != json.loads((bundle / 'sources.json').read_text()):
            raise RuntimeError('Mixed source generations')
        for name, checksum in metadata['files'].items():
            if Path(name).name != name or digest(directory / name) != checksum:
                raise RuntimeError(f'Package/index checksum mismatch: {name}')
        destination = checkout / 'releases' / series / arch
        if (destination / 'build.json').exists():
            previous = json.loads((destination / 'build.json').read_text())
            if int(previous['revision']) >= int(metadata['revision']):
                raise RuntimeError('Refusing an older/equal publication revision')
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copytree(directory, destination, dirs_exist_ok=True)
    shutil.copytree(ROOT / 'ci/keys', checkout / 'keys', dirs_exist_ok=True)
    shutil.copy2(ROOT / 'docs/package-repository.md', checkout / 'README.md')
    unchanged(bundle)


if __name__ == '__main__':
    command, *args = sys.argv[1:]
    if command == 'matrix':
        print(json.dumps({'include': matrix()}))
    elif command == 'sdk':
        download_sdk(json.loads(args[0]), Path(args[1]).resolve())
    else:
        {'prepare': prepare, 'check': unchanged, 'stage': stage, 'publish': publish}[command](
            *(Path(arg).resolve() for arg in args))
