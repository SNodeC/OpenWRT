# Rocky Linux

## Installation and configuration

- [Find supported releases and architectures](#releases-architectures-and-repositories)
- [Prepare the repository using the script or manual commands](#prepare-the-repository)
- [Install and configure SNode.C](install-snodec.md)
- [Install and configure MQTTSuite](install-mqttsuite.md)
- [Update packages and troubleshoot](#updates-and-troubleshooting)

## Package repository

- [Browse production packages for Rocky Linux](https://github.com/SNodeC/OpenWRT/tree/packages/rocky)
- [SNode.C build results and versions](https://github.com/SNodeC/OpenWRT/blob/packages/snodec/README.md)
- [MQTTSuite build results and versions](https://github.com/SNodeC/OpenWRT/blob/packages/mqttsuite/README.md)

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

Continue with the [project installation instructions](#install-packages).

### Manual preparation

These commands configure the signed feed without installing SNode.C or MQTTSuite.

APT and RPM repositories use the same signing key. Its download filename is
`snodec-apt.asc`; the commands below install it under the RPM-specific name
`RPM-GPG-KEY-snodec`.

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
- [Return to the top of this guide](#rocky-linux)
