#!/usr/bin/env bash
# Runs inside the target distribution, natively or under QEMU.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
cd /work
case "${DISTRIBUTION:-raspberrypios}" in
    raspberrypios|debian|ubuntu)
        format=DEB
        libdir=lib
        apt-get update
        apt-get install -y build-essential cmake ninja-build pkg-config git ca-certificates adduser libbluetooth-dev \
            libmagic-dev libmariadb-dev libssl-dev libncurses-dev nlohmann-json3-dev file
        bash feed/ci/debian/postinst configure
        ;;
    rocky|fedora)
        format=RPM
        libdir=lib64
        if [ "$DISTRIBUTION" = rocky ]; then
            dnf install -y dnf-plugins-core epel-release
            dnf config-manager --set-enabled crb
        fi
        dnf install -y gcc gcc-c++ cmake ninja-build make pkgconf-pkg-config git ca-certificates \
            bluez-libs-devel file-devel mariadb-connector-c-devel openssl-devel ncurses-devel \
            json-devel file rpm-build shadow-utils
        if [ "$DISTRIBUTION:$SUITE" = rocky:9 ]; then
            dnf install -y gcc-toolset-14-gcc-c++
            source /opt/rh/gcc-toolset-14/enable
        fi
        bash feed/ci/rpm/postinst
        ;;
esac
mkdir -p sources packages
for project in snode.c mqttsuite; do
    mkdir "sources/$project"
    tar -xzf bundle/"$project"-*.tar.gz --strip-components=1 -C "sources/$project"
done
cmake -S sources/snode.c -B build-snodec -G Ninja \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr \
    -DCMAKE_INSTALL_LIBDIR="$libdir" -DCMAKE_INSTALL_SYSCONFDIR=/etc \
    -DSNODEC_BUILD_TESTS=ON -DSNODEC_BUILD_APPS=ON \
    -DCPACK_PACKAGE_NAME=snodec -DSPDLOG_SYSTEM_INCLUDES=ON
cmake --build build-snodec --parallel 4
ctest --test-dir build-snodec --output-on-failure
package() {
    local build=$1 version
    version=$(sed -n 's/^set(CPACK_PACKAGE_VERSION "\([^" ]*\)")/\1/p' "$build/CPackConfig.cmake")
    local options=()
    if [ "$format" = DEB ]; then
        options=(-D "CPACK_PACKAGE_VERSION=$version-$PACKAGE_RELEASE~$SUITE")
    else
        local suffix=fc
        [ "$DISTRIBUTION" != rocky ] || suffix=el
        options=(-D "CPACK_RPM_PACKAGE_RELEASE=$PACKAGE_RELEASE.$suffix$SUITE")
    fi
    (cd "$build" && cpack -G "$format" "${options[@]}" \
        -D CPACK_PROJECT_CONFIG_FILE=/work/feed/ci/components.cmake \
        -D COMPONENT_OUTPUT=/work/packages)
    cp "$build"/_packages/*."${format,,}" packages/
}
package build-snodec
if [ "$format" = DEB ]; then
    apt-get install -y /work/packages/*.deb
else
    dnf install -y /work/packages/*.rpm
fi
ldconfig
cmake -S sources/mqttsuite -B build-mqttsuite -G Ninja \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr \
    -DCMAKE_INSTALL_LIBDIR="$libdir" -DCMAKE_INSTALL_SYSCONFDIR=/etc
cmake --build build-mqttsuite --parallel 4
package build-mqttsuite
