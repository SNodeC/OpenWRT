# SNode.C and MQTTSuite Linux packages

[![Distribution packages](https://github.com/SNodeC/OpenWRT/actions/workflows/openwrt.yml/badge.svg)](https://github.com/SNodeC/OpenWRT/actions/workflows/openwrt.yml)

Install [SNode.C](https://github.com/SNodeC/snode.c) and
[MQTTSuite](https://github.com/SNodeC/mqttsuite) from signed repositories for
**OpenWrt, Raspberry Pi OS, Debian, Ubuntu, Rocky Linux and Fedora**.
SNode.C provides a C++ networking framework and runtime modules. MQTTSuite
provides an MQTT broker, bridge, integrator, client, store and mapping plugins.

The **`main` branch** contains package recipes and documentation. Ready-to-install
packages, signed indexes and public keys live on the
**[`packages` branch](https://github.com/SNodeC/OpenWRT/tree/packages)**.
No source checkout or compilation is needed on the device.

## Distribution and architecture matrix

Choose your installed **distribution, release and package architecture**. Each
installation guide includes repository preparation, full and selective installation,
updates and package links. Architectures share a guide because package managers
select the correct index; separate guides per CPU would duplicate instructions.

| Distribution | Releases / suites | Architectures and package links | Installation | Repository |
| --- | --- | --- | --- | --- |
| OpenWrt | 24.10, 25.12 | [Architecture matrix](docs/openwrt.md#releases-architectures-and-repositories) | [Guide](docs/openwrt.md#prepare-the-repository) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt) |
| Raspberry Pi OS | bookworm, trixie | [Architecture matrix](docs/raspberrypi.md#releases-architectures-and-repositories) | [Guide](docs/raspberrypi.md#prepare-the-repository) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios) |
| Debian | trixie, forky, sid | [Architecture matrix](docs/debian.md#releases-architectures-and-repositories) | [Guide](docs/debian.md#prepare-the-repository) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/debian) |
| Ubuntu | noble, resolute | [Architecture matrix](docs/ubuntu.md#releases-architectures-and-repositories) | [Guide](docs/ubuntu.md#prepare-the-repository) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu) |
| Rocky Linux | 9, 10 | [Architecture matrix](docs/rocky.md#releases-architectures-and-repositories) | [Guide](docs/rocky.md#prepare-the-repository) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/rocky) |
| Fedora | 43, 44 | [Architecture matrix](docs/fedora.md#releases-architectures-and-repositories) | [Guide](docs/fedora.md#prepare-the-repository) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/fedora) |

Each guide lists every supported release/architecture combination with links to
package files and repository metadata. Architecture names follow the distribution's
package manager. Packages from different distributions are not interchangeable.

## Installation

1. Open your distribution's guide in the table above.
2. Prepare the repository: import its signing key, add the matching feed and refresh indexes.
3. Choose full installation or individual applications. Keep official repositories enabled for dependencies.
4. Configure application listeners, credentials and TLS before starting services.

Every distribution guide provides an **installation script** (full installation
by default, **`--prepare`** for repository setup only), complete **manual setup**,
selective installation, application configuration and updates. All use the same
[installer](ci/install-feed.sh), which selects the distribution's package manager.
Package names and hardware requirements are documented in each guide.

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

## Repository troubleshooting

| Symptom | What to check |
| --- | --- |
| Feed or index returns 404 | Verify the distribution, release and architecture; check that the matching feed is available. A raw directory URL is not a browsable index. |
| Signature verification fails | Check the key, system clock and feed URL. Keep signature verification enabled. |
| Dependencies cannot be installed | Enable the matching official repositories; on Rocky also enable CRB and EPEL as documented. Do not mix distribution releases. |
| Download fails just after publication | Refresh metadata and retry after GitHub's raw-content caches update. |
| Latest build is unavailable | Failed or unfinished runs retain the previous published feed. Inspect Actions and `build.json`. |
