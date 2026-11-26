#!/bin/bash
# EVW2D: write the bound copies of the launch scripts into launch/bound/, every pin computed by command, none typed.
#   bash fill_pins.sh <tool commit C>
# C must be an ancestor of HEAD (or HEAD) and carry the binding's config.json: against the reviewed config.json
# (5fdb4c3f, merged at 4d9147f9 by #1347) only declaration_sha256, lane_root, driver_tree.root and
# inputs.staging.root may differ (the declaration's §10.4), with lane_root /pscratch/sd/j/josephrb/evw2d-<yyyymmdd>,
# driver_tree.root <lane>/deploy_M, the staging root <lane>/stage, and declaration_sha256 the declaration's digest at C.
# evw2d.py and sbatch_evw2d.sh at C must equal this checkout's. The templates (launch/*.sh, with __PLACEHOLDER__ pins)
# stay as they are, because the tests use them. Order: the digests at C -> connect, post and cleanup -> their digests
# -> the launcher. Prints every digest, and refuses if any placeholder is left.
set -euo pipefail
TOOLC=${1:?tool commit}
HERE=$(cd "$(dirname "$0")" && pwd)
TOP=$(git -C "$HERE" rev-parse --show-toplevel)
B="$HERE/bound"
REVIEWED_AT=4d9147f9a94c14b0c313f2e611a35e044b327704
REVIEWED_CFG=5fdb4c3f632a820d0f2542652731d90b06099c0c3b8ac3b0e54f2f2fdd800255
EV=2d-unfolding/evw2d
DECL=docs/orchestration/state/2d-closeout/evw2d-20261124/EVW2D-DECLARATION.md
[ ! -e "$B" ] || { echo "STOP: $B exists"; exit 2; }
full=$(git -C "$TOP" rev-parse --verify "$TOOLC^{commit}")
git -C "$TOP" merge-base --is-ancestor "$full" HEAD || { echo "STOP: $full is not an ancestor of HEAD"; exit 2; }
sha_at() { git -C "$TOP" show "$1:$2" | shasum -a 256 | cut -d' ' -f1; }
[ "$(sha_at "$REVIEWED_AT" "$EV/config.json")" = "$REVIEWED_CFG" ] || { echo "STOP: the reviewed config.json is not $REVIEWED_CFG"; exit 2; }
EVW=$(sha_at "$full" "$EV/evw2d.py")
SB=$(sha_at "$full" "$EV/sbatch_evw2d.sh")
CFG=$(sha_at "$full" "$EV/config.json")
DEC=$(sha_at "$full" "$DECL")
REFS=$(sha_at "$full" "$EV/references.npz")
[ "$REFS" = 1b21458283c06531c9791efdc1e15f9d685d0733e398288a715768d61b612a03 ] || { echo "STOP: references.npz at C is not the reviewed one"; exit 2; }
[ "$EVW" = "$(shasum -a 256 "$TOP/$EV/evw2d.py" | cut -d' ' -f1)" ] || { echo "STOP: evw2d.py differs from C's"; exit 2; }
[ "$SB" = "$(shasum -a 256 "$TOP/$EV/sbatch_evw2d.sh" | cut -d' ' -f1)" ] || { echo "STOP: sbatch_evw2d.sh differs from C's"; exit 2; }
LANE=$(python3 -I - "$DEC" <(git -C "$TOP" show "$REVIEWED_AT:$EV/config.json") <(git -C "$TOP" show "$full:$EV/config.json") <<'PY'
import json, re, sys
dec, base, bound = sys.argv[1], json.load(open(sys.argv[2])), json.load(open(sys.argv[3]))
def strip(c):
    c = json.loads(json.dumps(c))
    c["declaration_sha256"] = c["lane_root"] = c["driver_tree"]["root"] = c["inputs"]["staging"]["root"] = None
    return c
lane = bound["lane_root"]
ok = (strip(bound) == strip(base) and isinstance(lane, str)
      and re.fullmatch(r"/pscratch/sd/j/josephrb/evw2d-20\d{6}", lane) is not None
      and bound["driver_tree"]["root"] == lane + "/deploy_M" and bound["inputs"]["staging"]["root"] == lane + "/stage"
      and bound["declaration_sha256"] == dec)
if not ok:
    sys.exit("STOP: config.json at C is not the reviewed one with exactly the four binding fields set to this layout")
print(lane)
PY
)
mkdir "$B"
fill() { sed -e "s|__LANE_ROOT__|$LANE|" -e "s/__TOOL_COMMIT__/$full/" -e "s/__EVW2D_PY_SHA256__/$EVW/" \
             -e "s/__SBATCH_SHA256__/$SB/" -e "s/__CONFIG_SHA256__/$CFG/" -e "s/__DECLARATION_SHA256__/$DEC/" "$1"; }
for s in evw2d_connect.sh evw2d_post.sh evw2d_cleanup.sh; do fill "$HERE/$s" > "$B/$s"; done
CON=$(shasum -a 256 "$B/evw2d_connect.sh" | cut -d' ' -f1)
POST=$(shasum -a 256 "$B/evw2d_post.sh" | cut -d' ' -f1)
CLEAN=$(shasum -a 256 "$B/evw2d_cleanup.sh" | cut -d' ' -f1)
fill "$HERE/evw2d_launch.sh" | sed -e "s/__CONNECT_SHA256__/$CON/" -e "s/__POST_SHA256__/$POST/" \
  -e "s/__CLEANUP_SHA256__/$CLEAN/" > "$B/evw2d_launch.sh"
if grep -n '__[A-Z0-9_]*__' "$B"/*.sh; then echo "STOP: a placeholder is left"; exit 3; fi
for f in "$B"/*.sh; do bash -n "$f"; done
LAUNCH=$(shasum -a 256 "$B/evw2d_launch.sh" | cut -d' ' -f1)
cat <<EOF | tee "$B/PINS.txt"
tool commit        $full
lane root          $LANE
evw2d.py           $EVW
sbatch_evw2d.sh    $SB
config.json        $CFG
declaration        $DEC
references.npz     $REFS
evw2d_connect.sh   $CON
evw2d_post.sh      $POST
evw2d_cleanup.sh   $CLEAN
evw2d_launch.sh    $LAUNCH
EOF
