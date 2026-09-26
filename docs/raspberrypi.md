# Raspberry Pi OS packages

The package CI targets **Raspberry Pi 3, 4 and 5 running 64-bit Raspberry Pi OS**.
It builds one ARM64 package set for Bookworm and one for Trixie, using the
[official Raspberry Pi OS Lite images](https://www.raspberrypi.com/software/operating-systems/).
The image URLs and verification checksums are maintained in
[`ci/raspberrypi.json`](../ci/raspberrypi.json). Binaries use the common ARMv8-A
baseline; no Pi-specific CPU tuning is used. 32-bit installations are not covered.

## Installation

Run these commands on the Pi. Keep the official Raspberry Pi OS repositories
configured: they supply system dependencies. This feed supplies individual component packages. The `snodec` and `mqttsuite`
metapackages install all components of their respective projects.

```sh
. /etc/os-release
case "$VERSION_CODENAME" in bookworm|trixie) ;; *) echo 'Unsupported OS release'; exit 1;; esac
[ "$(dpkg --print-architecture)" = arm64 ] || { echo '64-bit Raspberry Pi OS required'; exit 1; }
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -d -m 755 /etc/apt/keyrings
curl -fsSL https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/keys/snodec-apt.asc |
    sudo tee /etc/apt/keyrings/snodec.asc >/dev/null
sudo chmod 644 /etc/apt/keyrings/snodec.asc
printf 'deb [arch=arm64 signed-by=/etc/apt/keyrings/snodec.asc] https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/apt %s main\n' "$VERSION_CODENAME" |
    sudo tee /etc/apt/sources.list.d/snodec.list
sudo apt-get update
```

These commands only prepare the feed. To install the full system:

```sh
sudo apt-get install snodec mqttsuite
```

For a broker and command-line client only:

```sh
sudo apt-get install mqttsuite-broker mqttsuite-cli
```

APT installs the required SNode.C components automatically. It does not install
other MQTTSuite applications or all of SNode.C merely to run the broker.

| Package | Contents |
| --- | --- |
| `mqttsuite-broker` | Broker, its library, WebSocket plugin and web assets |
| `mqttsuite-bridge` | Bridge, its library, WebSocket plugin and web assets |
| `mqttsuite-integrator` | Integrator, its library and WebSocket plugin |
| `mqttsuite-cli` | Command-line client, its library and WebSocket plugin |
| `mqttsuite-store` | Store, its library and WebSocket plugin |
| `mqttsuite-mapping-double` | Double mapping plugin |
| `mqttsuite-mapping-storage` | Storage mapping plugin |
| `mqttsuite` | All seven MQTTSuite components |
| `snodec` | All SNode.C components, including headers, examples and control tool |

SNode.C package names follow its upstream CPack components: for example,
`snodec-core`, `snodec-http-server`, `snodec-mqtt-server` and `snodec-apps`.
The upstream `Unspecified` component is published as `snodec-unspecified` and
includes `snodec-control`. List all available framework packages with:

```sh
apt-cache pkgnames snodec- | sort
```

The complete package names, versions and dependencies are in the
[Bookworm index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/apt/dists/bookworm/main/binary-arm64/Packages)
and [Trixie index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/apt/dists/trixie/main/binary-arm64/Packages).

To upgrade an existing combined-package installation, run
`sudo apt-get update && sudo apt-get install snodec mqttsuite`. This installs the
new component dependencies as well as updating the two full-install metapackages.
`apt-get upgrade` alone can hold back this transition because it requires new
packages. Component packages declare replacement of files from older combined
packages; subsequent updates use the normal APT update process.

APT signing-key fingerprint:
`8BBF D49E 3C82 6FDB 1416 C79E 6004 6744 B15B 0E05`.

Installation creates the required `snodec` system group. The applications are
installed in `/usr/bin`. Start the broker explicitly with
`mqttbroker --daemonize=false`; installation does not start network services.
Use `mqttbroker --help`, `mqttcli --help` or `snodec-control --help` for options.
For a persistent service, configure your systemd service according to the desired
user, listeners and TLS configuration.

## Repository layout and validation

On the `packages` branch:

- `apt/pool/bookworm/` and `apt/pool/trixie/`: `.deb` files.
- `apt/dists/<suite>/main/binary-arm64/`: package indexes and SHA256 by-hash indexes.
- `apt/dists/<suite>/`: signed `InRelease`, `Release`, `Release.gpg` and build provenance.
- `keys/snodec-apt.asc`: public APT signing key.

[Browse Bookworm packages](https://github.com/SNodeC/OpenWRT/tree/packages/apt/pool/bookworm)
· [Browse Trixie packages](https://github.com/SNodeC/OpenWRT/tree/packages/apt/pool/trixie)

Creation or movement of `RaspberryPiOS` in either source repository triggers only
the Raspberry Pi jobs. Both projects are built from their `RaspberryPiOS` tags.
The independent `OpenWRT` tags trigger only OpenWrt jobs. Sources and recipes are
captured once for each run. Actions use
version tags. Source commit IDs in provenance record what was built; they are
not pinned checkout references.

Each Pi job builds inside an official image's root filesystem on a native ARM64
runner. SNode.C's CTests run during the build. A second, clean image filesystem
installs only the broker and CLI through the signed APT feed and tests their
runtime dependency closure before installing all components. A third clean
filesystem tests upgrades from the original combined packages. Runtime tests
cover CLI startup and MQTT publish/subscribe over TCP, TLS, WebSocket and secure
WebSocket. Publication checks the complete CPack-derived component inventory for
both OS releases.

These are userspace tests, not Pi boot, kernel, peripheral or physical-hardware
tests. Both Raspberry Pi OS jobs must pass before APT publication. OpenWrt builds
and tests gate only OpenWrt publication. Runs are serialized per release tag;
the two platforms can build independently. A shared publication-job lock
serializes writes, and each publication starts from the latest `packages` snapshot
and preserves the other platform’s feeds. Publication rejects incomplete matrices, corrupt
packages, invalid signatures, mixed source generations and superseded tags.
Superseded packages and by-hash indexes remain available for 30 days after
retirement, then are pruned during publication or daily maintenance. See the
[shared retention policy](package-repository.md#retention-and-maintenance).
The branch still contains only one commit after each publication.

The private APT key is stored in the repository secret `APT_SIGNING_KEY`, alongside
the existing OpenWrt signing secrets. Only its public key is committed.
