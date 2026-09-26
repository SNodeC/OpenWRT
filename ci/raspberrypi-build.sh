#!/usr/bin/env bash
# Runs inside an official Raspberry Pi OS rootfs on a native ARM64 runner.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
cd /work
apt-get update
apt-get install -y build-essential cmake ninja-build pkg-config git ca-certificates adduser libbluetooth-dev \
    libmagic-dev libmariadb-dev libssl-dev libncurses-dev nlohmann-json3-dev file
mkdir -p sources packages
for project in snode.c mqttsuite; do
    mkdir "sources/$project"
    tar -xzf bundle/"$project"-*.tar.gz --strip-components=1 -C "sources/$project"
done
cmake -S sources/snode.c -B build-snodec -G Ninja \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr \
    -DCMAKE_INSTALL_LIBDIR=lib -DCMAKE_INSTALL_SYSCONFDIR=/etc \
    -DCMAKE_CXX_FLAGS=-march=armv8-a -DSNODEC_BUILD_TESTS=ON -DSNODEC_BUILD_APPS=ON \
    -DCPACK_PACKAGE_NAME=snodec -DSPDLOG_SYSTEM_INCLUDES=ON
cmake --build build-snodec --parallel 4
bash feed/ci/debian/postinst configure
ctest --test-dir build-snodec --output-on-failure
package() {
    local build=$1 version
    version=$(sed -n 's/^set(CPACK_PACKAGE_VERSION "\([^" ]*\)")/\1/p' "$build/CPackConfig.cmake")
    (cd "$build" && cpack -G DEB \
        -D "CPACK_PACKAGE_VERSION=$version-$PACKAGE_RELEASE~$SUITE" \
        -D CPACK_PROJECT_CONFIG_FILE=/work/feed/ci/debian-components.cmake \
        -D COMPONENT_OUTPUT=/work/packages)
    cp "$build"/_packages/*.deb packages/
}
package build-snodec
apt-get install -y /work/packages/*.deb
ldconfig
cmake -S sources/mqttsuite -B build-mqttsuite -G Ninja \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr \
    -DCMAKE_INSTALL_LIBDIR=lib -DCMAKE_INSTALL_SYSCONFDIR=/etc \
    -DCMAKE_CXX_FLAGS=-march=armv8-a
cmake --build build-mqttsuite --parallel 4
package build-mqttsuite
