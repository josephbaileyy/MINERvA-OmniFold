#!/bin/bash
# EVW2D: write the bound copies of the HPSS and deposit-fetch scripts into launch/bound-deposit/, every pin computed by
# command from committed files, none typed.
#   bash fill_deposit_pins.sh <run receipts directory, relative to the checkout's top>
# Every input is read from the commit HEAD (git show HEAD:<path>), each a regular blob in HEAD's tree (mode 100644),
# so neither the working tree nor a symlink can supply a pin. The pins: the lane root, evw2d.py and config.json from
# EVW2D BINDING 1's bound/PINS.txt; the products' SHA256SUMS digest and the evw2d.done digest are the sha256 of the
# receipts' post/out/SHA256SUMS and post/out/evw2d.done; the job id is the receipts' post/logs/evw2d.jobid. They must
# agree with the receipts' post/accepted.json (pass, config and job bound, done equal to the marker, whose SHA256SUMS is
# the bound digest) and the post log. evw2d.py and the two templates must equal HEAD's. Order: the pins ->
# evw2d_hpss.sh -> its digest -> evw2d_deposit.sh. Prints every pin, and refuses if any placeholder is left.
set -euo pipefail
RD=${1:?run receipts directory}
HERE=$(cd -- "$(dirname "$0")" && pwd -P)
TOP=$(git -C "$HERE" rev-parse --show-toplevel)
B="$HERE/bound-deposit"
REL=${HERE#"$TOP"/}
PINS1="$REL/bound/PINS.txt"
[ ! -e "$B" ] || { echo "STOP: $B exists"; exit 2; }
blob() {   # blob <path>: a regular file in HEAD's tree; prints its bytes
  local m
  m=$(git -C "$TOP" ls-tree HEAD -- "$1" | awk '{ print $1 " " $2 }') || return 1
  [ "$m" = "100644 blob" ] || { echo "STOP: $1 is not a regular file in HEAD ($m)" >&2; return 1; }
  git -C "$TOP" show "HEAD:$1"
}
hblob() { blob "$1" | shasum -a 256 | cut -d' ' -f1; }
PINS_TEXT=$(blob "$PINS1") || exit 2
pin() { printf '%s\n' "$PINS_TEXT" | awk -v k="$1" '{ v = $NF; $NF = ""; sub(/ +$/, ""); if ($0 == k) { print v; n++ } } END { exit n != 1 }'; }
LANE=$(pin "lane root")
EVW=$(pin "evw2d.py")
CFG=$(pin "config.json")
for f in post/out/SHA256SUMS post/out/evw2d.done post/logs/evw2d.jobid post/accepted.json post/post.log; do
  blob "$RD/$f" > /dev/null || exit 2
done
for f in "$REL/evw2d_hpss.sh" "$REL/evw2d_deposit.sh" 2d-unfolding/evw2d/evw2d.py; do
  blob "$f" > /dev/null || exit 2
  git -C "$TOP" diff --quiet HEAD -- "$f" || { echo "STOP: $f differs from HEAD"; exit 2; }
done
BOUND=$(hblob "$RD/post/out/SHA256SUMS")
DONE=$(hblob "$RD/post/out/evw2d.done")
JOBID=$(blob "$RD/post/logs/evw2d.jobid")
case "$JOBID" in *[!0-9]*|"") echo "STOP: job id '$JOBID'"; exit 2;; esac
[ "$(hblob 2d-unfolding/evw2d/evw2d.py)" = "$EVW" ] || { echo "STOP: evw2d.py is not the bound one"; exit 2; }
python3 -I - "$BOUND" "$CFG" "$JOBID" 3< <(blob "$RD/post/accepted.json") 4< <(blob "$RD/post/post.log") \
  5< <(blob "$RD/post/out/evw2d.done") <<'PY'
import json, os, sys
bound, cfg, job = sys.argv[1:4]
acc = json.load(os.fdopen(3)); log = os.fdopen(4).read(); marker = json.load(os.fdopen(5))
ok = (acc.get("pass") is True and acc.get("config_bound") is True and acc.get("job_bound") is True
      and acc.get("run_config_sha256") == cfg and str(acc.get("run_slurm_job")) == job
      and acc.get("done", {}).get("verdict") == "PASS"
      and f"SHA256SUMS sha256 {bound}\n" in log and "PASS=true" in log
      and marker == acc.get("done") and marker.get("SHA256SUMS") == bound)
sys.exit(0 if ok else "STOP: the receipts do not show this job's accepted products with the bound digests")
PY
mkdir "$B"
fill() { sed -e "s|__LANE_ROOT__|$LANE|" -e "s/__EVW2D_PY_SHA256__/$EVW/" -e "s/__CONFIG_SHA256__/$CFG/" \
             -e "s/__PRODUCTS_SHA256SUMS_SHA256__/$BOUND/" -e "s/__EVW2D_DONE_SHA256__/$DONE/" -e "s/__JOB_ID__/$JOBID/" "$1"; }
blob "$REL/evw2d_hpss.sh" | fill /dev/stdin > "$B/evw2d_hpss.sh"
HPSS=$(shasum -a 256 "$B/evw2d_hpss.sh" | cut -d' ' -f1)
blob "$REL/evw2d_deposit.sh" | fill /dev/stdin | sed -e "s/__HPSS_SHA256__/$HPSS/" > "$B/evw2d_deposit.sh"
if grep -n '__[A-Z0-9_]*__' "$B"/*.sh; then echo "STOP: a placeholder is left"; exit 3; fi
for f in "$B"/*.sh; do bash -n "$f"; done
DEP=$(shasum -a 256 "$B/evw2d_deposit.sh" | cut -d' ' -f1)
cat <<EOF | tee "$B/PINS.txt"
run receipts       $RD
lane root          $LANE
evw2d.py           $EVW
config.json        $CFG
products SHA256SUMS  $BOUND
evw2d.done         $DONE
job                $JOBID
evw2d_hpss.sh      $HPSS
evw2d_deposit.sh   $DEP
EOF
