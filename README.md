# SNode.C and MQTTSuite packages

[Install](#installation) · [Distributions](#distribution-and-architecture-matrix) · [Package status](#build-and-publication-status) · [Package catalogs](#package-catalogs) · [Repository layout](#repository-layout-and-links) · [Troubleshooting](#repository-troubleshooting)

Signed packages for **OpenWrt, Raspberry Pi OS, Debian, Ubuntu, Rocky Linux and Fedora**.
Install directly with your distribution's package manager; no source checkout or
compilation is needed on the device.

[SNode.C](https://github.com/SNodeC/snode.c) provides the C++ networking framework
and runtime libraries. [MQTTSuite](https://github.com/SNodeC/mqttsuite) provides an
MQTT broker, bridge, integrator, command-line client, store and mapping plugins.

## Installation

Choose your distribution below. Every guide includes both installation methods:

- **Full installation:** the installer configures the signed repository and installs the complete package set.
- **Prepare only:** `--prepare` configures the repository; you choose which packages to install afterwards.

Each guide also provides complete manual setup, selective installation, updates
and application configuration. Keep the official distribution repositories enabled
for dependencies, and select the release and architecture installed on your device.

The guides and installer use the **[production feeds](https://github.com/SNodeC/OpenWRT/tree/packages)**.
Configure application listeners, credentials and TLS before starting services.

## Distribution and architecture matrix

| Distribution | Releases / suites | Architectures and installation | Production packages | Validation results |
| --- | --- | --- | --- | --- |
| OpenWrt | 24.10, 25.12 | [OpenWrt guide](docs/openwrt.md) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt) | [All targets](https://github.com/SNodeC/OpenWRT/blob/packages-dev/README.md#openwrt) |
| Raspberry Pi OS | bookworm, trixie | [Raspberry Pi OS guide](docs/raspberrypi.md) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios) | [All targets](https://github.com/SNodeC/OpenWRT/blob/packages-dev/README.md#raspberry-pi-os) |
| Debian | trixie, forky, sid | [Debian guide](docs/debian.md) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/debian) | [All targets](https://github.com/SNodeC/OpenWRT/blob/packages-dev/README.md#debian) |
| Ubuntu | noble, resolute | [Ubuntu guide](docs/ubuntu.md) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu) | [All targets](https://github.com/SNodeC/OpenWRT/blob/packages-dev/README.md#ubuntu) |
| Rocky Linux | 9, 10 | [Rocky Linux guide](docs/rocky.md) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/rocky) | [All targets](https://github.com/SNodeC/OpenWRT/blob/packages-dev/README.md#rocky-linux) |
| Fedora | 43, 44 | [Fedora guide](docs/fedora.md) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/fedora) | [All targets](https://github.com/SNodeC/OpenWRT/blob/packages-dev/README.md#fedora) |

Every guide lists all supported release/architecture combinations with package
and repository-index links. Architecture names follow the distribution's package
manager. Packages from different distributions are not interchangeable.

## Build and publication status

The **[publication validation README](https://github.com/SNodeC/OpenWRT/blob/packages-dev/README.md)**
lists all 76 configured targets, grouped by distribution. Each row shows its
latest build badge, published project versions, publication time and repository
links. Click a build badge for its GitHub Actions run or **Provenance** for the
source tags and resolved commits recorded with the packages.

The validation README describes the separate **`packages-dev` channel**, with all
76 targets enabled for validation. Each successful target publishes independently.
**Not built** or **Not published** in that channel does not mean a production
package is unavailable. Use the production links above for installations.

Build status and published versions are separate: a failed or unfinished rebuild
leaves the previous published feed available. See also the
[production build runs](https://github.com/SNodeC/OpenWRT/actions/workflows/openwrt.yml).

## Package catalogs

For OpenWrt's individual package names and contents, see the complete catalogs:

- [SNode.C packages](docs/snodec-package-options.md)
- [MQTTSuite packages](docs/mqttsuite-package-options.md)

For Raspberry Pi OS, Debian, Ubuntu, Rocky Linux and Fedora, see the shared
[DEB/RPM component package guide](docs/linux.md#component-packages). Each
distribution guide provides the installation commands and common selections.
The `snodec` and `mqttsuite` metapackages in the DEB/RPM repositories install
their respective complete component sets.

## Repository layout and links

The `main` branch contains recipes and documentation. Published packages, signed
indexes and [public keys](https://github.com/SNodeC/OpenWRT/tree/packages/keys)
live on the `packages` branch, using these paths:

| Distribution | Package files | Repository metadata |
| --- | --- | --- |
| OpenWrt | `openwrt/<series>/<architecture>/` | Signed opkg index or `packages.adb` in the same directory |
| Raspberry Pi OS | `raspberrypios/pool/<suite>/` | `raspberrypios/dists/<suite>/main/binary-<architecture>/` |
| Debian | `debian/pool/<suite>/` | `debian/dists/<suite>/main/binary-<architecture>/` |
| Ubuntu | `ubuntu/pool/<suite>/` | `ubuntu/dists/<suite>/main/binary-<architecture>/` |
| Rocky Linux | `rocky/<major>/<architecture>/Packages/` | `rocky/<major>/<architecture>/repodata/` |
| Fedora | `fedora/<release>/<architecture>/Packages/` | `fedora/<release>/<architecture>/repodata/` |

GitHub directory links let you browse packages. Package managers use the raw file
URLs in the installation guides; raw URLs do not provide directory listings.

## Repository troubleshooting

| Symptom | What to check |
| --- | --- |
| Feed or index returns 404 | Check the distribution, release, architecture and channel. Use GitHub links to browse directories. |
| Signature verification fails | Check the installed public key, system clock and feed URL. Keep signature verification enabled. |
| Dependencies cannot be installed | Keep matching official repositories enabled; on Rocky also enable CRB and EPEL as documented. |
| Download fails just after publication | Refresh package metadata and retry after GitHub's raw-content caches update. |
| Latest rebuild failed | Check the target's published versions and feed links; the previous successful publication remains available. |
