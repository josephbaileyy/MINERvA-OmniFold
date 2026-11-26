#!/bin/bash
# EVW2D: write the bound copies of the HPSS and deposit-fetch scripts into launch/bound-deposit/, every pin computed by
# command from committed files, none typed.
#   bash fill_deposit_pins.sh <run receipts directory, relative to the checkout's top>
# The pins: the lane root, evw2d.py and config.json from EVW2D BINDING 1's bound/PINS.txt; the products' SHA256SUMS
# digest is the sha256 of the receipts' post/out/SHA256SUMS; the job id is the receipts' post/logs/evw2d.jobid. They
# must agree with the receipts' post/accepted.json (pass, config and job bound, done.SHA256SUMS) and post.pass's
# fields as the post log printed them, and this checkout's evw2d.py must be the bound bytes. Order: the four pins ->
# evw2d_hpss.sh -> its digest -> evw2d_deposit.sh. Prints every pin, and refuses if any placeholder is left.
set -euo pipefail
RD=${1:?run receipts directory}
HERE=$(cd "$(dirname "$0")" && pwd)
TOP=$(git -C "$HERE" rev-parse --show-toplevel)
B="$HERE/bound-deposit"
PINS1="$HERE/bound/PINS.txt"
[ ! -e "$B" ] || { echo "STOP: $B exists"; exit 2; }
[ -f "$PINS1" ] || { echo "STOP: no $PINS1"; exit 2; }
pin() { awk -v k="$1" '{ v = $NF; $NF = ""; sub(/ +$/, ""); if ($0 == k) { print v; n++ } } END { exit n != 1 }' "$PINS1"; }
LANE=$(pin "lane root")
EVW=$(pin "evw2d.py")
CFG=$(pin "config.json")
D="$TOP/$RD"
for f in post/out/SHA256SUMS post/logs/evw2d.jobid post/accepted.json post/post.log; do
  [ -f "$D/$f" ] && [ ! -L "$D/$f" ] || { echo "STOP: no $RD/$f"; exit 2; }
  git -C "$TOP" ls-files --error-unmatch "$RD/$f" > /dev/null 2>&1 || { echo "STOP: $RD/$f is not tracked"; exit 2; }
done
git -C "$TOP" diff --quiet HEAD -- "$RD" "$PINS1" || { echo "STOP: the receipts or PINS differ from HEAD"; exit 2; }
BOUND=$(shasum -a 256 "$D/post/out/SHA256SUMS" | cut -d' ' -f1)
JOBID=$(cat "$D/post/logs/evw2d.jobid")
case "$JOBID" in *[!0-9]*|"") echo "STOP: job id '$JOBID'"; exit 2;; esac
[ "$(shasum -a 256 "$TOP/2d-unfolding/evw2d/evw2d.py" | cut -d' ' -f1)" = "$EVW" ] || { echo "STOP: evw2d.py is not the bound one"; exit 2; }
python3 -I - "$D/post/accepted.json" "$D/post/post.log" "$BOUND" "$CFG" "$JOBID" <<'PY'
import json, sys
acc, log, bound, cfg, job = json.load(open(sys.argv[1])), open(sys.argv[2]).read(), *sys.argv[3:]
ok = (acc.get("pass") is True and acc.get("config_bound") is True and acc.get("job_bound") is True
      and acc.get("run_config_sha256") == cfg and str(acc.get("run_slurm_job")) == job
      and acc.get("done", {}).get("SHA256SUMS") == bound and acc.get("done", {}).get("verdict") == "PASS"
      and f"SHA256SUMS sha256 {bound}\n" in log and "PASS=true" in log)
sys.exit(0 if ok else "STOP: the receipts do not show this job's accepted products with the bound digests")
PY
mkdir "$B"
fill() { sed -e "s|__LANE_ROOT__|$LANE|" -e "s/__EVW2D_PY_SHA256__/$EVW/" -e "s/__CONFIG_SHA256__/$CFG/" \
             -e "s/__PRODUCTS_SHA256SUMS_SHA256__/$BOUND/" -e "s/__JOB_ID__/$JOBID/" "$1"; }
fill "$HERE/evw2d_hpss.sh" > "$B/evw2d_hpss.sh"
HPSS=$(shasum -a 256 "$B/evw2d_hpss.sh" | cut -d' ' -f1)
fill "$HERE/evw2d_deposit.sh" | sed -e "s/__HPSS_SHA256__/$HPSS/" > "$B/evw2d_deposit.sh"
if grep -n '__[A-Z0-9_]*__' "$B"/*.sh; then echo "STOP: a placeholder is left"; exit 3; fi
for f in "$B"/*.sh; do bash -n "$f"; done
DEP=$(shasum -a 256 "$B/evw2d_deposit.sh" | cut -d' ' -f1)
cat <<EOF | tee "$B/PINS.txt"
run receipts       $RD
lane root          $LANE
evw2d.py           $EVW
config.json        $CFG
products SHA256SUMS  $BOUND
job                $JOBID
evw2d_hpss.sh      $HPSS
evw2d_deposit.sh   $DEP
EOF
