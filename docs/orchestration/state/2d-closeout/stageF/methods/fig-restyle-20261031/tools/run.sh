#!/bin/bash
# The bound restyle run and its checks (DECLARATION.md §3-§4), driven from a local clone.
# usage: bash run.sh <base sha> <bound sha> <local out dir>
# 1. Each commit is archived with git archive (technote_style.py, 2d-unfolding/ and this tools/ directory) together
#    with a COMMIT file, copied to a new /pscratch/.../2d-closeout-restyle-20261031/run/<base|bound>/deploy and
#    unpacked there. No existing checkout is moved or written. The run root must not exist.
# 2. Three arms run on a login node (run_remote.sh): "before" (the base commit's producers), "off" (the bound commit's
#    producers without the option) and "after" (the bound commit's producers with --style restyle-2026-10).
# 3. Their outputs (no PNGs) come back to <local out dir>, and the checks run here:
#    check 2, the eleven PDFs of "before" and of "off" against the committed copies, pixel for pixel (raster.py);
#    checks 3-5, "before" against "after" (compare.py); the printed text sizes of "after" against the 4.0 pt floor
#    (textsize.py); and no raw-ASCII label in the PDFs of "after" (a "_" or "^" in their text).
# RESTYLE AMENDMENT 1 (AMENDMENT-1.md): checks 3-5 run with the palette (--recolour recolour.tsv --palette palette.tsv)
# and the one named binning exception (--rebin MEFHC_5iter_pull_full.png), and the overlap gate (overlap.py --gate)
# holds every in-panel text of the eleven "after" figures clear of the data.
# RESTYLE AMENDMENT 2 (AMENDMENT-2.md): check 3 also holds each series line to its identity's declared style (--styles
# styles.tsv --restyle restyle.tsv, on the data-only hash), and the names gate (names.py --gate) holds every legend
# entry of the eleven "after" figures to an identity's one name or a declared non-series entry (legend-other.tsv).
# Writes <local out dir>/CHECKS.txt. Exit 0 only if every check passes.
set -o pipefail
BASE=$1; BOUND=$2; OUT=$3
[ -n "$OUT" ] && [ ! -e "$OUT" ] || { echo "usage: run.sh <base sha> <bound sha> <new local out dir>"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(git -C "$HERE" rev-parse --show-toplevel)
# RESTYLE_RUN_ROOT moves the run root, for a dry run under the dev directory; the bound run uses the default. The first
# bound run (BINDING.md) used .../run, amendment 1's bound rerun .../run-a1, and amendment 2's uses .../run-a2, since
# a run root must not exist.
R=${RESTYLE_RUN_ROOT:-/pscratch/sd/j/josephrb/2d-closeout-restyle-20261031/run-a2}
H=saul.nersc.gov
TOOLS=docs/orchestration/state/2d-closeout/stageF/methods/fig-restyle-20261031/tools
FIGS="MEFHC_5iter_fig13 MEFHC_5iter_xsec_proj_pt MEFHC_5iter_xsec_proj_pz MEFHC_5iter_pull_full
MEFHC_5iter_xsec_paper_pt_slices MEFHC_5iter_xsec_paper_pz_slices tension_spectrum tension_chi2_map tension_mode_maps
model_comp_projections model_comp_ratio_maps"
mkdir -p "$OUT/pack"
BASE=$(git -C "$REPO" rev-parse "$BASE^{commit}") && BOUND=$(git -C "$REPO" rev-parse "$BOUND^{commit}") || exit 2
ssh -o BatchMode=yes "$H" "[ ! -e $R ]" || { echo "$R exists"; exit 2; }
for arm in base bound; do
    sha=$BASE; paths="technote_style.py 2d-unfolding"
    [ "$arm" = bound ] && { sha=$BOUND; paths="$paths $TOOLS"; }
    d=$OUT/pack/$arm; mkdir -p "$d"
    git -C "$REPO" archive "$sha" $paths | tar -x -C "$d" && echo "$sha" > "$d/COMMIT"
    COPYFILE_DISABLE=1 tar --no-xattrs -czf "$OUT/pack/$arm.tgz" -C "$d" .
    ssh -o BatchMode=yes "$H" "mkdir -p $R/$arm/deploy && tar -xzf - -C $R/$arm/deploy" < "$OUT/pack/$arm.tgz" || exit 3
done
ssh -o BatchMode=yes "$H" "cat > $R/run_remote.sh" < "$HERE/run_remote.sh" || exit 3
for spec in "before base none" "off bound none" "after bound restyle-2026-10"; do
    set -- $spec
    ssh -o BatchMode=yes "$H" "bash $R/run_remote.sh $R/$2/deploy $R/bound/deploy $R/$1 $3" || { echo "arm $1 failed"; exit 4; }
done
ssh -o BatchMode=yes "$H" "cd $R && tar -czf - --exclude='*.png' --exclude=tmp --exclude=mpl before off after" | tar -xzf - -C "$OUT"
T=$REPO/$TOOLS
F=$REPO/docs/orchestration/state/2d-closeout/stageF/methods/re2-integration/figs
ok=1
{
    echo "base $BASE, bound $BOUND"
    for arm in before off; do
        for f in $FIGS; do
            r=$(python3 -I "$T/raster.py" "$F/$f.pdf" "$OUT/$arm/out/$f.pdf") || ok=0
            echo "check 2 ($arm) $f: $r"
        done
    done
    figs=$(cd "$OUT/before/capture" && ls */*.json | grep -v capture-done | sed 's#.*/##; s#\.json$##' | sort -u | paste -sd, -)
    python3 -I "$T/compare.py" "$OUT/before" "$OUT/after" --figures "$figs" --strip "$R/before=RUN" --strip "$R/after=RUN" \
        --strip "$R/base/deploy=DEPLOY" --strip "$R/bound/deploy=DEPLOY" \
        --outputs out/model_comp_report.txt,out/tension_report.txt,logs/models.log,logs/tension.log,logs/fig13.log,logs/paper_slices.log,logs/xsec_proj.log,logs/pull_full.log \
        --recolour "$T/../recolour.tsv" --palette "$T/../palette.tsv" --rebin MEFHC_5iter_pull_full.png \
        --styles "$T/../styles.tsv" --restyle "$T/../restyle.tsv" \
        || ok=0
    python3 -I "$T/names.py" "$OUT/after" --styles "$T/../styles.tsv" --other "$T/../legend-other.tsv" \
        --figures "$(for f in $FIGS; do printf '%s.png,' "$f"; done | sed 's/,$//')" --gate || ok=0
    python3 -I "$T/overlap.py" "$OUT/after" --figures "$(for f in $FIGS; do printf '%s.png,' "$f"; done | sed 's/,$//')" --gate \
        || ok=0
    python3 -I "$T/textsize.py" "$OUT/after" "$OUT/pack/bound" --floor 4.0 || ok=0
    for f in $FIGS; do
        a=$(pdftotext "$OUT/after/out/$f.pdf" - | grep -c -E '_|\^')
        [ "$a" = 0 ] || ok=0
        echo "ascii $f: $a line(s) with _ or ^"
    done
    echo "RUN CHECKS :: $([ $ok = 1 ] && echo PASS || echo FAIL)"
} > "$OUT/CHECKS.txt" 2>&1   # not piped: a pipe would run this block in a subshell and lose ok
cat "$OUT/CHECKS.txt"
[ $ok = 1 ]
