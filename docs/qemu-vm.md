# AArch64 OpenWrt VM verification

Verified on 22 September 2026. In the validation workspace, the VM was installed
in `sdks/qemu-openwrt-25.12.5/` and left running. All VM images, credentials,
configuration, test programs and logs are inside the workspace. Only Debian's
`qemu-system-arm` package and its dependencies were installed system-wide.
No application recipe or upstream source was changed during this VM test.
These local artifacts are ignored by Git and are not included in a fresh clone.

## Access

These commands apply to the original validation workspace, where the local
VM and helper scripts already exist. Run them from the repository root:

```sh
# Connect to the running VM:
./sdks/qemu-openwrt-25.12.5/ssh.sh

# Shut it down cleanly:
./sdks/qemu-openwrt-25.12.5/ssh.sh poweroff

# Start it again after shutdown:
./sdks/qemu-openwrt-25.12.5/start.sh

# Repeat the four broker/CLI message tests while it is running:
python3 sdks/qemu-openwrt-25.12.5/test-mqtt.py
```

SSH is forwarded on `127.0.0.1:2222`, native MQTT on `127.0.0.1:18883`, and
broker HTTP/WebSocket on `127.0.0.1:18884`. The broker dashboard is available
at <http://127.0.0.1:18884/clients>. Forwarded ports bind only to localhost.
The helper keeps SSH keys and known-host records in the VM directory.

The guest has four emulated Cortex-A53 CPUs, 2 GiB RAM and a 2 GiB persistent
ext4 disk. QEMU uses software emulation on the x86-64 host. The image is
OpenWrt's generic `armsr/armv8` machine, not an emulation of GL-MT3000 hardware.

## Images and installation

The kernel and ext4 root filesystem came from the official
[OpenWrt 25.12.5 armsr/armv8 release](https://downloads.openwrt.org/releases/25.12.5/targets/armsr/armv8/).
Both downloads passed SHA256 verification:

| File suffix | SHA256 |
| --- | --- |
| `generic-kernel.bin` | `8cf43c4901efae72b0a04bb655158e03335067e8757926bca4c81d5c952aca51` |
| `generic-ext4-rootfs.img.gz` | `03172dd9a91e7cb477ab73bcb5de544bfe19f42698d7f66d9b2bb80ca692eaa6` |

The guest runs Linux 6.12.94 and OpenWrt `r33051-f5dae5ece4`. Its APK
architecture list contains both `aarch64_generic` and `aarch64_cortex-a53`;
the latter matches the emulated CPU and the previously built project APKs.

All **76 project APKs** were installed using `apk add --allow-untrusted`,
including their real installation scripts. SHA256 checks confirm that the
installed input archives are identical to the GL-MT3000 build artifacts.
Dependencies were resolved through the VM's official feeds. Its kernel and
Bluetooth modules use the **armsr kernel ABI**, rather than the incompatible
filogic kernel packages in the router bundle. APK installed 91 additional
packages, bringing this VM to 296 packages in total.

## Verified behavior

| Check | Result |
| --- | --- |
| All five MQTTSuite executables | Help/configuration startup works |
| SNode.C control tool | Help and inspection of broker's `in-http.local.port` work |
| SNode.C IPv4 echo server | Returned exact `snodec-qemu-echo-ok` payload |
| Broker and CLI over native MQTT | Publish/subscribe passed |
| Broker and CLI over MQTT/TLS | Publish/subscribe passed with explicit test CA |
| Broker and CLI over WS | HTTP upgrade, MQTT session and publish/subscribe passed |
| Broker and CLI over WSS | TLS, HTTP upgrade, MQTT session and publish/subscribe passed |
| Integrator over WS | Mapped topic `value` into `mapping/json`, delivering `{"state":"vm-integrator-ok"}` |
| Broker HTTP dashboard | Redirect and resulting page returned successfully |
| Dynamic libraries | `dlopen(RTLD_NOW)` passed for all five application WebSocket plugins, three SNode.C WebSocket libraries and both mapping plugins |
| Actual plugin use | Process maps confirm broker, CLI and integrator loaded their application-specific WebSocket libraries |
| Guest reboot | All 76 project packages retained; broker and integrator restarted under procd; integrator reconnected over WS |

These checks use the installed RPATHs and normal musl loader behavior, with
no `LD_LIBRARY_PATH` override or copied-library workaround. The TLS client
trusts the generated test certificate; `ca-cert-accept-unknown` stays false.
The test certificate expires two days after generation and must be renewed
for later TLS tests.

## Runtime observations

- The integrator initially exited with a missing required endpoint and procd
  retried it until the crash limit. Supplying
  `/etc/snode.c/mqttintegrator.conf`, enabling its IPv4 WS endpoint and disabling
  unused endpoints made the service run and map messages. The VM retains that
  configuration. The recipe should gain the same missing-config startup guard
  already used by the bridge, or an equivalent explicit configuration policy.
- A broker restart temporarily left port 8080 unavailable; the existing retry
  mechanism subsequently bound it successfully. This is consistent with the
  default `reuse-address=false` and recently closed connections. The first WS
  test recorded the refusal; the complete repeat after listener readiness
  passed. Enabling address reuse for deployed server listeners should be
  considered if prompt restarts are required.
- SNode.C applications return **2** for help/configuration-only exits. The
  framework's event loop assigns this when configuration bootstrap chooses
  not to enter the event loop; it is not a missing-library failure.
- `snodec-control` successfully inspects the broker, but emits warnings because
  framework startup/shutdown logs accompany configuration discovery output.
  That is a source-level output-separation issue, not an APK/RPATH failure.

No recipe changes were made to hide these observations. Bridge forwarding,
MQTTStore database writes, mapping-plugin behavior beyond loading, IPv6/Unix
traffic and physical Bluetooth/router hardware behavior were not exercised.
The bridge and Store executables and their WebSocket plugins passed startup
and load checks only.

## Evidence

The VM directory contains `logs/package-install.log`, `logs/mqtt-results.json`,
per-transport publisher/subscriber logs, process maps, `logs/dlopen-check.log`,
`logs/echo-response.log`, `logs/integrator-mapping-result.log`, installed-package
lists and serial output. Earlier failures remain recorded separately.
`test-mqtt.py` checks subscription acknowledgment, publisher exit status and
the delivered payload; `dlopen-check.c` is the separate target-side loader test.

VM validation changed **zero production lines**. Test programs added **86 lines**;
VM launch/access helpers add **19 lines**; the network and integrator test
configuration fixtures add **28 lines**. These files are confined to the
ignored `sdks/` directory. Documentation and generated logs/configuration are
excluded from those counts. Previous recipe/build change accounting remains in
[verification.md](verification.md).
