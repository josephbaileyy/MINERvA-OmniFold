#!/bin/bash
# The two arms of one locally drawn note figure, and their checks (README.md, "The method").
#   bash arms.sh <worktree> <family> <venv> <base commit> <out name: the saved PNG stem> <extra PYTHONPATH or -> \
#                <producer> [producer args, with @OUT@ for the arm's output directory]
# Arm 0 runs the producer unchanged under capture_palette.py; arm 1 runs it under palette_run.py (the record's edits)
# and capture_palette.py. Both under env -i with an empty HOME, in the venv given. Then:
#   arm 0's <stem>.pdf against the file installed at the base: bytes_but_date.py and raster.py;
#   arm 1 against arm 0: fig-restyle-20261031/tools/compare.py --recolour --palette --styles --restyle;
#   text overlaps (capture_any.py's measure) of arm 0 and arm 1.
# Arm outputs go to $FIGRUN/<family>/{arm0,arm1}; captures to runs/<family>/{arm0,arm1}/capture/<family>/.
# Each arm must capture at least one figure, and the same files (compare.py alone passes on none). Exit 0 only if
# every check passes.
set -u
W=$1; FAM=$2; VENV=$3; BASE=$4; STEM=$5; XP=$6; shift 6
R=$W/docs/orchestration/state/2d-closeout/stageF/methods; N=$R/note-figstyle-20261117
FIGRUN=${FIGRUN:-/Users/josephbailey/cov2d-work/figrun}
P=/Users/josephbailey/miniconda3/bin/python3
PP=""; [ "$XP" != - ] && PP=$XP
ok=1
for arm in arm0 arm1; do
  O=$FIGRUN/$FAM/$arm; C=$N/runs/$FAM/$arm/capture/$FAM
  [ -e "$O" ] && find "$O" -type f -delete; [ -e "$C" ] && find "$C" -type f -delete
  mkdir -p "$O" "$FIGRUN/home" "$FIGRUN/mplcfg-$(basename "$VENV")"
  args=(); for a in "$@"; do args+=("${a//@OUT@/$O}"); done
  wrap=(); [ $arm = arm1 ] && wrap=("$N/tools/palette_run.py")
  (cd "$O" && env -i PATH="$VENV/bin:/usr/bin:/bin" HOME="$FIGRUN/home" MPLCONFIGDIR="$FIGRUN/mplcfg-$(basename "$VENV")" \
     PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PP" python3 "$N/tools/capture_palette.py" "$C" ${wrap[@]+"${wrap[@]}"} "${args[@]}" \
     > "$O/log.txt" 2>&1) || { echo "FAIL $FAM $arm: rc $? ($(tail -2 "$O/log.txt" | tr '\n' ' '))"; ok=0; }
done
inst=$(mktemp); git -C "$W" show "$BASE:docs/analysis-note/figures/$STEM.pdf" > "$inst"
echo "== $FAM ($STEM): arm 0 against the file installed at $BASE"
"$P" -I "$N/tools/bytes_but_date.py" "$inst" "$FIGRUN/$FAM/arm0/$STEM.pdf" || ok=0
echo "raster: $("$P" -I "$R/fig-restyle-20261031/tools/raster.py" "$inst" "$FIGRUN/$FAM/arm0/$STEM.pdf")" || ok=0
rm -f "$inst"
echo "== $FAM: arm 1 against arm 0"
c0=$(cd "$N/runs/$FAM/arm0/capture/$FAM" 2>/dev/null && ls *.json 2>/dev/null | sort | tr "\n" " ")
c1=$(cd "$N/runs/$FAM/arm1/capture/$FAM" 2>/dev/null && ls *.json 2>/dev/null | sort | tr "\n" " ")
[ -n "$c0" ] && [ "$c0" = "$c1" ] && echo "captures: $c0" \
  || { echo "FAIL captures: arm 0 [$c0], arm 1 [$c1] (none, or not the same files)"; ok=0; }
"$P" -I "$R/fig-restyle-20261031/tools/compare.py" "$N/runs/$FAM/arm0" "$N/runs/$FAM/arm1" --recolour "$N/recolour.tsv" \
  --palette "$N/palette.tsv" --styles "$N/styles.tsv" --restyle "$N/restyle.tsv" || ok=0
"$P" - "$N/runs/$FAM" "$FAM" <<'PY'
import json, sys
from pathlib import Path
d, fam = Path(sys.argv[1]), sys.argv[2]
for p in sorted((d / "arm0" / "capture" / fam).glob("*.pdf.texts")):
    q = d / "arm1" / "capture" / fam / p.name
    a = json.loads(p.read_text())["text_overlaps"]
    b = json.loads(q.read_text())["text_overlaps"] if q.exists() else None
    print(f"text overlaps {p.name[:-len('.pdf.texts')]}: {len(a)} -> {'missing' if b is None else len(b)}"
          + ("" if not b else f" {[o[:2] for o in b]}"))
PY
echo "ARMS $FAM :: $([ $ok = 1 ] && echo PASS || echo FAIL)"
[ $ok = 1 ]
