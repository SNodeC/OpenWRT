# Ubuntu

[All distributions](../README.md) · [Browse repository](https://github.com/SNodeC/OpenWRT/tree/packages/ubuntu)

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

Install your chosen packages afterwards using the commands below.

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

```sh
sudo apt-get install snodec mqttsuite
```

## Selective installation

For only the broker and command-line client:

```sh
sudo apt-get install mqttsuite-broker mqttsuite-cli
```

Required SNode.C components are installed automatically. See the shared
[component package guide](linux.md#component-packages) for package names and contents.

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

```sh
sudo apt-get update
sudo apt-get install snodec mqttsuite
```

For a selective installation, name only the packages you want to update instead
of the full-install metapackages.

After a distribution upgrade, select a supported matching release and refresh
metadata. For missing feeds, signature errors or dependency failures, see
[repository troubleshooting](../README.md#repository-troubleshooting).

| Symptom | What to check |
| --- | --- |
| Feed returns 404 | Check the release and package architecture against the table above and the published repository. |
| Signature verification fails | Check the installed public key, device clock and feed URL. Keep signature checks enabled. |
| Dependencies cannot be installed | Keep the official repositories enabled for the installed release, including any prerequisites listed above. |
| Download fails just after publication | Refresh package metadata and retry after GitHub's raw-content caches update. |
| Application does not start | Inspect its `--help` output, configuration and logs; verify installation completed. |
| A newer build is unavailable | Check [Actions](https://github.com/SNodeC/OpenWRT/actions/workflows/openwrt.yml). Unfinished or failed builds do not replace the feed. |

## Build and validation

These targets use the independent `Linux` source tags. See
[shared CI and publication details](linux.md#ci-and-publication) for build,
installation, runtime tests and publication gates.
