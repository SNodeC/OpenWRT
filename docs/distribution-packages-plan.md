# Distribution packaging refactor: discussion and plan

Recorded on 28 September 2026. This is a development planning document, not
installation documentation or a description of an already implemented system.

## Starting point and scope

Work takes place on `refactor/distribution-packages`, starting from main commit
`f1a21e6a909a699ddb688d6719f78fd067a56938`. The temporary
`backup/main-before-recipe-sync-20260927` branch was explicitly deleted locally
and on GitHub. The current production workflow remains operational on `main`.

The repository now serves OpenWRT, Raspberry Pi OS, Debian, Ubuntu, Rocky Linux
and Fedora. Treat them consistently in build status, publication, repository
access and installation documentation. Their native packaging mechanisms still
differ; consistency does not mean forcing them into the same build environment.

The current matrix contains 50 OpenWRT combinations, two Raspberry Pi OS
combinations and 24 other Linux combinations. Preserve the supported release
and architecture definitions throughout the refactor.

## Recipe ownership and branches

Keep the canonical OpenWRT recipes together on `main`:

- `net/snode.c/`
- `net/mqttsuite/`

CI should consume the recipes and orchestration from one captured packaging
repository commit, rather than independently moving recipe branches.

The earlier proposal to synchronize permanent `SNode.C` and `MQTTSuite` recipe
branches and merge them back into main was superseded. The preferred direction
is to retire those branches after verifying that no unique work needs preserving.
They have not yet been deleted. This concerns branches of the packaging
repository, not the separate upstream source repositories.

Current main already contains the working recipes. The old recipe branches still
contain obsolete source patches and test/configuration files; these must not be
reintroduced. Do not add source patches, rewrite upstream sources in CI, or move
CPack policy into CI. DEB/RPM component packaging remains upstream; OpenWRT
package selection and configuration remain in its recipes.

The obsolete `ci/openwrt-32bit`, `ci/openwrt-infra` and `ci/openwrt-packages`
branches and their associated local worktrees were already removed.

## Build and test organization

Use independent matrix instances for each distribution, release and architecture.
Each instance has its own build/test result, logs, artifacts and publication.
Do not create one duplicated workflow file per combination. Reusable workflows
may separate genuinely different build mechanisms:

- OpenWRT: official SDK and target execution through QEMU where applicable.
- Raspberry Pi OS: official OS-image filesystem.
- Other Linux distributions: appropriate distribution containers, with native
  execution or QEMU as required.

Run available upstream tests. Keep test policy in upstream test configuration;
do not recreate duplicate application test suites in the packaging repository
or introduce production test hooks.

At the start of development, run only these three representative combinations:

| Family | Release | Architecture |
| --- | --- | --- |
| Linux | Debian Trixie | amd64 |
| OpenWRT | 25.12 | x86_64 |
| Raspberry Pi OS | Trixie | arm64 |

Keep the complete matrix defined, but select this subset for development runs.
Use an isolated publication destination so development output cannot replace
production feeds. The exact destination is still to be chosen. Once the
mechanics work, enable the full matrix for architecture and release validation.
The subset alone cannot validate every package format, older distribution or ABI.

## Independent publication

The preferred design supersedes the earlier all-matrix publication gate:
publish a combination as soon as its own build and tests succeed. Other running
or failed combinations must not block it. A failed combination keeps its last
successfully published packages.

Serialize writes to the shared `packages` branch. Every publisher must start from
the latest snapshot, update only its destination and preserve other publications.
Reject stale builds that would replace newer packages. Never lose another
publisher's changes when updating the single-commit snapshot.

Repository boundaries determine the update operation:

- OpenWRT feeds have independent release/architecture directories.
- RPM feeds have independent distribution/release/architecture directories.
- APT suites share release metadata across architectures. Publishing one
  architecture must preserve the other architectures, then regenerate and sign
  the suite metadata coherently.

Preserve native repository layouts, package and index signing, source provenance,
and the existing retention policy. Superseded, unreferenced files remain for
30 days; cleanup runs during publication and scheduled maintenance. Current
referenced packages remain protected. Keep one authority for APT index generation.

Capture both upstream source revisions once per run. Use tags as the user-facing
source selectors and record resolved commits for reproducibility, rather than
replacing tag selection with hard-coded commit pins. Define publication ordering
and stale-run behavior explicitly before enabling concurrent live publication.

## README status and user documentation

Show status per distribution/release/architecture using badges and a table.
Separate two facts:

- Latest build: running, passed or failed, with a link to its run.
- Published feed: SNode.C and MQTTSuite package versions, publication date,
  source provenance and package/feed links.

A failed latest rebuild does not make an existing feed unavailable. Derive
published information from feed manifests, not merely workflow success. GitHub's
ordinary workflow badge does not directly represent individual matrix results;
the mechanism for per-combination badges remains to be implemented.

Keep generated publication information on the `packages` branch and link to it
from the main README. Avoid committing generated status to main after every
build. During development, show the three development combinations separately
from production publication status; expand coverage with the full matrix.

Remove CI-development history, obsolete validation explanations and feed-directory
migration sections from user-facing documentation. Preserve installation scripts,
manual installation, release/architecture tables, catalogs, feed links, updates
and useful troubleshooting, consistently for all distributions.

Give remaining non-main branches a concise README describing their actual
purpose where needed. Do not replace main's user-facing README with a branch
description. The published README is copied from `docs/package-repository.md`
during both publication and cleanup, so edit that authority rather than making
an isolated change that the next run overwrites.

Branch-specific README merge scripts and required PR checks were discussed but
not adopted. Retiring permanent recipe branches removes the main reason for that
extra machinery. No new branch protections or merge automation were authorized.

## Repository name

The proposed name is `SNodeC/packages`; `linux-packages` was another option.
No rename has happened, and the final rename remains a separate step.

Renaming the existing repository is preferred to creating a new repository: retain
history, settings, GitHub App integration and existing feeds. Update and verify
workflow references, installer URLs, documentation and package-manager feed URLs
together. Do not rely on GitHub redirects without testing package-manager access.

## Release triggers and tag-driven versioning

The initial proposal was one movable tag in each upstream repository, replacing
the separate `OpenWRT`, `RaspberryPiOS` and `Linux` trigger groups. Names discussed
included `Packages` and `Packaging`; no final new tag name was selected.

The discussion then moved toward real upstream release management:

- Use conventional versioned tags such as `v2.0.1` for SNode.C and `v1.0.2` for
  MQTTSuite. The projects have independent version sequences.
- Consider triggering packaging when a GitHub Release is published, with an
  explicit policy for prereleases, rather than treating every matching tag push
  as a production release.
- Select and record an explicit compatible pair of upstream releases. A release
  in one project must not silently select an arbitrary revision of the other.
- Published versioned release tags stay fixed. Packaging-only rebuilds increment
  the package revision, which package managers also compare when upgrading.

Tag-derived upstream CMake versions are possible, but are a separate task:

| Source form | Required version policy |
| --- | --- |
| Exact release tag | Derive MAJOR.MINOR.PATCH from that tag |
| Development checkout | Identify development commits distinctly from a release |
| Prepared release archive | Carry version metadata derived from the tag |
| Clone without usable tags or metadata | Explicit override or clear failure |
| Automatic GitHub source archive | Provide a deliberate export/fallback mechanism |

Calling `git describe` alone is insufficient for all these cases. A normal clone
usually fetches tags, but shallow or no-tags clones may not. Automatic GitHub
source archives do not automatically acquire files generated by a release job.
Archive metadata export and prepared release assets were discussed as options;
the final implementation is not selected.

Library VERSION can follow the release version. Deriving SOVERSION from the
release major is valid only with an explicit rule that ABI breaks require a major
release. Development builds after an ABI break need the upcoming ABI generation,
not blindly the previous release's major. Libraries/plugins governed by another
project's ABI require separate consideration. Do not change SOVERSION mechanically
before that policy is settled.

## Agreed implementation sequence

1. Refactor CI and publication first, keeping current upstream versioning and tag
   selectors initially. Use manual/refactor-branch runs and the three-job subset;
   keep production triggers operational until deliberate cutover.
2. Validate partial publication, preservation of other architectures, stale builds,
   concurrent writers, signatures and retention against temporary snapshots.
3. Enable and validate the entire matrix before calling the CI refactor complete.
4. Clean user documentation and carry out the repository rename as a coordinated,
   separately verified change.
5. Implement upstream tag-driven release/version handling separately, after
   choosing archive, development, prerelease and ABI policies; then connect it to
   package CI and retire the old trigger scheme.

No production C++ changes are planned for the CI refactor. Upstream release
notification and versioning changes require their own review. This document
records the direction and outstanding decisions; it does not claim that the
refactor, branch retirement, rename or release-versioning work is complete.
