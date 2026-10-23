#!/bin/bash
#SBATCH --job-name=re1-f1
#SBATCH --account=m3246
#SBATCH --qos=debug
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --time=00:11:00
#SBATCH --output=/pscratch/sd/j/josephrb/methods-paper/re1-20261022/logs/%x-%j.out
# RE-1 run 2, F1: K3 (the unchanged producers on the current inputs, compared with the current figures) and the
# P3/P4 container conversion. Nothing is written under a checkout: every output goes to $O/f/.
set -eo pipefail
source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re1/run2/launch/re1_env.sh"
source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re1/run2/launch/re1_f_env.sh"
re1_preflight
for p in "$CUR3D $CUR3D_SHA" "$CUR4D $CUR4D_SHA" "$EU $EU_SHA" "$EC $EC_SHA"; do re1_check $p; done
(cd "$O" && sha256sum -c SHA256SUMS.nd)
mkdir -p "$F/k3" "$F/new"
cd "$F/k3"
export OMP_NUM_THREADS=4
rc=0
run() { local label=$1; shift; srun -n1 -c 4 --exact --cpu-bind=cores bash -c "$(declare -f re1_py); C=$C O=$O; re1_py $label $*" > "$F/k3/$label.log" 2>&1 || { echo "[re1] $label rc=$?"; rc=1; }; }
run k3_eavail 3d-unfolding/plot_eavail_spectrum.py --infile "$CUR3D" --out "$F/k3/eavail_spectrum.png"
run k3_marg 2d-unfolding/compare_to_paper_fullcov.py --ours "$CUR3D" --out-prefix "$F/k3/eavail_marginal_vs_paper"
run k3_redraw3d docs/analysis-note/redraw_central_only.py --genfig "$S7G" --outdir "$F/k3" --only generators modedecomp mec
run k3_redraw4d docs/analysis-note/redraw_central_only.py --xsec4d "$CUR4D" --supplemental "$SUPP" --outdir "$F/k3" --only ascencio
for n in eavail_spectrum eavail_marginal_vs_paper_pull_full generators_vs_unfolded_band_central \
         mode_decomp_eavail_central compare_mec_eavail_central ascencio_fullcov_compare_central; do
    re1_py "k3cmp_$n" nd-unfolding/re1/re1_cmp_fig.py "$F/k3/$n.pdf" "$FIGS/$n.pdf" 2>/dev/null \
        | grep '^{' >> "$F/k3/k3_compare.jsonl" || true   # one JSON line each; equal:false is a K3 failure, read later
done
sha() { sha256sum "$1" | cut -d' ' -f1; }
run conv3 nd-unfolding/re1/re1_to_root.py --dim 3 --product "$O/3d/p3.npz" --expect-product-sha256 "$(sha $O/3d/p3.npz)" \
    --current "$CUR3D" --expect-current-sha256 "$CUR3D_SHA" --out "$F/new/xsec_3d_p3.root" --json "$F/new/conv3.json"
run conv4 nd-unfolding/re1/re1_to_root.py --dim 4 --product "$O/4d/p4.npz" --expect-product-sha256 "$(sha $O/4d/p4.npz)" \
    --current "$CUR4D" --expect-current-sha256 "$CUR4D_SHA" --out "$F/new/xsec_4d_p4.root" --json "$F/new/conv4.json"
run k3_numbers nd-unfolding/re1/re1_f_numbers.py --current "$CUR3D" --p3 "$F/new/xsec_3d_p3.root" --eu "$EU" --ec "$EC" \
    --anc "$ANC" --out "$F/numbers.json"
(cd "$F" && sha256sum k3/*.pdf k3/*.png new/*.root numbers.json > SHA256SUMS.f1) || rc=1
echo "[re1] end $(date -u +%FT%TZ) rc=$rc"
exit $rc
