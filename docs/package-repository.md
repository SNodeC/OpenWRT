# SNode.C and MQTTSuite Linux packages

This is the binary feed for `SNodeC/OpenWRT`, published on branch `packages`.
OpenWrt 24.10 uses IPK/opkg; 25.12 uses APK. Each series supports the same
25 platform variants, including all devices described by the `infra` branch.
The RISC-V architecture is named `riscv64_riscv64` on 24.10 and
`riscv64_generic` on 25.12. See `ci/platforms.json` on `main` for the matrix.

## Distribution feeds

| Distribution | Repository root | Metadata |
|---|---|---|
| Debian | `debian/` | `dists/{trixie,forky,sid}/` and `pool/` |
| Ubuntu | `ubuntu/` | `dists/{noble,resolute}/` and `pool/` |
| Rocky Linux | `rocky/<major>/<architecture>/` | `repodata/`, RPMs in `Packages/` |
| Fedora | `fedora/<release>/<architecture>/` | `repodata/`, RPMs in `Packages/` |
| Raspberry Pi OS | `raspberrypios/` | `dists/{bookworm,trixie}/` and `pool/` |
| OpenWrt | `openwrt/<series>/<architecture>/` | opkg or APK index |

Installation guides: [OpenWrt](https://github.com/SNodeC/OpenWRT/blob/main/docs/openwrt.md),
[Raspberry Pi OS](https://github.com/SNodeC/OpenWRT/blob/main/docs/raspberrypi.md),
[Debian](https://github.com/SNodeC/OpenWRT/blob/main/docs/debian.md),
[Ubuntu](https://github.com/SNodeC/OpenWRT/blob/main/docs/ubuntu.md),
[Rocky Linux](https://github.com/SNodeC/OpenWRT/blob/main/docs/rocky.md) and
[Fedora](https://github.com/SNodeC/OpenWRT/blob/main/docs/fedora.md).
See the [complete matrix](https://github.com/SNodeC/OpenWRT/blob/main/README.md#distribution-and-architecture-matrix)
for all distributions and architectures.

## Feed directory migration

The feeds now use distribution names. The old paths have been removed:

| Distribution | Previous path | Current path |
|---|---|---|
| OpenWrt | `releases/<series>/<architecture>/` | `openwrt/<series>/<architecture>/` |
| Raspberry Pi OS | `apt/` | `raspberrypios/` |

In existing feed URLs, replace `/SNodeC/OpenWRT/packages/releases/` with
`/SNodeC/OpenWRT/packages/openwrt/`, or `/SNodeC/OpenWRT/packages/apt` with
`/SNodeC/OpenWRT/packages/raspberrypios`. Keep the release, architecture and
any `packages.adb` suffix unchanged. Edit the file containing your existing entry:

- OpenWrt 24.10: `/etc/opkg/customfeeds.conf` or your custom `/etc/opkg/*.conf` file;
  then run `opkg update`.
- OpenWrt 25.12: `/etc/apk/repositories.d/snodec.list`; then run `apk update`.
- Raspberry Pi OS: `/etc/apt/sources.list.d/snodec.list` (or the `URIs` field in
  your `.sources` file); then run `sudo apt-get update`.

Signing keys, packages and signed indexes are unchanged. No package reinstall is
needed. Retention timestamps are preserved. The installation instructions below
and the preparation scripts already use the new paths.

## Configure your router

Keep the official distribution feeds enabled for dependencies. These feeds
contain userspace applications, not firmware or kernel modules. Vendor firmware
is not assumed compatible merely because its CPU matches.

The optional `ci/install-feed.sh` script on `main` performs this setup and
installation explicitly on a router, rejecting unsupported/unpublished feeds.
Pass `--prepare` to import the signing key, configure the feed and update package
lists without installing packages. Without options it installs the full selection.
CI never runs it on your devices.

Read `/etc/openwrt_release` and select its `DISTRIB_ARCH` and release series.
For example, for 24.10 on `aarch64_cortex-a53`, download the public key:

```sh
wget -O /tmp/snodec-usign.pub https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/keys/snodec-usign.pub
opkg-key add /tmp/snodec-usign.pub
```

Add this line to `/etc/opkg/customfeeds.conf` (replace the architecture as needed):

```text
src/gz snodec https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/24.10/aarch64_cortex-a53
```

For 25.12, install the APK public key instead:

```sh
wget -O /etc/apk/keys/snodec-apk.pem https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/keys/snodec-apk.pem
```

Create `/etc/apk/repositories.d/snodec.list` containing:

```text
https://raw.githubusercontent.com/SNodeC/OpenWRT/packages/openwrt/25.12/aarch64_cortex-a53/packages.adb
```

Do not mix release series or architecture directories. There is no automatic
recursive directory discovery. Configure the correct feed once, then install:

```sh
# 24.10
opkg update
opkg install mqttsuite-full snode.c-full snode.c-apps snode.c-control
# 25.12
apk update
apk add mqttsuite-full snode.c-full snode.c-apps snode.c-control
```

Individual applications and modules are also installable. Configure services
before enabling them. Public key files on `main` provide a separate reference
for checking the initial key download. Never disable signature verification.

## Build and publication policy

Only creation/movement of the `OpenWRT` tag in SNode.C or MQTTSuite initiates
OpenWrt CI. Branch pushes, pull requests, releases, schedules and manual
workflow dispatch are not enabled. Both tags must exist. GitHub loads tag-push
workflows from the tagged commit, so that commit must contain the source
repository's `.github/workflows/openwrt.yml`. Moving a tag to older code without
that workflow cannot trigger Actions. Push tags using a user/App credential;
GitHub suppresses recursive push events made with an Actions `GITHUB_TOKEN`.

The source workflows notify this repository using a dedicated GitHub App.
Install it on `SNodeC/OpenWRT` with Contents: write permission, then configure
`OPENWRT_APP_ID` (Actions variable) and `OPENWRT_APP_PRIVATE_KEY` (secret) in
both source repositories. The App is used only to create repository dispatches;
it does not need access to the signing secrets.

This repository requires `OPENWRT_USIGN_KEY` and `OPENWRT_APK_KEY` secrets
matching the public files in `ci/keys`. Private keys are never committed or
included in artifacts. Previously tracked private keys must not be reused.

Source checkouts always use `refs/tags/OpenWRT`, including submodules at the
revisions specified by those tagged sources. All matrix jobs consume the same
fresh source archives. Disposable SDK recipes receive checksums of those archives
so the SDK accepts the shared snapshot without downloading the tag again. These
archive checksums are not source revision pins. Commit identities in `build.json`
only detect moving tags and identify builds; they never replace tag references.
No downloaded source archive cache is reused between runs.

The [official packages CI](https://github.com/openwrt/packages/blob/master/.github/workflows/multi-arch-test-build.yml)
uses the OpenWrt SDK. This workflow uses official SDK archives directly:
the `gh-action-sdk` wrapper has no hook for our full-package configuration and existing
SDK audits. SDK release numbers are maintained in `ci/platforms.json`; downloads
are checked against the official release's SHA256 checksums. GitHub Actions use
version tags, not commit pins.

Publication requires all 50 builds and four clean-VM installation/runtime jobs.
Matrix jobs do not stop when a different job fails. Packages get increasing
integer `PKG_RELEASE` values from the centralized workflow run number plus one
(the first CI revision is 2, above the existing recipe revision 1). APK does not
accept dotted revisions. Reruns retain their revision; an already-published
revision cannot be overwritten.
A publisher checks the complete matrix, source generation and file checksums,
then publishes all architectures together as a single root commit, replacing
the `packages` branch with an explicit force-with-lease against its fetched tip.
Each publication has no parent commits; a concurrent branch update is rejected.
Source and recipe branch history is unaffected. It preserves old package files for
cached indexes and rejects stale/equal publication revisions. A tag change
during the run invalidates it; its later dispatch builds the current tags.
The old feed remains available if any job fails.

GitHub raw content caches can briefly serve indexes from different commits.
Retaining prior package files avoids breaking clients with an older index;
clients encountering a propagation delay can retry their update.

## Validation

Run `python3 tests/test_repository.py` for publication boundary tests.
Each SDK build runs the existing configuration, RPATH and package audits.
The package audit supports APK and IPK and compares ELF class, endianness and
machine to that SDK's libc. Four QEMU guests (x86-64 and AArch64, both releases)
install the signed staged feed with official dependencies, exercise TCP, TLS,
WS and WSS MQTT, and test broker service restart. Logs are retained in Actions.
Physical-router behavior is not implied by QEMU results.

## Raspberry Pi OS APT feed

ARM64 `.deb` packages for Raspberry Pi 3, 4 and 5 live in `raspberrypios/pool/`, with
signed Bookworm and Trixie indexes in `raspberrypios/dists/` and the public key at
`keys/snodec-apt.asc`. See the
[installation instructions](https://github.com/SNodeC/OpenWRT/blob/main/docs/raspberrypi.md).

The independent `RaspberryPiOS` source tags trigger APT builds; `OpenWRT` tags
trigger OpenWrt builds. Each publishes after its own checks pass. A shared
publication lock and snapshot preserve the other package format’s files.

## Retention and maintenance

Files referenced by a current publication are always retained. Superseded
OpenWrt `.ipk`/`.apk` packages, distribution `.deb`/`.rpm` packages, obsolete APT
SHA256 `by-hash` indexes and superseded RPM metadata are removed after
**30 days without a current reference**.
The clock starts when cleanup first observes that a file is unreferenced, not
from its build date or filesystem timestamp. Existing leftovers receive a full
30-day grace period when this policy is first enabled.

`retention.json` on the `packages` branch records retirement dates and checksums.
A renewed reference clears the retirement date; changed file contents restart it.
Cleanup validates all current publication manifests and their file checksums
before deleting anything. The inventories accompany the opkg, APK, APT and RPM indexes
produced by the publishers; missing, incomplete or inconsistent inventories stop
cleanup. Keys, current metadata and other repository files are not candidates.

The same cleanup runs after each publication and in **Package retention cleanup**,
scheduled daily at **04:23 UTC** (GitHub may delay scheduled runs). It can also be
started manually from Actions. Maintenance never builds packages. Both workflows
share the `package-publication` lock, queue waiting jobs with `queue: max`,
and use a force-with-lease single-commit
snapshot. An unchanged cleanup produces no new commit.

The revision-14 Debian upgrade-test archives are permanently stored in the
[Debian upgrade fixtures release](https://github.com/SNodeC/OpenWRT/releases/tag/debian-upgrade-fixtures),
with checksums verified by the tests; they do not depend on files retained in the
live package pool.
