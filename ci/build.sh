#!/usr/bin/env bash
set -euo pipefail
feed=$(realpath "$1")
bundle=$(realpath "$2")
sdk=$(realpath "$3")
: "${PACKAGE_RELEASE:?}" "${OPENWRT_USIGN_KEY:?}" "${OPENWRT_APK_KEY:?}"
python3 "$feed/ci/repository.py" check "$bundle"
cd "$sdk"
umask 077
printf '%s\n' "$OPENWRT_USIGN_KEY" > key-build
printf '%s\n' "$OPENWRT_APK_KEY" > private-key.pem
unset OPENWRT_USIGN_KEY OPENWRT_APK_KEY
trap 'rm -f key-build private-key.pem' EXIT
umask 022
cp "$feed/ci/keys/snodec-usign.pub" key-build.pub
cp "$feed/ci/keys/snodec-apk.pem" public-key.pem
# These archives were made from fresh OpenWRT-tag checkouts, including submodules.
mkdir -p dl
# Bind disposable recipes to the shared archives; source refs stay OpenWRT.
for package in snode.c mqttsuite; do
    cp "$bundle/$package-"*.tar.gz dl/
    sed -i "s/^PKG_RELEASE:=.*/PKG_RELEASE:=$PACKAGE_RELEASE\nPKG_MIRROR_HASH:=$(sha256sum "$bundle/$package-"*.tar.gz | cut -d' ' -f1)/; /^PKG_MIRROR_HASH:=/d" "$feed/net/$package/Makefile"
done
cp feeds.conf.default feeds.conf
printf '\nsrc-link snodec %s\n' "$feed" >> feeds.conf
./scripts/feeds update base packages snodec
./scripts/feeds install -a -p snodec
# Select publication packages; feature defaults come from their Config.in files.
cat > .config <<'EOF'
# CONFIG_ALL is not set
# CONFIG_ALL_NONSHARED is not set
# CONFIG_ALL_KMODS is not set
# CONFIG_AUTOREMOVE is not set
CONFIG_SIGNED_PACKAGES=y
CONFIG_PACKAGE_snode.c-full=m
CONFIG_PACKAGE_snode.c-apps=m
CONFIG_PACKAGE_snode.c-control=m
CONFIG_PACKAGE_mqttsuite-full=m
EOF
make defconfig
make -j"$(nproc)" package/mqttsuite/compile V=s BUILD_LOG=1
python3 "$feed/tests/test_upstream.py" "$sdk"
make package/index V=s
arch=$(sed -n 's/^CONFIG_TARGET_ARCH_PACKAGES="\(.*\)"/\1/p' .config)
repository="bin/packages/$arch/snodec"
if [ -f "$repository/packages.adb" ]; then
    staging_dir/host/bin/apk verify --keys-dir "$feed/ci/keys" "$repository/packages.adb"
else
    staging_dir/host/bin/usign -V -p "$feed/ci/keys/snodec-usign.pub" \
        -m "$repository/Packages" -x "$repository/Packages.sig"
fi
python3 "$feed/ci/repository.py" check "$bundle"
