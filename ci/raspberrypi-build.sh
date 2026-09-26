#!/usr/bin/env bash
# Runs inside an official Raspberry Pi OS rootfs on a native ARM64 runner.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
cd /work
apt-get update
apt-get install -y build-essential cmake ninja-build pkg-config libbluetooth-dev \
    libmagic-dev libmariadb-dev libssl-dev libncurses-dev nlohmann-json3-dev file
mkdir -p sources packages
for project in snode.c mqttsuite; do
    mkdir "sources/$project"
    tar -xzf bundle/"$project"-*.tar.gz --strip-components=1 -C "sources/$project"
done
cmake -S sources/snode.c -B build-snodec -G Ninja \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr \
    -DCMAKE_INSTALL_LIBDIR=lib/aarch64-linux-gnu -DCMAKE_INSTALL_SYSCONFDIR=/etc \
    -DCMAKE_CXX_FLAGS=-march=armv8-a -DSNODEC_BUILD_TESTS=ON -DSNODEC_BUILD_APPS=ON \
    -DCPACK_PACKAGE_NAME=snodec -DSPDLOG_SYSTEM_INCLUDES=ON
cmake --build build-snodec --parallel 4
ctest --test-dir build-snodec --output-on-failure
snodec_version=$(sed -n 's/^set(CPACK_PACKAGE_VERSION "\([^"]*\)")/\1/p' build-snodec/CPackConfig.cmake)
snodec_version="$snodec_version-$PACKAGE_RELEASE~$SUITE"
(cd build-snodec && cpack -G DEB -D CPACK_DEB_COMPONENT_INSTALL=OFF \
    -D "CPACK_PACKAGE_VERSION=$snodec_version" -D CPACK_DEBIAN_PACKAGE_ARCHITECTURE=arm64)
cp build-snodec/_packages/*.deb packages/
apt-get install -y /work/packages/*.deb
ldconfig
cmake -S sources/mqttsuite -B build-mqttsuite -G Ninja \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr \
    -DCMAKE_INSTALL_LIBDIR=lib/aarch64-linux-gnu -DCMAKE_INSTALL_SYSCONFDIR=/etc \
    -DCMAKE_CXX_FLAGS=-march=armv8-a
cmake --build build-mqttsuite --parallel 4
mqtt_version=$(sed -n 's/^PKG_VERSION:=//p' feed/net/mqttsuite/Makefile)
mkdir package-mqttsuite
(cd package-mqttsuite && cmake -DBUILD=/work/build-mqttsuite \
    -D "VERSION=$mqtt_version-$PACKAGE_RELEASE~$SUITE" -D "SNODEC_VERSION=$snodec_version" \
    -P /work/feed/ci/mqttsuite-deb.cmake && cpack)
cp package-mqttsuite/*.deb packages/
