# SNode.C and MQTTSuite packages

[Project & installation](https://github.com/SNodeC/OpenWRT/blob/main/README.md#installation) · [Package catalogs](https://github.com/SNodeC/OpenWRT/blob/main/README.md#package-catalogs) · [Production feeds](https://github.com/SNodeC/OpenWRT/tree/packages) · [Signing keys](keys/)

Find a distribution below to see every configured release and architecture.
Published versions and links come from the repository manifests; a build badge
alone is not evidence that new packages are available.

[OpenWrt](#openwrt) · [Raspberry Pi OS](#raspberry-pi-os) · [Debian](#debian) · [Ubuntu](#ubuntu) · [Rocky Linux](#rocky-linux) · [Fedora](#fedora)

## OpenWrt

[Installation & architecture guide](https://github.com/SNodeC/OpenWRT/blob/main/docs/openwrt.md) · [Production packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt)

<!-- targets:openwrt -->

## Raspberry Pi OS

[Installation & architecture guide](https://github.com/SNodeC/OpenWRT/blob/main/docs/raspberrypi.md) · [Production packages](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios)

<!-- targets:raspberrypios -->

## Debian

[Installation & architecture guide](https://github.com/SNodeC/OpenWRT/blob/main/docs/debian.md) · [Production packages](https://github.com/SNodeC/OpenWRT/tree/packages/debian)

<!-- targets:debian -->

## Ubuntu

[Installation & architecture guide](https://github.com/SNodeC/OpenWRT/blob/main/docs/ubuntu.md) · [Production packages](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu)

<!-- targets:ubuntu -->

## Rocky Linux

[Installation & architecture guide](https://github.com/SNodeC/OpenWRT/blob/main/docs/rocky.md) · [Production packages](https://github.com/SNodeC/OpenWRT/tree/packages/rocky)

<!-- targets:rocky -->

## Fedora

[Installation & architecture guide](https://github.com/SNodeC/OpenWRT/blob/main/docs/fedora.md) · [Production packages](https://github.com/SNodeC/OpenWRT/tree/packages/fedora)

<!-- targets:fedora -->

[How to read the matrix](#reading-the-matrix) · [Choose a distribution](https://github.com/SNodeC/OpenWRT/blob/main/README.md#distribution-and-architecture-matrix)

## Reading the matrix

- **Result:** click a badge to open its run. **Running** includes a target awaiting publication after its build; **passed** confirms publication completed. Status is refreshed when feeds are published and when the run finishes. **Not built** means no build is recorded for that target in this channel.
- **SNode.C / MQTTSuite:** the packages currently offered by this channel, independently of the latest build result. A dash means no version is recorded; a row without repository links has not been published in this channel.
- **Published:** the UTC publication date. Click it for the complete timestamp in the build record.
- **Repository:** **Packages** opens the package directory; **Build** opens the record containing source tags, resolved commits and publication details. Signed indexes are available in the repository directories described by each installation guide.

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

[Installation guides](https://github.com/SNodeC/OpenWRT/blob/main/README.md#distribution-and-architecture-matrix) · [Package catalogs](https://github.com/SNodeC/OpenWRT/blob/main/README.md#package-catalogs) · [Repository troubleshooting](https://github.com/SNodeC/OpenWRT/blob/main/README.md#repository-troubleshooting)
