#!/usr/bin/env bash
set -euo pipefail
row=$1
readarray -t fields < <(python3 - "$row" <<'PY'
import json, sys
row = json.loads(sys.argv[1])
for key in ['distribution', 'suite', 'arch', 'platform', 'image']:
    print(row[key])
PY
)
export DISTRIBUTION=${fields[0]} SUITE=${fields[1]} ARCH=${fields[2]}
platform=${fields[3]}
image=${fields[4]}
mkdir -p packages output logs
docker pull --platform "$platform" "$image"
container=(docker run --rm --platform "$platform" -v "$PWD:/work" -w /work
    -e DISTRIBUTION -e SUITE -e ARCH -e PACKAGE_RELEASE)
"${container[@]}" "$image" bash /work/feed/ci/package-build.sh 2>&1 | tee logs/build.log
sudo chown -R "$(id -u):$(id -g)" packages
python3 feed/ci/linux.py stage "$row" packages bundle output
export REPOSITORY="/work/output/linux/$DISTRIBUTION/$SUITE/$ARCH"
if [ "$DISTRIBUTION" = debian ] || [ "$DISTRIBUTION" = ubuntu ]; then
    "${container[@]}" -e REPOSITORY "$image" bash /work/feed/tests/test_debian_install.sh "$SUITE" test 2>&1 | tee logs/install.log
else
    "${container[@]}" -e REPOSITORY "$image" bash /work/feed/tests/test_rpm_install.sh 2>&1 | tee logs/install.log
fi
sudo chown -R "$(id -u):$(id -g)" output logs
