#!/bin/bash
# Tier 2's six steps (note-figstyle-20261113 family 2's argv, --style restyle-2026-10 --print-font), each through
# remap_anc.py on the fetched inputs, in the local ROOT environment; arm 0 judged against family 2's after capture.
W=/Users/josephbailey/cov2d-work/wt-figs; R=$W/docs/orchestration/state/2d-closeout/stageF/methods; N=$R/note-figstyle-20261117
O=$R/note-figstyle-20261113; X=/Users/josephbailey/cov2d-work/figfetch/er-anc/xsec.root; A=/Users/josephbailey/cov2d-work/figfetch/anc
V=/Users/josephbailey/cov2d-work/figenv/rootmpl3108; B=2fe070feca48256639797278eff0e1ac6f17abd7; P2=$W/2d-unfolding; ST=(--style restyle-2026-10 --print-font)
step() { local fam=$1 stem=$2; shift 2
  { echo "# tier 2 $fam ($(date -u +%FT%TZ)): ROOT $($V/bin/python -c 'import ROOT;print(ROOT.gROOT.GetVersion())' 2>/dev/null), matplotlib 3.10.8, numpy 1.26.4; inputs xsec.root a5c13fc3 and cov_ptpl_minerva_inclusive_6GeV.root 6c6dce72 (the fetch of 2026-11-17); ${ARM1_EXTRA:+arm 1 adds $ARM1_EXTRA}"
    CLUSTER_CAP=$O/runs/family2/after/capture/$fam NUMERIC_REF=${NUMERIC_REF:-} RTOL=${RTOL:-1e-9} bash $N/tools/arms.sh $W $fam $V $B $stem - $N/tools/remap_anc.py $A "$@" "${ST[@]}" 2>&1; } \
    | sed "s#$W/##g; s#/Users/josephbailey/cov2d-work/##g" > $N/runs/$fam/CHECKS.txt.new
  mkdir -p $N/runs/$fam; mv $N/runs/$fam/CHECKS.txt.new $N/runs/$fam/CHECKS.txt; echo "$fam: $(tail -1 $N/runs/$fam/CHECKS.txt)"; }
mkdir -p $N/runs/{models,tension,fig13,paper_slices,xsec_proj,pull_full}
step models model_comp_projections $P2/compare_to_models.py --ours $X --out-prefix @OUT@/model_comp
NUMERIC_REF=$R/fig-restyle-20261031/run-a2/after/capture/tension RTOL=1e-5 step tension tension_spectrum $P2/diagnose_tension.py --ours $X --out-prefix @OUT@/tension
step fig13 MEFHC_5iter_fig13 $P2/plot_2d_threeway_fig13.py --infile $X --paper $A/cov_ptpl_minerva_inclusive_6GeV.root --out @OUT@/MEFHC_5iter_fig13.png
step paper_slices MEFHC_5iter_xsec_paper_pt_slices $P2/plot_2d_paper_comparison.py --infile $X --prefix @OUT@/MEFHC_5iter_xsec_paper
step xsec_proj MEFHC_5iter_xsec_proj_pt $P2/plot_2d_cross_section.py --infile $X --prefix @OUT@/MEFHC_5iter_xsec
ARM1_EXTRA=--sd-label step pull_full MEFHC_5iter_pull_full $P2/compare_to_paper_fullcov.py --ours $X --out-prefix @OUT@/MEFHC_5iter
