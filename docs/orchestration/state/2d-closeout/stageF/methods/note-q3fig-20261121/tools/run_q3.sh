#!/bin/bash
# Fig. 5 (fig:q3excess): the two arms and their checks (README.md). Writes runs/q3/CHECKS.txt; exit 0 only if all pass.
#   bash run_q3.sh <worktree> <base commit>
# Arm 0: the installed recipe, note-figpass-20261119/tools/layout_run.py on the unchanged producer (its runs/q3 row).
# Arm 1: tools/compose_q3_labels.py on the same producer and arguments (the recipe, then the label fixes).
# Both under note-figstyle-20261117's capture_palette.py, env -i, an empty HOME, figenv/mpl3108, BLAS threads 1.
set -u
W=$1; BASE=$2
R=$W/docs/orchestration/state/2d-closeout/stageF/methods; N=$R/note-q3fig-20261121; PT=$R/note-figstyle-20261117/tools
FIGRUN=${FIGRUN:-/Users/josephbailey/cov2d-work/figrun}; VENV=/Users/josephbailey/cov2d-work/figenv/mpl3108
P=/Users/josephbailey/miniconda3/bin/python3; STEM=q3_excess_projection
CK=$N/runs/q3/CHECKS.txt; : > "$CK"
log() { echo "$*" | tee -a "$CK"; }
ok=1
log "# q3 ($(date -u +%Y-%m-%dT%H:%M:%SZ)): bash tools/run_q3.sh <wt> $BASE"
log "# compose_q3_labels.py sha256 $(shasum -a 256 "$N/tools/compose_q3_labels.py" | cut -c1-64)"
for arm in arm0 arm1; do
  O=$FIGRUN/q3fix/$arm; C=$N/runs/q3/$arm/capture/q3
  [ -e "$O" ] && find "$O" -type f -delete; [ -e "$C" ] && find "$C" -type f -delete
  mkdir -p "$O" "$C" "$FIGRUN/home" "$FIGRUN/mplcfg-mpl3108"
  if [ $arm = arm0 ]; then wrap=$R/note-figpass-20261119/tools/layout_run.py; else wrap=$N/tools/compose_q3_labels.py; fi
  (cd "$O" && env -i PATH="$VENV/bin:/usr/bin:/bin" HOME="$FIGRUN/home" MPLCONFIGDIR="$FIGRUN/mplcfg-mpl3108" \
     LAYOUT_PALETTE=1 Q3FIX_JSON="$N/runs/q3/compose_q3_labels.json" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 \
     OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
     PYTHONPATH="$R/note-figstyle-20261113/tools/fakeroot5" python3 "$PT/capture_palette.py" "$C" "$wrap" \
     "$W/nd-unfolding/q3_excess_projection.py" --from-arrays "$R/note-figstyle-20261113/runs/family5/dumps/q3_arrays.npz" \
     --out "$O/$STEM.png" --print-style > "$O/log.txt" 2>&1) || { log "FAIL $arm: rc $? ($(tail -2 "$O/log.txt" | tr '\n' ' '))"; ok=0; }
done
inst=$(mktemp); git -C "$W" show "$BASE:docs/analysis-note/figures/$STEM.pdf" > "$inst"
log "== arm 0 against docs/analysis-note/figures/$STEM.pdf at $BASE"
"$P" -I "$PT/bytes_but_date.py" "$inst" "$FIGRUN/q3fix/arm0/$STEM.pdf" 2>&1 | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
r=$("$P" -I "$R/fig-restyle-20261031/tools/raster.py" "$inst" "$FIGRUN/q3fix/arm0/$STEM.pdf"); rc=$?
log "raster: $r"; [ $rc = 0 ] || ok=0
rm -f "$inst"
log "== arm 1 against arm 0: data artists (fig-restyle compare.py, full hashes: data, colours, styles)"
"$P" -I "$R/fig-restyle-20261031/tools/compare.py" "$N/runs/q3/arm0" "$N/runs/q3/arm1" 2>&1 | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
log "== arm 1 against arm 0: drawn strings and sizes"
"$P" - "$N/runs/q3" "$STEM" 2>&1 <<'PY' | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
import json, sys
from collections import Counter
from pathlib import Path
d, stem = Path(sys.argv[1]), sys.argv[2]
OLD, NEW = "unfolded / GENIE prior", "unfolded / Tune v1 prior"
bad = 0
for ext in ("pdf", "png"):
    t0 = json.load(open(d / f"arm0/capture/q3/{stem}.{ext}.texts")); t1 = json.load(open(d / f"arm1/capture/q3/{stem}.{ext}.texts"))
    want = Counter((s, NEW if x == OLD else x) for s, x in t0["texts"]); got = Counter((s, x) for s, x in t1["texts"])
    n_old = sum(x == OLD for _, x in t0["texts"])
    same = want == got and t0["size_in"] == t1["size_in"]
    print(f"  {'equal' if same else 'DIFFER'} {stem}.{ext}: {len(t1['texts'])} strings (arm 0's with {n_old} x {OLD!r} -> {NEW!r}); "
          f"canvas {t1['size_in']}; min font {min(s for s, _ in t1['texts'])} pt; overlaps arm 0 {len(t0.get('text_overlaps', []))}, "
          f"arm 1 {len(t1.get('text_overlaps', []))}")
    if not same or n_old != 2 or any(x == OLD for _, x in t1["texts"]) or len(t1.get("text_overlaps", [])) > len(t0.get("text_overlaps", [])):
        bad = 1; print("  missing:", want - got, "extra:", got - want)
sys.exit(bad)
PY
log "== the label colours (runs/q3/compose_q3_labels.json)"
"$P" - "$N/runs/q3/compose_q3_labels.json" 2>&1 <<'PY' | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
import json, sys
j = json.load(open(sys.argv[1]))
w = sorted((c["value"], c["label"]) for c in j["cells"] if c["label_colour"] == "white")
b = sorted(c["value"] for c in j["cells"] if c["label_colour"] == "black")
print(f"  {j['n_labels']} labels, one per finite cell: {j['n_white']} white, {j['n_black']} black; cmap {j['cmap']}, "
      f"(vmin, vmax, vcenter) = {tuple(round(x, 6) for x in j['clim_vmin_vmax_vcenter'])} (unchanged)")
print(f"  white: {[l for _, l in w]}")
print(f"  black values span {min(b):.2f}..{max(b):.2f}")
# every white cell lies at an end of the scale, every black one between: the rule picks by luminance, not by value
lo = [v for v, _ in w if v < 1]; hi = [v for v, _ in w if v > 1]
okk = (not lo or max(lo) < min(b)) and (not hi or min(hi) > max(b)) and j["n_white"] > 0
mx = max(c["luminance"] for c in j["cells"] if c["label_colour"] == "white")
mn = min(c["luminance"] for c in j["cells"] if c["label_colour"] == "black")
print(f"  luminance: white labels on L <= {mx:.4f}, black on L >= {mn:.4f} (the contrast crossover is L = 0.1791)")
okk = okk and mx < 0.1791 <= mn + 1e-12
print("  LABELS ::", "PASS" if okk else "FAIL")
sys.exit(0 if okk else 1)
PY
if [ "${INSTALL:-0}" = 1 ] && [ $ok = 1 ]; then   # arm 1's PDF becomes the note's figure; its sha256 must be arm 1's
  cp "$FIGRUN/q3fix/arm1/$STEM.pdf" "$W/docs/analysis-note/figures/$STEM.pdf"
  a=$(shasum -a 256 "$FIGRUN/q3fix/arm1/$STEM.pdf" | cut -c1-64); i=$(shasum -a 256 "$W/docs/analysis-note/figures/$STEM.pdf" | cut -c1-64)
  log "== installed docs/analysis-note/figures/$STEM.pdf: sha256 $i (arm 1: $a)"; [ "$a" = "$i" ] || ok=0
fi
log "RUN-Q3 :: $([ $ok = 1 ] && echo PASS || echo FAIL)"
[ $ok = 1 ]
