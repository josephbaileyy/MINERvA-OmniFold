#!/bin/bash
# (a) POWER CONTROL for the receipt predicate, (b) stage-1 merge skip, all READ-ONLY.
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
ND=$REPO/nd-unfolding
source "$REPO/setup_salloc_env.sh" >/dev/null 2>&1
MERGEDIR=$ND/active_universe_5d/standard/merged
OUTDIR=$ND/active_universe_5d/standard/unfolds
cd $ND || exit 9

echo "=== (a) POWER CONTROL: same receipt, WRONG tag -- must be rejected ==="
OUT="$OUTDIR/5d_xsec_MEFHC_5iter_lgbm_uni_full_BeamAngleX_0.root"
MERGED="$MERGEDIR/runEventLoopOmniFold_5D_MEFHC_active_BeamAngleX_0.root"
if python3 p4_check_receipt.py --receipt "$OUT.done" --tag BeamAngleY_1 --root "$OUT" --merged "$MERGED" >/tmp/pc1.txt 2>&1; then
  echo "*** ACCEPTED A WRONG TAG -- the predicate has no power, disregard the SKIP results ***"
else
  echo "REJECTED as required: $(tail -1 /tmp/pc1.txt)"
fi
echo
echo "=== (a2) POWER CONTROL: wrong MERGED input -- must be rejected ==="
OTHER="$MERGEDIR/runEventLoopOmniFold_5D_MEFHC_active_Muon_Energy_MINOS_1.root"
if python3 p4_check_receipt.py --receipt "$OUT.done" --tag BeamAngleX_0 --root "$OUT" --merged "$OTHER" >/tmp/pc2.txt 2>&1; then
  echo "*** ACCEPTED A FOREIGN MERGED INPUT -- weaker than assumed ***"
else
  echo "REJECTED as required: $(tail -1 /tmp/pc2.txt)"
fi
echo
echo "=== (b) STAGE 1: would each of the 10 merges SKIP? (valid_merged = 4 trees present) ==="
for BAND in BeamAngleX BeamAngleY MuonResolution Muon_Energy_MINERvA Muon_Energy_MINOS; do
for EP in 0 1; do
  M="$MERGEDIR/runEventLoopOmniFold_5D_MEFHC_active_${BAND}_${EP}.root"
  printf '%-24s ' "${BAND}_${EP}"
  [[ -s "$M" ]] || { echo "WOULD-MERGE: absent"; continue; }
  R=$(python3 -c "
import ROOT,sys
ROOT.gErrorIgnoreLevel=ROOT.kFatal
f=ROOT.TFile.Open('$M')
if not f or f.IsZombie(): print('unopenable'); sys.exit(1)
miss=[t for t in ('mc_truth_denom','mc_signal_reco','mc_background','data') if not f.Get(t)]
print('ok' if not miss else 'missing '+','.join(miss))
" 2>&1 | tail -1)
  [[ "$R" == "ok" ]] && echo "WOULD-SKIP  (valid)" || echo "WOULD-REDO: $R"
done; done
