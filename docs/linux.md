# Debian, Ubuntu, Rocky Linux and Fedora

Individual SNode.C and MQTTSuite component packages are built separately for each
supported distribution, release and architecture. Keep the distribution's normal
repositories enabled for dependencies. The `snodec` and `mqttsuite` metapackages
install all components; `mqttsuite-broker` and `mqttsuite-cli` provide a smaller
broker/client installation. Package ownership comes from upstream CMake components.

| Distribution | Suite/version | Architectures | Format |
|---|---|---|---|
| Debian stable | `trixie` | `amd64`, `arm64`, `armhf`, `riscv64` | DEB |
| Debian testing | `forky` | `amd64`, `arm64`, `armhf`, `riscv64` | DEB |
| Debian unstable | `sid` | `amd64`, `arm64`, `armhf`, `riscv64` | DEB |
| Ubuntu 24.04 LTS | `noble` | `amd64`, `arm64` | DEB |
| Ubuntu 26.04 LTS/current | `resolute` | `amd64`, `arm64` | DEB |
| Rocky Linux | `9`, `10` | `x86_64`, `aarch64` | RPM |
| Fedora | `43`, `44` | `x86_64`, `aarch64` | RPM |

Ubuntu policy: two latest LTS releases plus the current stable interim release
when newer than the latest LTS. No unreleased Ubuntu versions are included.
Rocky 10 requires x86-64-v3 on x86 systems. Rocky 9 builds use GCC Toolset 14.
Support for Rocky does not imply separately validated RHEL or AlmaLinux support.

## Debian and Ubuntu

Use the suite matching the installed system; do not mix distribution releases.
Example for Debian Trixie (replace `debian trixie` with `ubuntu noble`,
`ubuntu resolute`, `debian forky` or `debian sid` as appropriate):

```sh
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -d -m 755 /etc/apt/keyrings
curl -fsSL https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/keys/snodec-apt.asc |
    sudo tee /etc/apt/keyrings/snodec.asc >/dev/null
sudo chmod 644 /etc/apt/keyrings/snodec.asc
printf '%s\n' 'deb [signed-by=/etc/apt/keyrings/snodec.asc] https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/debian trixie main' |
    sudo tee /etc/apt/sources.list.d/snodec.list
sudo apt-get update
```

APT selects the native architecture. Codenames prevent accidental release changes
when Debian's stable/testing aliases move. Install the full selection:

```sh
sudo apt-get install snodec mqttsuite
```

Or install only the broker and command-line client:

```sh
sudo apt-get install mqttsuite-broker mqttsuite-cli
```

## Rocky Linux and Fedora

On Rocky, enable CRB and EPEL for additional dependencies:

```sh
sudo dnf install -y dnf-plugins-core epel-release
sudo dnf config-manager --set-enabled crb
```

Download the public key (shared with the APT feeds):

```sh
sudo curl -fsSL https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/keys/snodec-apt.asc \
    -o /etc/pki/rpm-gpg/RPM-GPG-KEY-snodec
sudo rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-snodec
```

Create `/etc/yum.repos.d/snodec.repo`. For Fedora replace `rocky` with `fedora`;
leave `$releasever` and `$basearch` literal so DNF expands them:

```ini
[snodec]
name=SNode.C and MQTTSuite
baseurl=https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/rocky/$releasever/$basearch/
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-snodec
```

```sh
sudo dnf makecache
sudo dnf install snodec mqttsuite
```

For a smaller installation use `sudo dnf install mqttsuite-broker mqttsuite-cli`.

## CI and publication

The independent `Linux` tag in **both** source repositories selects the source
generation. Creating or moving either tag requests all 24 targets. Tags are used
for checkout; recorded commit IDs only prove provenance. `OpenWRT` and
`RaspberryPiOS` keep their separate roles. The matrix is maintained in
[`ci/linux.json`](../ci/linux.json); container images use distribution release tags.

x86-64 and ARM64 build natively on GitHub runners. ARM32 and RISC-V use QEMU
where required. Each target runs the upstream SNode.C tests, creates CPack
component packages, then installs from the signed feed in a fresh container.
Tests exercise selective dependency installation, the full component inventory,
application startup, MQTT TCP/TLS and MQTT over WebSocket/WSS. Containers test
userspace compatibility, not physical hardware, boot or service-manager behavior.

Publication requires the entire Linux matrix to pass. APT indexes are combined
per suite with one index per architecture; RPM metadata remains per release and
architecture. RPM packages and `repomd.xml` are signed. APT uses signed `InRelease`
and `Release.gpg` plus by-hash indexes. The existing `APT_SIGNING_KEY` secret and
public key serve both formats; no additional signing secret is required.

All feeds share the existing publication lock and parentless `packages` snapshot.
Publication preserves other distributions. Superseded packages and metadata use
the shared [30-day retention policy](package-repository.md#retention-and-maintenance).
