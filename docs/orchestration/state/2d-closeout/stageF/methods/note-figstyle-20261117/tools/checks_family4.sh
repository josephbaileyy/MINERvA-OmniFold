#!/bin/bash
# Family 4's checks (Figs. 19-22) for the record: arm 0 against the files installed at the branch base, arm 1 against
# arm 0. Run after both arms (README.md, family 4). Writes to stdout.
#   bash checks_family4.sh <worktree> <arm-0 out dir> <arm-1 out dir> <base commit> <python with numpy and PIL>
set -u
W=$1; A0=$2; A1=$3; BASE=$4; P=$5
R=$W/docs/orchestration/state/2d-closeout/stageF/methods; N=$R/note-figstyle-20261117
F="generators_vs_unfolded_band_central mode_decomp_eavail_central compare_mec_eavail_central ascencio_fullcov_compare_central"
T=$(mktemp -d "${TMPDIR:-/tmp}/cf4.XXXXXX")
echo "# Family 4 (Figs. 19-22), the note palette pass, $(date -u +%FT%TZ); base $BASE"
echo "## arm 0 (note-figstyle-20261113/tools/restyle_family4.py, unchanged) against the files installed at the base"
args=()
for f in $F; do git -C "$W" show "$BASE:docs/analysis-note/figures/$f.pdf" > "$T/$f.pdf"; args+=("$T/$f.pdf" "$A0/$f.pdf"); done
"$P" -I "$N/tools/bytes_but_date.py" "${args[@]}"; echo "bytes_but_date rc=$?"
for f in $F; do echo "raster $f: $("$P" -I "$R/fig-restyle-20261031/tools/raster.py" "$T/$f.pdf" "$A0/$f.pdf")"; done
echo "## arm 1 (tools/palette_family4.py) against arm 0: fig-restyle-20261031/tools/compare.py"
"$P" -I "$R/fig-restyle-20261031/tools/compare.py" "$N/runs/family4/arm0" "$N/runs/family4/arm1" --recolour "$N/recolour.tsv" \
  --palette "$N/palette.tsv" --styles "$N/styles.tsv" --restyle "$N/restyle.tsv"; echo "compare rc=$?"
echo "## text overlaps (capture_any.py's measure), arm 0 -> arm 1"
"$P" - "$N/runs/family4" $F <<'PY'
import json, sys
d = sys.argv[1]
for f in sys.argv[2:]:
    a = json.load(open(f"{d}/arm0/capture/family4/{f}.pdf.texts"))["text_overlaps"]
    b = json.load(open(f"{d}/arm1/capture/family4/{f}.pdf.texts"))["text_overlaps"]
    print(f, len(a), "->", len(b), [o[:2] for o in b])
PY
echo "## arm 1 PDFs as installed (figs/), sha256"
for f in $F; do cmp -s "$A1/$f.pdf" "$N/figs/$f.pdf" && echo "$(shasum -a 256 "$N/figs/$f.pdf")" || echo "MISMATCH $f"; done
find "$T" -type f -delete; rmdir "$T"
