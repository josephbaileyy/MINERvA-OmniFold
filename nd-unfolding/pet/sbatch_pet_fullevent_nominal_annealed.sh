#!/bin/bash
#SBATCH --job-name=fe_pet_ann
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=12:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_nominal_annealed/logs/fe_pet_ann_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_nominal_annealed/logs/fe_pet_ann_%j.err
#
# ANNEALED PRODUCTION NOMINAL — the first production artifact under the LR anneal adopted 2026-08-10.
# Reproduction test PREDECLARED in docs/orchestration/PREDECLARATION-20260810-annealed-production-reproduction.md
#   fold-forward dev expected -0.011724, band +/-0.010, PASS window [-0.021724, -0.001724]
#
# WHY THIS EXISTS RATHER THAN REUSING sbatch_pet_fullevent_nominal.sh. Job 56563092 used the canonical
# launcher and was CORRECTLY REFUSED by the driver's own guard: the 2026-08-08 artifact at
# fullevent_nominal/ exists and is marked complete, and the driver will not overwrite a finished
# publication artifact. That guard was right and the refusal cost 1:12 instead of destroying the
# baseline that the predeclaration, CLM-012's measured values, and the entire shape-validation chain are
# measured against.
#
# So this writes to a SEPARATE DIRECTORY. --allow-overwrite is deliberately NOT used: the annealed run is
# a DIFFERENT ESTIMATOR (different training policy), not a redo of the same one, so it gets its own
# artifact. Whether it ever becomes the canonical nominal is a PROMOTION decision and Joseph's -- he
# authorized the run, not a promotion. `--tag` is constrained to nominal|floor by the driver, so
# separation comes from --out, and weights_folder follows dirname(--out) automatically.
#
# Runs BOTH arms, same as the canonical launcher. That is deliberate: the predeclared +/-0.010 band was
# scaled from the ONE matched pair available (0.003380 in deviation), which is a scale and not a
# distribution. A fresh matched pair measures the annealed configuration's OWN scatter, which is the
# weakest part of the predeclaration, at no extra authorized cost (~6 GPU-h covers both arms).
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DRIVER="${REPO}/nd-unfolding/pet/train_fullevent_nominal.py"
TARGET_NPZ="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
EXPECTED_TARGET_SHA="fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
GATE3_MANIFEST="${REPO}/docs/orchestration/state/p3f-pet-gate3-source-manifest-56169838.json"

OUTDIR="${REPO}/nd-unfolding/pet/fullevent_nominal_annealed"
LOG_DIR="${OUTDIR}/logs"
NOMINAL_OUT="${OUTDIR}/pet_fullevent_nominal_weights.npz"
FLOOR_OUT="${OUTDIR}/pet_fullevent_floor_weights.npz"
BASELINE="${REPO}/nd-unfolding/pet/fullevent_nominal/pet_fullevent_nominal_weights.npz"

# THE POLICY IS NOT RESTATED HERE. Same reason as the canonical launcher (2026-08-06): a launcher that
# hardcodes policy drifts from the driver and the drift is only detected after a full training run.
# lr_policy in particular has NO FLAG by design -- see test_pet_fullevent_nominal_launcher.py.

mkdir -p "$LOG_DIR"
die() { echo "[fe_pet_ann][FAIL] $*" >&2; exit "${2:-1}"; }

echo "[fe_pet_ann] job=${SLURM_JOB_ID:-nojob} host=$(hostname)"
for f in "$DRIVER" "$TARGET_NPZ" "$GATE3_MANIFEST"; do
  [[ -s "$f" ]] || die "missing $f"
done
gs="$(sha256sum "$TARGET_NPZ" | cut -d' ' -f1)"
[[ "$gs" == "$EXPECTED_TARGET_SHA" ]] || die "target sha mismatch: $gs != $EXPECTED_TARGET_SHA" 3
echo "[fe_pet_ann] target sha OK ${gs:0:16}"

# The baseline must SURVIVE this job. Asserted before and after, because the whole reason this launcher
# exists is that the canonical one would have overwritten it.
[[ -s "$BASELINE" ]] || die "the 2026-08-08 baseline is missing; refusing to run without it" 4
BASE_SHA_BEFORE="$(sha256sum "$BASELINE" | cut -d' ' -f1)"
echo "[fe_pet_ann] baseline preserved-check, before: ${BASE_SHA_BEFORE:0:16}"

echo "[fe_pet_ann] engine sha256 (must be UNTOUCHED by the adoption): $(sha256sum "${REPO}/omnifold_nn/omnifold/omnifold.py" | cut -d' ' -f1 | cut -c1-16)"
echo "[fe_pet_ann] driver sha256: $(sha256sum "$DRIVER" | cut -d' ' -f1 | cut -c1-16)"

source "${REPO}/setup_salloc_env.sh"
module load tensorflow/2.15.0
export PYTHONUNBUFFERED=1

# BEN-075 rule (1): probe imports up front, and assert the driver actually carries the adopted policy.
python3 -c "
import sys; sys.path.insert(0, '${REPO}/nd-unfolding/pet')
import train_fullevent_nominal as d
p = d.NOMINAL_SEED_POLICY['lr_policy']
assert p['base_lr'] == 1e-4 and p['annealed_lr'] == 1e-5, p
assert p['applies_from_iteration'] == 1, p
print('[fe_pet_ann] driver declares the adopted lr_policy:', p['schedule'])
" || die "the driver does not declare the adopted lr_policy" 5

echo "[fe_pet_ann] ANNEALED NOMINAL train $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
python3 "$DRIVER" --inputs "$TARGET_NPZ" --out "$NOMINAL_OUT" --tag nominal \
  --gate3-manifest "$GATE3_MANIFEST" \
  || die "annealed nominal training failed"

echo "[fe_pet_ann] MATCHED GPU-FLOOR repeat (same seeds/config) $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
python3 "$DRIVER" --inputs "$TARGET_NPZ" --out "$FLOOR_OUT" --tag floor \
  --gate3-manifest "$GATE3_MANIFEST" \
  || die "annealed floor repeat failed"

BASE_SHA_AFTER="$(sha256sum "$BASELINE" | cut -d' ' -f1)"
[[ "$BASE_SHA_AFTER" == "$BASE_SHA_BEFORE" ]] \
  || die "THE 2026-08-08 BASELINE WAS MODIFIED (${BASE_SHA_BEFORE:0:16} -> ${BASE_SHA_AFTER:0:16})" 6
echo "[fe_pet_ann] baseline preserved-check, after: ${BASE_SHA_AFTER:0:16} UNCHANGED"

# Report the predeclared reproduction test. Reports, never decides -- and never widens the band.
python3 - "$NOMINAL_OUT" "$FLOOR_OUT" <<'PY'
import json, sys
import numpy as np
EXP, BAND = -0.011724, 0.010
def dev(p):
    with np.load(p, allow_pickle=True) as z:
        t = z["target"]
        try: t = t.item()
        except Exception: pass
        R = float(t["step1_class_ratio"])
        num = float(np.asarray(z["fold_forward_sum_w_push_reco"]).ravel()[0])
        den = float(np.asarray(z["fold_forward_sum_w_reco"]).ravel()[0])
        sp = z["seed_policy"]
        try: sp = sp.item()
        except Exception: pass
        lr = z["lr_policy_realized"].item() if "lr_policy_realized" in z.files else None
    return (num/den)/R - 1.0, sp.get("lr_policy"), lr
dn, pol_n, real_n = dev(sys.argv[1])
df, pol_f, real_f = dev(sys.argv[2])
print("[fe_pet_ann] ===== PREDECLARED REPRODUCTION TEST =====")
print(f"[fe_pet_ann] expected dev {EXP:+.6f}  band +/-{BAND}  window [{EXP-BAND:+.6f}, {EXP+BAND:+.6f}]")
for name, d in (("nominal", dn), ("floor", df)):
    verdict = ("REPRODUCED" if abs(d - EXP) <= BAND
               else ("FINDING: code paths disagree" if abs(d) < 0.05
                     else "FINDING: anneal did not take effect"))
    print(f"[fe_pet_ann]   {name:<8} dev {d:+.6f}   {verdict}")
print(f"[fe_pet_ann] MEASURED annealed scatter (nominal vs floor): {abs(dn-df):.6f} in deviation")
print(f"[fe_pet_ann]   -- the predeclared band was scaled from 0.003380 (one 08-08 pair); this is the "
      f"annealed configuration's own")
print(f"[fe_pet_ann] discriminator: lr_policy={pol_n}")
print(f"[fe_pet_ann]   realized nominal: {None if real_n is None else {k: real_n[k] for k in ('n_fits_base_lr','n_fits_annealed','verified_from_optimizer')}}")
print("[fe_pet_ann] No promotion. Branch C closed. Baseline untouched. Report before anything downstream.")
PY
echo "[fe_pet_ann] DONE $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
