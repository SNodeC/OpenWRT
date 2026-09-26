# Raspberry Pi OS packages

The package CI targets **Raspberry Pi 3, 4 and 5 running 64-bit Raspberry Pi OS**.
It builds one ARM64 package set for Bookworm and one for Trixie, using the
[official Raspberry Pi OS Lite images](https://www.raspberrypi.com/software/operating-systems/).
The image URLs and verification checksums are maintained in
[`ci/raspberrypi.json`](../ci/raspberrypi.json). Binaries use the common ARMv8-A
baseline; no Pi-specific CPU tuning is used. 32-bit installations are not covered.

## Installation

Run these commands on the Pi. Keep the official Raspberry Pi OS repositories
configured: they supply system dependencies. This feed supplies two complete
packages: `snodec` (framework, modules, headers, examples and control tool) and
`mqttsuite` (broker, bridge, integrator, CLI, store and plugins).

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

Or install `snodec` alone for the networking framework. Installing `mqttsuite`
automatically installs its matching SNode.C dependency. Subsequent versions are
installed through normal `sudo apt-get update && sudo apt-get upgrade`.

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
then installs both packages through the signed APT feed, resolving dependencies
without the build environment. Runtime tests cover CLI startup and MQTT
publish/subscribe over TCP, TLS, WebSocket and secure WebSocket.

These are userspace tests, not Pi boot, kernel, peripheral or physical-hardware
tests. Both Raspberry Pi OS jobs must pass before APT publication. OpenWrt builds
and tests gate only OpenWrt publication. Runs are serialized per release tag;
the two platforms can build independently. A shared publication-job lock
serializes writes, and each publication starts from the latest `packages` snapshot
and preserves the other platform’s feeds. Publication rejects incomplete matrices, corrupt
packages, invalid signatures, mixed source generations and superseded tags.
Old packages and by-hash indexes remain available to clients with cached indexes.
The branch still contains only one commit after each publication.

The private APT key is stored in the repository secret `APT_SIGNING_KEY`, alongside
the existing OpenWrt signing secrets. Only its public key is committed.
