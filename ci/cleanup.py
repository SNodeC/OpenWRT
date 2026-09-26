"""Retire unreferenced feed files after 30 days, using publication inventories."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys

from repository import digest

RETENTION = timedelta(days=30)


def cleanup(root, now=None):
    now = now or datetime.now(timezone.utc)
    if any(path.is_symlink() for path in root.rglob("*")):
        raise RuntimeError("Symlink in package snapshot; refusing cleanup")
    protected, candidates = set(), set()
    manifests = []
    for directory in (root / 'openwrt').glob('*/*'):
        if directory.is_dir():
            manifests.append((directory / 'build.json', directory))
            candidates.update(directory.glob('*.ipk'))
            candidates.update(directory.glob('*.apk'))
    for distribution in ['raspberrypios', 'debian', 'ubuntu']:
        base = root / distribution
        suites = {p.name for part in ['pool', 'dists'] for p in (base / part).glob('*') if p.is_dir()}
        for suite in suites:
            manifests.append((base / 'dists' / suite / 'build.json', base))
            candidates.update((base / 'pool' / suite).glob('*.deb'))
            candidates.update((base / 'dists' / suite).glob('**/by-hash/SHA256/*'))
    for distribution in ['rocky', 'fedora']:
        for directory in (root / distribution).glob('*/*'):
            if directory.is_dir():
                manifests.append((directory / 'build.json', directory))
                candidates.update((directory / 'Packages').glob('*.rpm'))
                candidates.update((directory / 'repodata').glob('*'))
    if not manifests:
        raise RuntimeError('No publication manifests; refusing cleanup')
    # The publishers create these inventories from the very same staged files as
    # the opkg, APK and APT indexes. Validate them before considering any removal.
    for manifest, base in manifests:
        info = json.loads(manifest.read_text())
        files = info['files']
        if base.name in {'raspberrypios', 'debian', 'ubuntu'}:
            suite = manifest.parent.name
            required = {f'dists/{suite}/{name}' for name in ['Release', 'InRelease', 'Release.gpg']}
            for arch in info.get('architectures', ['arm64']):
                required.update(f'dists/{suite}/main/binary-{arch}/{name}' for name in ['Packages', 'Packages.gz'])
        elif base.parent.parent.name in {'rocky', 'fedora'}:
            required = {'repodata/repomd.xml', 'repodata/repomd.xml.asc'}
        else:
            series = base.parent.name
            if series not in {'24.10', '25.12'}:
                raise RuntimeError(f'Unknown OpenWrt index format: {series}')
            required = {'Packages', 'Packages.gz', 'Packages.sig'} if series == '24.10' else {'packages.adb'}
        if not required <= files.keys():
            raise RuntimeError(f'Incomplete publication inventory: {manifest}')
        for name, checksum in files.items():
            path = base / name
            if Path(name).is_absolute() or '..' in Path(name).parts or path.is_symlink():
                raise RuntimeError(f'Unsafe publication path: {name}')
            if not path.resolve().is_relative_to(root.resolve()) or digest(path) != checksum:
                raise RuntimeError(f'Publication checksum mismatch: {path}')
            protected.add(path)
    state_path = root / 'retention.json'
    previous = json.loads(state_path.read_text()) if state_path.exists() else {}
    retired, expired = {}, []
    for path in sorted(candidates - protected):
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
            raise RuntimeError(f'Unsafe cleanup candidate: {path}')
        name = path.relative_to(root).as_posix()
        checksum = digest(path)
        record = previous.get(name, {})
        since = datetime.fromisoformat(record['unreferenced_since']) if record.get('sha256') == checksum else now
        if since.tzinfo is None or since > now:
            raise RuntimeError(f'Invalid retirement date: {name}')
        if now - since >= RETENTION:
            expired.append(path)
        else:
            retired[name] = dict(sha256=checksum, unreferenced_since=since.isoformat())
    # All validation is complete. Reappearing references automatically lose their
    # retirement date; replaced bytes start a fresh grace period.
    for path in expired:
        path.unlink()
        print(f'Removed {path.relative_to(root)}')
    contents = json.dumps(retired, indent=2, sort_keys=True) + '\n'
    if not state_path.exists() or state_path.read_text() != contents:
        state_path.write_text(contents)
    print(f'Protected {len(protected)} files; retained {len(retired)} retired files; removed {len(expired)}')
    return expired


if __name__ == '__main__':
    cleanup(Path(sys.argv[1]).resolve())
