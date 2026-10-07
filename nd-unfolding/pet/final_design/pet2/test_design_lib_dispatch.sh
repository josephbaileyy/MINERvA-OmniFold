#!/bin/bash
# DESIGN_DRY_RUN test of final_design/jobs/design_lib.sh's runner dispatch (needs bash >= 4).
#   bash test_design_lib_dispatch.sh      -> prints "PASS n" and exits 0, or "FAIL ..." and exits 1
set -uo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
MINE=$(cd "$HERE/../../../.." && pwd)
export MINE SLURM_JOB_ID=dryrun
OUT=$(mktemp -d); export OUT
trap 'rm -rf "$OUT"' EXIT
source "$MINE/nd-unfolding/pet/improvement_campaign/confirm/jobs/confirm_lib.sh"
source "$MINE/nd-unfolding/pet/final_design/jobs/design_lib.sh"
export DESIGN_DRY_RUN=1 BANKS=/nonexistent/banks.npz
T=$'\t'
n=0; fail() { echo "FAIL: $*"; exit 1; }
has() { grep -qxF -- "$2" <<< "$1" || fail "$3: missing '$2'"; }
hasnt() { ! grep -qxF -- "$2" <<< "$1" || fail "$3: unexpected '$2'"; }
row7="d1-H1-F0${T}../../../final_design/configs/dev1/x.json${T}abc${T}F:0${T}dev${T}-${T}--step2-miss-mode efficiency_corrected"
out=$(run_row "$row7" 0 123) || fail "7-column row returned non-zero"
has "$out" "$MINE/nd-unfolding/pet/final_design/runner/run_design.py" 7col; n=$((n+1))
hasnt "$out" "--theirs-cache" 7col; n=$((n+1))
has "$out" "efficiency_corrected" 7col; n=$((n+1))
for r in - runner/run_design.py final_design/runner/run_design.py; do
  out=$(run_row "${row7}${T}${r}" 0 123) || fail "8-column row '$r' returned non-zero"
  has "$out" "$MINE/nd-unfolding/pet/final_design/runner/run_design.py" "runner $r"; n=$((n+1))
done
rowp="dev2P-P2preS1-T1-R1${T}../../../final_design/configs/dev2P/y.json${T}def${T}T:1${T}R1_x1.05+D1_p0.350${T}-${T}--step2-miss-mode efficiency_corrected --nonfinite-momentum zero --nonfinite-addinfo zero${T}final_design/pet2/run_pet2_replicate.py"
out=$(run_row "$rowp" 0 123) || fail "PET2 row returned non-zero"
has "$out" "$MINE/nd-unfolding/pet/final_design/pet2/run_pet2_replicate.py" pet2; n=$((n+1))
has "$out" "--theirs-cache" pet2; n=$((n+1))
has "$out" "$OUT/theirs-cache/T_1-R1_x1.05-mz-az.npz" pet2; n=$((n+1))
has "$out" "--pool" pet2; has "$out" "T" pet2; has "$out" "--replicate" pet2; n=$((n+1))
has "$out" "$MINE/nd-unfolding/mnv_guarded_run.py" pet2; has "$out" "PFD-dev2P-P2preS1-T1-R1" pet2; n=$((n+1))
has "$out" "--nonfinite-addinfo" pet2; n=$((n+1))
rowb="dev2P-P2scrS1-B${T}../../../final_design/configs/dev2P/z.json${T}ghi${T}BANK:DEV:S2:4${T}null${T}-${T}--step2-miss-mode efficiency_corrected${T}final_design/pet2/run_pet2_replicate.py"
out=$(PET2_THEIRS_CACHE_DIR=/tmp/pc run_row "$rowb" 0 123) || fail "PET2 bank row returned non-zero"
has "$out" "--bank-draw" bank; has "$out" "S2:4" bank; has "$out" "/tmp/pc/BANK_DEV_S2_4.npz" bank; n=$((n+1))
if run_row "${row7}${T}evil/other.py" 0 123 >/dev/null 2>&1; then fail "unknown runner accepted"; fi
grep -q "unknown runner 'evil/other.py'" "$OUT/exit-codes.txt" || fail "unknown runner not logged"; n=$((n+1))
echo "PASS $n"
