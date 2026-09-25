# SNode.C and MQTTSuite packages for OpenWrt

[![OpenWrt packages](https://github.com/SNodeC/OpenWRT/actions/workflows/openwrt.yml/badge.svg)](https://github.com/SNodeC/OpenWRT/actions/workflows/openwrt.yml)

Install [SNode.C](https://github.com/SNodeC/snode.c) and
[MQTTSuite](https://github.com/SNodeC/mqttsuite) on OpenWrt devices from signed
package feeds. SNode.C provides the C++ networking framework and its runtime
modules; MQTTSuite provides an MQTT broker, bridge, integrator, command-line
client, store and mapping plugins.

This repository hosts the package recipes, build automation and installation
instructions on **`main`**. Ready-to-install packages, repository indexes and
public signing keys are published on the **[`packages` branch](https://github.com/SNodeC/OpenWRT/tree/packages)**.
You do not need to clone this repository or compile anything on your router.

## Supported releases and devices

| OpenWrt series | Package manager | Package format | Current SDK release |
| --- | --- | --- | --- |
| 24.10 | `opkg` | IPK | 24.10.8 |
| 25.12 | `apk` | APK | 25.12.5 |

Use the feed matching **both your OpenWrt release series and package
architecture**. These are userspace packages for official OpenWrt. A matching
CPU does not establish compatibility with a manufacturer's modified firmware.
Keep the official OpenWrt feeds enabled: they supply dependencies such as the
C++ runtime, OpenSSL and database libraries.

SSH into your device as `root` and identify it:

```sh
cat /etc/openwrt_release
. /etc/openwrt_release
printf 'OpenWrt: %s\nPackage architecture: %s\n' "$DISTRIB_RELEASE" "$DISTRIB_ARCH"
```

Use `DISTRIB_ARCH`, rather than `uname -m`, when selecting a feed. The same
package architecture can be shared by several hardware targets.

Both release series currently publish these 18 architecture variants:

| Package architecture | Representative SDK target | OpenWrt 24.10 | OpenWrt 25.12 |
| --- | --- | --- | --- |
| `x86_64` | `x86/64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/x86_64) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/x86_64) |
| `i386_pentium-mmx` | `x86/geode` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/i386_pentium-mmx) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/i386_pentium-mmx) |
| `aarch64_cortex-a53` | `mediatek/filogic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/aarch64_cortex-a53) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/aarch64_cortex-a53) |
| `aarch64_cortex-a72` | `bcm27xx/bcm2711` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/aarch64_cortex-a72) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/aarch64_cortex-a72) |
| `aarch64_generic` | `armsr/armv8` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/aarch64_generic) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/aarch64_generic) |
| `arm_cortex-a7` | `mediatek/mt7629` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/arm_cortex-a7) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/arm_cortex-a7) |
| `arm_cortex-a7_neon-vfpv4` | `ipq40xx/generic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/arm_cortex-a7_neon-vfpv4) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/arm_cortex-a7_neon-vfpv4) |
| `arm_cortex-a7_vfpv4` | `at91/sama7` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/arm_cortex-a7_vfpv4) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/arm_cortex-a7_vfpv4) |
| `arm_cortex-a9` | `bcm53xx/generic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/arm_cortex-a9) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/arm_cortex-a9) |
| `arm_cortex-a9_neon` | `imx/cortexa9` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/arm_cortex-a9_neon) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/arm_cortex-a9_neon) |
| `arm_cortex-a9_vfpv3-d16` | `mvebu/cortexa9` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/arm_cortex-a9_vfpv3-d16) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/arm_cortex-a9_vfpv3-d16) |
| `arm_cortex-a15_neon-vfpv4` | `armsr/armv7` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/arm_cortex-a15_neon-vfpv4) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/arm_cortex-a15_neon-vfpv4) |
| `mips_24kc` | `ath79/generic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/mips_24kc) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/mips_24kc) |
| `mipsel_24kc` | `ramips/mt76x8` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/mipsel_24kc) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/mipsel_24kc) |
| `mipsel_74kc` | `ramips/rt3883` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/mipsel_74kc) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/mipsel_74kc) |
| `powerpc_464fp` | `apm821xx/nand` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/powerpc_464fp) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/powerpc_464fp) |
| `powerpc_8548` | `mpc85xx/p1010` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/powerpc_8548) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/powerpc_8548) |
| `riscv64_riscv64` (24.10), `riscv64_generic` (25.12) | `sifiveu/generic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/24.10/riscv64_riscv64) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/releases/25.12/riscv64_generic) |

The build matrix is maintained in [ci/platforms.json](ci/platforms.json).
Available feeds can be browsed under [packages/releases](https://github.com/SNodeC/OpenWRT/tree/packages/releases).

## Quick installation

Run either option on the device as `root`. Use `--help` for usage. The installer
does not configure your MQTT endpoints or certificates.

### Full installation

For a complete installation, run the following on the device as `root`:

```sh
wget -O /tmp/snodec-install-feed.sh \
  https://raw.githubusercontent.com/SNodeC/OpenWRT/main/ci/install-feed.sh &&
sh /tmp/snodec-install-feed.sh
```

The [installer](ci/install-feed.sh) detects the release and architecture, checks
that the feed exists, imports its public signing key, adds the feed and refreshes
the package lists. It then installs **`mqttsuite-full`, `snode.c-full`,
`snode.c-apps` and `snode.c-control`**, including their dependencies.

### Prepare the package feed

To prepare the feed without installing any packages, pass **`--prepare`**:

```sh
wget -O /tmp/snodec-install-feed.sh \
  https://raw.githubusercontent.com/SNodeC/OpenWRT/main/ci/install-feed.sh &&
sh /tmp/snodec-install-feed.sh --prepare
```

This imports the signing key, configures the feed and refreshes package lists.
You then [install the packages you want](#choose-and-install-packages) yourself.
Running without an option still installs the complete selection above.

## Add the feed manually

Run the block for your release as `root`. These commands only configure the feed
and refresh its index; package installation is a separate step. Existing feeds
are preserved. The public keys can also be inspected in [ci/keys](ci/keys).

### OpenWrt 24.10: opkg

```sh
(
  set -eu
  . /etc/openwrt_release
  case "$DISTRIB_RELEASE" in 24.10.*) ;; *) echo 'Requires OpenWrt 24.10'; exit 1 ;; esac
  base=https://raw.githubusercontent.com/SNodeC/OpenWRT/packages
  feed="$base/releases/24.10/$DISTRIB_ARCH"
  wget -O /tmp/snodec-feed-build.json "$feed/build.json"
  wget -O /tmp/snodec-usign.pub "$base/keys/snodec-usign.pub"
  opkg-key add /tmp/snodec-usign.pub
  touch /etc/opkg/customfeeds.conf
  sed -i '/^src\/gz snodec /d' /etc/opkg/customfeeds.conf
  printf 'src/gz snodec %s\n' "$feed" >> /etc/opkg/customfeeds.conf
  opkg update
)
```

### OpenWrt 25.12: apk

```sh
(
  set -eu
  . /etc/openwrt_release
  case "$DISTRIB_RELEASE" in 25.12.*) ;; *) echo 'Requires OpenWrt 25.12'; exit 1 ;; esac
  base=https://raw.githubusercontent.com/SNodeC/OpenWRT/packages
  feed="$base/releases/25.12/$DISTRIB_ARCH"
  wget -O /tmp/snodec-feed-build.json "$feed/build.json"
  wget -O /tmp/snodec-apk.pem "$base/keys/snodec-apk.pem"
  mkdir -p /etc/apk/keys /etc/apk/repositories.d
  cp /tmp/snodec-apk.pem /etc/apk/keys/snodec-apk.pem
  printf '%s/packages.adb\n' "$feed" > /etc/apk/repositories.d/snodec.list
  apk update
)
```

### Example: GL.iNet GL-MT3000 running official OpenWrt

This device uses `aarch64_cortex-a53`.

On **24.10**, the entry in
`/etc/opkg/customfeeds.conf` is:

```text
src/gz snodec https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/releases/24.10/aarch64_cortex-a53
```

On **25.12**, `/etc/apk/repositories.d/snodec.list` contains:

```text
https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/releases/25.12/aarch64_cortex-a53/packages.adb
```

Import the corresponding signing key as shown above. For other devices, use
their `DISTRIB_ARCH`; each architecture has its own directory. After an OpenWrt
release-series upgrade, reconfigure this feed for the new series.

## Choose and install packages

**Complete package catalogs:** [SNode.C — all 67 packages](docs/snodec-package-options.md)
· [MQTTSuite — all 9 packages](docs/mqttsuite-package-options.md).
The catalogs list individual package names and their contents. Common choices
are shown below.

| Package | What it installs |
| --- | --- |
| `mqttsuite-broker` | MQTT broker and its service |
| `mqttsuite-cli` | MQTT publish/subscribe command-line client |
| `mqttsuite-bridge` | MQTT bridge |
| `mqttsuite-integrator` | MQTT integrator |
| `mqttsuite-store` | MQTT store with MariaDB support |
| `mqttsuite-full` | All five applications and both mapping plugins |
| `snode.c-full` | All SNode.C runtime modules |
| `snode.c-apps` | SNode.C demonstration applications |
| `snode.c-control` | SNode.C control utility |

Application packages select their required SNode.C modules automatically.
Installing `snode.c-full` separately is optional when you only want a particular
MQTTSuite application. The store still requires a configured database service.

For a broker and command-line client:

```sh
# OpenWrt 24.10
opkg install mqttsuite-broker mqttsuite-cli
```

```sh
# OpenWrt 25.12
apk add mqttsuite-broker mqttsuite-cli
```

For the complete selection used by the installer:

```sh
# OpenWrt 24.10
opkg install mqttsuite-full snode.c-full snode.c-apps snode.c-control
```

```sh
# OpenWrt 25.12
apk add mqttsuite-full snode.c-full snode.c-apps snode.c-control
```

### Configure and start the broker

Inspect `mqttbroker --help` and configure `/etc/snode.c/mqttbroker.conf` for your
listeners and, where applicable, TLS certificates. Refer to the
[MQTTSuite documentation](https://github.com/SNodeC/mqttsuite#readme) for options
and client examples. Then enable the service at boot and start it:

```sh
/etc/init.d/mqttbroker enable
/etc/init.d/mqttbroker start
pidof mqttbroker
logread -e mqttbroker
```

After changing its configuration, run `/etc/init.d/mqttbroker restart`.
The bridge and integrator also provide services named `mqttbridge` and
`mqttintegrator`; configure each application before enabling it.

## Updates and troubleshooting

Refresh indexes and inspect available updates:

```sh
# OpenWrt 24.10
opkg update
opkg list-upgradable
```

```sh
# OpenWrt 25.12
apk update
apk list --upgradable
```

Upgrade selected packages with `opkg upgrade <package> ...` or
`apk upgrade <package> ...`. Review related SNode.C and MQTTSuite updates together;
a package update does not upgrade the OpenWrt firmware or change its release series.

| Symptom | What to check |
| --- | --- |
| Feed returns 404 | Check the release series and `DISTRIB_ARCH` against the published directories. An unsupported device has no feed. |
| Signature verification fails | Check the installed public key, device clock and feed URL. Keep signature verification enabled. |
| Dependencies cannot be installed | Keep the official feeds enabled and matching the installed OpenWrt release. Do not mix architectures or release series. |
| Download fails just after publication | Refresh the package index and retry; GitHub's raw-content caches can take time to update. |
| Application does not start | Check its `--help` output, configuration and `logread`; verify that installation completed successfully. |
| A newer build is not available | Check [Actions](https://github.com/SNodeC/OpenWRT/actions/workflows/openwrt.yml). Failed or unfinished runs do not replace the published feed. |

## Build and publication

Creation or movement of the upstream **`OpenWRT` tag** in SNode.C or MQTTSuite
triggers the central build. Both projects are built from those tags using
official OpenWrt SDKs. All 36 release/architecture builds must pass package
configuration, dependency, architecture, symlink, RPATH and plugin checks.

Four additional jobs boot clean OpenWrt VMs: x86_64 and AArch64 on both releases.
They install all 76 packages from signed feeds, check application startup,
exercise MQTT publish/subscribe over TCP, TLS, WebSocket and secure WebSocket,
and check the broker service lifecycle. These are installation and runtime
smoke tests; other architectures currently receive build and package audits.

Only after every gate passes are all feeds published together. Each directory
contains packages, a signed package index and `build.json` with build provenance.
Public signing keys live under `keys/` on the `packages` branch. Publication
replaces that branch with a single root commit; source and recipe history stays
on the development branches. Older package files are retained for cached indexes.

Further documentation:

- [Feed layout, signing and CI setup](docs/package-repository.md)
- [Building from the package recipes and branch ownership](docs/openwrt-build.md)
- [Package and build options](docs/package-options.md)
- [Recorded validation details](docs/verification.md)
