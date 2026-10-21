#!/bin/bash
#SBATCH -A m3246
#SBATCH -q debug
#SBATCH -C cpu
#SBATCH -N 1
#SBATCH -t 00:30:00
#SBATCH -J re1-f-chain
#SBATCH -o /pscratch/sd/j/josephrb/methods-paper/re1-20261020/logs/re1-f-chain-%j.out
# RE-1 K3/F chain: unchanged producers from the fresh clone at 2e2ffd20; only the input product changes.
S=/pscratch/sd/j/josephrb/methods-paper/re1-20261020
C=$S/deploy-2e2ffd20
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold
OMNI=$A/nd-unfolding/runEventLoopOmniFold_5D_MEFHC.root
CUR5D=$A/nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root
CUREXC=$A/nd-unfolding/products/5d/excess_eavail_W.root
P5=/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data/data_b-_j-.npz
GEN=/pscratch/sd/j/josephrb/s5p-20260926/stage7/genfig/3d-unfolding/genie
# environment: root_6_28 by full prefix through its creating conda's hook (as setup_salloc_env.sh); no set -u before it
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook 2>/dev/null)"
conda activate $HOME/.conda/envs/root_6_28
export TMPDIR=$SCRATCH/tmp OMP_NUM_THREADS=8
PY=python
echo "[env] $(which python) $(python -c 'import sys,numpy,ROOT;print(sys.version.split()[0],numpy.__version__,ROOT.gROOT.GetVersion())')"
echo "[code] $(git -C $C rev-parse HEAD) dirty=$(git -C $C status --porcelain | wc -l)"
mkdir -p $S/k3 $S/f
t() { echo "[time] $(date +%T) $*"; }
t start
# 1. P5 container (+ control repackaging of the current product)
$PY -I $S/scripts/p5_to_root.py --code-root $C --p5 $P5 \
  --expect-p5-sha256 fb5cc6798b97b5902ad8f0fecbc49990271f7772f98d3063c1dc8596340e680c \
  --npz-inputs $A/nd-unfolding/of_inputs_5d.npz --current-5d $CUR5D \
  --out $S/f/xsec_5d_p5.root --control-out $S/k3/xsec_5d_current_repackaged.root --json $S/f/p5_to_root.json
echo "[rc] p5_to_root $?"; t
# 2. K3: excess_eavail_W.py on the current product reproduces the current excess_eavail_W.root
cd $C/nd-unfolding
$PY $C/nd-unfolding/excess_eavail_W.py --omnifile $OMNI --xsec5d $CUR5D --out $S/k3/excess_eavail_W_current.root --png $S/k3/excess_eavail_W_current.png > $S/k3/excess_current.log 2>&1
echo "[rc] excess_current $?"; t
$PY $S/scripts/cmp_root_hists.py $CUREXC $S/k3/excess_eavail_W_current.root hData2D,hGenCV2D,hExcess2D > $S/k3/cmp_excess_current.json
echo "[rc] cmp_excess_current $?"
# 3. F: same producer, P5 input
$PY $C/nd-unfolding/excess_eavail_W.py --omnifile $OMNI --xsec5d $S/f/xsec_5d_p5.root --out $S/f/excess_eavail_W_p5.root --png $S/f/excess_eavail_W_p5.png > $S/f/excess_p5.log 2>&1
echo "[rc] excess_p5 $?"; t
$PY $S/scripts/cmp_root_hists.py $S/k3/excess_eavail_W_current.root $S/f/excess_eavail_W_p5.root hGenCV2D > $S/f/cmp_gencv_p5_vs_current.json
echo "[rc] cmp_gencv_unchanged $?"
# 4. K3: export_fig_arrays.py on current inputs reproduces fig_arrays.npz 72394a2b (array by array)
$PY $C/publication/release/figs/export_fig_arrays.py --code-root $C --out $S/k3/fig_arrays_current.npz > $S/k3/export_current.log 2>&1
echo "[rc] export_current $?"
$PY $S/scripts/cmp_npz.py /pscratch/sd/j/josephrb/pub-release-20261006/figs/fig_arrays.npz $S/k3/fig_arrays_current.npz > $S/k3/cmp_fig_arrays_current.json
echo "[rc] cmp_fig_arrays_current $?"; t
# 5. F: export with the P5-derived inputs, through a staged analysis root that differs only in the two 5D files
R=$S/f/analysis-root-p5
mkdir -p $R/2d-unfolding/minerva_paper_anc $R/nd-unfolding/products/5d
ln -sfn $A/2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root $R/2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root
ln -sfn $A/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root $R/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root
ln -sfn $A/2d-unfolding/minerva_paper_anc/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt $R/2d-unfolding/minerva_paper_anc/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt
ln -sfn $S/f/excess_eavail_W_p5.root $R/nd-unfolding/products/5d/excess_eavail_W.root
ln -sfn $S/f/xsec_5d_p5.root $R/nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root
$PY $C/publication/release/figs/export_fig_arrays.py --code-root $C --analysis-root $R --out $S/f/fig_arrays_p5.npz > $S/f/export_p5.log 2>&1
echo "[rc] export_p5 $?"
$PY $S/scripts/cmp_npz.py $S/k3/fig_arrays_current.npz $S/f/fig_arrays_p5.npz > $S/f/cmp_fig_arrays_p5_vs_current.json
echo "[rc] cmp_fig_arrays_p5_vs_current $? (nonzero expected: only the data-derived arrays may differ)"; t
# 6. K3: overlay_eavailW_band.py (note eavailW_band.pdf) on current inputs
cd $C/3d-unfolding/genie
$PY $C/3d-unfolding/genie/overlay_eavailW_band.py --data $CUREXC --gen GENIE-CV:$GEN/genie_cv_xsec_eavailW.root --gen GENIE+MEC:$GEN/genie_mec_xsec_eavailW.root --gen NuWro:$GEN/nuwro_cv_xsec_eavailW.root --gen GiBUU:$GEN/gibuu_cv_xsec_eavailW.root --png $S/k3/eavailW_band_current.png --out $S/k3/eavailW_band_current.root > $S/k3/band_current.log 2>&1
echo "[rc] band_current $?"
sha256sum $S/k3/eavailW_band_current.pdf
# 7. control: the repackaged current product through the same producer (container neutrality)
cd $C/nd-unfolding
$PY $C/nd-unfolding/excess_eavail_W.py --omnifile $OMNI --xsec5d $S/k3/xsec_5d_current_repackaged.root --out $S/k3/excess_eavail_W_repackaged.root --png $S/k3/excess_eavail_W_repackaged.png > $S/k3/excess_repackaged.log 2>&1
echo "[rc] excess_repackaged $?"
$PY $S/scripts/cmp_root_hists.py $CUREXC $S/k3/excess_eavail_W_repackaged.root hData2D,hGenCV2D,hExcess2D > $S/k3/cmp_excess_repackaged.json
echo "[rc] cmp_excess_repackaged $?"; t end
