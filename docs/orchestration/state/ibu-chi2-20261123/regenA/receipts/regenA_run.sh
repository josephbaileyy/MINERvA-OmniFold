#!/bin/bash
# regenA on login02 (AMENDMENT-A1): plain Python, nice 19, each producer under a 900 s timeout; writes only under $R.
set -o pipefail
R=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/regenA; REPO=$R/repo; ST=$R/stage; OUT=$R/out
MAIN=e766ee5290de9dfc81b490b6165565daee6fa8d5
ANC=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc
E=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/tier1/units_e/er.root
echo "[regenA] start $(date -u +%FT%TZ) host $(hostname)"
for p in $REPO $ST $OUT; do [ ! -e $p ] || { echo "REFUSED: $p exists"; exit 2; }; done
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git $REPO && git -C $REPO -c advice.detachedHead=false checkout -q $MAIN
[ "$(git -C $REPO rev-parse HEAD)" = $MAIN ] || { echo "REFUSED: HEAD"; exit 2; }
n=$(git -C $REPO status --porcelain --ignored | wc -l); echo "[regenA] clone $MAIN porcelain --ignored lines: $n"; [ "$n" = 0 ] || exit 2
mkdir -p $ST $OUT/old $OUT/e
dd if=/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/ER/xsec.root of=$ST/er_old.root iflag=noatime status=none && chmod a-w $ST/er_old.root
echo "[regenA] C-PINS before:"; sha256sum $ST/er_old.root $E $ANC/cov_ptpl_minerva_inclusive_6GeV.root $ANC/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt
[ "$(sha256sum < $ST/er_old.root | cut -d' ' -f1)" = a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef ] || { echo "STOP: OLD pin"; exit 3; }
[ "$(sha256sum < $E | cut -d' ' -f1)" = 5171c7b8ecacda6090e242349dd622218c1c38885c60ef8b91027033a8c4b780 ] || { echo "STOP: E pin"; exit 3; }
[ "$(sha256sum < $ANC/cov_ptpl_minerva_inclusive_6GeV.root | cut -d' ' -f1)" = 6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3 ] || { echo "STOP: release pin"; exit 3; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"; set +u; conda activate $HOME/.conda/envs/root_6_28
export MPLBACKEND=Agg PYTHONDONTWRITEBYTECODE=1 MNV_REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
cd $REPO/2d-unfolding
echo "[regenA] C-AXES:"; python3 - $E $ANC/cov_ptpl_minerva_inclusive_6GeV.root <<'PY' || { echo "STOP: C-AXES"; exit 3; }
import sys, ROOT
f = ROOT.TFile.Open(sys.argv[1]); h = f.Get("hXSec2D"); g = ROOT.TFile.Open(sys.argv[2]); p = g.Get("pt_pl_cross_section")
ax = lambda a: [a.GetBinLowEdge(i) for i in range(1, a.GetNbins() + 1)] + [a.GetBinUpEdge(a.GetNbins())]
ok = ax(h.GetXaxis()) == ax(p.GetYaxis()) and ax(h.GetYaxis()) == ax(p.GetXaxis())
print("E pT axis", ax(h.GetXaxis())); print("release pT axis", ax(p.GetYaxis())); print("C-AXES", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
PY
step() { name=$1; shift; echo "[regenA] $name start $(date -u +%TZ)"; /usr/bin/time -v -o $OUT/$name.time timeout 900 nice -n 19 "$@" > $OUT/$name.log 2>&1; rc=$?; echo "[regenA] $name rc=$rc $(grep -E 'Elapsed|Maximum resident' $OUT/$name.time | tr -s ' \t' ' ' | tr '\n' ';')"; }
for X in old e; do
  IN=$ST/er_old.root; [ $X = e ] && IN=$E; O=$OUT/$X
  step ${X}_P1a_chi2_paperonly python3 compare_to_paper_fullcov.py --ours $IN --out-prefix $O/paperonly
  step ${X}_P1b_pull_full      python3 compare_to_paper_fullcov.py --ours $IN --out-prefix $O/MEFHC_5iter
  step ${X}_P2_interior        python3 compare_to_paper_interior.py --ours $IN --out $O/MEFHC_5iter_pull_interior.png
  step ${X}_P3_shape           python3 normalize_xsec_shape.py --ours $IN --out $O/xsec_shape.root
  step ${X}_P4_tension         python3 diagnose_tension.py --ours $IN --out-prefix $O/tension
  step ${X}_P5_models          python3 compare_to_models.py --ours $IN --out-prefix $O/model_comp
  step ${X}_P6_tune            python3 receipt_model_chi2_2d.py --ours $IN --out $O/receipt_model_chi2.json
  step ${X}_P7_agreement       python3 agreement_windows_receipt.py --ours $IN --out $O/RECEIPT-agreement-windows.json
  step ${X}_P8_strip           python3 strip_ratio_receipt.py --ours $IN --out $O/strip_ratio_receipt.json
  step ${X}_P9_fig13           python3 plot_2d_threeway_fig13.py --infile $IN --paper $ANC/cov_ptpl_minerva_inclusive_6GeV.root --out $O/MEFHC_5iter_fig13.png
done
echo "[regenA] C-GRID: cross-grid NOTE lines in E logs: $(grep -l 'cross-grid shape chi2' $OUT/e_*.log 2>/dev/null | wc -l)"
echo "[regenA] C-PINS after:"; sha256sum $ST/er_old.root $E $ANC/cov_ptpl_minerva_inclusive_6GeV.root
echo "[regenA] porcelain after: $(git -C $REPO status --porcelain --ignored | wc -l)"
cd $OUT && find . -type f | sort | xargs sha256sum > $R/out.sha256; echo "[regenA] end $(date -u +%FT%TZ)"
