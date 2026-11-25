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
# OLD first: its readout (C5-REP inside) and C5-LIT; E only if both pass (the director's GO, 2026-11-25).
PYTHONDONTWRITEBYTECODE=1 "$PY" "$D/a5_readout.py" --module-dir "$W/2d-unfolding" --anc "$A" --xsec "$XO" --report "$RO" \
  --out "$O/readout_old.json" > "$O/readout_old.out" 2>&1; r=$?; echo "readout old rc=$r" >> "$O/prerun.txt"
rep=$("$PY" -c "import json,sys; print(json.load(open(sys.argv[1]))['C5-REP']['pass'])" "$O/readout_old.json" 2>/dev/null)
PYTHONDONTWRITEBYTECODE=1 "$PY" "$D/a5_literals.py" "$O/readout_old.json" > "$O/c5_lit.out" 2>&1; lit=$?
echo "OLD: C5-REP $rep, C5-LIT rc=$lit" >> "$O/prerun.txt"
if [ $r = 0 ] && [ "$rep" = True ] && [ $lit = 0 ]; then
  PYTHONDONTWRITEBYTECODE=1 "$PY" "$D/a5_readout.py" --module-dir "$W/2d-unfolding" --anc "$A" --xsec "$XE" --report "$RE" \
    --out "$O/readout_e.json" > "$O/readout_e.out" 2>&1 || rc=1
  echo "readout e rc=$?" >> "$O/prerun.txt"
else
  echo "STOP before E: OLD's readout or C5-REP or C5-LIT failed" >> "$O/prerun.txt"; rc=1
fi
shasum -a 256 "${PINS[@]}" | sed "s#$HOME#~#" > "$O/pins_after.sha256"
cmp -s "$O/pins_before.sha256" "$O/pins_after.sha256" && echo "C-PINS: equal" >> "$O/prerun.txt" || { echo "C-PINS: CHANGED" >> "$O/prerun.txt"; rc=1; }
exit $rc
