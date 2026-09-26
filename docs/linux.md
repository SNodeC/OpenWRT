# DEB and RPM component packages

Installation guides: [Debian](debian.md) · [Ubuntu](ubuntu.md) ·
[Rocky Linux](rocky.md) · [Fedora](fedora.md) · [Raspberry Pi OS](raspberrypi.md).
OpenWrt has [its own package names and guide](openwrt.md).

## Component packages

DEB and RPM packages follow upstream CMake components. The `snodec` and
`mqttsuite` metapackages install all components of their respective projects.
Selective application installs pull their required framework modules automatically.

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
# RPM distributions
dnf list --available 'snodec-*'
```

## Configure applications

Installation creates the `snodec` system group and installs executables in
`/usr/bin`; it does not start network services. Run `mqttbroker --help` and
`mqttcli --help` for configuration options. Start a foreground broker explicitly
with `mqttbroker --daemonize=false`. Configure listeners, credentials and TLS
certificates for your deployment. The store requires a configured database.
For a persistent service, configure systemd with the desired user and arguments.
See the [MQTTSuite documentation](https://github.com/SNodeC/mqttsuite#readme).

The APT and RPM public signing key has fingerprint
`8BBF D49E 3C82 6FDB 1416 C79E 6004 6744 B15B 0E05`.

## CI and publication

The independent `Linux` tag in **both** source repositories selects the source
generation. Creating or moving either tag requests all 24 targets. Tags are used
for checkout; recorded commit IDs only prove provenance. `OpenWRT` and
`RaspberryPiOS` keep their separate roles. The matrix is maintained in
[`ci/linux.json`](../ci/linux.json); container images use distribution release tags.

x86-64 and ARM64 build natively on GitHub runners. ARM32 and RISC-V use QEMU
where required. Build and installation containers share the runner’s network
namespace, as the Raspberry Pi OS chroots do, so IPv6 tests see configured host
interfaces instead of an IPv4-only Docker bridge. Each target runs the upstream SNode.C tests, creates CPack
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
