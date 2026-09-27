#!/usr/bin/env bash
# Both publishers and maintenance hold the package-publication job lock.
set -euo pipefail
cd "$1"
previous=$2
message=$3
git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add .
if git diff --cached --quiet; then exit 0; fi
snapshot=$(git commit-tree "$(git write-tree)" -m "$message")
git push --force-with-lease="refs/heads/packages:$previous" origin "$snapshot:refs/heads/packages"
