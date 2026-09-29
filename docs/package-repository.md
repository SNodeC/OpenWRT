# SNode.C and MQTTSuite packages

Find a distribution below to see every configured release and architecture.
Published versions and links come from the repository manifests; a build badge
alone is not evidence that new packages are available.

## Installation

- [Choose your distribution and install packages](https://github.com/SNodeC/OpenWRT/blob/main/README.md#installation)
- [Browse the production package repository](https://github.com/SNodeC/OpenWRT/tree/packages)

## Package catalogs

- [SNode.C packages for OpenWrt](https://github.com/SNodeC/OpenWRT/blob/main/docs/snodec-package-options.md)
- [MQTTSuite packages for OpenWrt](https://github.com/SNodeC/OpenWRT/blob/main/docs/mqttsuite-package-options.md)
- [DEB and RPM component packages](https://github.com/SNodeC/OpenWRT/blob/main/docs/linux.md#component-packages)

## Build and publication results

Select a distribution to see its releases, architectures and published versions:

- [OpenWrt](#openwrt)
- [Raspberry Pi OS](#raspberry-pi-os)
- [Debian](#debian)
- [Ubuntu](#ubuntu)
- [Rocky Linux](#rocky-linux)
- [Fedora](#fedora)

[Understand the status badges and publication columns](#reading-the-matrix).

## OpenWrt

- [Install packages on OpenWrt](https://github.com/SNodeC/OpenWRT/blob/main/docs/openwrt.md)
- [Browse production packages for OpenWrt](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt)

<!-- targets:openwrt -->

## Raspberry Pi OS

- [Install packages on Raspberry Pi OS](https://github.com/SNodeC/OpenWRT/blob/main/docs/raspberrypi.md)
- [Browse production packages for Raspberry Pi OS](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios)

<!-- targets:raspberrypios -->

## Debian

- [Install packages on Debian](https://github.com/SNodeC/OpenWRT/blob/main/docs/debian.md)
- [Browse production packages for Debian](https://github.com/SNodeC/OpenWRT/tree/packages/debian)

<!-- targets:debian -->

## Ubuntu

- [Install packages on Ubuntu](https://github.com/SNodeC/OpenWRT/blob/main/docs/ubuntu.md)
- [Browse production packages for Ubuntu](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu)

<!-- targets:ubuntu -->

## Rocky Linux

- [Install packages on Rocky Linux](https://github.com/SNodeC/OpenWRT/blob/main/docs/rocky.md)
- [Browse production packages for Rocky Linux](https://github.com/SNodeC/OpenWRT/tree/packages/rocky)

<!-- targets:rocky -->

## Fedora

- [Install packages on Fedora](https://github.com/SNodeC/OpenWRT/blob/main/docs/fedora.md)
- [Browse production packages for Fedora](https://github.com/SNodeC/OpenWRT/tree/packages/fedora)

<!-- targets:fedora -->

## Reading the matrix

- **SNode.C / MQTTSuite:** the published version appears above each project's status badge. A dash means no version is recorded. Click a badge to open its build or publication job. **Pending** means waiting to build or publish; **running** means building; **publishing** means the publication job is active; **published** confirms the packages were pushed. **Failed**, **cancelled**, **skipped**, and **superseded** identify unfinished releases. Badges are snapshots refreshed by publication jobs, not live monitors. **Not built** means neither a project result nor a published version is recorded.
- **Published:** the UTC publication date appears above the repository links. **Packages** opens the package directory; **Build** opens the record containing the complete timestamp, source tags, resolved commits and publication details. A row without repository links has not been published in this channel. Signed indexes are available in the repository directories described by each installation guide.

A failed or unfinished rebuild retains the previous successful publication.
Superseded package files remain available for 30 days after leaving the active
index, so clients with cached metadata can finish downloads.

## Installation and repository access

Use the [distribution guides](https://github.com/SNodeC/OpenWRT/blob/main/README.md#distribution-and-architecture-matrix)
for the full installer, prepare-only mode and complete manual instructions.
They use the production feeds and keep official repositories enabled for system
dependencies. Select the release and package architecture installed on the device.

Use **Packages** to browse this channel on GitHub and **Build** for the
publication record. Package
managers use raw file URLs; opening a raw directory URL in a browser can return
404 even when the individual package and index files exist.

## Repository help

- [Inspect the public signing keys](keys/)
- [Troubleshoot repository access](https://github.com/SNodeC/OpenWRT/blob/main/README.md#repository-troubleshooting)
- [Return to the project overview](https://github.com/SNodeC/OpenWRT/blob/main/README.md)
