# Verification result

Built and checked on 22 September 2026 for GL.iNet GL-MT3000 using the official
OpenWrt 25.12.5 mediatek/filogic SDK (GCC 14.3.0, musl, aarch64_cortex-a53).

| Source | Revision | Package version |
| --- | --- | --- |
| SNode.C feature/per-operation-socket-flows | `bb63e8a87aeda88123e8c0d72cb6d298908a9fe6` | 2.0.0-r1 |
| MQTTSuite master | `f96daffdbae8f95531a73fb52c9d22d410044211` | 1.0.1-r1 |

The delivered configuration enables all modules, all five MQTTSuite
applications, both mapping plugins, the SNode.C demos/control tool, and every
MQTT transport, including TLS over Unix sockets.

| Check | Result |
| --- | --- |
| Full SDK cross-build and package creation | 67 SNode.C + 9 MQTTSuite APKs; passed |
| Final archive audit | 76 packages, 142 AArch64 ELF files; zero errors |
| ELF runtime lookup | Every DT_NEEDED resolves through that package's declared dependency closure and ELF search paths |
| ABI/SONAME and symlinks | SNode.C 2, MQTTSuite application libraries 1, application WebSocket plugins 2; passed |
| Dynamic WebSocket loads | HTTP upgrade library and per-application MQTT plugin exist in each app's dependency closure; passed |
| RPATH leakage | No SDK staging/build paths in final RPATH/RUNPATH entries |
| CLI-only, IPv4 TCP, no TLS/WS | Builds; 2 ELF files audited; no disabled plugin/transport dependencies |
| All five applications, IPv4 TCP, no MQTT TLS/WS | Builds; 137 ELF files audited; no disabled WebSocket plugins/dependencies |
| Kconfig tests | After splitting ownership: 7 SNode.C cases, 2 MQTTSuite cases and 2 integration cases; all passed, retaining the original assertions and adding per-project inventory checks |
| RPATH helper tests | 3 test methods: actual ELF paths/tags/permissions, missing inputs, injected patchelf failures; passed |
| Reconfiguration without cache deletion | Nine non-default SNode.C CMake values applied, then all nine defaults restored; passed |
| APK install dependency simulation | 76 project APKs + 30 dependency APKs solve successfully; 106 packages, 49.0 MiB installed size |
| Service shell syntax and diff whitespace | Passed |

The install check used an isolated empty user-mode APK database, `--simulate`,
`--no-scripts`, and `--no-network`. It executed no target binaries or package
installation scripts. Subsequent [QEMU VM verification](qemu-vm.md) installed
all 76 project packages and tested real MQTT/TLS/WS/WSS traffic, dynamic
WebSocket loading, integrator mapping and SNode.C echo behavior. **Physical
router execution, database writes and Bluetooth hardware operation remain
unverified.** The VM report records configuration and restart observations.

The SDK feed's unrelated libcurl/LDAP Kconfig recursion diagnostic remains;
these recipes have no Kconfig dependency cycles. Full-build logs and archive
inventories accompany the APKs. Build prerequisites use the SDK's pinned feeds.
No changes were made in either upstream source repository.

The branch split changed no recipe, helper, service or source patch bytes.
The configuration cases and RPATH tests passed again from the project
worktrees. The SDK's active `.config` was unchanged. The archive/build/runtime
results above therefore remain evidence for the same production files; no
new cross-build was required merely to reorganize their Git ownership.
Whitespace checks exclude unified-diff context markers in patch files;
the patches parse successfully and their added source lines were checked
separately for trailing whitespace.

## Changes implemented

- Pinned both requested branch tips and their source archive hashes; updated
  SNode.C to ABI 2 and added a checked spdlog download.
- Kept every runtime layer independently selectable, including all L2CAP and
  RFCOMM layers; added a separate control-tool package, MQTTStore, and two
  separate mapping-plugin packages.
- Replaced Make-time dependency filtering with OpenWrt conditional dependency
  declarations. Fixed the multiplexer selection cycle, IPv6 reuse option
  names, Nagle options, IPv6-only values and stale CMake defaults. Added the
  three write-queue defaults and MQTTStore's eight transport options.
- Used a separate MQTTSuite CMake build directory to prevent the private/public
  Log.h collision. Recipe patches honor application selection, omit disabled
  WebSocket targets/helpers, enforce broker WS/WSS switches, and correct
  SNode.C's handling of optional CMake components.
- Replaced the error-masking RPATH macro with one normalization helper, and
  verified library lookup in stripped APK payloads. Kept both required ABI
  symlinks and real plugin files.
- Removed site-specific service arguments and used the existing persistent
  SNode.C application configuration with foreground procd supervision.

## Change accounting

Recipe/configuration/service/helper lines: **+438 / -568**
(net -130). Applied CMake/C++ patch changes: **+60 /
-36** (net +24). The source additions make existing
application/transport selections effective and guard WebSocket-only code;
the optional-component correction removes code. Combined functional line
change: **-106**.

Tests, case data and configuration fixture after the split: **+444 / -0**
lines relative to the original repository (previously +298). The extra test
data gives each project its own cases while one runner owns SDK execution.
The split itself adds no production lines. Documentation and
unified-diff context lines are excluded from these functional counts.
