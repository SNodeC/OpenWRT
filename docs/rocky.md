# Rocky Linux

[All distributions](../README.md) · [Browse repository](https://github.com/SNodeC/OpenWRT/tree/packages/rocky)

## Releases, architectures and repositories

| Release / suite | Architecture | Package files | Signed repository metadata |
| --- | --- | --- | --- |
| `9` | `x86_64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/rocky/9/x86_64/Packages) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/rocky/9/x86_64/repodata) |
| `9` | `aarch64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/rocky/9/aarch64/Packages) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/rocky/9/aarch64/repodata) |
| `10` | `x86_64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/rocky/10/x86_64/Packages) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/rocky/10/x86_64/repodata) |
| `10` | `aarch64` | [Packages](https://github.com/SNodeC/OpenWRT/tree/packages/rocky/10/aarch64/Packages) | [Index](https://github.com/SNodeC/OpenWRT/tree/packages/rocky/10/aarch64/repodata) |

Keep the official distribution repositories enabled for dependencies. Use the
feed matching the installed distribution and release; matching CPU architectures
alone do not make packages interchangeable between distributions.

Rocky Linux 10 requires x86-64-v3 on x86 systems. ARM64 uses `aarch64`.
Rocky support does not imply separately validated RHEL or AlmaLinux support.

## Prepare the repository

The installer requires `curl` or `wget` and system CA certificates. Install these with `sudo dnf install ca-certificates curl` if needed.

For both installation methods, enable dependency repositories first:

```sh
sudo dnf install -y dnf-plugins-core epel-release
sudo dnf config-manager --set-enabled crb
```

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

```sh
sudo install -d -m 755 /etc/pki/rpm-gpg
sudo curl -fsSL https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/keys/snodec-apt.asc \
  -o /etc/pki/rpm-gpg/RPM-GPG-KEY-snodec
sudo rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-snodec
sudo tee /etc/yum.repos.d/snodec.repo >/dev/null <<'REPO'
[snodec]
name=SNode.C and MQTTSuite
baseurl=https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/rocky/$releasever/$basearch/
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-snodec
REPO
sudo dnf makecache
```

The quoted `REPO` delimiter preserves `$releasever` and `$basearch`; DNF expands
them for the installed system. Both RPM packages and repository metadata are
signature-checked.

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
sudo dnf install snodec mqttsuite
```

## Selective installation

For only the broker and command-line client:

```sh
sudo dnf install mqttsuite-broker mqttsuite-cli
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
dnf list --available 'snodec-*'
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
sudo dnf upgrade 'snodec*' 'mqttsuite*'
```

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
