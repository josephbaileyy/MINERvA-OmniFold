#!/bin/bash
#SBATCH --job-name=re1-f2
#SBATCH --account=m3246
#SBATCH --qos=debug
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --time=00:22:00
#SBATCH --output=/pscratch/sd/j/josephrb/methods-paper/re1-20261022/logs/%x-%j.out
# RE-1 run 2, F2: the same producers on P3/P4 (director's F-R1: the two redraw copies differ from the original
# only in one data pin, committed with their diffs). Outputs go to $O/f/new/.
set -eo pipefail
source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re1/run2/launch/re1_env.sh"
source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re1/run2/launch/re1_f_env.sh"
re1_preflight
(cd "$F" && sha256sum -c SHA256SUMS.f1)
G=$F/new/genfig/3d-unfolding                  # Stage-7 inputs with P3 in place of the current 3D product
mkdir -p "$G"
ln -sfn "$S7G/genie" "$G/genie"
ln -sfn "$F/new/xsec_3d_p3.root" "$G/xsec_3d_MEFHC_5iter_lgbm.root"
cd "$F/new"
export OMP_NUM_THREADS=4
rc=0
run() { local label=$1; shift; srun -n1 -c 4 --exact --cpu-bind=cores bash -c "$(declare -f re1_py); C=$C O=$O; re1_py $label $*" > "$F/new/$label.log" 2>&1 || { echo "[re1] $label rc=$?"; rc=1; }; }
P3R=$F/new/xsec_3d_p3.root; P4R=$F/new/xsec_4d_p4.root
run f_eavail 3d-unfolding/plot_eavail_spectrum.py --infile "$P3R" --out "$F/new/eavail_spectrum.png"
run f_marg 2d-unfolding/compare_to_paper_fullcov.py --ours "$P3R" --out-prefix "$F/new/eavail_marginal_vs_paper"
run f_redraw3d nd-unfolding/re1/redraw_central_only_p3.py --genfig "$G" --outdir "$F/new" --only generators modedecomp mec
run f_redraw4d nd-unfolding/re1/redraw_central_only_p4.py --xsec4d "$P4R" --supplemental "$SUPP" --outdir "$F/new" --only ascencio
(cd "$F" && sha256sum new/*.pdf new/*.png > SHA256SUMS.f2) || rc=1
echo "[re1] end $(date -u +%FT%TZ) rc=$rc"
exit $rc
