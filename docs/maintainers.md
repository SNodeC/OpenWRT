# How this repository works

[← Installation overview](../README.md)

This page describes repository maintenance. Device installation belongs in the
[distribution guides](../README.md#distributions).

## Repository layout and links

The `main` branch contains recipes and documentation. Published packages, signed
indexes and [public keys](https://github.com/SNodeC/OpenWRT/tree/packages/keys)
live on the `packages` branch, using these paths:

| Distribution | Package files | Repository metadata |
| --- | --- | --- |
| OpenWrt | `openwrt/<series>/<architecture>/` | Signed opkg index or `packages.adb` in the same directory |
| Raspberry Pi OS | `raspberrypios/pool/<suite>/` | `raspberrypios/dists/<suite>/main/binary-<architecture>/` |
| Debian | `debian/pool/<suite>/` | `debian/dists/<suite>/main/binary-<architecture>/` |
| Ubuntu | `ubuntu/pool/<suite>/` | `ubuntu/dists/<suite>/main/binary-<architecture>/` |
| Rocky Linux | `rocky/<major>/<architecture>/Packages/` | `rocky/<major>/<architecture>/repodata/` |
| Fedora | `fedora/<release>/<architecture>/Packages/` | `fedora/<release>/<architecture>/repodata/` |

GitHub directory links let you browse packages. Package managers use the raw file
URLs in the installation guides; raw URLs do not provide directory listings.


## Branches and history

- `main` owns the OpenWrt recipes in `net/`, CI in `ci/` and `.github/workflows/`, and user documentation in `docs/`.
- `packages` holds production package files, signed indexes, signing keys and generated status pages.
- `packages-dev` is an archived validation snapshot. Production no longer publishes there. Its [archive README](https://github.com/SNodeC/OpenWRT/blob/packages-dev/README.md) is retained unchanged.

The package branch uses a single snapshot commit after publication rather than
accumulating package history. The recipes remain together on `main`; the
[historical refactor plan](distribution-packages-plan.md) records earlier designs
and the transition to production. Historical workflows in that record are not
additional current entry points.

## Publication model

A source version-tag notification selects the source release. Each target has
its own sequence: build and test SNode.C, publish it, then build and test MQTTSuite
against those packages and publish MQTTSuite. An application-only notification
uses the target's already-published framework packages. Publication writes are
serialized; targets do not wait for the entire build matrix to finish.

A failed or unfinished rebuild leaves the previous feed available. Superseded
files remain available for 30 days after leaving the active index so clients
with cached indexes can finish downloads. Cleanup runs during publication;
there is no independent scheduled cleanup workflow. The retention record spans
all feeds, while each publication checks and cleans its affected feed.

## Workflows and source records

- [Release notification entry point](../.github/workflows/openwrt.yml)
- [Distribution matrix](../.github/workflows/packages.yml)
- [Per-target dependency chain](../.github/workflows/package-target.yml)
- [Build and tests](../.github/workflows/package-build.yml)
- [Serialized publication](../.github/workflows/package-write.yml)
- [Workflow runs](https://github.com/SNodeC/OpenWRT/actions/workflows/openwrt.yml)

Each feed's `build.json` records package versions, file checksums, source tags
and resolved commits, the build run and publication details. APT records group
architectures within a suite. Status badges describe the latest build attempt;
the manifest's package versions describe what is actually available. The
publication date belongs to the feed and can change when either project publishes.

The captured source and build records provide provenance; they do not replace
package or index signatures. Use the **Published** links in the generated status
tables to inspect the manifest associated with a feed.

## Coverage and ordering

OpenWrt targets come from `ci/platforms.json`, other Linux targets from
`ci/linux.json`, and Raspberry Pi OS releases from `ci/raspberrypi.json`.
Presentation sorts package architectures alphabetically without changing CI's
matrix order or scheduling. Raspberry Pi builds use the common ARMv8-A baseline,
without board-specific CPU tuning.

Ubuntu coverage policy is the two latest LTS releases plus the latest stable
interim release when newer. New releases require an explicit matrix update and
successful validation. Rocky coverage does not imply separately validated RHEL
or AlmaLinux coverage.

## Signing-key verification

The committed public keys are in [ci/keys](../ci/keys). Compare them with the
production keys before updating the fingerprints shown on the landing page:

```sh
for key in ci/keys/*; do
  git show "origin/packages:keys/${key##*/}" | cmp - "$key" || exit 1
done
```

Compute the native usign fingerprint, the SHA-256 digest of the APK public key
in DER form, and the OpenPGP primary-key fingerprint:

```sh
usign -F -p ci/keys/snodec-usign.pub
```

```sh
openssl pkey -pubin -in ci/keys/snodec-apk.pem -outform DER |
  openssl dgst -sha256
```

```sh
gpg --batch --show-keys --with-colons ci/keys/snodec-apt.asc |
  awk -F: '$1 == "fpr" { print $10; exit }'
```

APT and RPM use the same OpenPGP key. The APK value is a full public-key SHA-256
fingerprint, not a filename or an APK-specific shortened key identifier.

## Further maintenance documentation

- [OpenWrt recipe configuration and build options](openwrt-build.md)
- [Recorded design and release workflow history](distribution-packages-plan.md)
- [Package status](https://github.com/SNodeC/OpenWRT/blob/packages/README.md)
