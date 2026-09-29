# <!-- project --> packages

Published versions and build results for every supported distribution, release
and architecture.

## Installation

- [Install <!-- project -->](https://github.com/SNodeC/OpenWRT/blob/main/docs/install-<!-- directory -->.md)
- [Browse the OpenWrt package catalog](https://github.com/SNodeC/OpenWRT/blob/main/docs/<!-- directory -->-package-options.md)
- [Choose a distribution and prepare its repository](https://github.com/SNodeC/OpenWRT/blob/main/README.md#distribution-and-architecture-matrix)

## Build and publication results

| Distribution | Release | Architecture | Version | Status | Published | Packages |
| --- | --- | --- | --- | --- | --- | --- |
<!-- targets -->

## Reading the table

**Version** is the version currently available for installation. A dash means
no published version is recorded. **Status** belongs only to <!-- project -->;
click a badge to open its build or publication job.

- **Pending:** waiting to build or publish.
- **Running:** building and testing.
- **Publishing:** updating the package repository.
- **Published:** packages have been pushed.
- **Failed**, **cancelled**, **skipped** or **superseded:** the rebuild did not publish.
- **Not built:** neither a result nor a published version is recorded.

Badges are snapshots refreshed by publication jobs. An unfinished or failed
rebuild leaves the previous published version available.

**Published** is the feed's latest publication date in UTC. Click it for the
manifest containing the full timestamp and source revisions. **Packages** opens
the distribution's shared package directory. Superseded files remain available
for 30 days after leaving the active index; package managers use the signed index.

## Repository help

- [Troubleshoot repository access](https://github.com/SNodeC/OpenWRT/blob/main/README.md#repository-troubleshooting)
- [Return to the package repository overview](../README.md)
