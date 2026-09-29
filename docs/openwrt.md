# OpenWrt

## Installation and configuration

- [Find supported releases and architectures](#releases-architectures-and-repositories)
- [Prepare the repository using the script or manual commands](#prepare-the-repository)
- [Install and configure SNode.C](install-snodec.md)
- [Install and configure MQTTSuite](install-mqttsuite.md)
- [Update packages and troubleshoot](#updates-and-troubleshooting)

## Package repository

- [Browse production packages for OpenWrt](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt)
- [SNode.C build results and versions](https://github.com/SNodeC/OpenWRT/blob/packages/snodec/README.md)
- [MQTTSuite build results and versions](https://github.com/SNodeC/OpenWRT/blob/packages/mqttsuite/README.md)

## Releases, architectures and repositories

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

Both series cover the same 25 platform variants, listed in the established
priority order within each release. RISC-V uses a different package architecture
name in each series. The matrix is maintained in [ci/platforms.json](../ci/platforms.json).

<details>
<summary>All 50 OpenWrt release and architecture combinations</summary>

| Release / suite | Architecture | Package files | Signed repository metadata |
| --- | --- | --- | --- |
| `24.10` | `aarch64_cortex-a53` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/aarch64_cortex-a53) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/aarch64_cortex-a53/Packages.gz) |
| `24.10` | `x86_64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/x86_64) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/x86_64/Packages.gz) |
| `24.10` | `aarch64_generic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/aarch64_generic) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/aarch64_generic/Packages.gz) |
| `24.10` | `aarch64_cortex-a72` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/aarch64_cortex-a72) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/aarch64_cortex-a72/Packages.gz) |
| `24.10` | `aarch64_cortex-a76` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/aarch64_cortex-a76) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/aarch64_cortex-a76/Packages.gz) |
| `24.10` | `mipsel_24kc` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/mipsel_24kc) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/mipsel_24kc/Packages.gz) |
| `24.10` | `mips_24kc` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/mips_24kc) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/mips_24kc/Packages.gz) |
| `24.10` | `mipsel_24kc_24kf` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/mipsel_24kc_24kf) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/mipsel_24kc_24kf/Packages.gz) |
| `24.10` | `arm_cortex-a7_neon-vfpv4` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a7_neon-vfpv4) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/arm_cortex-a7_neon-vfpv4/Packages.gz) |
| `24.10` | `arm_cortex-a15_neon-vfpv4` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a15_neon-vfpv4) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/arm_cortex-a15_neon-vfpv4/Packages.gz) |
| `24.10` | `arm_cortex-a9_vfpv3-d16` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a9_vfpv3-d16) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/arm_cortex-a9_vfpv3-d16/Packages.gz) |
| `24.10` | `arm_cortex-a9` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a9) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/arm_cortex-a9/Packages.gz) |
| `24.10` | `arm_cortex-a9_neon` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a9_neon) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/arm_cortex-a9_neon/Packages.gz) |
| `24.10` | `arm_cortex-a7` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a7) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/arm_cortex-a7/Packages.gz) |
| `24.10` | `mips64_octeonplus` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/mips64_octeonplus) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/mips64_octeonplus/Packages.gz) |
| `24.10` | `riscv64_riscv64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/riscv64_riscv64) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/riscv64_riscv64/Packages.gz) |
| `24.10` | `arm_cortex-a7_vfpv4` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a7_vfpv4) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/arm_cortex-a7_vfpv4/Packages.gz) |
| `24.10` | `i386_pentium4` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/i386_pentium4) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/i386_pentium4/Packages.gz) |
| `24.10` | `arm_cortex-a8_vfpv3` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a8_vfpv3) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/arm_cortex-a8_vfpv3/Packages.gz) |
| `24.10` | `mipsel_74kc` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/mipsel_74kc) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/mipsel_74kc/Packages.gz) |
| `24.10` | `loongarch64_generic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/loongarch64_generic) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/loongarch64_generic/Packages.gz) |
| `24.10` | `powerpc_8548` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/powerpc_8548) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/powerpc_8548/Packages.gz) |
| `24.10` | `arm_cortex-a5_vfpv4` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a5_vfpv4) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/arm_cortex-a5_vfpv4/Packages.gz) |
| `24.10` | `powerpc_464fp` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/powerpc_464fp) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/powerpc_464fp/Packages.gz) |
| `24.10` | `i386_pentium-mmx` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/i386_pentium-mmx) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/i386_pentium-mmx/Packages.gz) |
| `25.12` | `aarch64_cortex-a53` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/aarch64_cortex-a53) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/aarch64_cortex-a53/packages.adb) |
| `25.12` | `x86_64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/x86_64) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/x86_64/packages.adb) |
| `25.12` | `aarch64_generic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/aarch64_generic) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/aarch64_generic/packages.adb) |
| `25.12` | `aarch64_cortex-a72` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/aarch64_cortex-a72) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/aarch64_cortex-a72/packages.adb) |
| `25.12` | `aarch64_cortex-a76` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/aarch64_cortex-a76) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/aarch64_cortex-a76/packages.adb) |
| `25.12` | `mipsel_24kc` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/mipsel_24kc) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/mipsel_24kc/packages.adb) |
| `25.12` | `mips_24kc` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/mips_24kc) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/mips_24kc/packages.adb) |
| `25.12` | `mipsel_24kc_24kf` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/mipsel_24kc_24kf) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/mipsel_24kc_24kf/packages.adb) |
| `25.12` | `arm_cortex-a7_neon-vfpv4` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a7_neon-vfpv4) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/arm_cortex-a7_neon-vfpv4/packages.adb) |
| `25.12` | `arm_cortex-a15_neon-vfpv4` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a15_neon-vfpv4) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/arm_cortex-a15_neon-vfpv4/packages.adb) |
| `25.12` | `arm_cortex-a9_vfpv3-d16` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a9_vfpv3-d16) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/arm_cortex-a9_vfpv3-d16/packages.adb) |
| `25.12` | `arm_cortex-a9` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a9) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/arm_cortex-a9/packages.adb) |
| `25.12` | `arm_cortex-a9_neon` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a9_neon) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/arm_cortex-a9_neon/packages.adb) |
| `25.12` | `arm_cortex-a7` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a7) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/arm_cortex-a7/packages.adb) |
| `25.12` | `mips64_octeonplus` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/mips64_octeonplus) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/mips64_octeonplus/packages.adb) |
| `25.12` | `riscv64_generic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/riscv64_generic) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/riscv64_generic/packages.adb) |
| `25.12` | `arm_cortex-a7_vfpv4` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a7_vfpv4) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/arm_cortex-a7_vfpv4/packages.adb) |
| `25.12` | `i386_pentium4` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/i386_pentium4) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/i386_pentium4/packages.adb) |
| `25.12` | `arm_cortex-a8_vfpv3` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a8_vfpv3) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/arm_cortex-a8_vfpv3/packages.adb) |
| `25.12` | `mipsel_74kc` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/mipsel_74kc) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/mipsel_74kc/packages.adb) |
| `25.12` | `loongarch64_generic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/loongarch64_generic) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/loongarch64_generic/packages.adb) |
| `25.12` | `powerpc_8548` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/powerpc_8548) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/powerpc_8548/packages.adb) |
| `25.12` | `arm_cortex-a5_vfpv4` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a5_vfpv4) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/arm_cortex-a5_vfpv4/packages.adb) |
| `25.12` | `powerpc_464fp` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/powerpc_464fp) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/powerpc_464fp/packages.adb) |
| `25.12` | `i386_pentium-mmx` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/i386_pentium-mmx) | [Index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/i386_pentium-mmx/packages.adb) |

</details>

## Prepare the repository

### Preparation script

To prepare the feed without installing any packages, pass **`--prepare`**:

```sh
wget -O /tmp/snodec-install-feed.sh \
  https://raw.githubusercontent.com/SNodeC/OpenWRT/main/ci/install-feed.sh &&
sh /tmp/snodec-install-feed.sh --prepare
```

This imports the signing key, configures the feed and refreshes package lists.
Continue with the [project installation instructions](#install-packages).

### Manual preparation

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

## Install packages

### SNode.C

[Full installation, individual components, configuration and updates](install-snodec.md).

### MQTTSuite

[Full installation, individual components, configuration and updates](install-mqttsuite.md).

## Updates and troubleshooting

Use your project's installation guide above for update commands. After a distribution
upgrade, select the matching supported repository release and refresh its indexes.
Keep signature verification and the official repositories enabled.

| Symptom | What to check |
| --- | --- |
| Feed returns 404 | Check the release series and `DISTRIB_ARCH` against the published directories. An unsupported device has no feed. |
| Signature verification fails | Check the installed public key, device clock and feed URL. Keep signature verification enabled. |
| Dependencies cannot be installed | Keep the official feeds enabled and matching the installed OpenWrt release. Do not mix architectures or release series. |
| Download fails just after publication | Refresh the package index and retry; GitHub's raw-content caches can take time to update. |
| Application does not start | Check its `--help` output, configuration and `logread`; verify that installation completed successfully. |
| A newer build is not available | Check [Actions](https://github.com/SNodeC/OpenWRT/actions/workflows/openwrt.yml). Failed or unfinished runs do not replace the published feed. |

## Related navigation

- [Choose another distribution](../README.md#distribution-and-architecture-matrix)
- [Return to the top of this guide](#openwrt)
