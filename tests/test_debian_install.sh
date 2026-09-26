#!/usr/bin/env bash
# Run inside a pristine official rootfs, using only the staged signed feed.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
suite=$1
phase=$2
install -m 644 /work/feed/ci/keys/snodec-apt.asc /etc/apt/keyrings/snodec.asc
echo "deb [arch=arm64 signed-by=/etc/apt/keyrings/snodec.asc] file:/work/output/raspberrypios $suite main" > /etc/apt/sources.list.d/snodec.list
apt-get update
apt-get install -y openssl python3 ca-certificates
if [ "$phase" = upgrade ]; then
    # Immutable first-release archives exercise upgrades from combined packages.
    python3 - "$suite" <<'PY'
import hashlib, json, pathlib, sys, urllib.request
for name, checksum in json.load(open('/work/feed/tests/debian-monolithic.json')).items():
    if name.startswith('pool/' + sys.argv[1] + '/'):
        data = urllib.request.urlopen('https://github.com/SNodeC/OpenWRT/releases/download/debian-upgrade-fixtures/' + pathlib.Path(name).name).read()
        assert hashlib.sha256(data).hexdigest() == checksum
        pathlib.Path('/tmp/' + pathlib.Path(name).name).write_bytes(data)
PY
    apt-get install -y /tmp/*.deb
else
    apt-get install -y mqttsuite-broker mqttsuite-cli
    for package in mqttsuite snodec mqttsuite-store mqttsuite-bridge mqttsuite-integrator; do
        test "$(dpkg-query -W -f='${db:Status-Status}' "$package" 2>/dev/null || true)" != installed
    done
    python3 /work/feed/tests/test_raspberrypi_runtime.py mqttbroker mqttcli
    cp /work/logs/results.json /work/logs/selective-results.json
fi
apt-get install -y snodec mqttsuite
ldconfig
python3 /work/feed/tests/test_raspberrypi_runtime.py
cp /work/logs/results.json "/work/logs/$phase-results.json"
python3 - <<'PY'
import pathlib, subprocess
for inventory in pathlib.Path('/work/packages').glob('*.packages'):
    for name in inventory.read_text().splitlines():
        assert subprocess.check_output(['dpkg-query', '-W', '-f=${db:Status-Status}', name], text=True) == 'installed', name
for name in ['snodec', 'mqttsuite']:
    assert '/usr/' not in subprocess.check_output(['dpkg-query', '-L', name], text=True), name
PY
