#!/bin/bash
# Guard tests for sbatch_foldforward_instrumented_closure.sh's G0/G1 -- run with NO allocation.
#
# WHY THIS EXISTS. G0's first version pinned the driver, the annealed wrapper and the engine and NOT
# closure_foldforward_instrumented.py -- the module that decides what the arm actually does -- so a
# task could satisfy every pin the launcher declared while running different code. The wrapper pin was
# added 2026-08-15 and this script is what makes it a guard that has been SEEN TO REFUSE rather than
# one nobody has watched fire. Generalised in BEN-312: the thing that verifies a run must name every
# object the run's behaviour depends on.
#
# REQUIRES bash >= 4 (the launcher uses `declare -A`). macOS ships bash 3.2, so run this on
# Perlmutter or any Linux login node. It touches no Slurm state, submits nothing, and writes only
# under a mktemp sandbox.
#
#   bash nd-unfolding/tests/test_foldforward_launcher_guards.sh
set -uo pipefail

if (( BASH_VERSINFO[0] < 4 )); then
  echo "SKIP: bash ${BASH_VERSION} < 4; the launcher uses declare -A. Run on a Linux login node." >&2
  exit 0
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ND="$(dirname "$HERE")"
REPO_REAL="$(dirname "$ND")"
LAUNCHER="${ND}/pet/sbatch_foldforward_instrumented_closure.sh"
[[ -s "$LAUNCHER" ]] || { echo "FAIL: launcher not found at $LAUNCHER" >&2; exit 1; }

pass=0; fail=0
ok()   { echo "  PASS  $1"; pass=$((pass+1)); }
bad()  { echo "  FAIL  $1"; fail=$((fail+1)); }

# Build a sandbox mirroring the paths G0 resolves, with real file contents.
sandbox() {
  local root; root="$(mktemp -d)"
  mkdir -p "${root}/nd-unfolding/pet" "${root}/omnifold_nn/omnifold" \
           "${root}/nd-unfolding/g2_fullevent/input"
  cp "${ND}/pet/closure_foldforward_instrumented.py" "${root}/nd-unfolding/pet/"
  cp "${ND}/pet/closure_powered_annealed_lr.py"      "${root}/nd-unfolding/pet/"
  cp "${ND}/pet/closure_powered_truth_reweight.py"   "${root}/nd-unfolding/pet/"
  cp "${REPO_REAL}/omnifold_nn/omnifold/omnifold.py" "${root}/omnifold_nn/omnifold/"
  : > "${root}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
  echo "$root"
}

run_guards() {  # run_guards <sandbox> <task_id> -> prints output, returns launcher's exit code
  local root="$1" task="$2"
  FF_GUARDS_ONLY=1 FF_REPO_OVERRIDE="$root" SLURM_ARRAY_TASK_ID="$task" \
    bash "$LAUNCHER" 2>&1
}

echo "== 1. clean sandbox: G0 must PASS and the guards must exit 0 =="
root="$(sandbox)"
out="$(run_guards "$root" 0)"; rc=$?
if (( rc == 0 )) && grep -q "G0 PASS" <<<"$out"; then ok "clean tree accepted (rc=0)"
else bad "clean tree rejected (rc=${rc}); output:"; echo "$out" | sed 's/^/        /'; fi
grep -q "guards passed, exiting before any work" <<<"$out" \
  && ok "guards-only mode stopped before any work" \
  || bad "guards-only mode did not stop before the work"
rm -rf "$root"

echo "== 2. THE NEW PIN: mutate the instrumentation wrapper -- G0 must REFUSE =="
root="$(sandbox)"
printf '\n# mutation: one comment line, nothing functional\n' \
  >> "${root}/nd-unfolding/pet/closure_foldforward_instrumented.py"
out="$(run_guards "$root" 0)"; rc=$?
if (( rc != 0 )) && grep -q "digest drift on closure_foldforward_instrumented.py" <<<"$out"; then
  ok "wrapper drift REFUSED (rc=${rc}) and the message names the file"
else
  bad "wrapper drift was NOT refused (rc=${rc}) -- the new pin does not fire"; echo "$out" | sed 's/^/        /'
fi
rm -rf "$root"

echo "== 3. the pre-existing pins still fire: mutate the driver =="
root="$(sandbox)"
printf '\n# mutation\n' >> "${root}/nd-unfolding/pet/closure_powered_truth_reweight.py"
out="$(run_guards "$root" 0)"; rc=$?
if (( rc != 0 )) && grep -q "digest drift on closure_powered_truth_reweight.py" <<<"$out"; then
  ok "driver drift REFUSED (rc=${rc})"
else bad "driver drift not refused (rc=${rc})"; echo "$out" | sed 's/^/        /'; fi
rm -rf "$root"

echo "== 4. engine pin fires =="
root="$(sandbox)"
printf '\n# mutation\n' >> "${root}/omnifold_nn/omnifold/omnifold.py"
out="$(run_guards "$root" 0)"; rc=$?
if (( rc != 0 )) && grep -q "digest drift on omnifold.py" <<<"$out"; then
  ok "engine drift REFUSED (rc=${rc})"
else bad "engine drift not refused (rc=${rc})"; echo "$out" | sed 's/^/        /'; fi
rm -rf "$root"

echo "== 5. G1 arm assignment: 0-2 -> arm0, 3-5 -> arm1 (with --correct-fold-forward), else refuse =="
root="$(sandbox)"
for t in 0 1 2; do
  out="$(run_guards "$root" "$t")"
  grep -q "G1 task=${t} -> arm0_draw${t}  extra=''" <<<"$out" \
    && ok "task ${t} -> arm0_draw${t}, no correction flag" \
    || { bad "task ${t} arm assignment wrong"; echo "$out" | sed 's/^/        /'; }
done
for t in 3 4 5; do
  d=$((t-3))
  out="$(run_guards "$root" "$t")"
  grep -q "G1 task=${t} -> arm1_draw${d}  extra='--correct-fold-forward'" <<<"$out" \
    && ok "task ${t} -> arm1_draw${d}, correction flag present" \
    || { bad "task ${t} arm assignment wrong"; echo "$out" | sed 's/^/        /'; }
done
out="$(run_guards "$root" 6)"; rc=$?
if (( rc != 0 )) && grep -q "outside 0-5" <<<"$out"; then ok "task 6 REFUSED by G1 (rc=${rc})"
else bad "task 6 was not refused (rc=${rc})"; fi
rm -rf "$root"

echo "== 6. FF_REPO_OVERRIDE must be INERT without FF_GUARDS_ONLY =="
root="$(sandbox)"
# MUTATE THE DRIVER, NOT THE WRAPPER, AND THE REASON IS A CONFOUND THIS TEST ALREADY HIT ONCE.
# The first version mutated the wrapper and asserted "no wrapper-drift message". It FAILED -- not
# because the override leaked, but because the REAL tree can legitimately carry a stale wrapper (it
# did: the fix for 57012031_3 was deliberately withheld from the cluster while _4/_5 were pending),
# so a wrapper-drift message arises either way and the assertion could not discriminate. The driver
# is receipt-pinned and matches its digest everywhere, so a DRIVER-drift message can ONLY come from
# this sandbox -- which is what makes it a discriminator rather than a coincidence.
printf '\n# mutation\n' >> "${root}/nd-unfolding/pet/closure_powered_truth_reweight.py"
# No FF_GUARDS_ONLY: the override must be ignored, so G0 reads the REAL tree, not this sandbox.
#
# TASK 6 IS DELIBERATE AND IS NOT INCIDENTAL. Without FF_GUARDS_ONLY there is no guards-only exit, so
# a valid task id would fall through G0/G1/G2 into `module load` and `python3 -u $WRAPPER` and START A
# REAL TRAINING ON A LOGIN NODE. Task 6 is refused by G1, which stops execution before any work while
# still discriminating exactly what this case is about: if the override HAD taken effect, G0 would
# have failed on wrapper drift BEFORE G1 ever ran. So "no drift message, and G1 refused" is the pass.
out="$(FF_REPO_OVERRIDE="$root" SLURM_ARRAY_TASK_ID=6 bash "$LAUNCHER" 2>&1 || true)"
if grep -q "digest drift on closure_powered_truth_reweight.py" <<<"$out"; then
  bad "the override took effect WITHOUT FF_GUARDS_ONLY -- a real run could be redirected"
else
  ok "override inert without FF_GUARDS_ONLY (the sandbox's mutated driver was never read)"
fi
rm -rf "$root"

echo
echo "guards: ${pass} passed, ${fail} failed"
(( fail == 0 )) || exit 1
