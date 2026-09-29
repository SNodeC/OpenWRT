# Debian

## Installation and configuration

- [Find supported releases and architectures](#releases-architectures-and-repositories)
- [Prepare the repository using the script or manual commands](#prepare-the-repository)
- [Install and configure SNode.C](install-snodec.md)
- [Install and configure MQTTSuite](install-mqttsuite.md)
- [Update packages and troubleshoot](#updates-and-troubleshooting)

## Package repository

- [Browse production packages for Debian](https://github.com/SNodeC/OpenWRT/tree/packages/debian)
- [SNode.C build results and versions](https://github.com/SNodeC/OpenWRT/blob/packages/snodec/README.md)
- [MQTTSuite build results and versions](https://github.com/SNodeC/OpenWRT/blob/packages/mqttsuite/README.md)

## Releases, architectures and repositories

| Release / suite | Architecture | Package files | Signed repository metadata |
| --- | --- | --- | --- |
| `trixie` | `amd64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/debian/pool/trixie) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/debian/dists/trixie/main/binary-amd64) |
| `trixie` | `arm64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/debian/pool/trixie) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/debian/dists/trixie/main/binary-arm64) |
| `trixie` | `armhf` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/debian/pool/trixie) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/debian/dists/trixie/main/binary-armhf) |
| `trixie` | `riscv64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/debian/pool/trixie) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/debian/dists/trixie/main/binary-riscv64) |
| `forky` | `amd64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/debian/pool/forky) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/debian/dists/forky/main/binary-amd64) |
| `forky` | `arm64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/debian/pool/forky) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/debian/dists/forky/main/binary-arm64) |
| `forky` | `armhf` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/debian/pool/forky) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/debian/dists/forky/main/binary-armhf) |
| `forky` | `riscv64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/debian/pool/forky) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/debian/dists/forky/main/binary-riscv64) |
| `sid` | `amd64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/debian/pool/sid) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/debian/dists/sid/main/binary-amd64) |
| `sid` | `arm64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/debian/pool/sid) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/debian/dists/sid/main/binary-arm64) |
| `sid` | `armhf` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/debian/pool/sid) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/debian/dists/sid/main/binary-armhf) |
| `sid` | `riscv64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/debian/pool/sid) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/debian/dists/sid/main/binary-riscv64) |

Keep the official distribution repositories enabled for dependencies. Use the
feed matching the installed distribution and release; matching CPU architectures
alone do not make packages interchangeable between distributions.

Trixie is the stable series, Forky the testing series and Sid unstable in this
matrix. Use these explicit suite names instead of moving stable/testing aliases.
For Sid, select `sid` explicitly; `/etc/os-release` may identify a testing codename.

## Prepare the repository

The installer requires `curl` or `wget` and system CA certificates. Install these with
`sudo apt-get update && sudo apt-get install ca-certificates curl` if needed.

The [installer](../ci/install-feed.sh) detects the distribution, release and
package architecture, verifies that the feed exists, imports the public key,
configures the repository and refreshes indexes. Run it with `sudo`; it does not
configure application listeners or certificates. Use `--help` for usage.

On Debian Sid, append `--suite sid` to the installer invocation below.
For testing, use `--suite forky` if the release cannot be detected. The option
selects the installed suite; it does not upgrade the operating system.

### Preparation script

Pass **`--prepare`** to configure the feed without installing any packages:

```sh
curl -fsSL https://raw.githubusercontent.com/SNodeC/OpenWRT/main/ci/install-feed.sh \
  -o /tmp/snodec-install-feed.sh &&
sudo sh /tmp/snodec-install-feed.sh --prepare
```

Continue with the [project installation instructions](#install-packages).

### Manual preparation

These commands configure the signed feed without installing SNode.C or MQTTSuite.

Select your suite below (`trixie` is the example), then run the block:

```sh
(
  set -eu
  suite=trixie
  case "$suite" in trixie|forky|sid) ;; *) echo "Unsupported suite"; exit 1;; esac
  arch=$(dpkg --print-architecture)
  case "$arch" in amd64|arm64|armhf|riscv64) ;; *) echo "Unsupported architecture"; exit 1;; esac
  sudo apt-get update
  sudo apt-get install -y ca-certificates curl
  sudo install -d -m 755 /etc/apt/keyrings
  curl -fsSL https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/keys/snodec-apt.asc |
    sudo tee /etc/apt/keyrings/snodec.asc >/dev/null
  sudo chmod 644 /etc/apt/keyrings/snodec.asc
  printf 'deb [arch=%s signed-by=/etc/apt/keyrings/snodec.asc] https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/debian %s main\n' "$arch" "$suite" |
    sudo tee /etc/apt/sources.list.d/snodec.list
  sudo apt-get update
)
```

APT selects packages from the index for your native architecture. Package files
for all architectures share the suite’s `pool/` directory.

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
- [Return to the top of this guide](#debian)
