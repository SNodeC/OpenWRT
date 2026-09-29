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
# Archives include submodules and come from the captured tag pair.
mkdir -p dl
for package in snode.c mqttsuite; do
    cp "$bundle/$package-"*.tar.gz dl/
done
export SNODEC_PACKAGE_RELEASE="$PACKAGE_RELEASE" MQTTSUITE_PACKAGE_RELEASE="$PACKAGE_RELEASE"
SNODEC_SOURCE_TAG=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["source_tags"]["snode.c"])' "$bundle/context.json")
MQTTSUITE_SOURCE_TAG=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["source_tags"]["mqttsuite"])' "$bundle/context.json")
SNODEC_SOURCE_HASH=$(sha256sum "$bundle/snode.c-"*.tar.gz | cut -d' ' -f1)
MQTTSUITE_SOURCE_HASH=$(sha256sum "$bundle/mqttsuite-"*.tar.gz | cut -d' ' -f1)
SNODEC_PACKAGE_VERSION=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["versions"]["snode.c"])' "$bundle/context.json")
MQTTSUITE_PACKAGE_VERSION=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["versions"]["mqttsuite"])' "$bundle/context.json")
export SNODEC_SOURCE_TAG MQTTSUITE_SOURCE_TAG SNODEC_SOURCE_HASH MQTTSUITE_SOURCE_HASH SNODEC_PACKAGE_VERSION MQTTSUITE_PACKAGE_VERSION
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
if [ "${RELEASE_PROJECT:-}" != mqttsuite ]; then
    make -j"$(nproc)" package/snode.c/compile V=s BUILD_LOG=1
    python3 "$feed/tests/test_upstream.py" "$sdk"
fi
python3 "$feed/ci/repository.py" sdk-dependency "$sdk" "$bundle" "$feed/../dependencies"
# SNode.C is either built above or restored from its published development files.
# Keep all other dependencies under the SDK's normal dependency graph.
make -j"$(nproc)" MAKE="make -o package/feeds/snodec/snode.c/compile" package/mqttsuite/compile V=s BUILD_LOG=1
arch=$(sed -n 's/^CONFIG_TARGET_ARCH_PACKAGES="\(.*\)"/\1/p' .config)
repository="bin/packages/$arch/snodec"
if [ "${RELEASE_PROJECT:-}" = mqttsuite ]; then
    find "$feed/../dependencies" -maxdepth 1 -type f \( -name '*.ipk' -o -name '*.apk' \) -exec cp -t "$repository" {} +
fi
make package/index V=s
if [ -f "$repository/packages.adb" ]; then
    staging_dir/host/bin/apk verify --keys-dir "$feed/ci/keys" "$repository/packages.adb"
else
    staging_dir/host/bin/usign -V -p "$feed/ci/keys/snodec-usign.pub" \
        -m "$repository/Packages" -x "$repository/Packages.sig"
fi
python3 "$feed/ci/repository.py" check "$bundle"
