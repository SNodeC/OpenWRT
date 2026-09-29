# Ubuntu

## Installation and configuration

- [Find supported releases and architectures](#releases-architectures-and-repositories)
- [Prepare the repository using the script or manual commands](#prepare-the-repository)
- [Install and configure SNode.C](install-snodec.md)
- [Install and configure MQTTSuite](install-mqttsuite.md)
- [Update packages and troubleshoot](#updates-and-troubleshooting)

## Package repository

- [Browse production packages for Ubuntu](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu)
- [SNode.C build results and versions](https://github.com/SNodeC/OpenWRT/blob/packages/snodec/README.md)
- [MQTTSuite build results and versions](https://github.com/SNodeC/OpenWRT/blob/packages/mqttsuite/README.md)

## Releases, architectures and repositories

| Release / suite | Architecture | Package files | Signed repository metadata |
| --- | --- | --- | --- |
| `noble` | `amd64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu/pool/noble) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu/dists/noble/main/binary-amd64) |
| `noble` | `arm64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu/pool/noble) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu/dists/noble/main/binary-arm64) |
| `resolute` | `amd64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu/pool/resolute) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu/dists/resolute/main/binary-amd64) |
| `resolute` | `arm64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu/pool/resolute) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu/dists/resolute/main/binary-arm64) |

Keep the official distribution repositories enabled for dependencies. Use the
feed matching the installed distribution and release; matching CPU architectures
alone do not make packages interchangeable between distributions.

Noble is Ubuntu 24.04 LTS; Resolute is Ubuntu 26.04 LTS. Coverage policy is the
two latest LTS releases plus the latest stable interim release when newer. New
releases require an explicit matrix update and successful validation.

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

These commands configure the signed feed without installing SNode.C or MQTTSuite.

Select your suite below (`noble` is the example), then run the block:

```sh
(
  set -eu
  suite=noble
  case "$suite" in noble|resolute) ;; *) echo "Unsupported suite"; exit 1;; esac
  arch=$(dpkg --print-architecture)
  case "$arch" in amd64|arm64) ;; *) echo "Unsupported architecture"; exit 1;; esac
  sudo apt-get update
  sudo apt-get install -y ca-certificates curl
  sudo install -d -m 755 /etc/apt/keyrings
  curl -fsSL https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/keys/snodec-apt.asc |
    sudo tee /etc/apt/keyrings/snodec.asc >/dev/null
  sudo chmod 644 /etc/apt/keyrings/snodec.asc
  printf 'deb [arch=%s signed-by=/etc/apt/keyrings/snodec.asc] https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/ubuntu %s main\n' "$arch" "$suite" |
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
- [Return to the top of this guide](#ubuntu)
