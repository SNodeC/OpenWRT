"""One serialized writer for per-target publications and their displayed status."""
from datetime import datetime, timezone
from html import escape
import importlib
import json
import os
from pathlib import Path
import shutil
import sys

from repository import ROOT, matrix, linux_matrix, unchanged, run, select, snodec_file, digest


def targets():
    rows = [dict(family='openwrt', distribution='openwrt', suite=r['series'], arch=r['arch'],
                 runner='ubuntu-24.04', build=r) for r in matrix()]
    rows += [dict(family='raspberrypi', distribution='raspberrypios', suite=suite, arch='arm64',
                  runner='ubuntu-24.04-arm', build=dict(suite=suite))
             for suite in json.loads((ROOT / 'ci/raspberrypi.json').read_text())]
    rows += [dict(family='linux', distribution=r['distribution'], suite=r['suite'], arch=r['arch'],
                  runner=r['runner'], build=r) for r in linux_matrix()]
    for row in rows:
        row['id'] = '-'.join(row[k] for k in ('distribution', 'suite', 'arch'))
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
    sections = {}
    colors = {'queued': '#57606a', 'running': '#0969da', 'passed': '#1a7f37', 'failed': '#cf222e',
              'cancelled': '#57606a', 'superseded': '#9a6700', 'publication failed': '#cf222e', 'not built': '#57606a'}
    for row in targets():
        item = state['targets'].get(row['id'], {})
        status = item.get('status', 'not built')
        width = len(status) * 7 + 16
        (badges / f"{row['id']}.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20" role="img" aria-label="{escape(status)}"><rect width="{width}" height="20" rx="3" fill="{colors[status]}"/><text x="{width / 2}" y="14" text-anchor="middle" fill="white" font-family="Verdana,sans-serif" font-size="11">{escape(status)}</text></svg>\n')
        info, feed = published(root, row)
        versions = info.get('versions', {})
        snodec = versions.get('snodec', versions.get('snode.c'))
        version_cells = ' | '.join(f'`{version}`' if version else '—' for version in (snodec, versions.get('mqttsuite')))
        date = f"[{info['published_at'][:10]}]({feed}/build.json)" if info.get('published_at') else '—'
        packages = f"{row['distribution']}/pool/{row['suite']}" if row['distribution'] in {'debian', 'ubuntu', 'raspberrypios'} else f'{feed}/Packages' if row['distribution'] in {'rocky', 'fedora'} else feed
        links = f'[Packages]({packages}/) · [Build]({feed}/build.json)' if info else '—'
        badge = f"![{status}](status/{row['id']}.svg)"
        badge = f"[{badge}]({item['run_url']})" if item.get('run_url') else badge
        sections.setdefault(row['distribution'], {}).setdefault(row['suite'], []).append(f"| `{row['arch']}` | {badge} | {version_cells} | {date} | {links} |")
    text = (ROOT / 'docs/package-repository.md').read_text()
    for distribution, suites in sections.items():
        tables = [f'### {suite}\n\n| Architecture | Result | SNode.C | MQTTSuite | Published | Repository |\n| --- | --- | --- | --- | --- | --- |\n' + '\n'.join(lines) for suite, lines in suites.items()]
        text = text.replace(f'<!-- targets:{distribution} -->', '\n\n'.join(tables))
    (root / 'README.md').write_text(text)
    (root / 'STATUS.md').unlink(missing_ok=True)


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
        if (generation['context'] != context or generation['sources'] != read(bundle / 'sources.json')
                or generation['targets'] != rows or generation['profiles_hash'] != digest(bundle / 'profiles.json')):
            raise RuntimeError('A retry cannot change its captured sources or matrix')
    else:
        maximum = max([int(g['revision']) for g in state['runs'].values()] + [0])
        for manifest in root.rglob('build.json'):
            maximum = max(maximum, int(read(manifest)['revision']))
        generation = dict(revision=str(maximum + 1), context=context, sources=read(bundle / 'sources.json'),
                          targets=rows, profiles_hash=digest(bundle / 'profiles.json'), run_id=run_id, run_url=context['run_url'])
        state['runs'][run_id] = generation
    for row in rows:
        previous = state['targets'].get(row['id'], {})
        attempt = int(os.environ.get('GITHUB_RUN_ATTEMPT', '1'))
        if previous.get('run_id') != run_id or previous.get('attempt', 0) < attempt:
            update(state, row, generation, 'queued', attempt)
    return generation['revision']


def publish(root, bundle, incoming, row, generation):
    profile = read(bundle / 'profiles.json')[row['id']]
    if digest(bundle / 'profiles.json') != generation['profiles_hash']:
        raise RuntimeError('Target source selection changed')
    if 'baseline' in profile:
        current, _ = published(root, row)
        old = profile['baseline']
        dependency_files = lambda info: {k: v for k, v in info.get('files', {}).items()
                                         if snodec_file(k)}
        if (current.get('sources', {}).get('snode.c') != old['sources']['snode.c']
                or dependency_files(current) != dependency_files(old)):
            raise RuntimeError('Superseded build: published SNode.C dependency changed')
    select(bundle, row['id'])
    manifests = list(incoming.rglob('build.json'))
    if len(manifests) != 1:
        raise RuntimeError('A publisher must receive exactly one target artifact')
    metadata = read(manifests[0])
    if 'baseline' in profile and dependency_files(metadata) != dependency_files(profile['baseline']):
        raise RuntimeError('Artifact changed the published SNode.C packages')
    if (metadata['revision'] != generation['revision'] or metadata['sources'] != profile['sources']
            or metadata['context'] != profile['context']):
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
    endpoint = f'repos/{os.environ["GITHUB_REPOSITORY"]}/actions/runs/{run_id}'
    details = json.loads(run('gh', 'api', endpoint))
    if details['run_attempt'] != attempt:
        return
    lines = run('gh', 'api', '--paginate', f'{endpoint}/attempts/{attempt}/jobs?per_page=100', '--jq', '.jobs[] | [.name, .status] | @json')
    jobs = {name.rsplit(' / ', 1)[-1]: status for name, status in map(json.loads, lines.splitlines())}
    for row in generation['targets']:
        latest = state['targets'].get(row['id'], {})
        if latest.get('run_id') == run_id and latest['status'] in {'queued', 'running'}:
            status = 'running' if jobs.get(f'Build and test {row["id"]}') in {'in_progress', 'completed'} else 'queued'
            if details['status'] == 'completed':
                status = 'cancelled' if details['conclusion'] == 'cancelled' else 'failed'
            update(state, row, generation, status, attempt)


def main():
    command, *args = sys.argv[1:]
    if command == 'matrix':
        print(json.dumps({'include': targets()}))
        return
    root, bundle = (Path(p).resolve() for p in args[:2])
    state = read(root / 'status.json', dict(branch='packages', runs={}, targets={}))
    if state['branch'] != 'packages':
        raise RuntimeError('Publication destination mismatch')
    if command == 'cleanup':
        if any(root.rglob('build.json')):
            importlib.import_module('cleanup').cleanup(root)
        render(root, state)
        return
    context = read(bundle / 'context.json')
    if context['destination'] != state['branch']:
        raise RuntimeError('Publication destination mismatch')
    result = 0
    if command == 'allocate':
        revision = allocate(root, bundle, state, context)
        with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
            output.write(f'revision={revision}\n')
    elif command == 'reconcile':
        reconcile(state, context['run_id'], int(os.environ['RECONCILE_ATTEMPT']))
    elif command == 'finish':
        try:
            reconcile(state, context['run_id'], int(os.environ.get('GITHUB_RUN_ATTEMPT', '1')))
        except Exception as error:
            print(f'Status refresh unavailable; keeping recorded results: {error}', file=sys.stderr)
        row = json.loads(args[2])
        generation = state['runs'][context['run_id']]
        if row not in generation['targets']:
            raise RuntimeError('Unknown publication target')
        status = args[3]
        if status not in {'success', 'failure', 'cancelled', 'skipped'}:
            raise ValueError('Unknown job status')
        if status == 'success':
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
        else:
            status = 'cancelled' if status == 'cancelled' else 'failed'
        update(state, row, generation, status, int(os.environ.get('GITHUB_RUN_ATTEMPT', '1')))
    else:
        raise ValueError(f'Unknown publication operation: {command}')
    write(root / 'status.json', state)
    render(root, state)
    sys.exit(result)


if __name__ == '__main__':
    main()
