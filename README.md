# SNode.C and MQTTSuite Linux packages

[![Distribution packages](https://github.com/SNodeC/OpenWRT/actions/workflows/openwrt.yml/badge.svg)](https://github.com/SNodeC/OpenWRT/actions/workflows/openwrt.yml)

Install [SNode.C](https://github.com/SNodeC/snode.c) and
[MQTTSuite](https://github.com/SNodeC/mqttsuite) from signed repositories for
**OpenWrt, Raspberry Pi OS, Debian, Ubuntu, Rocky Linux and Fedora**.
SNode.C provides a C++ networking framework and runtime modules. MQTTSuite
provides an MQTT broker, bridge, integrator, client, store and mapping plugins.

The **`main` branch** contains recipes, CI and documentation. Ready-to-install
packages, signed indexes and public keys live on the
**[`packages` branch](https://github.com/SNodeC/OpenWRT/tree/packages)**.
No source checkout or compilation is needed on the device.

## Distribution and architecture matrix

Choose your installed **distribution, release and package architecture**. Each
installation guide includes repository preparation, full and selective installation,
updates and package links. Architectures share a guide because package managers
select the correct index; separate guides per CPU would duplicate instructions.

| Distribution / installation guide | Release / suite | Package architectures | Format / manager | Repository |
| --- | --- | --- | --- | --- |
| [OpenWrt](docs/openwrt.md) | 24.10 | [25 variants below](#openwrt-architectures) | IPK / opkg | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10) |
| [OpenWrt](docs/openwrt.md) | 25.12 | [25 variants below](#openwrt-architectures) | APK / apk | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12) |
| [Raspberry Pi OS](docs/raspberrypi.md) | bookworm | `arm64` — Pi 3, 4 and 5 | DEB / APT | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios/dists/bookworm) |
| [Raspberry Pi OS](docs/raspberrypi.md) | trixie | `arm64` — Pi 3, 4 and 5 | DEB / APT | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios/dists/trixie) |
| [Debian](docs/debian.md) | trixie | `amd64`, `arm64`, `armhf`, `riscv64` | DEB / APT | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/debian/dists/trixie) |
| [Debian](docs/debian.md) | forky | `amd64`, `arm64`, `armhf`, `riscv64` | DEB / APT | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/debian/dists/forky) |
| [Debian](docs/debian.md) | sid | `amd64`, `arm64`, `armhf`, `riscv64` | DEB / APT | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/debian/dists/sid) |
| [Ubuntu](docs/ubuntu.md) | noble | `amd64`, `arm64` | DEB / APT | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu/dists/noble) |
| [Ubuntu](docs/ubuntu.md) | resolute | `amd64`, `arm64` | DEB / APT | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu/dists/resolute) |
| [Rocky Linux](docs/rocky.md) | 9 | `x86_64`, `aarch64` | RPM / DNF | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/rocky/9) |
| [Rocky Linux](docs/rocky.md) | 10 | `x86_64`, `aarch64` | RPM / DNF | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/rocky/10) |
| [Fedora](docs/fedora.md) | 43 | `x86_64`, `aarch64` | RPM / DNF | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/fedora/43) |
| [Fedora](docs/fedora.md) | 44 | `x86_64`, `aarch64` | RPM / DNF | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/fedora/44) |

**76 build targets:** 50 OpenWrt, 2 Raspberry Pi OS and 24 Debian/Ubuntu/Rocky/Fedora.
The three source-tag groups build and publish independently. Check
[Actions](https://github.com/SNodeC/OpenWRT/actions/workflows/openwrt.yml) and each
feed's `build.json` for build status and the published generation.

`amd64` / `x86_64` both mean 64-bit x86; `arm64` / `aarch64` both mean 64-bit ARM.
Debian also builds `armhf` (32-bit ARM hard-float) and `riscv64`.
OpenWrt requires its more specific `DISTRIB_ARCH` value. Raspberry Pi OS coverage
is 64-bit only; one package set per release supports Pi 3, 4 and 5.
Packages from different distributions are not interchangeable.

The authoritative matrices are [OpenWrt](ci/platforms.json),
[Raspberry Pi OS](ci/raspberrypi.json) and [other distributions](ci/linux.json).

## Installation

1. Open your distribution's guide in the table above.
2. Prepare the repository: import its signing key, add the matching feed and refresh indexes.
3. Choose full installation or individual applications. Keep official repositories enabled for dependencies.
4. Configure application listeners, credentials and TLS before starting services.

OpenWrt additionally offers a [quick installer](docs/openwrt.md#quick-installation),
with separate full-install and **`--prepare`** modes. Its guide retains the
[complete manual setup](docs/openwrt.md#add-the-feed-manually).

| Selection | OpenWrt | Debian, Ubuntu, Raspberry Pi OS, Rocky Linux, Fedora |
| --- | --- | --- |
| Full installation | `mqttsuite-full snode.c-full snode.c-apps snode.c-control` | `snodec mqttsuite` |
| Broker and client | `mqttsuite-broker mqttsuite-cli` | `mqttsuite-broker mqttsuite-cli` |
| Component catalog | [SNode.C](docs/snodec-package-options.md) · [MQTTSuite](docs/mqttsuite-package-options.md) | [DEB/RPM component packages](docs/linux.md#component-packages) |

OpenWrt and CPack-based distributions use different framework package names;
follow the matching guide rather than substituting names between formats.

## OpenWrt architectures

Both OpenWrt series build the same 25 platform variants. The established
priority order is retained below. RISC-V's package architecture name differs
between releases; the links use the correct name for each series.

| Package architecture | Representative SDK target | OpenWrt 24.10 | OpenWrt 25.12 |
| --- | --- | --- | --- |
| `aarch64_cortex-a53` | `mediatek/filogic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/aarch64_cortex-a53) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/aarch64_cortex-a53) |
| `x86_64` | `x86/64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/x86_64) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/x86_64) |
| `aarch64_generic` | `armsr/armv8` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/aarch64_generic) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/aarch64_generic) |
| `aarch64_cortex-a72` | `bcm27xx/bcm2711` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/aarch64_cortex-a72) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/aarch64_cortex-a72) |
| `aarch64_cortex-a76` | `bcm27xx/bcm2712` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/aarch64_cortex-a76) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/aarch64_cortex-a76) |
| `mipsel_24kc` | `ramips/mt76x8` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/mipsel_24kc) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/mipsel_24kc) |
| `mips_24kc` | `ath79/generic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/mips_24kc) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/mips_24kc) |
| `mipsel_24kc_24kf` | `pistachio/generic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/mipsel_24kc_24kf) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/mipsel_24kc_24kf) |
| `arm_cortex-a7_neon-vfpv4` | `ipq40xx/generic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a7_neon-vfpv4) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a7_neon-vfpv4) |
| `arm_cortex-a15_neon-vfpv4` | `armsr/armv7` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a15_neon-vfpv4) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a15_neon-vfpv4) |
| `arm_cortex-a9_vfpv3-d16` | `mvebu/cortexa9` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a9_vfpv3-d16) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a9_vfpv3-d16) |
| `arm_cortex-a9` | `bcm53xx/generic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a9) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a9) |
| `arm_cortex-a9_neon` | `imx/cortexa9` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a9_neon) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a9_neon) |
| `arm_cortex-a7` | `mediatek/mt7629` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a7) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a7) |
| `mips64_octeonplus` | `octeon/generic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/mips64_octeonplus) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/mips64_octeonplus) |
| `riscv64_riscv64` (24.10), `riscv64_generic` (25.12) | `sifiveu/generic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/riscv64_riscv64) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/riscv64_generic) |
| `arm_cortex-a7_vfpv4` | `at91/sama7` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a7_vfpv4) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a7_vfpv4) |
| `i386_pentium4` | `x86/generic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/i386_pentium4) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/i386_pentium4) |
| `arm_cortex-a8_vfpv3` | `sunxi/cortexa8` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a8_vfpv3) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a8_vfpv3) |
| `mipsel_74kc` | `ramips/rt3883` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/mipsel_74kc) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/mipsel_74kc) |
| `loongarch64_generic` | `loongarch64/generic` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/loongarch64_generic) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/loongarch64_generic) |
| `powerpc_8548` | `mpc85xx/p1010` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/powerpc_8548) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/powerpc_8548) |
| `arm_cortex-a5_vfpv4` | `at91/sama5` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/arm_cortex-a5_vfpv4) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/arm_cortex-a5_vfpv4) |
| `powerpc_464fp` | `apm821xx/nand` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/powerpc_464fp) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/powerpc_464fp) |
| `i386_pentium-mmx` | `x86/geode` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/24.10/i386_pentium-mmx) | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt/25.12/i386_pentium-mmx) |

## Repository layout and links

All paths below are relative to the `packages` branch:

| Distribution | Package files | Repository metadata |
| --- | --- | --- |
| OpenWrt | `openwrt/<series>/<architecture>/` | Signed opkg index or `packages.adb` in the same directory |
| Raspberry Pi OS | `raspberrypios/pool/<suite>/` | `raspberrypios/dists/<suite>/main/binary-<architecture>/` |
| Debian | `debian/pool/<suite>/` | `debian/dists/<suite>/main/binary-<architecture>/` |
| Ubuntu | `ubuntu/pool/<suite>/` | `ubuntu/dists/<suite>/main/binary-<architecture>/` |
| Rocky Linux | `rocky/<major>/<architecture>/Packages/` | `rocky/<major>/<architecture>/repodata/` |
| Fedora | `fedora/<release>/<architecture>/Packages/` | `fedora/<release>/<architecture>/repodata/` |

APT suites also contain signed `InRelease` and `Release.gpg` files. RPM feeds
include signed `repomd.xml` metadata and signed packages. Public keys are in
[`keys/`](https://github.com/SNodeC/OpenWRT/tree/packages/keys).

Use **github.com links to browse directories**. Package managers use the
**raw.githubusercontent.com URLs** shown in the guides; raw URLs serve files,
not directory listings. Opening a raw directory URL in a browser can return 404
although its package files and indexes exist.

Existing feeds using `releases/` or `apt/` need the
[feed URL migration](docs/package-repository.md#feed-directory-migration).

## Repository troubleshooting

| Symptom | What to check |
| --- | --- |
| Feed or index returns 404 | Verify the distribution, release and architecture; check whether its CI has published successfully. A raw directory URL is not a browsable index. |
| Signature verification fails | Check the key, system clock and feed URL. Keep signature verification enabled. |
| Dependencies cannot be installed | Enable the matching official repositories; on Rocky also enable CRB and EPEL as documented. Do not mix distribution releases. |
| Download fails just after publication | Refresh metadata and retry after GitHub's raw-content caches update. |
| Latest build is unavailable | Failed or unfinished runs retain the previous published feed. Inspect Actions and `build.json`. |

## Build, validation and publication

| Distribution group | Source tag in both projects | Build targets | Validation |
| --- | --- | --- | --- |
| OpenWrt | `OpenWRT` | 50 | Package audits on every target; four additional VM runtime jobs (x86-64 and ARM64 on both releases) |
| Raspberry Pi OS | `RaspberryPiOS` | 2 | Official OS image userspace builds, upstream tests, selective/full installation, MQTT runtime and upgrade tests |
| Debian, Ubuntu, Rocky Linux, Fedora | `Linux` | 24 | Distribution container builds, upstream tests, selective/full installation and MQTT runtime tests on every target |

MQTT runtime checks cover TCP, TLS, WebSocket and secure WebSocket. Container
and VM tests do not imply validation on every physical device. All required
jobs in a group must pass before that group publishes; publication preserves
other distributions and uses a shared lock.

The `packages` branch contains one parentless snapshot commit. Source history
stays on development branches. Superseded packages and metadata are retained
for 30 days, then cleaned during publication and daily maintenance.

Further documentation:

- [Repository signing, CI setup, migration and retention](docs/package-repository.md)
- [OpenWrt build recipes and branch ownership](docs/openwrt-build.md)
- [DEB/RPM component packages and Linux CI](docs/linux.md)
- [Raspberry Pi OS validation](docs/raspberrypi.md#repository-layout-and-validation)
- [OpenWrt package options](docs/package-options.md) and [recorded validation](docs/verification.md)
