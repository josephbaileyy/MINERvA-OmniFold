#!/bin/bash
# Run a frozen package's own checks at the commit it is frozen at, never at a later HEAD.
#
#   frozen_package_checks.sh {sb1|xr} [PYTHON]
#
# The SB1 preparation package (Q/sb1-prep, frozen at d4335d3b) and the XR package
# (Q/two-d-followup/xr, frozen at 07428e5d) pin the 2D driver they were admitted with, sha256
# 3cc5adc7... Any later driver change (here --branch-select, Q/selective-io/REPORT.md) makes
# their at-HEAD checks refuse it by design: SB1's tests load the driver against that digest,
# and the XR manifest reports OUT OF DATE. This script is the check-routing change proposed to
# integration (REPORT §7): it checks each package in a throwaway detached worktree at its own
# commit, after confirming that the package bytes at HEAD still equal those at the commit.
# It never edits a package, a manifest or a test.
#
# PYTHON must have PyROOT on PYTHONPATH; the XR suite also needs LightGBM 4.6.0 and
# scikit-learn 1.8.0. Default: python3. Exit status: 0 every check passed; 1 a check failed;
# 2 usage or the package at HEAD differs from its frozen commit.
set -u
case "${1:-}" in
  sb1) commit=d4335d3b9bc2502002f93390f9555d07e134855f
       pkg=docs/orchestration/state/next-preparation-20261009/sb1-prep ;;
  xr)  commit=07428e5d
       pkg=docs/orchestration/state/next-preparation-20261009/two-d-followup/xr ;;
  *)   echo "usage: $0 {sb1|xr} [PYTHON]" >&2; exit 2 ;;
esac
py=${2:-python3}
repo=$(git rev-parse --show-toplevel) || exit 2
if ! git -C "$repo" cat-file -e "$commit^{commit}" 2>/dev/null; then
  echo "[frozen] commit $commit is not in this repository; fetch it first" >&2
  exit 2
fi
if ! git -C "$repo" diff --quiet "$commit" HEAD -- "$pkg"; then
  echo "[frozen] $pkg at HEAD differs from $commit: not a frozen package any more" >&2
  exit 2
fi
wt=$(mktemp -d "${TMPDIR:-/tmp}/frozen-$1-XXXXXX")
rmdir "$wt"
git -C "$repo" worktree add -q --detach "$wt" "$commit" || exit 2
trap 'git -C "$repo" worktree remove --force "$wt"' EXIT
echo "[frozen] $pkg at $(git -C "$wt" rev-parse HEAD), driver sha256" \
     "$(shasum -a 256 "$wt/2d-unfolding/unfold_2d_omnifold_unbinned.py" | cut -c1-64)"
cd "$wt" || exit 2
export OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
rc=0
if [ "$1" = sb1 ]; then
  for t in test_package_consistency test_branch_select test_sb1_guarded test_launch_chain; do
    "$py" -m unittest discover -s "$pkg/tests" -t "$pkg/tests" -p "$t.py" || rc=1
  done
else
  "$py" "$pkg/xr_admit.py" manifest --check || rc=1
  "$py" -m unittest discover -s "$pkg/tests" -t "$pkg/tests" -p test_xr.py || rc=1
fi
echo "[frozen] $1 rc=$rc"
exit $rc
