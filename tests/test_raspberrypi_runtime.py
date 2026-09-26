"""Exercise installed .debs in a pristine official Raspberry Pi OS rootfs."""
import json
from pathlib import Path
import subprocess
import time

logs = Path('/work/logs')


def wait_for(path, needle):
    deadline = time.monotonic() + 40
    while time.monotonic() < deadline:
        text = path.read_text()
        if needle in text:
            return text
        time.sleep(0.2)
    raise AssertionError(f'{needle!r} missing from {path}:\n{path.read_text()}')


results = []
for app in ['mqttbroker', 'mqttbridge', 'mqttintegrator', 'mqttcli', 'mqttstore', 'snodec-control']:
    result = subprocess.run([app, '--help'], capture_output=True, text=True)
    results.append(dict(test=app, passed=result.returncode in (0, 2) and 'Usage:' in result.stdout))
subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '1',
                '-subj', '/CN=127.0.0.1', '-addext', 'subjectAltName=IP:127.0.0.1',
                '-keyout', '/tmp/server.key', '-out', '/tmp/server.crt'], check=True)
config = 'log-level=5\n'
for instance in ['in-mqtt', 'in-mqtts', 'in-http', 'in-https']:
    config += f'{instance}.socket.reuse-address=true\n'
for instance in ['in-mqtts', 'in-https']:
    config += f'{instance}.tls.cert="/tmp/server.crt"\n{instance}.tls.cert-key="/tmp/server.key"\n'
Path('/etc/snode.c').mkdir(exist_ok=True)
Path('/etc/snode.c/mqttbroker.conf').write_text(config)
with (logs / 'broker.log').open('w') as broker_log:
    broker = subprocess.Popen(['mqttbroker', '--daemonize=false', '--quiet=false', '--enforce-log-file=false'],
                              stdout=broker_log, stderr=subprocess.STDOUT)
    try:
        for protocol, instance, port, secure in [('tcp', 'in-mqtt', 1883, False), ('ws', 'in-wsmqtt', 8080, False),
                                                ('tls', 'in-mqtts', 8883, True), ('wss', 'in-wsmqtts', 8088, True)]:
            subscriber = None
            try:
                args = ['mqttcli', '--log-level=5', instance, '--disabled=false', 'remote', '--host', '127.0.0.1',
                        '--port', str(port), 'socket', '--retry=true', '--reconnect=false']
                if secure:
                    args += ['tls', '--ca-cert', '/tmp/server.crt']
                topic, payload = 'ci/' + protocol, 'raspberrypi-' + protocol + '-ok'
                path = logs / (protocol + '.log')
                with path.open('w') as output:
                    subscriber = subprocess.Popen(args + ['sub', '--topic', topic], stdout=output,
                                                  stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
                    wait_for(path, '  r: 0')
                    subprocess.run(args + ['pub', '--topic', topic, '--message', payload], check=True, timeout=30)
                    received = wait_for(path, payload)
                    if protocol in ('ws', 'wss'):
                        assert 'websocket established: subprotocol=mqtt' in received
                results.append(dict(test=protocol, passed=True))
            except Exception as error:
                results.append(dict(test=protocol, passed=False, error=str(error)))
            finally:
                if subscriber:
                    subscriber.terminate()
                    subscriber.wait(timeout=10)
    finally:
        broker.terminate()
        broker.wait(timeout=10)
(logs / 'results.json').write_text(json.dumps(results, indent=2))
assert all(result['passed'] for result in results), results
