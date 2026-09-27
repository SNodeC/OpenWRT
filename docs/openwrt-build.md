# SNode.C and MQTTSuite for GL-MT3000

These recipes use the movable `OpenWRT` tag in both source repositories:
SNode.C 2.0.0 and MQTTSuite 1.0.1. All integration patches live in the OpenWrt recipes; the source
repositories are not modified.

The build uses the official OpenWrt 25.12.5 `mediatek/filogic` SDK with GCC
14.3.0 and musl, producing `aarch64_cortex-a53` APK packages. The release's
`glinet_gl-mt3000` profile identifies this target. These packages require the
matching OpenWrt userspace and, for Bluetooth dependencies, matching kernel
ABI. They are not a claim of compatibility with GL.iNet's vendor firmware or
with an older OpenWrt release using opkg/IPK.

SDK: <https://downloads.openwrt.org/releases/25.12.5/targets/mediatek/filogic/>

Archive: `openwrt-sdk-25.12.5-mediatek-filogic_gcc-14.3.0_musl.Linux-x86_64.tar.zst`

SHA256: `ff4a38a397caa2cfe1c39e18f84ddede14878221b3593c3f2c4cfe24e3ec4c25`

## Branch ownership

The tag-triggered multi-platform CI and signed binary feed are described in
[Package repository](package-repository.md). The device-specific steps below
remain useful for local SDK validation; CI builds both release series for all
platforms listed in `ci/platforms.json`.

| Branch | Files maintained there |
| --- | --- |
| `SNode.C` | `net/snode.c/`, `docs/snodec-package-options.md` |
| `MQTTSuite` | `net/mqttsuite/`, `docs/mqttsuite-package-options.md` |
| `main` | Shared build/verification documents, package inventory index and upstream test runner |
| `infra` | Build, publishing and deployment orchestration |

Merge project branches separately into `main`. Do not merge all of `main`
back into a project branch: that would bring in the other recipe.

## Package selection

Use **Network / SNode.C** and **Network / MQTTSuite** in `make menuconfig`.
OpenWrt generates a `CONFIG_PACKAGE_<package>` tristate for each package in
these recipes. `m` builds an installable package; `y` also selects it for an
image build; `n` omits it unless a selected consumer requires it. Required
lower layers are selected automatically at the consumer's selection level.
No second set of module booleans overrides these package selectors.
The complete tables live with their respective branches:
[SNode.C packages and options](snodec-package-options.md) and
[MQTTSuite packages and options](mqttsuite-package-options.md).

`snode.c-full` selects all 63 shared runtime modules. The demonstration
applications and `snodec-control` have separate packages. Static/internal
CMake targets have no separate runtime payload and therefore no empty module
packages. Both RFCOMM (`net-rc`) and L2CAP (`net-l2`) have six separate layers:
address/configuration, physical socket, physical stream, stream configuration,
legacy stream and TLS stream. RFCOMM also has legacy/TLS Express packages.

`mqttsuite-full` selects all five applications and both mapping plugins.
Each application has eight existing-style transport options, including the
new MQTTStore menu. TLS depends on its base socket family; WSS depends on WS
and an enabled TLS family. WS requires a socket family. If both IPv6 and Unix
sockets are disabled, IPv4 TCP is retained so the application remains usable.
Bridge/integrator retain their upstream unconditional IPv4 HTTP/HTTPS admin
servers, even when their MQTT TLS transport is disabled.

SNode.C compiles a shared set of library targets, then packages only the
selected modules. Demonstrations compile only when their package is selected.
MQTTSuite compiles only selected applications; application WebSocket plugins
compile and ship only when WS is enabled. The mapping plugins are selected
individually for packaging.

## Reproduce the build

Extract the SDK and run the following inside it. Replace `/path/to/OpenWRT`
with this repository's absolute path. The SDK's default feed revisions are
retained.

```sh
./scripts/feeds update base packages
./scripts/feeds install nlohmannjson libopenssl libmagic bluez-libs libmariadb
mkdir -p package/local
ln -s /path/to/OpenWRT/net/snode.c package/local/snode.c
ln -s /path/to/OpenWRT/net/mqttsuite package/local/mqttsuite
cat > .config <<'EOF'
# CONFIG_ALL is not set
# CONFIG_ALL_NONSHARED is not set
# CONFIG_ALL_KMODS is not set
# CONFIG_SIGNED_PACKAGES is not set
# CONFIG_AUTOREMOVE is not set
CONFIG_PACKAGE_snode.c-full=m
CONFIG_PACKAGE_snode.c-apps=m
CONFIG_PACKAGE_snode.c-control=m
CONFIG_PACKAGE_mqttsuite-full=m
EOF
make defconfig
make -j16 package/local/mqttsuite/compile V=s
```

This selects all publication packages and uses the feature defaults from the
package Makefiles and `Config.in` files. In particular, MQTTSuite's Unix-socket
TLS options retain their default of disabled; CI does not override them.
The example disables signing for local validation. CI enables package signing
and supplies the publication keys.

MQTTSuite's build dependency builds and stages SNode.C first. MQTTSuite uses
a separate CMake build directory so its private `lib/Log.h` cannot shadow
SNode.C's public `Log.h` through a generated-header include path. spdlog 1.17.0 is
a checked OpenWrt download, supplied to FetchContent locally. No configure-time
network fetch is needed. Every recipe configuration option participates in
OpenWrt's reconfiguration stamp; SNode.C's derived CMake cache is reset when
configuring to avoid stale defaults.

The pinned SDK feed emits an unrelated libcurl/LDAP Kconfig recursion warning.
Its SDK kernel configuration also includes prebuilt kernel modules, so the
first dependency build packages more kernel modules than these applications
need. Neither behavior is introduced by these recipes.

## WebSocket loading and RPATH

The HTTP loader opens
`/usr/lib/snode.c/web/http/upgrade/libsnodec-websocket-{server,client}.so.2`.
The WebSocket subprotocol loader then opens the application-specific
`/usr/lib/snode.c/web/http/upgrade/websocket/mqtt<app>/libsnodec-websocket-mqtt-{server,client}.so.2`.
MQTTSuite's plugin SONAME follows SNode.C ABI **2**, while the real plugin file
version is **1.0.1**. Both the real file and ABI symlink are packaged. Ordinary
MQTTSuite libraries use ABI **1**.

The plugin directory identifies the `dlopen` object; its dependencies still
need the correct ELF library search paths. Before OpenWrt runs `rstrip`, the
MQTTSuite recipe removes only the literal staging-directory prefix from each
RPATH/RUNPATH entry. It preserves target subdirectories, `$ORIGIN`, unrelated
entries, permissions, and the original tag type; patchelf errors fail the
build. It does not delete or shrink all RPATHs. OpenWrt may subsequently remove
ordinary system-directory entries; the packaged libraries retain the remaining
paths on each ELF file against that package's dependency closure.

## Services and device verification

The three existing services (`mqttbroker`, `mqttintegrator`, `mqttbridge`) run
in the foreground under procd and send logs to logd. They load SNode.C's
existing `/etc/snode.c/<application>.conf` configuration files. The recipe
preserves `/etc/snode.c/` across upgrades. The bridge service starts only once
`/etc/snode.c/mqttbridge.conf` exists; configure its `bridge.definition` with a
valid bridge JSON file. Its packaged web assets are supplied through
`bridge --html-dir /usr/var/www/mqttsuite/mqttbridge`. No site-specific remote
brokers are built into the service.

MQTTStore and the CLI are independent executable packages. Configure database
credentials/storage projections and MQTT endpoints before running MQTTStore.
TLS endpoints need suitable certificates, keys and trust settings.

On the matching router firmware, install the desired APKs with their
dependencies (`apk add --allow-untrusted ./<package>.apk` for these unsigned
local builds). Supply all referenced local SNode.C packages or a local feed;
installing a single meta-package alone cannot discover unpublished packages.
Then check application help/configuration, native MQTT, WS and WSS connections,
service restart/logging, bridge forwarding, integrator mappings, and MQTTStore
writes. Physical router execution and hardware verification remain for the
owner. See [QEMU VM verification](qemu-vm.md) for completed virtual-machine
installation, MQTT/TLS/WS/WSS traffic tests and runtime observations.

## Upstream tests

CI runs the upstream SNode.C CTest suite for each SDK build using
`tests/test_upstream.py`. Target executables run under QEMU with the SDK's
libraries. Test failures block publication. This repository does not maintain
additional application, configuration, package-audit or installation tests.
