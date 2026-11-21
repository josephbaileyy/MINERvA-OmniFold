#!/bin/bash
# Fig. 5 (fig:q3excess) marginals on their bin edges: the two arms and their checks. Writes runs/q3/CHECKS.txt.
#   [INSTALL=1] bash run_q3_steps.sh <worktree> <base commit>
# Arm 0: the installed recipe, note-q3fig-20261121/tools/compose_q3_labels.py on the unchanged producer.
# Arm 1: tools/compose_q3_steps.py on the same producer and arguments (that recipe, then the step edges).
# Both under note-figstyle-20261117's capture_palette.py, env -i, an empty HOME, figenv/mpl3108, BLAS threads 1.
set -u
W=$1; BASE=$2
R=$W/docs/orchestration/state/2d-closeout/stageF/methods; N=$R/note-stepedges-20261121; PT=$R/note-figstyle-20261117/tools
FIGRUN=${FIGRUN:-/Users/josephbailey/cov2d-work/figrun}; VENV=/Users/josephbailey/cov2d-work/figenv/mpl3108
P=/Users/josephbailey/miniconda3/bin/python3; STEM=q3_excess_projection
CK=$N/runs/q3/CHECKS.txt; : > "$CK"; rm -f "$N/runs/q3/compose_q3_steps.json"
log() { echo "$*" | tee -a "$CK"; }
ok=1
log "# q3 steps ($(date -u +%Y-%m-%dT%H:%M:%SZ)): bash tools/run_q3_steps.sh <wt> $BASE"
for f in tools/compose_q3_steps.py tools/edges.py; do log "# $f sha256 $(shasum -a 256 "$N/$f" | cut -c1-64)"; done
log "# arm 0 recipe note-q3fig-20261121/tools/compose_q3_labels.py sha256 $(shasum -a 256 "$R/note-q3fig-20261121/tools/compose_q3_labels.py" | cut -c1-64)"
for arm in arm0 arm1; do
  O=$FIGRUN/q3steps/$arm; C=$N/runs/q3/$arm/capture/q3
  [ -e "$O" ] && find "$O" -type f -delete; [ -e "$C" ] && find "$C" -type f -delete
  mkdir -p "$O" "$C" "$FIGRUN/home" "$FIGRUN/mplcfg-mpl3108"
  if [ $arm = arm0 ]; then wrap=$R/note-q3fig-20261121/tools/compose_q3_labels.py; else wrap=$N/tools/compose_q3_steps.py; fi
  (cd "$O" && env -i PATH="$VENV/bin:/usr/bin:/bin" HOME="$FIGRUN/home" MPLCONFIGDIR="$FIGRUN/mplcfg-mpl3108" \
     LAYOUT_PALETTE=1 Q3STEPS_JSON="$N/runs/q3/compose_q3_steps.json" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 \
     OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
     PYTHONPATH="$R/note-figstyle-20261113/tools/fakeroot5" python3 "$PT/capture_palette.py" "$C" "$wrap" \
     "$W/nd-unfolding/q3_excess_projection.py" --from-arrays "$R/note-figstyle-20261113/runs/family5/dumps/q3_arrays.npz" \
     --out "$O/$STEM.png" --print-style > "$O/log.txt" 2>&1) || { log "FAIL $arm: rc $? ($(tail -2 "$O/log.txt" | tr '\n' ' '))"; ok=0; }
done
inst=$(mktemp); git -C "$W" show "$BASE:docs/analysis-note/figures/$STEM.pdf" > "$inst"
log "== arm 0 against docs/analysis-note/figures/$STEM.pdf at $BASE"
"$P" -I "$PT/bytes_but_date.py" "$inst" "$FIGRUN/q3steps/arm0/$STEM.pdf" 2>&1 | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
r=$("$P" -I "$R/fig-restyle-20261031/tools/raster.py" "$inst" "$FIGRUN/q3steps/arm0/$STEM.pdf"); rc=$?
log "raster: $r"; [ $rc = 0 ] || ok=0
rm -f "$inst"
log "== arm 1 against arm 0: captures (every item equal but the two stepped lines; those differ in drawing only)"
"$P" - "$N/runs/q3" "$STEM" 2>&1 <<'PY' | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
import json, sys
from collections import Counter
from pathlib import Path
import numpy as np
d, stem = Path(sys.argv[1]), sys.argv[2]
bad = 0
for ext in ("pdf", "png"):
    c0 = d / f"arm0/capture/q3/{stem}.{ext}"; c1 = d / f"arm1/capture/q3/{stem}.{ext}"
    i0, i1 = json.load(open(f"{c0}.json")), json.load(open(f"{c1}.json"))
    z0, z1 = np.load(f"{c0}.npz"), np.load(f"{c1}.npz")
    same_order = [(a["kind"], a["axes"]) for a in i0] == [(a["kind"], a["axes"]) for a in i1]
    diff = [k for k, (a, b) in enumerate(zip(i0, i1)) if a["hash"] != b["hash"]]
    want = [k for k, a in enumerate(i0) if a["kind"] == "line" and a["axes"] in (1, 2) and a["style"].get("drawstyle") == "steps-mid"]
    good = same_order and diff == want and len(want) == 2
    for k in want:
        a, b = i0[k], i1[k]
        x0, y0 = z0[f"i{k}.xy"].T; x1, y1 = z1[f"i{k}.xy"].T; n = len(x0)
        ok_k = (a["colours"] == b["colours"] and a["style"]["linestyle"] == b["style"]["linestyle"]
                and a["style"]["marker"] == b["style"]["marker"] and b["style"]["drawstyle"] == "steps-post"
                and np.array_equal(x0, np.arange(n)) and np.array_equal(x1, np.arange(n + 1))
                and np.array_equal(y1[:-1], y0) and y1[-1] == y0[-1])
        print(f"    item {k} (axes {a['axes']}): steps-mid x 0..{n - 1} -> steps-post x 0..{n}, y equal on the {n} bins, colours/line style equal: {ok_k}")
        good &= ok_k
    print(f"  {'ok' if good else 'FAIL'} {stem}.{ext}: {len(i0)} items, same order {same_order}; differ {diff} (want the two stepped lines {want})")
    t0 = json.load(open(f"{c0}.texts")); t1 = json.load(open(f"{c1}.texts"))
    rep = {"$q_3$, low edge (GeV)": "$q_3$ (GeV)", "$E_{\\rm avail}$, low edge (GeV)": "$E_{\\rm avail}$ (GeV)"}
    w = Counter((s, rep.get(x, x)) for s, x in t0["texts"]); w[(7.0, "100.0")] += 2
    g = Counter((s, x) for s, x in t1["texts"])
    st = w == g and t0["size_in"] == t1["size_in"]
    print(f"  {'equal' if st else 'DIFFER'} strings {stem}.{ext}: {len(t1['texts'])} (arm 0's {len(t0['texts'])}, the two x labels without ', low edge', "
          f"and each panel's last edge '100.0' added); min font {min(s for s, _ in t1['texts'])} pt; overlaps arm 0 {len(t0.get('text_overlaps', []))}, arm 1 {len(t1.get('text_overlaps', []))}")
    if not st:
        print("   missing:", w - g, "extra:", g - w)
    good &= st and len(t1.get("text_overlaps", [])) <= len(t0.get("text_overlaps", []))
    bad |= not good
print("CAPTURES ::", "PASS" if not bad else "FAIL")
sys.exit(bad)
PY
log "== the edge check (runs/q3/compose_q3_steps.json)"
"$P" - "$N/runs/q3/compose_q3_steps.json" 2>&1 <<'PY' | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
import json, sys
j = json.load(open(sys.argv[1])); good = True
for k, v in j.items():
    print(f"  {k}: {v['n_bins']} bins, edges {v['edges']}; before {v['check_before']}; after {v['check_after']}; ticks {v['tick_labels_after']}")
    good &= bool(v["check_before"]) and not v["check_after"]
print("EDGES ::", "PASS" if good else "FAIL"); sys.exit(0 if good else 1)
PY
if [ "${INSTALL:-0}" = 1 ] && [ $ok = 1 ]; then
  cp "$FIGRUN/q3steps/arm1/$STEM.pdf" "$W/docs/analysis-note/figures/$STEM.pdf"
  a=$(shasum -a 256 "$FIGRUN/q3steps/arm1/$STEM.pdf" | cut -c1-64); i=$(shasum -a 256 "$W/docs/analysis-note/figures/$STEM.pdf" | cut -c1-64)
  log "== installed docs/analysis-note/figures/$STEM.pdf: sha256 $i (arm 1: $a)"; [ "$a" = "$i" ] || ok=0
fi
log "RUN-Q3-STEPS :: $([ $ok = 1 ] && echo PASS || echo FAIL)"
[ $ok = 1 ]
