#!/bin/bash
# Fresh-reader navigation check. Each task starts at README.md and follows only the canonical
# documents. Every hop is a grep that must find its target line; the script prints the line and
# exits 1 if any hop is missing. Run from the repository root:
#   bash docs/orchestration/state/next-preparation-20261009/structure/checks/nav.sh
set -u
fail=0
hop() {  # hop <task> <file> <fixed string>
  local hit
  hit=$(grep -n -F -- "$3" "$2" | head -1)
  if [[ -n "${hit}" ]]; then
    printf '%s | %s:%s\n' "$1" "$2" "$(echo "${hit}" | cut -c1-160)"
  else
    printf '%s | MISSING in %s: %s\n' "$1" "$2" "$3"
    fail=1
  fi
}
R=2d-unfolding/2D_OMNIFOLD_REFERENCE.md
P=docs/POST_PUBLICATION_REORG_PLAN.md

# T1 central producer of the frozen 2D value.
hop T1 README.md 'sbatch 2d-unfolding/sbatch_unfold_2d_MEFHC.sh'
hop T1 README.md '2d-unfolding/2D_OMNIFOLD_REFERENCE.md'
hop T1 "${R}" 'sbatch_unfold_2d_MEFHC.sh'
[[ -f 2d-unfolding/sbatch_unfold_2d_MEFHC.sh ]] && echo "T1 | target exists: 2d-unfolding/sbatch_unfold_2d_MEFHC.sh" || fail=1

# T2 adopted uncertainty producer (VL170 replicas -> VL172 rollup) and its cell-identity contract.
hop T2 README.md 'Which script produced the quoted 2D uncertainty'
hop T2 "${R}" '## Which script produced the quoted 2D uncertainty'
hop T2 "${R}" 'state/ki84-rebuild-20261006/sbatch_ki84_replicas.sh'
hop T2 "${R}" '**`uq/rollup_vl170_adoption.sh`**'
hop T2 "${R}" '**Reported-cell identity.**'
hop T2 "${R}" 'next-preparation-20261009/structure/REPORT.md'
for f in docs/orchestration/state/ki84-rebuild-20261006/sbatch_ki84_replicas.sh 2d-unfolding/uq/rollup_vl170_adoption.sh 2d-unfolding/uq/reported_cells.py; do
  [[ -f "${f}" ]] && echo "T2 | target exists: ${f}" || { echo "T2 | MISSING target ${f}"; fail=1; }
done

# T3 supported prospective entry points: the 2D event loop, and guarded N-D/PET compute.
hop T3 "${R}" 'A prospective run'
hop T3 README.md 'route new compute through the guarded'
hop T3 README.md 'python3 nd-unfolding/mnv_guarded_run.py'
[[ -f nd-unfolding/mnv_guarded_run.py ]] && echo "T3 | target exists: nd-unfolding/mnv_guarded_run.py" || fail=1

# T4 recovery of a path removed from main, and the gen5d discovery route.
hop T4 README.md 'POST_PUBLICATION_REORG_PLAN.md'
hop T4 "${P}" 'evidence/prepublication-2026-08-20-0b329e8a'
hop T4 "${P}" '### Deferred move design: the s5p generator-prediction family'
hop T4 "${P}" '### Move constraint: the 2D covariance modules'
hop T4 README.md 'gen5d'
exit "${fail}"
