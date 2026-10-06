#!/bin/bash
# Adopt VL170 (KNOWN_ISSUES 84): rebuild the 2D statistical rollup and everything that consumes it,
# from the 300 rebuilt replicas, into NEW directories. The VL162-era products stay at their
# sha-pinned paths (uq/bootstrap_MEFHC_300/, uq/universe_stage2_MEFHC_full_matcorr_fluxfix/).
#
# This is the production chain behind the quoted 6.87 % and 1.481 (ledger "Active 2D Result"), not
# final_rollup_full.sh, whose universe step predates the matcorr/fluxfix sweep:
#   analyze_uq.py (boot300) -> analyze_universes.py --bootstrap-cov (hCov_combined = universe + boot)
#   -> compare_to_paper_fullcov.py hCov_combined + ML  (and --log-normal)
# Every old number is reproduced first, from the old inputs with the same commands (controls).
#
#   bash 2d-unfolding/uq/rollup_vl170_adoption.sh     # on a Perlmutter login node, from anywhere
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
UQ="${REPO}/2d-unfolding/uq"
REPL="/pscratch/sd/j/josephrb/ki84-rebuild-20261006/replicas"
BOOT_OLD="${UQ}/bootstrap_MEFHC_300"
BOOT_NEW="${UQ}/bootstrap_MEFHC_300_vl170"
UNIV_OLD="${UQ}/universe_stage2_MEFHC_full_matcorr_fluxfix"
UNIV_NEW="${UQ}/universe_stage2_MEFHC_full_matcorr_fluxfix_vl170"
CTRL="/pscratch/sd/j/josephrb/ki84-rebuild-20261006/adoption_controls"
ML="${UQ}/seedscan_lgbm_ml/uq_covariance_ml.root"
CV="uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"
SWEEP="uq/universe_sweep_fluxfix/2d_xsec_MEFHC_5iter_lgbm_uni_full_*.root"
UROOT="uq_universe_covariance_full_matcorr_fluxfix.root"

for d in "${BOOT_NEW}" "${UNIV_NEW}"; do
  [[ -e "${d}" ]] && { echo "[FAIL] ${d} exists; refusing to overwrite"; exit 2; }
done
n=$(ls "${REPL}"/2d_xsec_MEFHC_5iter_lgbm_boot*.root.done | wc -l)
[[ "${n}" -eq 300 ]] || { echo "[FAIL] ${n} rebuilt replicas, need 300"; exit 2; }
echo "[sha] $(sha256sum "${BOOT_OLD}/uq_covariance_boot300.root" "${UNIV_OLD}/${UROOT}" "${ML}")"
source "${REPO}/setup_salloc_env.sh" >/dev/null 2>&1
mkdir -p "${CTRL}" "${BOOT_NEW}" "${UNIV_NEW}"
cd "${REPO}/2d-unfolding"   # analyze_universes.py and the sweep globs are relative to here

echo "===== control: the universe rollup reproduces from the old bootstrap ====="
python uq/analyze_universes.py --cv "${CV}" --glob "${SWEEP}" --add-norm 0.014 \
  --bootstrap-cov "${BOOT_OLD}/uq_covariance_boot300.root" \
  --outdir "${CTRL}/univ_old" --out-root "${UROOT}" > "${CTRL}/univ_old.log" 2>&1
grep -A3 'COMBINED universe' "${CTRL}/univ_old.log"

echo "===== (1) bootstrap covariance from the 300 rebuilt replicas ====="
python uq/analyze_uq.py --glob "${REPL}/2d_xsec_MEFHC_5iter_lgbm_boot*.root" \
  --outdir "${BOOT_NEW}" --out-root uq_covariance_boot300.root 2>&1 | tee "${BOOT_NEW}/rollup.log" | grep -v Warning | tail -15

echo "===== (2) universe + bootstrap combined covariance ====="
python uq/analyze_universes.py --cv "${CV}" --glob "${SWEEP}" --add-norm 0.014 \
  --bootstrap-cov "${BOOT_NEW}/uq_covariance_boot300.root" \
  --outdir "${UNIV_NEW}" --out-root "${UROOT}" > "${UNIV_NEW}/rollup.log" 2>&1
grep -A3 'TOTAL universe\]\|COMBINED universe' "${UNIV_NEW}/rollup.log"

echo "===== (3) combined chi2 vs paper: old (control) and new ====="
for tag in old new; do
  if [[ ${tag} == old ]]; then U="${UNIV_OLD}/${UROOT}"; P="${CTRL}/MEFHC_5iter_old"; else U="${UNIV_NEW}/${UROOT}"; P="${UNIV_NEW}/MEFHC_5iter"; fi
  for ln in "" "--log-normal"; do
    python compare_to_paper_fullcov.py --omnifold-cov "${U}:hCov_combined" --omnifold-cov "${ML}:hCov2D_reported" \
      --out-prefix "${P}${ln:+_lognormal}" ${ln} > "${CTRL}/chi2_${tag}${ln:+_lognormal}.log" 2>&1
    echo "[${tag}${ln:+ log-normal}] $(grep -i 'chi.*ndf\|pull' "${CTRL}/chi2_${tag}${ln:+_lognormal}.log" | tail -4 | tr '\n' ' ')"
  done
  python compare_to_paper_fullcov.py --out-prefix "${CTRL}/MEFHC_5iter_papercov_${tag}" > "${CTRL}/chi2_papercov_${tag}.log" 2>&1
done

echo "===== (4) ours-only chi2 (universe total + bootstrap): old (control) and new ====="
python uq/_ours_only_chi2.py --universe-cov "${UNIV_OLD}/${UROOT}" --bootstrap-cov "${BOOT_OLD}/uq_covariance_boot300.root" > "${CTRL}/ours_only_old.log" 2>&1
python uq/_ours_only_chi2.py --universe-cov "${UNIV_NEW}/${UROOT}" --bootstrap-cov "${BOOT_NEW}/uq_covariance_boot300.root" > "${UNIV_NEW}/ours_only_chi2.log" 2>&1
cp "${UNIV_NEW}/ours_only_chi2.log" "${CTRL}/ours_only_new.log"

echo "===== (5) figures ====="
cd "${UQ}"
# --paper-root and --include-ml always are the flags the note's figure was drawn with. The script writes its
# own _summary.txt at the prefix, so stdout goes to a separate log. (The first run of this file on
# 2026-10-06 redirected stdout onto the summary and omitted both flags; this step was rerun as written
# here, and the same command on the VL162 inputs reproduces the July summary exactly: controls/fig67_old*.)
python plot_uncertainty_fig6_7_style.py --universe-root "${UNIV_NEW}/${UROOT}" \
  --bootstrap-root "${BOOT_NEW}/uq_covariance_boot300.root" \
  --paper-root "${REPO}/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root" --include-ml always \
  --out-prefix "${UNIV_NEW}/MEFHC_fig6_7_uncertainty" > "${UNIV_NEW}/fig6_7.log" 2>&1
python plot_bootstrap_figs.py --cov "${BOOT_NEW}/uq_covariance_boot300.root" --outdir "${BOOT_NEW}" > "${BOOT_NEW}/plot_bootstrap_figs.log" 2>&1
ls -la "${BOOT_NEW}" "${UNIV_NEW}"
echo "[sha] $(sha256sum "${BOOT_NEW}/uq_covariance_boot300.root" "${UNIV_NEW}/${UROOT}")"
echo "===== DONE ====="
