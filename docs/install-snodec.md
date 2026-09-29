# Install SNode.C

Install the complete SNode.C package set or select individual components.
The package manager installs required dependencies automatically.

## Choose your distribution

Each guide lists supported releases and architectures and provides both scripted
and complete manual repository preparation:

- [OpenWrt](openwrt.md#prepare-the-repository)
- [Raspberry Pi OS](raspberrypi.md#prepare-the-repository)
- [Debian](debian.md#prepare-the-repository)
- [Ubuntu](ubuntu.md#prepare-the-repository)
- [Rocky Linux](rocky.md#prepare-the-repository)
- [Fedora](fedora.md#prepare-the-repository)

Keep the matching official repositories enabled for system dependencies.

## Quick installation

### Prepare only

On **OpenWrt**, run as root:

```sh
wget -O /tmp/package-feed.sh \
  https://raw.githubusercontent.com/SNodeC/OpenWRT/main/ci/install-feed.sh &&
sh /tmp/package-feed.sh --prepare
```

On **Raspberry Pi OS, Debian, Ubuntu, Rocky Linux or Fedora**:

```sh
curl -fsSL https://raw.githubusercontent.com/SNodeC/OpenWRT/main/ci/install-feed.sh \
  -o /tmp/package-feed.sh &&
sudo sh /tmp/package-feed.sh --prepare
```

This configures the signed repository and refreshes its indexes without installing
application packages. Check the distribution guide for prerequisites; Debian users
can select a moving suite with `--suite forky` or `--suite sid` when appropriate.

### Full SNode.C installation

After preparation, run the command for your distribution:

**OpenWrt 24.10:**

```sh
opkg install snode.c-full snode.c-apps snode.c-control
```

**OpenWrt 25.12:**

```sh
apk add snode.c-full snode.c-apps snode.c-control
```

**Raspberry Pi OS, Debian and Ubuntu:**

```sh
sudo apt-get install snodec
```

**Rocky Linux and Fedora:**

```sh
sudo dnf install snodec
```

## Manual installation

Follow the **Manual preparation** section in your distribution guide above to
install the signing key, add the repository and refresh package indexes without
the script. Then use the same full or selective installation commands on this page.

## Selective installation

On OpenWrt, select runtime modules, demonstration applications or the control
utility from the [complete package catalog](snodec-package-options.md). For example:

```sh
# OpenWrt 24.10
opkg install snode.c-control
# OpenWrt 25.12
apk add snode.c-control
```

### DEB and RPM components

The `snodec` metapackage installs all components, including headers, examples and
the control tool. Individual names follow the upstream CPack components:

| Package | Contents |
| --- | --- |
| `snodec-core` | Core networking framework |
| `snodec-http-server` | HTTP server library |
| `snodec-mqtt-server` | MQTT server library |
| `snodec-apps` | Demonstration applications |
| `snodec-unspecified` | Unspecified component, including `snodec-control` |

List the available components:

```sh
# APT distributions
apt-cache pkgnames snodec- | sort
# RPM distributions
dnf list --available 'snodec-*'
```

Install selected names with `sudo apt-get install <package> ...` or
`sudo dnf install <package> ...`.

## Configuration

Inspect `snodec-control --help` for the configuration tool. Configure listeners,
credentials and TLS certificates before starting demonstration applications.
See the [framework documentation](https://github.com/SNodeC/snode.c#readme)
for development and runtime configuration.

## Updates

Refresh metadata and update the packages you installed. For a complete installation
on APT distributions:

```sh
sudo apt-get update
sudo apt-get install snodec
```

On Raspberry Pi OS, this also upgrades older combined packages to component
packages. `apt-get upgrade` alone can hold back that transition when new
dependencies are needed.

On RPM distributions:

```sh
sudo dnf upgrade 'snodec*'
```

On OpenWrt, use `opkg update` followed by `opkg upgrade <package> ...` (24.10),
or `apk update` followed by `apk upgrade <package> ...` (25.12). Select installed
package names from the catalog. Package updates do not upgrade the firmware.
For selective installations, update your chosen components instead of installing
the complete metapackage.

## Packages and help

- [Published SNode.C versions and build results](https://github.com/SNodeC/OpenWRT/blob/packages/snodec/README.md)
- [OpenWrt package catalog](snodec-package-options.md)
- [Troubleshoot repository access](../README.md#repository-troubleshooting)
- [Return to the repository overview](../README.md)
