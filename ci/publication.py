"""One serialized writer for per-target publications and their displayed status."""
from datetime import datetime, timezone
from html import escape
import importlib
import json
import os
from pathlib import Path
import shutil
import sys

from repository import ROOT, matrix, linux_matrix, unchanged, run


def targets(profile):
    rows = [dict(family='openwrt', distribution='openwrt', suite=r['series'], arch=r['arch'],
                 runner='ubuntu-24.04', build=r) for r in matrix()]
    rows += [dict(family='raspberrypi', distribution='raspberrypios', suite=suite, arch='arm64',
                  runner='ubuntu-24.04-arm', build=dict(suite=suite))
             for suite in json.loads((ROOT / 'ci/raspberrypi.json').read_text())]
    rows += [dict(family='linux', distribution=r['distribution'], suite=r['suite'], arch=r['arch'],
                  runner=r['runner'], build=r) for r in linux_matrix()]
    for row in rows:
        row['id'] = '-'.join(row[k] for k in ('distribution', 'suite', 'arch'))
    if profile == 'development':
        selected = {'openwrt-25.12-x86_64', 'debian-trixie-amd64', 'raspberrypios-trixie-arm64'}
        rows = [r for r in rows if r['id'] in selected]
        if len(rows) != 3:
            raise RuntimeError('Development matrix no longer resolves to exactly three targets')
    elif profile != 'full':
        raise ValueError('Unknown matrix profile')
    return rows


def read(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def published(root, row):
    if row['distribution'] in {'debian', 'ubuntu', 'raspberrypios'}:
        path = root / row['distribution'] / 'dists' / row['suite'] / 'build.json'
        info = read(path, {})
        info = info.get('targets', {}).get(row['arch'], info if row['arch'] in info.get('architectures', []) else {})
    else:
        path = root / row['distribution'] / row['suite'] / row['arch'] / 'build.json'
        info = read(path, {})
    return info, path.parent.relative_to(root).as_posix()


def render(root, state):
    badges = root / 'status'
    badges.mkdir(exist_ok=True)
    lines = ['# Package build and publication status', '',
             'Development feeds for validation only.' if state['branch'] == 'packages-dev' else 'Published distribution packages.', '',
             'Build badges describe the latest requested build. A failed rebuild leaves the previous published feed available.', '',
             '| Distribution | Release | Architecture | Latest build | Published versions | Published UTC | Feed |',
             '| --- | --- | --- | --- | --- | --- | --- |']
    colors = {'queued': '#777', 'running': '#007ec6', 'passed': '#4c1', 'failed': '#e05d44',
              'cancelled': '#777', 'superseded': '#dfb317', 'publication failed': '#e05d44'}
    for key, item in sorted(state['targets'].items()):
        row, status = item['target'], item['status']
        badge = f'<svg xmlns="http://www.w3.org/2000/svg" width="170" height="20" role="img" aria-label="{escape(status)}"><rect width="170" height="20" rx="3" fill="{colors[status]}"/><text x="85" y="14" text-anchor="middle" fill="white" font-family="Verdana,sans-serif" font-size="11">{escape(status)}</text></svg>\n'
        (badges / f'{key}.svg').write_text(badge)
        info, feed = published(root, row)
        versions = info.get('versions', {})
        label = ' · '.join(f'{name} `{version}`' for name, version in versions.items()) or ('revision ' + info['revision'] if info else 'Not published')
        date = info.get('published_at', '—')
        link = f'[Browse]({feed}/)' if info else '—'
        lines.append(f"| {row['distribution']} | {row['suite']} | {row['arch']} | [![{status}](status/{key}.svg)]({item['run_url']}) | {label} | {date} | {link} |")
    (root / 'STATUS.md').write_text('\n'.join(lines) + '\n')
    text = (ROOT / 'docs/package-repository.md').read_text()
    if state['branch'] == 'packages-dev':
        text = '> **Development feeds for validation only.** Installation guides below describe the production feeds.\n\n' + text
    (root / 'README.md').write_text(text + '\n\n[Build badges and published versions](STATUS.md)\n')


def update(state, row, generation, status, attempt):
    previous = state['targets'].get(row['id'], {})
    order = (int(generation['revision']), attempt)
    if order < (int(previous.get('revision', 0)), previous.get('attempt', 0)):
        return
    state['targets'][row['id']] = dict(target=row, revision=generation['revision'], attempt=attempt,
                                      run_id=generation['run_id'], run_url=generation['run_url'], status=status)


def allocate(root, bundle, state, context):
    unchanged(bundle)
    run_id = context['run_id']
    rows = read(bundle / 'targets.json')
    generation = state['runs'].get(run_id)
    if generation:
        if generation['context'] != context or generation['sources'] != read(bundle / 'sources.json') or generation['targets'] != rows:
            raise RuntimeError('A retry cannot change its captured sources or matrix')
    else:
        maximum = max([int(g['revision']) for g in state['runs'].values()] + [0])
        for manifest in root.rglob('build.json'):
            maximum = max(maximum, int(read(manifest)['revision']))
        generation = dict(revision=str(maximum + 1), context=context, sources=read(bundle / 'sources.json'),
                          targets=rows, run_id=run_id, run_url=context['run_url'])
        state['runs'][run_id] = generation
    for row in rows:
        previous = state['targets'].get(row['id'], {})
        attempt = int(os.environ.get('GITHUB_RUN_ATTEMPT', '1'))
        if previous.get('run_id') != run_id or previous.get('attempt', 0) < attempt:
            update(state, row, generation, 'queued', attempt)
    return generation['revision']


def publish(root, bundle, incoming, row, generation):
    manifests = list(incoming.rglob('build.json'))
    if len(manifests) != 1:
        raise RuntimeError('A publisher must receive exactly one target artifact')
    metadata = read(manifests[0])
    if (metadata['revision'] != generation['revision'] or metadata['sources'] != generation['sources']
            or metadata['context'] != generation['context']):
        raise RuntimeError('Artifact does not belong to this build generation')
    if row['family'] == 'openwrt':
        expected = incoming / 'openwrt' / row['suite'] / row['arch'] / 'build.json'
    elif row['family'] == 'raspberrypi':
        expected = incoming / 'raspberrypios' / row['suite'] / row['arch'] / 'build.json'
    else:
        expected = incoming / 'linux' / row['distribution'] / row['suite'] / row['arch'] / 'build.json'
    if manifests[0] != expected:
        raise RuntimeError('Artifact belongs to a different target')
    if row['family'] == 'openwrt':
        importlib.import_module('repository').publish(incoming, root, bundle)
    elif row['family'] == 'raspberrypi':
        importlib.import_module('apt-repository').publish(incoming, root, bundle)
    else:
        importlib.import_module('linux').publish(incoming, root, bundle)
    info, directory = published(root, row)
    if 'published_at' not in info:
        info['published_at'] = datetime.now(timezone.utc).isoformat()
        manifest = root / directory / 'build.json'
        aggregate = read(manifest)
        if 'targets' in aggregate:
            aggregate['targets'][row['arch']] = info
        else:
            aggregate = info
        write(manifest, aggregate)
    shutil.copytree(ROOT / 'ci/keys', root / 'keys', dirs_exist_ok=True)
    importlib.import_module('cleanup').cleanup(root)


def reconcile(state, run_id, attempt):
    generation = state['runs'].get(run_id)
    if not generation:
        return
    repository = os.environ['GITHUB_REPOSITORY']
    details = json.loads(run('gh', 'api', f'repos/{repository}/actions/runs/{run_id}'))
    if details['status'] != 'completed' or details['run_attempt'] != attempt:
        return
    for row in generation['targets']:
        latest = state['targets'].get(row['id'], {})
        if latest.get('run_id') == run_id and latest['status'] in {'queued', 'running'}:
            update(state, row, generation, 'cancelled' if details['conclusion'] == 'cancelled' else 'failed', attempt)


def main():
    command, *args = sys.argv[1:]
    if command == 'matrix':
        print(json.dumps({'include': targets(args[0])}))
        return
    root, bundle = (Path(p).resolve() for p in args[:2])
    if command == 'cleanup':
        state = read(root / 'status.json')
        if state['branch'] != 'packages-dev':
            raise RuntimeError('Development cleanup may only update packages-dev')
        if any(root.rglob('build.json')):
            importlib.import_module('cleanup').cleanup(root)
        render(root, state)
        return
    context = read(bundle / 'context.json')
    branch = context['destination']
    if branch != 'packages-dev':
        raise RuntimeError('Development writer may only update packages-dev')
    state = read(root / 'status.json', dict(branch=branch, runs={}, targets={}))
    if state['branch'] != branch:
        raise RuntimeError('Publication destination mismatch')
    result = 0
    if command == 'allocate':
        revision = allocate(root, bundle, state, context)
        with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
            output.write(f'revision={revision}\n')
    elif command == 'reconcile':
        reconcile(state, context['run_id'], int(os.environ['RECONCILE_ATTEMPT']))
    else:
        row = json.loads(args[2])
        generation = state['runs'][context['run_id']]
        if row not in generation['targets']:
            raise RuntimeError('Unknown publication target')
        status = args[3]
        if status not in {'running', 'success', 'failure', 'cancelled', 'skipped'}:
            raise ValueError('Unknown job status')
        if command == 'finish' and status == 'success':
            try:
                publish(root, bundle, Path(args[4]).resolve(), row, generation)
                status = 'passed'
            except Exception as error:
                print(f'Publication rejected: {error}', file=sys.stderr)
                # Restore the checkout before recording failure; a partial local
                # assembly must never be pushed by the status update.
                run('git', '-C', str(root), 'reset', '--hard', 'HEAD')
                run('git', '-C', str(root), 'clean', '-fd')
                status = 'superseded' if 'superseded' in str(error).lower() else 'publication failed'
                result = 1
        elif command == 'finish':
            status = 'cancelled' if status == 'cancelled' else 'failed'
        update(state, row, generation, status, int(os.environ.get('GITHUB_RUN_ATTEMPT', '1')))
    write(root / 'status.json', state)
    render(root, state)
    sys.exit(result)


if __name__ == '__main__':
    main()
