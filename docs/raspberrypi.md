# Raspberry Pi OS

## Installation and configuration

- [Find supported releases and architectures](#releases-architectures-and-repositories)
- [Prepare the repository using the script or manual commands](#prepare-the-repository)
- [Install and configure SNode.C](install-snodec.md)
- [Install and configure MQTTSuite](install-mqttsuite.md)
- [Update packages and troubleshoot](#updates-and-troubleshooting)

## Package repository

- [Browse production packages for Raspberry Pi OS](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios)
- [SNode.C build results and versions](https://github.com/SNodeC/OpenWRT/blob/packages/snodec/README.md)
- [MQTTSuite build results and versions](https://github.com/SNodeC/OpenWRT/blob/packages/mqttsuite/README.md)

## Releases, architectures and repositories

| Release / suite | Architecture | Package files | Signed repository metadata |
| --- | --- | --- | --- |
| `bookworm` | `arm64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios/pool/bookworm) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios/dists/bookworm/main/binary-arm64) |
| `trixie` | `arm64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios/pool/trixie) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/raspberrypios/dists/trixie/main/binary-arm64) |

These packages support **Raspberry Pi 3, 4 and 5 running 64-bit Raspberry Pi OS**.
There is one ARM64 package set for Bookworm and one for Trixie, using the
[official Raspberry Pi OS Lite images](https://www.raspberrypi.com/software/operating-systems/).
Binaries use the common ARMv8-A baseline; no Pi-specific CPU tuning is used.
32-bit installations are not covered.

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

Continue with the [project installation instructions](#install-packages).

### Manual preparation

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

## Install packages

### SNode.C

[Full installation, individual components, configuration and updates](install-snodec.md).

### MQTTSuite

[Full installation, individual components, configuration and updates](install-mqttsuite.md).

## Updates and troubleshooting

Use your project's installation guide above for update commands. After a distribution
upgrade, select the matching supported repository release and refresh its indexes.
Keep signature verification and the official repositories enabled.

| Symptom | What to check |
| --- | --- |
| Feed returns 404 | Check the release and package architecture against the table above and the published repository. |
| Signature verification fails | Check the installed public key, device clock and feed URL. Keep signature checks enabled. |
| Dependencies cannot be installed | Keep the official repositories enabled for the installed release, including any prerequisites listed above. |
| Download fails just after publication | Refresh package metadata and retry after GitHub's raw-content caches update. |
| Application does not start | Inspect its `--help` output, configuration and logs; verify installation completed. |
| A newer build is unavailable | Check [Actions](https://github.com/SNodeC/OpenWRT/actions/workflows/openwrt.yml). Unfinished or failed builds do not replace the feed. |

## Related navigation

- [Choose another distribution](../README.md#distribution-and-architecture-matrix)
- [Return to the top of this guide](#raspberry-pi-os)
