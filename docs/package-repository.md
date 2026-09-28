# SNode.C and MQTTSuite — build and publication matrix

[Project & installation](https://github.com/SNodeC/OpenWRT#installation) · [Production feeds](https://github.com/SNodeC/OpenWRT/tree/packages) · [Signing keys](keys/)

Find a distribution below to see every configured release and architecture.
Published versions and links come from the repository manifests; a build badge
alone is not evidence that new packages are available.

[OpenWrt](#openwrt) · [Raspberry Pi OS](#raspberry-pi-os) · [Debian](#debian) · [Ubuntu](#ubuntu) · [Rocky Linux](#rocky-linux) · [Fedora](#fedora)

## Reading the matrix

- **Latest build:** click a badge to open its run. **Not built** means no build is recorded for that target in this channel.
- **Published versions:** the packages currently offered by this channel, independently of the latest build result. **Not published** means this channel has no feed for the target yet.
- **Published UTC:** when that target was last published successfully.
- **Repository:** package files, signed metadata and the provenance manifest containing the source tags and resolved commits.

A failed or unfinished rebuild retains the previous successful publication.
Superseded package files remain available for 30 days after leaving the active
index, so clients with cached metadata can finish downloads.

## OpenWrt

[Installation & architecture guide](https://github.com/SNodeC/OpenWRT/blob/main/docs/openwrt.md) · [Production packages](https://github.com/SNodeC/OpenWRT/tree/packages/openwrt)

| Release / suite | Architecture | Latest build | Published versions | Published UTC | Repository |
| --- | --- | --- | --- | --- | --- |
<!-- targets:openwrt -->

## Raspberry Pi OS

[Installation & architecture guide](https://github.com/SNodeC/OpenWRT/blob/main/docs/raspberrypi.md) · [Production packages](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios)

| Release / suite | Architecture | Latest build | Published versions | Published UTC | Repository |
| --- | --- | --- | --- | --- | --- |
<!-- targets:raspberrypios -->

## Debian

[Installation & architecture guide](https://github.com/SNodeC/OpenWRT/blob/main/docs/debian.md) · [Production packages](https://github.com/SNodeC/OpenWRT/tree/packages/debian)

| Release / suite | Architecture | Latest build | Published versions | Published UTC | Repository |
| --- | --- | --- | --- | --- | --- |
<!-- targets:debian -->

## Ubuntu

[Installation & architecture guide](https://github.com/SNodeC/OpenWRT/blob/main/docs/ubuntu.md) · [Production packages](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu)

| Release / suite | Architecture | Latest build | Published versions | Published UTC | Repository |
| --- | --- | --- | --- | --- | --- |
<!-- targets:ubuntu -->

## Rocky Linux

[Installation & architecture guide](https://github.com/SNodeC/OpenWRT/blob/main/docs/rocky.md) · [Production packages](https://github.com/SNodeC/OpenWRT/tree/packages/rocky)

| Release / suite | Architecture | Latest build | Published versions | Published UTC | Repository |
| --- | --- | --- | --- | --- | --- |
<!-- targets:rocky -->

## Fedora

[Installation & architecture guide](https://github.com/SNodeC/OpenWRT/blob/main/docs/fedora.md) · [Production packages](https://github.com/SNodeC/OpenWRT/tree/packages/fedora)

| Release / suite | Architecture | Latest build | Published versions | Published UTC | Repository |
| --- | --- | --- | --- | --- | --- |
<!-- targets:fedora -->

## Installation and repository access

Use the [distribution guides](https://github.com/SNodeC/OpenWRT#distribution-and-architecture-matrix)
for the full installer, prepare-only mode and complete manual instructions.
They use the production feeds and keep official repositories enabled for system
dependencies. Select the release and package architecture installed on the device.

Use **Packages** and **Metadata** to browse this channel on GitHub. Package
managers use raw file URLs; opening a raw directory URL in a browser can return
404 even when the individual package and index files exist.
