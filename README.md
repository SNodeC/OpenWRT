# SNode.C and MQTTSuite packages

Signed packages for **OpenWrt, Raspberry Pi OS, Debian, Ubuntu, Rocky Linux and Fedora**.
Install directly with your distribution's package manager; no source checkout or
compilation is needed on the device.

[SNode.C](https://github.com/SNodeC/snode.c) provides the C++ networking framework
and runtime libraries. [MQTTSuite](https://github.com/SNodeC/mqttsuite) provides an
MQTT broker, bridge, integrator, command-line client, store and mapping plugins.

## Explore this repository

### Install packages

- [Choose your distribution and architecture](#distribution-and-architecture-matrix)
- [Choose the project to install](#installation)

### Available packages and build results

- [Browse the package catalogs](#package-catalogs)
- [Check build results and published versions](#build-and-publication-status)

### Repository help

- [Understand the repository layout](#repository-layout-and-links)
- [Troubleshoot repository access](#repository-troubleshooting)

## Installation

### SNode.C

[Install the framework and tools](docs/install-snodec.md), or choose individual components.

### MQTTSuite

[Install the applications](docs/install-mqttsuite.md), or select only those you need.

Both project guides provide full and selective installation, configuration and
updates. Use **prepare only** (`--prepare`) to configure the repository without
installing packages, then install your chosen project. The distribution guides
below retain complete manual repository setup instructions.

The installer without `--prepare` still installs both complete project sets.
Keep matching official repositories enabled for dependencies.

## Distribution and architecture matrix

| Distribution | Releases / suites | Architectures and installation | Production packages |
| --- | --- | --- | --- |
| OpenWrt | 24.10, 25.12 | [OpenWrt guide](docs/openwrt.md) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt) |
| Raspberry Pi OS | bookworm, trixie | [Raspberry Pi OS guide](docs/raspberrypi.md) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios) |
| Debian | trixie, forky, sid | [Debian guide](docs/debian.md) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/debian) |
| Ubuntu | noble, resolute | [Ubuntu guide](docs/ubuntu.md) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu) |
| Rocky Linux | 9, 10 | [Rocky Linux guide](docs/rocky.md) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/rocky) |
| Fedora | 43, 44 | [Fedora guide](docs/fedora.md) | [Browse](https://github.com/SNodeC/OpenWRT/tree/packages/fedora) |

Every guide lists all supported release/architecture combinations with package
and repository-index links. Architecture names follow the distribution's package
manager. Packages from different distributions are not interchangeable.

## Build and publication status

### SNode.C

[Check published versions and build results](https://github.com/SNodeC/OpenWRT/blob/packages/snodec/README.md).

### MQTTSuite

[Check published versions and build results](https://github.com/SNodeC/OpenWRT/blob/packages/mqttsuite/README.md).

Each project page lists all 76 configured targets in a flat table with its own
version and status badge. Each successful project build publishes independently
for its target. An unfinished or failed rebuild leaves the previous published
packages available.

## Package catalogs

### SNode.C

- [OpenWrt package names and contents](docs/snodec-package-options.md)
- [DEB and RPM components](docs/install-snodec.md#deb-and-rpm-components)

### MQTTSuite

- [OpenWrt package names and contents](docs/mqttsuite-package-options.md)
- [DEB and RPM components](docs/install-mqttsuite.md#components)

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
