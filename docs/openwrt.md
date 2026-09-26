# OpenWrt

[All distributions](../README.md) · [Browse repository](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt)

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

Both series cover the same 25 platform variants. See the complete
[architecture table and per-release package links](../README.md#openwrt-architectures).
The matrix is maintained in [ci/platforms.json](../ci/platforms.json).

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

The [installer](../ci/install-feed.sh) detects the release and architecture, checks
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
are preserved. The public keys can also be inspected in [ci/keys](../ci/keys).

### OpenWrt 24.10: opkg

```sh
(
  set -eu
  . /etc/openwrt_release
  case "$DISTRIB_RELEASE" in 24.10.*) ;; *) echo 'Requires OpenWrt 24.10'; exit 1 ;; esac
  base=https://raw.githubusercontent.com/SNodeC/OpenWRT/packages
  feed="$base/openwrt/24.10/$DISTRIB_ARCH"
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
  feed="$base/openwrt/25.12/$DISTRIB_ARCH"
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
src/gz snodec https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/aarch64_cortex-a53
```

On **25.12**, `/etc/apk/repositories.d/snodec.list` contains:

```text
https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/aarch64_cortex-a53/packages.adb
```

Import the corresponding signing key as shown above. For other devices, use
their `DISTRIB_ARCH`; each architecture has its own directory. After an OpenWrt
release-series upgrade, reconfigure this feed for the new series.

## Choose and install packages

**Complete package catalogs:**

- [SNode.C — all 67 packages](snodec-package-options.md)
- [MQTTSuite — all 9 packages](mqttsuite-package-options.md)

The catalogs list individual package names and their contents.

**Common choices:**

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
official OpenWrt SDKs. All 50 release/architecture builds must pass package
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

- [Feed layout, signing and CI setup](package-repository.md)
- [Building from the package recipes and branch ownership](openwrt-build.md)
- [Package and build options](package-options.md)
- [Recorded validation details](verification.md)
