#!/bin/bash
# PTMC: write launch/bound/ with every pin computed by command (OOFVC's fill_pins.sh form).
#   bash fill_pins.sh <tool commit>
# The tool commit must be an ancestor of HEAD (or HEAD) and carry this checkout's 2d-unfolding/ptmc/ byte for byte (the
# remote steps run sbatch files and helpers from a clone at that commit). Order: the tool commit and the pinned PTMC
# driver's sha (make_tree.sh's PTMC_SHA, which make_tree checks the built driver against) into ptmc_remote.sh, then its
# digest into ptmc_launch.sh. Refuses if any placeholder is left. The binding pins the filled bytes.
set -euo pipefail
TOOLC=${1:?tool commit}
HERE=$(cd "$(dirname "$0")" && pwd)
TOP=$(git -C "$HERE" rev-parse --show-toplevel)
B="$HERE/bound"
[ ! -e "$B" ] || { echo "STOP: $B exists"; exit 2; }
full=$(git -C "$TOP" rev-parse --verify "$TOOLC^{commit}")
git -C "$TOP" merge-base --is-ancestor "$full" HEAD || { echo "STOP: $full is not an ancestor of HEAD"; exit 2; }
n=0
for f in $(git -C "$TOP" ls-tree -r --name-only "$full" -- 2d-unfolding/ptmc); do
  case "$f" in */launch/bound/*) continue;; esac
  [ "$(git -C "$TOP" show "$full:$f" | shasum -a 256 | cut -d' ' -f1)" = "$(shasum -a 256 "$TOP/$f" | cut -d' ' -f1)" ] \
    || { echo "STOP: $f differs from the tool commit's"; exit 2; }
  n=$((n + 1))
done
[ "$n" -gt 10 ] || { echo "STOP: the tool commit carries only $n PTMC files"; exit 2; }
DS=$(sed -n 's/^PTMC_SHA=\([0-9a-f]\{64\}\)$/\1/p' "$HERE/../make_tree.sh")
[ "$(printf '%s\n' "$DS" | grep -c .)" = 1 ] || { echo "STOP: make_tree.sh does not carry exactly one PTMC_SHA pin"; exit 2; }
mkdir "$B"
sed -e "s/__TOOL_COMMIT__/$full/" -e "s/__DRIVER_SHA256__/$DS/" "$HERE/ptmc_remote.sh" > "$B/ptmc_remote.sh"
RS=$(shasum -a 256 "$B/ptmc_remote.sh" | cut -d' ' -f1)
sed -e "s/__REMOTE_SHA256__/$RS/" "$HERE/ptmc_launch.sh" > "$B/ptmc_launch.sh"
if grep -n '__[A-Z0-9_]*__' "$B"/*.sh; then echo "STOP: a placeholder is left"; exit 3; fi
for f in "$B"/*.sh; do bash -n "$f"; done
LS=$(shasum -a 256 "$B/ptmc_launch.sh" | cut -d' ' -f1)
cat <<PINS | tee "$B/PINS.txt"
tool commit       $full
driver (deployed) $DS
ptmc_remote.sh    $RS
ptmc_launch.sh    $LS
pilot.sbatch      $(shasum -a 256 "$HERE/pilot.sbatch" | cut -d' ' -f1)
replicas.sbatch   $(shasum -a 256 "$HERE/replicas.sbatch" | cut -d' ' -f1)
ptmc_pilot_post.py $(shasum -a 256 "$HERE/ptmc_pilot_post.py" | cut -d' ' -f1)
ptmc_stage_d4.py  $(shasum -a 256 "$HERE/ptmc_stage_d4.py" | cut -d' ' -f1)
make_tree.sh      $(shasum -a 256 "$HERE/../make_tree.sh" | cut -d' ' -f1)
ptmc_driver.diff  $(shasum -a 256 "$HERE/../ptmc_driver.diff" | cut -d' ' -f1)
PINS
