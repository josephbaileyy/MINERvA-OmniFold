#!/bin/bash
# Phase-7 FINAL launcher: run the predeclared retraining-response set on the
# background-aware throw-bank (KNOWN_ISSUES #13/#16 fix). Non-destructive:
# writes to products/pet/bkgsub/p7_final/ (PRELIMINARY pre-fix results stay in
# p7/). PET reads the SHARED throw-bank directly (KNOWN_ISSUES #12), so we just
# repoint --bank; no PET rebank needed. Alignment is gated below.
#
# Sequence:
#   1. this script: alignment spot-check + submit 5 non-flux retrains + flux rank
#   2. when p7_final/pet_p7_flux_rank.json lands -> submit dominant flux retrain
#   3. when all 6 responses + null land -> assemble C_retrain (material bands)
set -eo pipefail
export HOME=/global/homes/j/josephrb
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
ND=$REPO/nd-unfolding
cd "$ND"

BANK="${PET_P7_BANK:-$ND/bank_uthrow_5d_bkgaware}"
OUTDIR="${PET_P7_OUTDIR:-products/pet/bkgsub/p7_final}"
NGLOBAL=32849103
mkdir -p "$OUTDIR"

echo "=== [final] bank presence + alignment gate: $BANK ==="
[[ -d "$BANK" ]] || { echo "[FAIL] bank dir absent: $BANK"; exit 2; }
for f in cv.npz sig_MaRES_t_1.npy sig_2p2h_t_1.npy sig_MaCCQE_t_1.npy \
         sig_LowQ2_t_1.npy sig_CCQEPauliSupViaKF_t_1.npy sig_flux_t_0.npy; do
  [[ -s "$BANK/$f" ]] || { echo "[FAIL] missing bank file: $BANK/$f"; exit 2; }
done

module load python 2>/dev/null || true
python3 - "$BANK" "$ND/bank_uthrow_5d" "$NGLOBAL" <<'PY'
import sys, numpy as np
bk, prefix, nglobal = sys.argv[1], sys.argv[2], int(sys.argv[3])
a = np.load(f"{bk}/sig_MaRES_t_1.npy").astype(np.float64)
assert a.shape == (nglobal,), f"[FAIL] bkgaware sig_MaRES_t_1 shape {a.shape} != ({nglobal},)"
assert np.isfinite(a).all(), "[FAIL] non-finite entries in bkgaware sig_MaRES_t_1"
b = np.load(f"{prefix}/sig_MaRES_t_1.npy").astype(np.float64)
# background-aware should differ from pre-fix (else the rebank was a no-op) but
# remain a small perturbation (background is ~0.35% of the selected sample)
d = np.abs(a - b)
frac_diff = float(np.mean(d > 1e-6))
print(f"[align] bkgaware sig_MaRES_t_1: shape={a.shape} finite=OK mean={a.mean():.4f} "
      f"min={a.min():.3e} max={a.max():.3e}")
print(f"[align] vs pre-fix: frac bins changed(>1e-6)={frac_diff:.4f} "
      f"max|Δratio|={d.max():.3e} (expect nonzero-but-small)")
if frac_diff == 0.0:
    print("[WARN] bkgaware ratio identical to pre-fix on MaRES — rebank may be a no-op; INVESTIGATE before trusting FINAL")
PY

echo "=== [final] squeue before submit ==="
squeue -u josephrb -o '%.12i %.24j %.8T %.10M' 2>/dev/null | grep -E 'pet_p7|JOBID' || true

echo "=== [final] submit 5 non-flux retrains (bkgaware -> $OUTDIR) ==="
for k in MaRES 2p2h MaCCQE LowQ2 CCQEPauliSupViaKF; do
  jid=$(sbatch -J pet_p7f_${k}_1 \
    --export=ALL,HOME=/global/homes/j/josephrb,UNIVERSE=${k}:1,PET_P7_BANK=$BANK,PET_P7_OUTDIR=$OUTDIR \
    pet/sbatch_phase7_retrain.sh | awk '{print $NF}')
  echo "  submitted FINAL ${k}:1 -> $jid"
done

echo "=== [final] submit flux ranking on bkgaware ==="
frjid=$(sbatch -J pet_p7f_fluxrank --account=m3246 --qos=shared --constraint=gpu \
  --nodes=1 --ntasks=1 --gpus=1 --cpus-per-task=32 --time=00:30:00 \
  --export=ALL,HOME=/global/homes/j/josephrb \
  --output=pet/pet_p7_%x_%j.out --error=pet/pet_p7_%x_%j.err \
  --wrap="cd $ND; module load python; python3 pet/phase7_flux_rank.py --bank $BANK --out $OUTDIR/pet_p7_flux_rank.json" \
  | awk '{print $NF}')
echo "  submitted FINAL flux rank -> $frjid"
echo "=== [final] launched. Dominant flux retrain submitted after ranking lands. ==="
