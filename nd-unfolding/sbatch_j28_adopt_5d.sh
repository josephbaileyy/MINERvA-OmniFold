#!/bin/bash
#SBATCH --job-name=j28_adopt_5d
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=120G --time=04:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_5d/j28_adopt_%j.out --error=uq_5d/j28_adopt_%j.err
# J28 adoption on the REPAIRED 160-throw ensemble (2026-08-06).
#
# Run with a dependency on the regeneration array:
#   sbatch --dependency=afterok:56427580 sbatch_j28_adopt_5d.sh
#
# WHY THIS EXISTS AS A SCRIPT rather than typed commands: the ensemble has MIXED PROVENANCE and the
# correct handling is not uniform. `unified_throw_cov.py:255` stamps `flux_normalized=1` on
# newly-written throws, so:
#
#   slabs 0-29   throws 0-119   UNSTAMPED, pre-J28 (Phi_CV)  -> MUST be rescaled
#   slabs 30-39  throws 120-159 STAMPED, already corrected    -> MUST NOT be rescaled
#
# Rescaling a stamped slab would double-correct it; `rescale_flux_universes.py:261` fails closed on
# exactly that, and `--combine` refuses UNSTAMPED slabs (`unified_throw_cov.py:332,372`). So both
# mistakes abort rather than corrupt -- but the split has to be built deliberately, which is what the
# symlink staging below does. Mixing the two halves is legitimate because the post-hoc rescale and the
# native correction were shown to agree to 1.4e-12 / 6.7e-12 over all 10,694 bins on throws 120/121
# (`validate_rescale_identity.py`; ledger 2026-08-06) -- they are the same object computed two ways.
#
# ADOPTS NOTHING INTO THE LEDGER. It writes its own ROOT and prints adopt output for BOTH mean-shift
# conventions. The F7 rule (`CORRECTED_UQ_PRODUCTION_STATUS.md:73-78`) requires the CV-centered variant
# because ||mean_shift|| is 4.69x the sampling floor; replacing the quarantined numbers is a separate,
# human-reviewed commit.
set -eo pipefail   # NOT -u: conda activate aborts under nounset (AGENTS.md)
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=32
cd "${REPO}/nd-unfolding"

TAG="20260806_full160"
STAGE_OLD="uq_5d/stage_old_${TAG}"
RESCALED="uq_5d/rescaled_${TAG}"
UNION="uq_5d/union_${TAG}"
OUT_ROOT="uq_5d/unified_throw_cov_5d_fluxfix_${TAG}.root"
OUT_JSON="uq_5d/rescaled_${TAG}/j28_reroll_${TAG}.json"

rm -rf "$STAGE_OLD" "$UNION"
mkdir -p "$STAGE_OLD" "$UNION" "$RESCALED"

# --- 0. fail closed unless the ensemble is complete and split exactly as expected -----------------
python3 - <<'PY'
import glob, re, sys
import numpy as np
have, stamped, unstamped = set(), [], []
for f in sorted(glob.glob("uq_5d/uthrow_slabs_5d_sb/uthrow5d_slab_*.npz")):
    i = int(re.search(r"slab_(\d+)", f).group(1))
    with np.load(f, allow_pickle=True) as d:
        have |= set(np.atleast_1d(d["throws"]).ravel().astype(int).tolist())
        (stamped if ("flux_normalized" in d.files and int(d["flux_normalized"]) == 1)
         else unstamped).append(i)
missing = [i for i in range(160) if i not in have]
if missing:
    sys.exit(f"[FAIL] ensemble incomplete: {len(missing)} throws missing {missing[:12]}...")
if sorted(unstamped) != list(range(30)) or sorted(stamped) != list(range(30, 40)):
    sys.exit(f"[FAIL] unexpected stamp split: unstamped={sorted(unstamped)} stamped={sorted(stamped)}")
print(f"[gate] 160/160 throws present; unstamped 0-29, stamped 30-39 -- split as expected")
PY

# --- 1. stage the pre-J28 half and rescale ONLY it ------------------------------------------------
for i in $(seq 0 29); do
  ln -sf "${REPO}/nd-unfolding/uq_5d/uthrow_slabs_5d_sb/uthrow5d_slab_${i}.npz" \
         "${STAGE_OLD}/uthrow5d_slab_${i}.npz"
done
echo "[stage] $(ls ${STAGE_OLD} | wc -l) pre-J28 throw slabs staged for rescale"

python3 rescale_flux_universes.py \
  --throw-slabs "${STAGE_OLD}/uthrow5d_slab_*.npz" \
  --block-slabs 'uq_5d/block_slabs_5d_sb/block5d_*.npz' \
  --bank bank_uthrow_5d \
  --cv products/5d/xsec_5d_MEFHC_5iter_lgbm.root \
  --out-dir "${RESCALED}" \
  --out-root "${RESCALED}/unified_throw_cov_5d_rescaledhalf.root" \
  --out-json "${OUT_JSON}"

# --- 2. build the union: rescaled 0-29 + natively-corrected 30-39 ---------------------------------
for i in $(seq 0 29); do
  ln -sf "${REPO}/nd-unfolding/${RESCALED}/uthrow5d_slab_${i}.npz" "${UNION}/uthrow5d_slab_${i}.npz"
done
for i in $(seq 30 39); do
  ln -sf "${REPO}/nd-unfolding/uq_5d/uthrow_slabs_5d_sb/uthrow5d_slab_${i}.npz" \
         "${UNION}/uthrow5d_slab_${i}.npz"
done
echo "[stage] union has $(ls ${UNION} | wc -l) slabs (expect 40)"

# --- 3. combine the full corrected 160 ------------------------------------------------------------
python3 unified_throw_cov_5d.py \
  --combine "${UNION}/uthrow5d_slab_*.npz" \
  --expected-throws 0-159 \
  --block-slabs "${RESCALED}/block5d_*.npz" \
  --bank bank_uthrow_5d --iters 5 --null \
  --out-root "${OUT_ROOT}"

# --- 4. adopt in BOTH conventions (F7: CV-centered is required, mean-centered kept for comparison) -
#
# --out IS PASSED EXPLICITLY, TWICE, AND NEITHER IS THE DEFAULT. `adopt_unified_5d.py:79-80` defaults
# --out to uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root and opens it
# "RECREATE" (:158). Taking the default would (a) overwrite the existing July adopted product, which is
# quarantined but is still the historical artifact the ledger describes, and (b) have the CV-centered run
# silently clobber the mean-centered one, leaving one file that looks like both. Distinct tagged paths.
ADOPT_MC="${RESCALED}/adopted_meancentered_${TAG}.root"
ADOPT_CV="${RESCALED}/adopted_cvcentered_${TAG}.root"
echo "=== adopt: mean-centered -> ${ADOPT_MC} ==="
python3 adopt_unified_5d.py --uthrow "${OUT_ROOT}" --out "${ADOPT_MC}" 2>&1 | tail -25
echo "=== adopt: CV-centered (the F7-required variant) -> ${ADOPT_CV} ==="
python3 adopt_unified_5d.py --uthrow "${OUT_ROOT}" --out "${ADOPT_CV}" --cv-centered 2>&1 | tail -25

echo "=== the July adopted product must be UNTOUCHED by this job ==="
ls -l uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root 2>/dev/null \
  || echo "  (not present on this tree)"

echo "[done] corrected 160-throw ROOT: ${OUT_ROOT}"
echo "[done] NOTHING ADOPTED INTO THE LEDGER -- replacing the quarantined numbers is a separate commit."
