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

These commands configure the signed feed without installing SNode.C or MQTTSuite.

Enable CRB and EPEL for dependencies first:

```sh
sudo dnf install -y dnf-plugins-core epel-release
sudo dnf config-manager --set-enabled crb
```

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

```sh
sudo dnf install snodec mqttsuite
```

## Selective installation

For only the broker and command-line client:

```sh
sudo dnf install mqttsuite-broker mqttsuite-cli
```

Required SNode.C components are installed automatically. See the shared
[component package guide](linux.md#component-packages) for package names and
[application configuration](linux.md#configure-applications).

## Updates and troubleshooting

```sh
sudo dnf upgrade 'snodec*' 'mqttsuite*'
```

After a distribution upgrade, select a supported matching release and refresh
metadata. For missing feeds, signature errors or dependency failures, see
[repository troubleshooting](../README.md#repository-troubleshooting).

## Build and validation

These targets use the independent `Linux` source tags. See
[shared CI and publication details](linux.md#ci-and-publication) for build,
installation, runtime tests and publication gates.
