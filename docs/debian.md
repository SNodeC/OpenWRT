# Debian

[All distributions](../README.md) · [Browse repository](https://github.com/SNodeC/OpenWRT/tree/packages/debian)

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
