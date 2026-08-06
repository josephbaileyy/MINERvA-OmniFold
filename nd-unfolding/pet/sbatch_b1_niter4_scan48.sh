#!/bin/bash
#SBATCH --job-name=b1nit4
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=04:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/b1_closure/logs/b1niter4_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/b1_closure/logs/b1niter4_%j.err
#
# B1 FOLD-FORWARD RATE-INJECTION CLOSURE at a parameterised niter -- the k-scan arms.
#
# WALLTIME MUST BE SIZED PER k, ON THE COMMAND LINE (BEN-030, second rule: measure the per-unit rate
# from the run you are actually sizing, never from a note about a differently-shaped one). Measured
# k=4 rates from the split arms themselves: 56400517 16 seeds / 01:34:24 = 5.90 min/seed; 56400519
# 32 seeds / 03:16:09 = 6.13 min/seed. Cost is ~linear in k, so scale by k/4 and add margin:
#   k=5 -> ~7.5 min/seed  =>  16 seeds ~2.0 h (4 h wall ok);  32 seeds ~4.0 h (NEEDS 8 h, not 4).
# The 4 h default in the header above is the k=4 sizing. Pass `--time` explicitly for any other k.
# Note the 48-seed job's apparent 2.9 min/seed was NOT reproducible on the split runs (different
# nodes / contention), which is itself the reason to re-measure rather than reuse a rate.
#
# WHY THIS ARM EXISTS. docs/OPEN_ITEMS.md item (e) says the niter=3 choice owes a REGULARIZATION
# justification rather than a gate-shaped one. The receipted 48-seed k=2/k=3 arms actually supply
# both halves of one -- bias 3.8008% -> 2.1876%, tracking the closed form (1-a)^k (R-1)/R to under
# 0.1 pp, at flat variance (sd 0.8153% vs 0.8444%, ratio 1.036). But that pair argues "k >= 3", not
# "k = 3": the bias term is monotone decreasing in k and nothing measured bounds k from above.
# This arm measures the k=4 point. Predicted bias 1.2617% from the closed form; if the spread is
# again flat, the record must say plainly that the stopping point is NOT set by this measurement
# (it is set by cost and by the literature default of 3), rather than implying the data chose it.
#
# LIKE-FOR-LIKE IS THE WHOLE POINT. Every parameter below is copied from the k=3 arm's own receipt
# entry (nd-unfolding/products/pet/b1_closure/..._scan32_measured_N240k_niter3_seeds23plus.json,
# runs[0]) and NOT from memory or from the script defaults -- the script's defaults are the STALE
# recoil-only operating point (r-inject 1.135, acceptance 0.621, niter 2), which is exactly the
# hardcoded-superseded-constant trap written up in
# docs/orchestration/FINDING-20260806-campaign-pin-inverted-on-insignificant-variance.md.
# Seeds 7..54 reproduce the union of the two existing arms, submitted as the SAME 16 + 32 split they
# use -- see the SPLIT THE ARM note below for why that split is load-bearing and not cosmetic.
# Submit both halves with:
#   sbatch --export=ALL,HOME=/global/homes/j/josephrb,B1_SEED_START=7,B1_SCAN_SEEDS=16  <this file>
#   sbatch --export=ALL,HOME=/global/homes/j/josephrb,B1_SEED_START=23,B1_SCAN_SEEDS=32 <this file>
#
# GPU, not login node, and not CPU. The k=2/k=3 arms were produced on interactive GPU; the local
# login-node wrapper for this same script was killed three times on 08-05
# (nd-unfolding/pet/AUTONOMOUS_LOG_20260805.md:1104). Matching hardware also keeps the seed spread
# comparable across arms, which is the quantity being compared.
#
# THE --output DIRECTORY MUST EXIST BEFORE sbatch -- slurmstepd opens it before exec'ing this
# script and will not create it. b1_closure/logs/.gitkeep is tracked so it exists in a checkout.
#
# set -u intentionally omitted (module/conda hooks abort under nounset -- AGENTS.md).
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DRIVER="${REPO}/nd-unfolding/pet/closure_b1_rate_injection.py"
OUTDIR="${REPO}/nd-unfolding/products/pet/b1_closure"
LOG_DIR="${REPO}/nd-unfolding/pet/b1_closure/logs"
RUN_ID="slurm-${SLURM_JOB_ID:-nojob}"

# The driver is hash-pinned in docs/orchestration/state/p3f-pet-gate4-launch-code-gate-20260806.json
# (`files.closure_rate_injection`). Pin it here too so an edit between submission and dispatch fails
# closed instead of silently producing an arm that is not comparable to the bound k=2/k=3 products.
EXPECTED_DRIVER_SHA="7b470ca22560c9c668c1dce34bce73603047538b6602f1166826dfb487c7fa24"

# Operating point -- read out of the k=3 arm's receipt, see header.
R_INJECT="1.1240802949941018"
ACCEPTANCE="0.4185618199216587"
N_EVENTS="240000"
EPOCHS="8"
TOLERANCE="0.05"

# `niter` is a parameter, not a constant, despite this file's name. The name is HISTORICAL and must
# not be changed: it is cited in ND_OMNIFOLD_RUN_LOG.md and in BEN-030, and renaming a tracked script
# cited in a RUN_LOG is forbidden (CLAUDE.md). Read the arm's k from `B1_NITER` or from the product
# filename, never from this file's name.
NITER="${B1_NITER:-4}"

# SPLIT THE ARM, and do not "tidy" it back into one job. The first attempt (56397442) ran all 48
# seeds in ONE job with a 2 h wall, sized off the k=3 arm's "~7 minutes" note. Measured rate here is
# ~2.9 min/seed, so 48 seeds needs ~2 h 20 m: it timed out at seed ~41 and wrote NOTHING, because the
# driver emits its single --json only after the last seed returns. ~1 h 50 m of GPU, zero product.
#
# The k=2/k=3 arms were split 16 (seeds 7-22) + 32 (seeds 23-54). That split was NOT cosmetic -- it is
# the only checkpointing this scan has. Collapsing it removed the partial credit and made a walltime
# kill total. Keeping the same split also makes the k=4 products file-for-file comparable with the
# four hash-bound k=2/k=3 products.
SEED_START="${B1_SEED_START:-7}"
SCAN_SEEDS="${B1_SCAN_SEEDS:-16}"

# Mirror the k=3 arm's exact naming so the four-arm set reads as one family.
if [[ "$SEED_START" == "7" ]]; then
  FINAL="${OUTDIR}/closure_b1_rate_injection_scan${SCAN_SEEDS}_measured_N240k_niter${NITER}.json"
else
  FINAL="${OUTDIR}/closure_b1_rate_injection_scan${SCAN_SEEDS}_measured_N240k_niter${NITER}_seeds${SEED_START}plus.json"
fi
PARTIAL="${FINAL}.partial"

mkdir -p "$OUTDIR" "$LOG_DIR"

sha_of() { sha256sum "$1" | awk '{print $1}'; }

fail() {
  echo "[b1nit${NITER}][FAIL] $1" >&2
  {
    echo "run_id=${RUN_ID}"
    echo "outcome=FAIL"
    echo "reason=$1"
    echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } > "${OUTDIR}/DONE.b1niter${NITER}.${RUN_ID}.txt"
  exit 1
}

[[ -n "${SLURM_JOB_ID:-}" ]] || fail "must run under sbatch (SLURM_JOB_ID unset)"
[[ -f "$DRIVER" ]] || fail "driver missing: $DRIVER"
[[ "$(sha_of "$DRIVER")" == "$EXPECTED_DRIVER_SHA" ]] || \
  fail "driver changed after submission (want $EXPECTED_DRIVER_SHA)"

module load tensorflow/2.15.0

cd "$REPO"
echo "[b1nit${NITER}] run_id=${RUN_ID} host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "[b1nit${NITER}] driver=${EXPECTED_DRIVER_SHA}"
echo "[b1nit${NITER}] HEAD=$(git rev-parse --short HEAD) dirty=$(git status --porcelain --untracked-files=no | wc -l)"
echo "[b1nit${NITER}] R=${R_INJECT} a=${ACCEPTANCE} niter=${NITER} epochs=${EPOCHS} N=${N_EVENTS} seeds=${SEED_START}..$((SEED_START + SCAN_SEEDS - 1))"

# Write to .partial and rename only after the driver returns. BEN-023 / J35: a resume guard that
# tests existence rather than completeness lets a truncated product permanently block its own
# repair, so the completed file must never appear at its final path mid-run.
set +e
srun -n 1 -c 32 --gpus=1 python3 "$DRIVER" \
  --r-inject "$R_INJECT" \
  --acceptance "$ACCEPTANCE" \
  --n-events "$N_EVENTS" \
  --niter "$NITER" \
  --epochs "$EPOCHS" \
  --seed "$SEED_START" \
  --scan-seeds "$SCAN_SEEDS" \
  --tolerance "$TOLERANCE" \
  --json "$PARTIAL"
rc=$?
set -e

echo "[b1nit${NITER}] driver exit=${rc} end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# rc=1 means VERDICT:FAIL, which for THIS arm is a result, not an error: the arm exists to measure
# the k=4 bias and spread, and those numbers are equally valid either way. Only a missing or
# unparseable report is a failure. Distinguish the two rather than discarding data on a nonzero rc.
[[ -s "$PARTIAL" ]] || fail "driver produced no report (exit ${rc})"
python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
runs=d['runs']
assert len(runs)==${SCAN_SEEDS}, 'want ${SCAN_SEEDS} runs, got %d'%len(runs)
assert all(r['niter']==${NITER} for r in runs), 'niter drift in report'
" "$PARTIAL" || fail "report incomplete or wrong configuration (exit ${rc})"

mv "$PARTIAL" "$FINAL"
echo "[b1nit${NITER}] wrote ${FINAL}"

# The sentinel records the OUTCOME and the two numbers this arm was launched to get, so a collector
# that reads only the sentinel is not misled into thinking "the job ran" means "the gate passed".
python3 - "$FINAL" "${OUTDIR}/DONE.b1niter${NITER}.${RUN_ID}.txt" "${RUN_ID}" "${rc}" <<'PY'
import json, statistics, sys
rep, out, run_id, rc = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
d = json.load(open(rep))
runs = d["runs"]
dev = [r["corrected"]["dev_from_R"] for r in runs]
tol = runs[0]["tolerance_used"]
with open(out, "w") as fh:
    fh.write("run_id=%s\n" % run_id)
    fh.write("outcome=REPORT_COMPLETE\n")
    fh.write("driver_exit=%s\n" % rc)
    fh.write("verdict=%s\n" % d["verdict"])
    fh.write("niter=%d\n" % runs[0]["niter"])
    fh.write("seeds=%d\n" % len(runs))
    fh.write("closed_form_floor=%.6f\n" % runs[0]["structural_floor_worst_case"])
    fh.write("dev_mean=%.6f\n" % statistics.fmean(dev))
    fh.write("dev_sd=%.6f\n" % statistics.stdev(dev))
    fh.write("dev_max=%.6f\n" % max(dev))
    fh.write("exceed_tol=%d/%d\n" % (sum(1 for x in dev if x > tol), len(dev)))
    fh.write("report=%s\n" % rep)
print(open(out).read())
PY

echo "[b1nit${NITER}] sentinel=${OUTDIR}/DONE.b1niter${NITER}.${RUN_ID}.txt"
