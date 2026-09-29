# Install MQTTSuite

Install the complete MQTTSuite package set or select individual components.
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

### Full MQTTSuite installation

After preparation, run the command for your distribution:

**OpenWrt 24.10:**

```sh
opkg install mqttsuite-full
```

**OpenWrt 25.12:**

```sh
apk add mqttsuite-full
```

**Raspberry Pi OS, Debian and Ubuntu:**

```sh
sudo apt-get install mqttsuite
```

**Rocky Linux and Fedora:**

```sh
sudo dnf install mqttsuite
```

## Manual installation

Follow the **Manual preparation** section in your distribution guide above to
install the signing key, add the repository and refresh package indexes without
the script. Then use the same full or selective installation commands on this page.

## Selective installation

For the broker and command-line client only:

```sh
# OpenWrt 24.10
opkg install mqttsuite-broker mqttsuite-cli
# OpenWrt 25.12
apk add mqttsuite-broker mqttsuite-cli
# Raspberry Pi OS, Debian and Ubuntu
sudo apt-get install mqttsuite-broker mqttsuite-cli
# Rocky Linux and Fedora
sudo dnf install mqttsuite-broker mqttsuite-cli
```

### Components

| Package | Contents |
| --- | --- |
| `mqttsuite-broker` | Broker, library, WebSocket plugin and web assets |
| `mqttsuite-bridge` | Bridge, library, WebSocket plugin and web assets |
| `mqttsuite-integrator` | Integrator, library and WebSocket plugin |
| `mqttsuite-cli` | Command-line client, library and WebSocket plugin |
| `mqttsuite-store` | Store, library and WebSocket plugin |
| `mqttsuite-mapping-double` | Double mapping plugin |
| `mqttsuite-mapping-storage` | Storage mapping plugin |

The full-install metapackage is `mqttsuite-full` on OpenWrt and `mqttsuite` on
DEB/RPM distributions. OpenWrt plugin availability follows the package build
configuration; see its [complete package catalog](mqttsuite-package-options.md).
The store requires a configured database service.

## Configuration

Inspect `mqttbroker --help` and `mqttcli --help`. Configure listeners, credentials
and TLS certificates before starting services. See the
[application documentation](https://github.com/SNodeC/mqttsuite#readme) for options
and client examples.

### OpenWrt services

Configure `/etc/snode.c/mqttbroker.conf`, then enable and start the broker:

```sh
/etc/init.d/mqttbroker enable
/etc/init.d/mqttbroker start
pidof mqttbroker
logread -e mqttbroker
```

After configuration changes, use `/etc/init.d/mqttbroker restart`. The bridge and
integrator provide `mqttbridge` and `mqttintegrator` services; configure each before
enabling it.

### DEB and RPM services

Packages install executables in `/usr/bin`; they do not start network services.
To run a foreground broker:

```sh
mqttbroker --daemonize=false
```

For persistent operation, configure a systemd service with the desired user and
arguments.

## Updates

Refresh metadata and update the packages you installed. For a complete installation
on APT distributions:

```sh
sudo apt-get update
sudo apt-get install mqttsuite
```

On Raspberry Pi OS, this also upgrades older combined packages to component
packages. `apt-get upgrade` alone can hold back that transition when new
dependencies are needed.

On RPM distributions:

```sh
sudo dnf upgrade 'mqttsuite*'
```

On OpenWrt, use `opkg update` followed by `opkg upgrade <package> ...` (24.10),
or `apk update` followed by `apk upgrade <package> ...` (25.12). Select installed
package names from the catalog. Package updates do not upgrade the firmware.
For selective installations, update your chosen components instead of installing
the complete metapackage.

## Packages and help

- [Published MQTTSuite versions and build results](https://github.com/SNodeC/OpenWRT/blob/packages/mqttsuite/README.md)
- [OpenWrt package catalog](mqttsuite-package-options.md)
- [Troubleshoot repository access](../README.md#repository-troubleshooting)
- [Return to the repository overview](../README.md)
