# SNode.C and MQTTSuite package repositories

This branch contains signed binary packages and repository indexes for installing
SNode.C and MQTTSuite on supported Linux distributions. It is not a source or
firmware repository.

## Distribution feeds

| Distribution | Repository root | Metadata |
|---|---|---|
| Debian | `debian/` | `dists/{trixie,forky,sid}/` and `pool/` |
| Ubuntu | `ubuntu/` | `dists/{noble,resolute}/` and `pool/` |
| Rocky Linux | `rocky/<major>/<architecture>/` | `repodata/`, RPMs in `Packages/` |
| Fedora | `fedora/<release>/<architecture>/` | `repodata/`, RPMs in `Packages/` |
| Raspberry Pi OS | `raspberrypios/` | `dists/{bookworm,trixie}/` and `pool/` |
| OpenWrt | `openwrt/<series>/<architecture>/` | opkg or APK index |

Installation guides: [OpenWrt](https://github.com/SNodeC/OpenWRT/blob/main/docs/openwrt.md),
[Raspberry Pi OS](https://github.com/SNodeC/OpenWRT/blob/main/docs/raspberrypi.md),
[Debian](https://github.com/SNodeC/OpenWRT/blob/main/docs/debian.md),
[Ubuntu](https://github.com/SNodeC/OpenWRT/blob/main/docs/ubuntu.md),
[Rocky Linux](https://github.com/SNodeC/OpenWRT/blob/main/docs/rocky.md) and
[Fedora](https://github.com/SNodeC/OpenWRT/blob/main/docs/fedora.md).
See the [complete matrix](https://github.com/SNodeC/OpenWRT/blob/main/README.md#distribution-and-architecture-matrix)
for all distributions and architectures.

## Using the repositories

Follow your distribution guide for automatic preparation, full installation or
manual setup. Select the matching release and architecture and keep the official
distribution repositories enabled for dependencies. Public signing keys are in
[`keys/`](keys/).

Use GitHub directory links for browsing. Package managers use the raw file URLs
provided by the installation guides.

## Package updates

A higher package revision is an upgrade even when the upstream version is
unchanged. Refresh package indexes before upgrading. Older package files remain
available for 30 days after they leave the active index, allowing clients with
cached metadata to finish downloads.
