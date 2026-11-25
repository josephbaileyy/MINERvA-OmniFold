#!/usr/bin/env bash
# regenA amendment A4b's controls for Fig. 2 (xsec_proj_pt/pz), after regenA4_run.sh has run on OLD in the archive of
# the installing commit (FR_OLD) and on E at main (FR_E).
#   bash a4b_controls.sh <main worktree W> <FR_OLD> <FR_E> <A4's E run dir, for the cross-check>
# C4b-OLD: OLD's two projections EQUAL-BUT-DATE against the installed files at W (bytes_but_date.py).
# C4b-PRE (OLD and E): compose_fig2_edges.json's check before the fix flags exactly one line in each projection's upper
#   panel, the declared 'Tune v1: published prediction', and none in the ratio; the check after the fix flags none.
# Information, not a control: E's projections against A4's E run (same code and input; EQUAL-BUT-DATE expected).
set -u
W=$1; FO=$2; FE=$3; FA=$4
M=$W/docs/orchestration/state/2d-closeout/stageF/methods; BBD=$M/note-figstyle-20261117/tools/bytes_but_date.py
P=$HOME/miniconda3/bin/python3; F=$W/docs/analysis-note/figures; ok=1
sha() { shasum -a 256 "$1" | cut -c1-64; }
echo "== C4b-OLD: OLD (the installing commit's code) against the installed files"
for f in MEFHC_5iter_xsec_proj_pt MEFHC_5iter_xsec_proj_pz; do "$P" -I "$BBD" "$F/$f.pdf" "$FO/fig2/out/$f.pdf" || ok=0; done
echo "== C4b-PRE: the edge-fix pre-check flags only the declared line"
"$P" -I - "$FO/fig2/out/compose_fig2_edges.json" "$FE/fig2/out/compose_fig2_edges.json" <<'PY' || ok=0
import json, sys
bad = 0
for tag, path in zip(("OLD", "E"), sys.argv[1:]):
    d = json.load(open(path))
    for stem in ("MEFHC_5iter_xsec_proj_pt", "MEFHC_5iter_xsec_proj_pz"):
        r = d[stem]; top, ratio = r["check_before"]["top"], r["check_before"]["ratio"]
        good = len(top) == 1 and "'Tune v1: published prediction'" in top[0] and not ratio \
            and not r["check_after"]["top"] and not r["check_after"]["ratio"]
        print(f"  {tag} {stem}: before {top + ratio}; after {r['check_after']}; edges {r['edges'][:8]}: {'PASS' if good else 'FAIL'}")
        bad |= not good
sys.exit(bad)
PY
echo "== information: E against A4's E run (not a reading there)"
for f in MEFHC_5iter_xsec_proj_pt MEFHC_5iter_xsec_proj_pz; do "$P" -I "$BBD" "$FA/fig2/out/$f.pdf" "$FE/fig2/out/$f.pdf"; done
echo "== sha256 (installed; OLD at the installing commit; E at main)"
for f in MEFHC_5iter_xsec_proj_pt MEFHC_5iter_xsec_proj_pz; do echo "$f.pdf installed $(sha "$F/$f.pdf") old $(sha "$FO/fig2/out/$f.pdf") e $(sha "$FE/fig2/out/$f.pdf")"; done
[ $ok = 1 ] && echo "A4B-CONTROLS :: PASS" || echo "A4B-CONTROLS :: FAIL"
[ $ok = 1 ]
