#!/bin/bash
# One arm of the bound restyle run (DECLARATION.md §4), on a Perlmutter login node, with no Slurm and 0 node-h.
# usage: bash run_remote.sh <deploy> <tools-deploy> <outdir> <style: none|restyle-2026-10>
# <deploy> holds the producers of this arm (the base commit for the before arm, the bound commit otherwise); the
# checks' own code (capture.py, artists.py) is always the bound commit's, from <tools-deploy>.
# Each of re2c_run.sh's six figure steps (re2c_run.sh:160-170) runs its producer through capture.py, with E_R and the
# published covariance file as its inputs, in the same argv except for the output paths, which go under <outdir>. The
# working directory is <outdir>, not $A/2d-unfolding, so that nothing is written under $A; every default input path of
# the six producers is absolute. <outdir> must not exist. A marker is stamped first, and files under $A newer than it
# are counted at the end (it must be 0). The arm stops itself at 15 minutes, as re2c_run.sh does. No `set -u`: it
# aborts the root_6_28 activation.
set -o pipefail
if [ -z "$RESTYLE_TIMED" ]; then
    RESTYLE_TIMED=1 exec timeout 900 bash "$0" "$@"
fi
D=$(cd "$1" && pwd); TD=$(cd "$2" && pwd); O=$3; STY=$4
case "$STY" in none|restyle-2026-10) ;; *) echo "style: none or restyle-2026-10"; exit 2 ;; esac
[ ! -e "$O" ] || { echo "$O exists"; exit 2; }
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold
X=/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/ER/xsec.root
ANC=$A/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root
T=$TD/docs/orchestration/state/2d-closeout/stageF/methods/fig-restyle-20261031/tools
mkdir -p "$O"/{out,capture,tmp,mpl,logs}
touch "$O/marker"
source "$A/setup_salloc_env.sh" > /dev/null 2>&1
export TMPDIR=$O/tmp MPLCONFIGDIR=$O/mpl XDG_CACHE_HOME=$O/tmp PYTHONDONTWRITEBYTECODE=1 MNV_REPO=$A
unset TECHNOTE_DARK
opt=(); [ "$STY" = none ] || opt=(--style "$STY")
echo "deploy=$D commit=$(cat "$D/COMMIT") tools=$(cat "$TD/COMMIT") style=$STY host=$(hostname) start=$(date -u +%FT%TZ)" > "$O/logs/run.txt"
sha256sum "$X" "$ANC" > "$O/logs/inputs.sha256"
printf 'step\trc\tseconds\targv\n' > "$O/logs/steps.tsv"
cd "$O" || exit 2
P=$D/2d-unfolding
step() {
    local name=$1 t0 rc; shift
    t0=$(date +%s)
    python3 -I -B "$T/capture.py" "$O/capture/$name" "$D" "$@" "${opt[@]}" > "$O/logs/$name.log" 2>&1
    rc=$?
    printf '%s\t%s\t%s\t%s\n' "$name" "$rc" "$(( $(date +%s) - t0 ))" "$* ${opt[*]}" >> "$O/logs/steps.tsv"
    [ "$rc" = 0 ] || { echo "STEP $name rc=$rc (see $O/logs/$name.log)"; exit 10; }
}
step models "$P/compare_to_models.py" --ours "$X" --out-prefix "$O/out/model_comp"
step tension "$P/diagnose_tension.py" --ours "$X" --out-prefix "$O/out/tension"
step fig13 "$P/plot_2d_threeway_fig13.py" --infile "$X" --paper "$ANC" --out "$O/out/MEFHC_5iter_fig13.png"
step paper_slices "$P/plot_2d_paper_comparison.py" --infile "$X" --prefix "$O/out/MEFHC_5iter_xsec_paper"
step xsec_proj "$P/plot_2d_cross_section.py" --infile "$X" --prefix "$O/out/MEFHC_5iter_xsec"
step pull_full "$D/2d-unfolding/compare_to_paper_fullcov.py" --ours "$X" --out-prefix "$O/out/MEFHC_5iter"
n=$(find "$A/2d-unfolding" "$A/docs" -newer "$O/marker" -type f 2>/dev/null | wc -l)
echo "files under \$A newer than the marker: $n" | tee -a "$O/logs/run.txt"
(cd "$O" && find out capture logs -type f ! -name '*.png' -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS)
echo "end=$(date -u +%FT%TZ)" >> "$O/logs/run.txt"
[ "$n" = 0 ] || exit 11
