# Raspberry Pi OS

[All distributions](../README.md) · [Browse repository](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios)

## Releases, architectures and repositories

| Release / suite | Architecture | Package files | Signed repository metadata |
| --- | --- | --- | --- |
| `bookworm` | `arm64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios/pool/bookworm) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios/dists/bookworm/main/binary-arm64) |
| `trixie` | `arm64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios/pool/trixie) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios/dists/trixie/main/binary-arm64) |

The package CI targets **Raspberry Pi 3, 4 and 5 running 64-bit Raspberry Pi OS**.
It builds one ARM64 package set for Bookworm and one for Trixie, using the
[official Raspberry Pi OS Lite images](https://www.raspberrypi.com/software/operating-systems/).
The image URLs and verification checksums are maintained in
[`ci/raspberrypi.json`](../ci/raspberrypi.json). Binaries use the common ARMv8-A
baseline; no Pi-specific CPU tuning is used. 32-bit installations are not covered.

## Prepare the repository

The installer requires `curl` or `wget` and system CA certificates. Install these with
`sudo apt-get update && sudo apt-get install ca-certificates curl` if needed.

The [installer](../ci/install-feed.sh) detects the distribution, release and
package architecture, verifies that the feed exists, imports the public key,
configures the repository and refreshes indexes. Run it with `sudo`; it does not
configure application listeners or certificates. Use `--help` for usage.

### Preparation script

Pass **`--prepare`** to configure the feed without installing any packages:

```sh
curl -fsSL https://raw.githubusercontent.com/SNodeC/OpenWRT/main/ci/install-feed.sh \
  -o /tmp/snodec-install-feed.sh &&
sudo sh /tmp/snodec-install-feed.sh --prepare
```

Install your chosen packages afterwards using the commands below.

### Manual preparation

If you previously configured the `/packages/apt` feed, first
[update its URL](package-repository.md#feed-directory-migration) to `/packages/raspberrypios`.

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
printf 'deb [arch=arm64 signed-by=/etc/apt/keyrings/snodec.asc] https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/raspberrypios %s main\n' "$VERSION_CODENAME" |
    sudo tee /etc/apt/sources.list.d/snodec.list
sudo apt-get update
```

## Full installation

### Installation script

Without options, the installer prepares the feed and installs **all SNode.C and
MQTTSuite components** through the `snodec` and `mqttsuite` metapackages:

```sh
curl -fsSL https://raw.githubusercontent.com/SNodeC/OpenWRT/main/ci/install-feed.sh \
  -o /tmp/snodec-install-feed.sh &&
sudo sh /tmp/snodec-install-feed.sh
```

### Manual installation

After preparing the repository, install the full system:

```sh
sudo apt-get install snodec mqttsuite
```

## Selective installation

For a broker and command-line client only:

```sh
sudo apt-get install mqttsuite-broker mqttsuite-cli
```

APT installs the required SNode.C components automatically. It does not install
other MQTTSuite applications or all of SNode.C merely to run the broker.

See the shared [component package guide](linux.md#component-packages) for
individual package names and contents.

The complete package names, versions and dependencies are in the
[Bookworm index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/raspberrypios/dists/bookworm/main/binary-arm64/Packages)
and [Trixie index](https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/raspberrypios/dists/trixie/main/binary-arm64/Packages).

**Common choices:**

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

## Configure applications

Installation creates the `snodec` system group and installs executables in
`/usr/bin`; it does not start network services. Inspect `mqttbroker --help`,
`mqttcli --help` and `snodec-control --help`. Configure listeners, credentials and
TLS certificates for your deployment, then start a foreground broker:

```sh
mqttbroker --daemonize=false
```

For persistent operation, configure a systemd service with the desired user and
arguments. The store requires a configured database. See the
[MQTTSuite documentation](https://github.com/SNodeC/mqttsuite#readme) for options
and client examples.

## Updates and troubleshooting

To upgrade an existing combined-package installation, run
`sudo apt-get update && sudo apt-get install snodec mqttsuite`. This installs the
new component dependencies as well as updating the two full-install metapackages.
`apt-get upgrade` alone can hold back this transition because it requires new
packages. Component packages declare replacement of files from older combined
packages; subsequent updates use the normal APT update process.

| Symptom | What to check |
| --- | --- |
| Feed returns 404 | Check the release and package architecture against the table above and the published repository. |
| Signature verification fails | Check the installed public key, device clock and feed URL. Keep signature checks enabled. |
| Dependencies cannot be installed | Keep the official repositories enabled for the installed release, including any prerequisites listed above. |
| Download fails just after publication | Refresh package metadata and retry after GitHub's raw-content caches update. |
| Application does not start | Inspect its `--help` output, configuration and logs; verify installation completed. |
| A newer build is unavailable | Check [Actions](https://github.com/SNodeC/OpenWRT/actions/workflows/openwrt.yml). Unfinished or failed builds do not replace the feed. |

## Build and validation

On the `packages` branch:

- `raspberrypios/pool/bookworm/` and `raspberrypios/pool/trixie/`: `.deb` files.
- `raspberrypios/dists/<suite>/main/binary-arm64/`: package indexes and SHA256 by-hash indexes.
- `raspberrypios/dists/<suite>/`: signed `InRelease`, `Release`, `Release.gpg` and build provenance.
- `keys/snodec-apt.asc`: public APT signing key.

[Browse Bookworm packages](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios/pool/bookworm)
· [Browse Trixie packages](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios/pool/trixie)

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
the distribution groups can build independently. A shared publication-job lock
serializes writes, and each publication starts from the latest `packages` snapshot
and preserves other distributions’ feeds. Publication rejects incomplete matrices, corrupt
packages, invalid signatures, mixed source generations and superseded tags.
Superseded packages and by-hash indexes remain available for 30 days after
retirement, then are pruned during publication or daily maintenance. See the
[shared retention policy](package-repository.md#retention-and-maintenance).
The branch still contains only one commit after each publication.

The private APT key is stored in the repository secret `APT_SIGNING_KEY`, alongside
the existing OpenWrt signing secrets. Only its public key is committed.
