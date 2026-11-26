#!/bin/bash
# EVW5D: write the bound copies of the launch scripts into launch/bound/, every pin computed by command, none typed.
#   bash fill_pins.sh <tool commit>
# The tool commit must be an ancestor of HEAD (or HEAD) and carry, byte for byte, the evw5d.py and sbatch_evw5d.sh of
# this checkout; the templates (launch/*.sh, with __PLACEHOLDER__ pins) stay as they are, because the tests use them.
# Order: evw5d.py and sbatch_evw5d.sh at the tool commit -> connect, hpss and the launcher's checker pin -> the
# connect, post and hpss digests -> the launcher. Prints every digest, and refuses if any placeholder is left.
set -euo pipefail
TOOLC=${1:?tool commit}
HERE=$(cd "$(dirname "$0")" && pwd)
TOP=$(git -C "$HERE" rev-parse --show-toplevel)
B="$HERE/bound"
[ ! -e "$B" ] || { echo "STOP: $B exists"; exit 2; }
full=$(git -C "$TOP" rev-parse --verify "$TOOLC^{commit}")
git -C "$TOP" merge-base --is-ancestor "$full" HEAD || { echo "STOP: $full is not an ancestor of HEAD"; exit 2; }
sha_at() { git -C "$TOP" show "$full:$1" | shasum -a 256 | cut -d' ' -f1; }
EVW=$(sha_at nd-unfolding/evw5d/evw5d.py)
SB=$(sha_at nd-unfolding/evw5d/sbatch_evw5d.sh)
CAP=$(sha_at nd-unfolding/ess_e/ess_capture.py)
[ "$EVW" = "$(shasum -a 256 "$TOP/nd-unfolding/evw5d/evw5d.py" | cut -d' ' -f1)" ] || { echo "STOP: evw5d.py differs from the tool commit's"; exit 2; }
[ "$SB" = "$(shasum -a 256 "$TOP/nd-unfolding/evw5d/sbatch_evw5d.sh" | cut -d' ' -f1)" ] || { echo "STOP: sbatch_evw5d.sh differs"; exit 2; }
[ "$CAP" = 4755681f6ba8bd5060fe6ed4902e940b71e3b641d87c978a1f8016faaec468da ] || { echo "STOP: ess_capture.py is not the ESS run's"; exit 2; }
mkdir "$B"
sed -e "s/__TOOL_COMMIT__/$full/" -e "s/__EVW5D_PY_SHA256__/$EVW/" -e "s/__SBATCH_SHA256__/$SB/" \
  "$HERE/evw5d_connect.sh" > "$B/evw5d_connect.sh"
sed -e "s/__EVW5D_PY_SHA256__/$EVW/" "$HERE/evw5d_hpss.sh" > "$B/evw5d_hpss.sh"
cp "$HERE/evw5d_post.sh" "$B/evw5d_post.sh"
CON=$(shasum -a 256 "$B/evw5d_connect.sh" | cut -d' ' -f1)
POST=$(shasum -a 256 "$B/evw5d_post.sh" | cut -d' ' -f1)
HPSS=$(shasum -a 256 "$B/evw5d_hpss.sh" | cut -d' ' -f1)
sed -e "s/__CONNECT_SHA256__/$CON/" -e "s/__POST_SHA256__/$POST/" -e "s/__HPSS_SHA256__/$HPSS/" \
  -e "s/__EVW5D_PY_SHA256__/$EVW/" \
  -e 's|TOP=$(cd "$HERE/../../../../../../../.." \&\& pwd) \|\| exit 9      # launch/ is 8 levels below|TOP=$(cd "$HERE/../../../../../../../../.." \&\& pwd) \|\| exit 9      # launch/bound/ is 9 levels below|' \
  "$HERE/evw5d_launch.sh" > "$B/evw5d_launch.sh"
grep -q 'launch/bound/ is 9 levels below' "$B/evw5d_launch.sh" || { echo "STOP: the bound launcher's TOP was not rewritten"; exit 3; }
[ "$(cd "$B/../../../../../../../../.." && pwd -P)" = "$(cd "$TOP" && pwd -P)" ] || { echo "STOP: nine levels up is not the checkout"; exit 3; }
if grep -n '__[A-Z0-9_]*__' "$B"/*.sh; then echo "STOP: a placeholder is left"; exit 3; fi
for f in "$B"/*.sh; do bash -n "$f"; done
LAUNCH=$(shasum -a 256 "$B/evw5d_launch.sh" | cut -d' ' -f1)
cat <<EOF | tee "$B/PINS.txt"
tool commit        $full
evw5d.py           $EVW
sbatch_evw5d.sh    $SB
ess_capture.py     $CAP
evw5d_connect.sh   $CON
evw5d_post.sh      $POST
evw5d_hpss.sh      $HPSS
evw5d_launch.sh    $LAUNCH
EOF
