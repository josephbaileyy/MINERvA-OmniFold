#!/bin/bash
# TEST the intended deterministic configuration, in the environment that matters.
#
# Joseph, 2026-09-18: "Before buying cross-allocation repeats, establish and test the intended
# deterministic configuration. Distinguish results from the historical configuration from results
# under changed controls. Do not assume that setting four OpenMP variables establishes determinism."
#
# THIS IS THE CHEAP TEST THAT COMES BEFORE THE EXPENSIVE ONE. It measures the MECHANISM -- thread
# count sets reduction order, and reduction order is how a cross-allocation difference reaches the
# numbers -- instead of sampling the outcome across allocations. If the output tracks the thread
# count, no number of cross-node repeats fixes it, and the repeat should not be bought.
#
# WHY IT RUNS HERE AND NOT ON A LOGIN NODE. It TRAINS. The prior backend inspection was done on a
# login node precisely because it trained nothing and wrote nothing; that precedent does not extend
# to fitting 18 models. This is a batch job in the production environment, which is also the only
# venue whose answer is about the campaign rather than about a laptop.
#
# WHAT A TERMINAL RESULT CANNOT AUTHORIZE: it does not adopt a configuration -- applying the
# overlay to the production estimator is a MATERIAL CHANGE TO THE ESTIMATOR and is Joseph's
# decision -- does not establish determinism across NODES, since one node cannot show whether a
# different CPU model selects different vector kernels, and does not license a repeat.
#
#SBATCH --job-name=z_det_probe
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=16G --time=00:15:00
#SBATCH --output=uq_5d/z_det_probe_%j.out --error=uq_5d/z_det_probe_%j.err
set -eo pipefail

# Asserted EQUAL to the #SBATCH directives above by tests/test_run_determinism_probe.sh_static.py,
# which reads this file statically: sbatch executes a COPY, so $0 and BASH_SOURCE both name the
# spool path and neither can be trusted to locate these directives at runtime.
ENFORCED_NTASKS=1
ENFORCED_WALL_HOURS=0.25
ENFORCED_TASK_HOURS=0.25

# shellcheck source=lib_r5_admission.sh
. "$(dirname "${BASH_SOURCE[0]:-$0}")/lib_r5_admission.sh" 2>/dev/null \
  || . "${MNV_CODE_ROOT:?set it to the reviewed deployment tree for this run}/nd-unfolding/lib_r5_admission.sh"

CODE_ROOT="${MNV_CODE_ROOT:?set it to the reviewed deployment tree for this run}"
OUT="${MNV_OUT:?set it to the output path for the probe record, under a DIAGNOSTIC directory}"
R5_RECEIPT="${MNV_R5_RECEIPT:?set it to a fresh committed R5 meter receipt}"
DECLARED_TASK_HOURS="${MNV_DECLARED_TASK_HOURS:?set it to the reservation you are declaring}"
ROWS="${MNV_ROWS:-200000}"
# ⚠ COLON-SEPARATED, NOT COMMA. `sbatch --export=ALL,A=1,B=2` parses its argument as a
# comma-separated list of NAME=VALUE, so a comma inside a value splits the LIST -- backslash
# escaping does not survive it. Job 58507305 COMPLETED with `MNV_THREAD_GRID=1` because of exactly
# that, and every cell ran at one thread: the run was green and the thread axis was gone.
THREAD_GRID="${MNV_THREAD_GRID:-1:2:4:8}"

QUESTION="Does the intended deterministic configuration actually deliver identical estimator \
output, and does it do so INVARIANTLY in the thread count -- the channel a cross-allocation \
difference would act through? Separately: do the four OpenMP variables change anything at all, \
given that this repository has measured LightGBM to ignore OMP_NUM_THREADS?"
DECISION_VALUE="Whether to buy cross-allocation repeats at all, and under WHICH configuration. A \
pinned result is a property of a different estimator than the one that made the existing \
products, which z_lgbm_overlay already declares as a divergence from the historical chain."

# ---- REFUSAL 6: separate outputs -- this is a diagnostic and is labelled as one ---------------
case "$OUT" in
  *DIAGNOSTIC*) : ;;
  *)
    echo "REFUSED -- MNV_OUT must contain DIAGNOSTIC in its path. Got: $OUT" >&2
    exit 6 ;;
esac
if [ -e "$OUT" ]; then
  echo "REFUSED -- $OUT already exists. Overwriting would destroy the record it replaces." >&2
  exit 7
fi

# ---- REFUSAL 14: THE THREAD AXIS IS THE SUBJECT, so a one-valued grid is refused -------------
# Job 58507305 COMPLETED, exit 0, verdict MEASURED, and measured nothing about thread-count
# invariance -- the channel this probe exists to test. A degenerate axis must not be able to
# produce a green run, so it is a refusal here rather than a caveat in the record.
_grid_n=$(printf %s "$THREAD_GRID" | tr ":, " "\n\n\n" | grep -c .)
if [ "${_grid_n:-0}" -lt 2 ]; then
  echo "REFUSED -- MNV_THREAD_GRID resolved to $_grid_n value(s): $THREAD_GRID" >&2
  echo "          The thread axis IS the subject. Use colons, not commas: sbatch --export parses" >&2
  echo "          its argument as a comma-separated NAME=VALUE list, so a comma inside a value" >&2
  echo "          splits the list and the grid silently becomes its first element." >&2
  exit 14
fi

# ---- THE ENVIRONMENT COMES FIRST, AND THE ORDER IS THE BUG THAT JOB 58506753 FOUND -----------
# That job failed in 4 s printing "R5 admission failed for 0.25 CPU task-h". It had not failed
# admission: this block ran AFTER the admission check, so `python3` was still the node default
# 3.6.15, which cannot parse `r5_meter.py` (`from __future__ import annotations`). The SyntaxError
# exited nonzero and the gate read it as a refusal. An environment fault reported as an accounting
# fault. The environment is a PRECONDITION of evaluating the boundary, so it is established first.
r5_source_environment "$CODE_ROOT" || exit $?
r5_require_interpreter "$CODE_ROOT" || exit $?
if ! python3 -c "import lightgbm, numpy" 2>/dev/null; then
  echo "REFUSED -- the interpreter cannot import lightgbm and numpy, so the subject of this" >&2
  echo "          probe cannot be loaded. Discovering that ON the node spends the reservation" >&2
  echo "          to learn it; run this import on a login node before submitting." >&2
  python3 -V >&2
  exit 11
fi
python3 -c "import lightgbm,sys,platform; print('  lightgbm      :', lightgbm.__version__); print('  python        :', sys.version.split()[0], platform.machine())"

# ---- REFUSAL 8 and 9: the reservation is the cap, and admission is verified -------------------
r5_require_declared_cap "$DECLARED_TASK_HOURS" "$ENFORCED_TASK_HOURS" \
  "$ENFORCED_NTASKS" "$ENFORCED_WALL_HOURS" || exit $?
r5_admission_check "$CODE_ROOT" "$R5_RECEIPT" "$ENFORCED_TASK_HOURS" 0 || exit $?

r5_record_preamble "$QUESTION" "$DECISION_VALUE" \
  "rows=$ROWS thread_grid=$THREAD_GRID arms=historical,det_only,pinned (synthetic data; the \
subject is estimator arithmetic, not physics)" \
  "$ENFORCED_NTASKS" "$ENFORCED_WALL_HOURS" "$ENFORCED_TASK_HOURS" "$R5_RECEIPT"

echo "=== environment, recorded because the answer is a property of it ==="
echo "  hostname       : $(hostname)"
echo "  SLURM_JOB_ID   : ${SLURM_JOB_ID:-unset}"
echo "  SLURM_CPUS     : ${SLURM_CPUS_PER_TASK:-unset}"

cd "$CODE_ROOT/nd-unfolding"
_rc=0
python3 z_determinism_probe.py --mode driver --rows "$ROWS" --thread-grid "$THREAD_GRID" \
  --repeats 2 --out "$OUT" || _rc=$?

if [ "$_rc" -ne 0 ]; then
  echo "DETERMINISM PROBE rc=$_rc." >&2
  echo "  rc 3 means UNAVAILABLE: the subject did not load, so NOTHING was measured. That is not" >&2
  echo "  a finding of determinism and the record says so in those words." >&2
  r5_retry_notice
  exit "$_rc"
fi
echo "DETERMINISM PROBE COMPLETE -- DIAGNOSTIC, NON-ADOPTED. Record: $OUT"
echo "  It adopts nothing. Applying the overlay is a material change to the estimator."
