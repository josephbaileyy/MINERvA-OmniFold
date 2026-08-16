#!/bin/bash
# READ-ONLY reproduction of stage 2's SKIP predicate, per endpoint. Writes nothing.
# stage 2 SKIPs iff:  -s OUT  &&  -s REC  &&  valid_root(OUT)  &&  p4_check_receipt.py passes
#
# ENVIRONMENT IS THE LAUNCHER'S OWN, NOT `module load tensorflow`. First attempt used the TF
# module and got 10/10 "valid_root failed" -- because ROOT is not importable there at all
# (perlmutter ROOT/TF env split). A uniform failure across every endpoint was the tell. Errors are
# now PRINTED rather than swallowed, so a failure can never again be attributed to the wrong cause.
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
ND=$REPO/nd-unfolding
source "$REPO/setup_salloc_env.sh" >/dev/null 2>&1
MERGEDIR=$ND/active_universe_5d/standard/merged
OUTDIR=$ND/active_universe_5d/standard/unfolds
cd $ND || exit 9
echo "python : $(python3 -V 2>&1)"
echo "ROOT   : $(python3 -c 'import ROOT;print(ROOT.gROOT.GetVersion())' 2>&1 | tail -1)"
echo "git    : $(git rev-parse --short HEAD)"
echo
for BAND in BeamAngleX BeamAngleY MuonResolution Muon_Energy_MINERvA Muon_Energy_MINOS; do
for EP in 0 1; do
  tag="${BAND}_${EP}"
  MERGED="$MERGEDIR/runEventLoopOmniFold_5D_MEFHC_active_${tag}.root"
  OUT="$OUTDIR/5d_xsec_MEFHC_5iter_lgbm_uni_full_${tag}.root"
  REC="$OUT.done"
  printf '%-24s ' "$tag"
  [[ -s "$OUT"    ]] || { echo "WOULD-RERUN: unfold ROOT absent/empty"; continue; }
  [[ -s "$REC"    ]] || { echo "WOULD-RERUN: receipt .done absent/empty"; continue; }
  [[ -s "$MERGED" ]] || { echo "WOULD-ABORT: merged input absent"; continue; }
  VR=$(python3 -c "
import ROOT,sys
ROOT.gErrorIgnoreLevel=ROOT.kFatal
f=ROOT.TFile.Open('$OUT')
if not f or f.IsZombie(): print('zombie/unopenable'); sys.exit(1)
if f.TestBit(ROOT.TFile.kRecovered): print('kRecovered'); sys.exit(1)
h=f.Get('hXSecND_flat')
if not h: print('no hXSecND_flat'); sys.exit(1)
n=h.GetNbinsX()
if n!=65856: print(f'nbins {n} != 65856'); sys.exit(1)
print('ok')
" 2>&1 | tail -1)
  if [[ "$VR" != "ok" ]]; then echo "WOULD-RERUN: valid_root -> $VR"; continue; fi
  if RCHK=$(python3 p4_check_receipt.py --receipt "$REC" --tag "$tag" --root "$OUT" --merged "$MERGED" 2>&1); then
    echo "WOULD-SKIP  (receipt validated)"
  else
    echo "WOULD-RERUN: $(echo "$RCHK" | tail -1)"
  fi
done; done
