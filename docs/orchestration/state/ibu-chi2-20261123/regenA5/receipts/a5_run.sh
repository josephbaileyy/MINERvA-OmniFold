#!/usr/bin/env bash
# regenA amendment A5: the eigenmode readout on OLD and E, then C5-LIT on OLD. Laptop; 0 node-h; reads only.
#   bash a5_run.sh <repo tree> <producer worktree W> <out dir in the tree: regenA5/out>
set -u
T=$1; W=$2; O=$3
[ -n "${A4_VENV+x}" ] && { echo "REFUSE: A4_VENV set"; exit 2; }
[ -e "$O" ] && { echo "REFUSE: $O exists"; exit 2; }
PY=$HOME/cov2d-work/figenv/rootmpl3108/bin/python; A=$HOME/cov2d-work/figfetch/anc
S=$T/docs/orchestration/state/ibu-chi2-20261123; D=$S/regenA5
XO=$HOME/cov2d-work/figfetch/er-anc/xsec.root; XE=$S/tier1/units/e/er.root
RO=$S/regenA/out/old/tension_report.txt; RE=$S/regenA/out/e/tension_report.txt
PINS=("$XO" "$XE" "$A/cov_ptpl_minerva_inclusive_6GeV.root" "$RO" "$RE" "$D/a5_readout.py" "$D/a5_literals.py" "$0")
mkdir -p "$O"
shasum -a 256 "${PINS[@]}" | sed "s#$HOME#~#" > "$O/pins_before.sha256" || exit 3
echo "W $(git -C "$W" rev-parse HEAD) porcelain=$(git -C "$W" status --porcelain | wc -l | tr -d ' '); env A4_: $(env | grep -c '^A4_')" > "$O/prerun.txt"
rc=0
for s in old e; do
  X=$XO; Rp=$RO; [ $s = e ] && { X=$XE; Rp=$RE; }
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$D/a5_readout.py" --module-dir "$W/2d-unfolding" --anc "$A" --xsec "$X" --report "$Rp" \
    --out "$O/readout_$s.json" > "$O/readout_$s.out" 2>&1 || rc=1
  echo "readout $s rc=$?" >> "$O/prerun.txt"
done
PYTHONDONTWRITEBYTECODE=1 "$PY" "$D/a5_literals.py" "$O/readout_old.json" > "$O/c5_lit.out" 2>&1 || rc=1
shasum -a 256 "${PINS[@]}" | sed "s#$HOME#~#" > "$O/pins_after.sha256"
cmp -s "$O/pins_before.sha256" "$O/pins_after.sha256" && echo "C-PINS: equal" >> "$O/prerun.txt" || { echo "C-PINS: CHANGED" >> "$O/prerun.txt"; rc=1; }
exit $rc
