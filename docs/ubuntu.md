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

```sh
sudo apt-get install snodec mqttsuite
```

## Selective installation

For only the broker and command-line client:

```sh
sudo apt-get install mqttsuite-broker mqttsuite-cli
```

Required SNode.C components are installed automatically. See the shared
[component package guide](linux.md#component-packages) for package names and
[application configuration](linux.md#configure-applications).

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

## Build and validation

These targets use the independent `Linux` source tags. See
[shared CI and publication details](linux.md#ci-and-publication) for build,
installation, runtime tests and publication gates.
