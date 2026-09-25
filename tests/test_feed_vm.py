"""Boot clean OpenWrt images and install signed feeds before exercising real MQTT."""
from functools import partial
import gzip
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shlex
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'ci'))
from repository import fetch, run

output, series, arch = sys.argv[1:]
output = Path(output).resolve()
metadata = json.loads((output / 'releases' / series / arch / 'build.json').read_text())
vm = Path('vm').resolve()
vm.mkdir()
logs = vm / 'logs'
logs.mkdir()
target = 'x86/64' if arch == 'x86_64' else 'armsr/armv8'
base = f'https://downloads.openwrt.org/releases/{metadata["release"]}/targets/{target}/'
checksums = dict((name.lstrip('*'), digest) for digest, name in
                (line.split() for line in fetch(base + 'sha256sums').decode().splitlines()))
for suffix, local in [('generic-kernel.bin', 'kernel'), ('generic-ext4-rootfs.img.gz', 'rootfs.gz')]:
    name = next(name for name in checksums if name.endswith(suffix))
    data = fetch(base + name)
    assert hashlib.sha256(data).hexdigest() == checksums[name]
    (vm / local).write_bytes(data)
with gzip.open(vm / 'rootfs.gz', 'rb') as source, (vm / 'rootfs.img').open('wb') as target:
    shutil.copyfileobj(source, target)
with (vm / 'rootfs.img').open('ab') as image:
    image.truncate(2 * 1024**3)
# e2fsck exit 1 means errors were corrected; other failures must stop the test.
assert subprocess.run(['/usr/sbin/e2fsck', '-fy', str(vm / 'rootfs.img')]).returncode in (0, 1)
run('/usr/sbin/resize2fs', str(vm / 'rootfs.img'))
run('ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-f', str(vm / 'id_ed25519'))
(vm / 'network').write_text("""config interface 'loopback'
 option device 'lo'
 option proto 'static'
 option ipaddr '127.0.0.1'
 option netmask '255.0.0.0'
config interface 'lan'
 option device 'eth0'
 option proto 'static'
 option ipaddr '10.0.2.15'
 option netmask '255.255.255.0'
 option gateway '10.0.2.2'
 option dns '10.0.2.3'
""")
commands = f'''mkdir /etc/dropbear
write {vm}/id_ed25519.pub /etc/dropbear/authorized_keys
rm /etc/config/network
write {vm}/network /etc/config/network
'''
(vm / 'debugfs.commands').write_text(commands)
run('/usr/sbin/debugfs', '-w', '-f', str(vm / 'debugfs.commands'), str(vm / 'rootfs.img'))
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    ssh_port = sock.getsockname()[1]
ssh_args = ['ssh', '-i', str(vm / 'id_ed25519'), '-p', str(ssh_port),
            '-o', f'UserKnownHostsFile={vm}/known_hosts', '-o', 'StrictHostKeyChecking=accept-new',
            '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=3', 'root@127.0.0.1']


def ssh(command, check=True, data=None):
    result = subprocess.run(ssh_args + [command], input=data, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
    with (logs / 'guest.log').open('a') as log:
        log.write(f'$ {command}\n{result.stdout}\n')
    if check and result.returncode:
        raise RuntimeError(result.stdout)
    return result


def wait_for(command, needle, seconds=45):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        result = ssh(command, check=False)
        if result.returncode == 0 and needle in result.stdout:
            return result.stdout
        time.sleep(1)
    raise RuntimeError(f'Timed out: {command}\n{result.stdout}')


server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(output)))
threading.Thread(target=server.serve_forever, daemon=True).start()
qemu = (['qemu-system-x86_64', '-machine', 'q35', '-cpu', 'max'] if arch == 'x86_64' else
        ['qemu-system-aarch64', '-machine', 'virt', '-cpu', 'cortex-a53'])
qemu += ['-accel', 'tcg', '-smp', '2', '-m', '2048', '-kernel', str(vm / 'kernel'),
         '-append', 'console=' + ('ttyS0' if arch == 'x86_64' else 'ttyAMA0') + ' root=/dev/vda rootwait rw',
         '-drive', f'file={vm}/rootfs.img,if=virtio,format=raw',
         '-netdev', f'user,id=net0,hostfwd=tcp:127.0.0.1:{ssh_port}-:22',
         '-device', 'virtio-net-pci,netdev=net0', '-display', 'none', '-serial', f'file:{logs}/serial.log']
process = subprocess.Popen(qemu)
try:
    wait_for('echo ready', 'ready', 240)
    if arch == 'aarch64_cortex-a53':
        # The generic image does not advertise the explicitly emulated Cortex-A53.
        ssh("printf 'aarch64_cortex-a53\\n' >> /etc/apk/arch" if series != '24.10' else
            "echo 'arch aarch64_cortex-a53 20' >> /etc/opkg.conf")
    key = ROOT / 'ci/keys' / ('snodec-usign.pub' if series == '24.10' else 'snodec-apk.pem')
    if series == '24.10':
        ssh('cat > /tmp/snodec.pub', data=key.read_text())
        ssh('opkg-key add /tmp/snodec.pub')
    else:
        ssh('cat > /etc/apk/keys/snodec-apk.pem', data=key.read_text())
    url = f'http://10.0.2.2:{server.server_port}/releases/{series}/{arch}'
    if series == '24.10':
        ssh('cat > /etc/opkg/customfeeds.conf', data=f'src/gz snodec {url}\n')
        ssh('opkg update')
        ssh('opkg install ' + ' '.join(metadata['packages']))
    else:
        ssh('cat > /etc/apk/repositories.d/snodec.list', data=url + '/packages.adb\n')
        ssh('apk update')
        ssh('apk add ' + ' '.join(metadata['packages']))
    for app in ['mqttbroker', 'mqttbridge', 'mqttintegrator', 'mqttcli', 'mqttstore', 'snodec-control']:
        result = ssh(app + ' --help', check=False)
        assert result.returncode in (0, 2) and 'Usage:' in result.stdout, result.stdout
    run('openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '1',
        '-subj', '/CN=127.0.0.1', '-addext', 'subjectAltName=IP:127.0.0.1',
        '-keyout', str(vm / 'server.key'), '-out', str(vm / 'server.crt'))
    ssh('mkdir -p /root/tests /root/logs')
    for name in ['server.key', 'server.crt']:
        ssh('cat > /root/tests/' + name, data=(vm / name).read_text())
    config = 'log-level=5\n'
    for instance in ['in-mqtt', 'in-mqtts', 'in-http', 'in-https']:
        config += f'{instance}.socket.reuse-address=true\n'
    for instance in ['in-mqtts', 'in-https']:
        config += f'{instance}.tls.cert="/root/tests/server.crt"\n{instance}.tls.cert-key="/root/tests/server.key"\n'
    ssh('cat > /etc/snode.c/mqttbroker.conf', data=config)
    ssh('/etc/init.d/mqttbroker restart')
    wait_for('pidof mqttbroker', '', 30)
    results = []
    for protocol, instance, port, secure in [('tcp', 'in-mqtt', 1883, False), ('ws', 'in-wsmqtt', 8080, False),
                                             ('tls', 'in-mqtts', 8883, True), ('wss', 'in-wsmqtts', 8088, True)]:
        pid = None
        try:
            args = ['mqttcli', '--log-level=5', instance, '--disabled=false', 'remote', '--host', '127.0.0.1',
                    '--port', str(port), 'socket', '--retry=true', '--reconnect=false']
            if secure:
                args += ['tls', '--ca-cert', '/root/tests/server.crt']
            log = '/root/logs/' + protocol + '.log'
            topic, payload = 'ci/' + protocol, 'ci-' + protocol + '-ok'
            command = shlex.join(args + ['sub', '--topic', topic])
            pid = int(ssh(f'{command} </dev/null > {log} 2>&1 & echo $!').stdout.strip())
            wait_for('cat ' + log, '  r: 0')
            ssh(shlex.join(args + ['pub', '--topic', topic, '--message', payload]))
            received = wait_for('cat ' + log, payload)
            if protocol in ('ws', 'wss'):
                assert 'websocket established: subprotocol=mqtt' in received
            results.append(dict(protocol=protocol, passed=True))
        except Exception as error:
            results.append(dict(protocol=protocol, passed=False, error=str(error)))
        finally:
            if pid:
                ssh(f'kill -TERM {pid}', check=False)
    (logs / 'mqtt-results.json').write_text(json.dumps(results, indent=2))
    ssh('/etc/init.d/mqttbroker stop')
    assert ssh('pidof mqttbroker', check=False).returncode != 0
    ssh('/etc/init.d/mqttbroker start')
    wait_for('pidof mqttbroker', '')
    assert all(result['passed'] for result in results), results
finally:
    try:
        ssh('logread', check=False)
    finally:
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        server.shutdown()
