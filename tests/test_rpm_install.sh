#!/usr/bin/env bash
# A pristine distribution container installs only from signed repositories.
set -euo pipefail
if [ "$DISTRIBUTION" = rocky ]; then
    dnf install -y dnf-plugins-core epel-release
    dnf config-manager --set-enabled crb
fi
rpm --import /work/feed/ci/keys/snodec-apt.asc
cat > /etc/yum.repos.d/snodec.repo <<REPO
[snodec]
name=SNode.C and MQTTSuite
baseurl=file://$REPOSITORY/$DISTRIBUTION/$SUITE/$ARCH
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=file:///work/feed/ci/keys/snodec-apt.asc
REPO
dnf install -y openssl python3 mqttsuite-broker mqttsuite-cli
for package in mqttsuite snodec mqttsuite-store mqttsuite-bridge mqttsuite-integrator; do
    if rpm -q "$package"; then echo "Unexpected full installation: $package" >&2; exit 1; fi
done
ldconfig
python3 /work/feed/tests/test_package_runtime.py mqttbroker mqttcli
cp /work/logs/results.json /work/logs/selective-results.json
dnf install -y snodec mqttsuite
ldconfig
python3 /work/feed/tests/test_package_runtime.py
cp /work/logs/results.json /work/logs/full-results.json
while read -r package; do rpm -q "$package"; done < <(cat /work/packages/*.packages)
for package in snodec mqttsuite; do
    if rpm -ql "$package" | grep -q '^/usr/'; then echo "Metapackage owns files" >&2; exit 1; fi
done
