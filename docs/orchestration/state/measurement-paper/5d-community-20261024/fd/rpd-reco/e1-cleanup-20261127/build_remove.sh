#!/bin/bash
# Builds e1-remove.sh from e1-remove.sh.in with the director-approved listing sha, computed from a listing file.
#   bash build_remove.sh <listing.txt>   (the stdout of e1-list.sh; refuses if e1-remove.sh exists)
set -euo pipefail
cd "$(dirname "$0")"
L=${1:?listing.txt}
[ ! -e e1-remove.sh ] || { echo "STOP: e1-remove.sh exists"; exit 2; }
# the listing lines are everything before "== summary"; their sha is computed here, never typed
sha=$(awk '/^== summary$/ {exit} {print}' "$L" | shasum -a 256 | cut -d' ' -f1)
node=$(awk '$1 == "listing_sha256" {print $2}' "$L")
[ "$sha" = "$node" ] || { echo "STOP: the listing's own sha line ($node) differs from its lines ($sha)"; exit 2; }
sed "s/@APPROVED@/$sha/" e1-remove.sh.in > e1-remove.sh
bash -n e1-remove.sh
echo "approved listing $sha"
echo "e1-remove.sh     $(shasum -a 256 < e1-remove.sh | cut -d' ' -f1)"
