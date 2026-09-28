"""Capture a release-tag generation; commit IDs are evidence, not pinned refs."""
from contextlib import contextmanager
import tempfile
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


@contextmanager
def signer():
    with tempfile.TemporaryDirectory() as home:
        subprocess.run(['gpg', '--homedir', home, '--batch', '--import'],
                       input=os.environ['APT_SIGNING_KEY'], text=True, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        yield home


def matrix():
    config = json.loads((ROOT / 'ci/platforms.json').read_text())
    return [dict(release=release, series=release.rsplit('.', 1)[0], target=target,
                 arch='riscv64_riscv64' if arch == 'riscv64_generic' and release.startswith('24.') else arch)
            for release in config['releases'] for arch, target in config['targets'].items()]


def linux_matrix():
    platforms = {'amd64': 'linux/amd64', 'x86_64': 'linux/amd64',
                 'arm64': 'linux/arm64', 'aarch64': 'linux/arm64',
                 'armhf': 'linux/arm/v7', 'riscv64': 'linux/riscv64'}
    return [dict(distribution=row['distribution'], suite=row['suite'], image=row['image'],
                 arch=arch, platform=platforms[arch],
                 runner='ubuntu-24.04-arm' if arch in {'arm64', 'aarch64', 'armhf'} else 'ubuntu-24.04')
            for row in json.loads((ROOT / 'ci/linux.json').read_text()) for arch in row['architectures']]


def source_tags():
    return {repo: os.environ.get(variable, os.environ.get('SOURCE_TAG', 'OpenWRT'))
            for repo, variable in [('snode.c', 'SNODEC_TAG'), ('mqttsuite', 'MQTTSUITE_TAG')]}


def sources(tags):
    result = {}
    for repo, tag in tags.items():
        run('git', 'check-ref-format', f'refs/tags/{tag}')
        refs = run('git', 'ls-remote', f'https://github.com/SNodeC/{repo}.git',
                   f'refs/tags/{tag}', f'refs/tags/{tag}^{{}}').splitlines()
        if not refs:
            raise RuntimeError(f'{repo}: {tag} tag is missing')
        result[repo] = dict(line.split()[::-1] for line in refs)
    return result


def unchanged(bundle):
    context = json.loads((bundle / 'context.json').read_text())
    tags = context.get('source_tags') or {repo: context['source_tag'] for repo in REPOSITORIES}
    if sources(tags) != json.loads((bundle / 'sources.json').read_text()):
        raise RuntimeError('Source tags changed: refusing superseded build')


def prepare(source_dir, bundle):
    bundle.mkdir(parents=True)
    tags = source_tags()
    observed = sources(tags)
    versions = {}
    for repo in REPOSITORIES:
        tag = tags[repo]
        ref = observed[repo].get(f'refs/tags/{tag}^{{}}', observed[repo][f'refs/tags/{tag}'])
        if run('git', '-C', str(source_dir / repo), 'rev-parse', 'HEAD') != ref:
            raise RuntimeError(f'{repo}: checkout no longer matches {tag}')
        recipe = (ROOT / 'net' / repo / 'Makefile').read_text()
        version = re.search(r'^PKG_VERSION:=(.+)$', recipe, re.M)[1]
        project = (source_dir / repo / 'CMakeLists.txt').read_text()
        project_version = re.search(r'\bVERSION\s+([0-9]+\.[0-9]+\.[0-9]+)', project)
        if not project_version or project_version[1] != version:
            raise RuntimeError(f'{repo}: source version does not match recipe version {version}')
        versions[repo] = version
        name = f'{repo}-{version}'
        run('tar', '-czf', str(bundle / f'{name}.tar.gz'), '--exclude=.git',
            f'--transform=s,^,{name}/,', '-C', str(source_dir / repo), '.')
    (bundle / 'sources.json').write_text(json.dumps(observed, indent=2) + '\n')
    (bundle / 'context.json').write_text(json.dumps({
        'source_tags': tags, 'versions': versions,
        'recipe_ref': os.environ.get('RECIPE_REF', 'main'),
        'recipe_commit': run('git', '-C', str(ROOT), 'rev-parse', 'HEAD'),
        'destination': os.environ.get('PACKAGE_BRANCH', 'packages'),
        'run_id': os.environ.get('GITHUB_RUN_ID', 'local'),
        'run_url': f'https://github.com/{os.environ.get("GITHUB_REPOSITORY", "SNodeC/OpenWRT")}/actions/runs/{os.environ.get("GITHUB_RUN_ID", "local")}'
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
    """Stage project packages and signed indexes; official feeds supply other dependencies."""
    info = json.loads((sdk / 'ci-sdk.json').read_text())
    feed = sdk / 'bin/packages' / info['arch'] / 'snodec'
    extension = '.ipk' if info['series'] == '24.10' else '.apk'
    packages = sorted(feed.glob('*' + extension))
    destination = output / 'openwrt' / info['series'] / info['arch']
    destination.mkdir(parents=True)
    indexes = ['Packages', 'Packages.gz', 'Packages.sig'] if extension == '.ipk' else ['packages.adb']
    for path in packages + [feed / name for name in indexes]:
        shutil.copy2(path, destination / path.name)
    files = {p.name: digest(p)
             for p in destination.iterdir()}
    info.update(sources=json.loads((bundle / 'sources.json').read_text()), files=files,
                revision=os.environ['PACKAGE_RELEASE'],
                context=json.loads((bundle / 'context.json').read_text()))
    info['versions'] = {repo: f"{version}-r{info['revision']}"
                        for repo, version in info['context']['versions'].items()}
    (destination / 'build.json').write_text(json.dumps(info, indent=2) + '\n')


def publication_needed(previous, incoming):
    if not previous.exists():
        return True
    current = json.loads(previous.read_text())
    if int(current['revision']) > int(incoming['revision']):
        raise RuntimeError('Superseded publication: a newer revision is already published')
    if int(current['revision']) == int(incoming['revision']):
        if all(current.get(key) == incoming.get(key) for key in ('sources', 'context', 'files')):
            return False
        raise RuntimeError('Different package content under the same publication revision')
    return True


def publish(incoming, checkout, bundle):
    unchanged(bundle)
    expected = {(r['series'], r['arch']) for r in matrix()}
    found = {(p.parent.parent.name, p.parent.name) for p in incoming.glob('openwrt/*/*/build.json')}
    if not found or not found <= expected:
        raise RuntimeError(f'Unexpected OpenWrt targets: {found - expected}')
    for series, arch in sorted(found):
        directory = incoming / 'openwrt' / series / arch
        metadata = json.loads((directory / 'build.json').read_text())
        if metadata['sources'] != json.loads((bundle / 'sources.json').read_text()):
            raise RuntimeError('Mixed source generations')
        for name, checksum in metadata['files'].items():
            if Path(name).name != name or digest(directory / name) != checksum:
                raise RuntimeError(f'Package/index checksum mismatch: {name}')
        destination = checkout / 'openwrt' / series / arch
        if not publication_needed(destination / 'build.json', metadata):
            continue
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copytree(directory, destination, dirs_exist_ok=True)
    unchanged(bundle)


if __name__ == '__main__':
    command, *args = sys.argv[1:]
    if command == 'matrix':
        print(json.dumps({'include': matrix()}))
    elif command == 'linux-matrix':
        print(json.dumps({'include': linux_matrix()}))
    elif command == 'sdk':
        download_sdk(json.loads(args[0]), Path(args[1]).resolve())
    else:
        {'prepare': prepare, 'check': unchanged, 'stage': stage, 'publish': publish}[command](
            *(Path(arg).resolve() for arg in args))
