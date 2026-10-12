#!/bin/bash
# Run the frozen XR Linux package's own checks at its delivery commit, never at a later HEAD.
#
#   frozen_xr_linux_check.sh [PYTHON]
#
# The XR Linux package (Q/xr-linux/xr, delivered at 4bde0670 and integrated by PR #91) pins the
# 2D driver it ran, sha256 3cc5adc7... Once selective I/O moves main's driver, its at-HEAD
# `xr_admit.py manifest --check` reports OUT OF DATE and test_xr.py refuses the driver, by design.
# This extends the routing of Q/selective-io/checks/frozen_package_checks.sh (sb1, xr) to that
# package, which landed after selective I/O was written. It never edits a package, a manifest or
# a test.
#
# PYTHON needs PyROOT, LightGBM 4.6.0 and scikit-learn 1.8.0. Exit: 0 all passed; 1 a check
# failed; 2 the package at HEAD differs from its commit, or the commit is absent.
set -u
commit=4bde0670b59166bf91fdf4e64e729d2e2e6864fb
pkg=docs/orchestration/state/next-preparation-20261009/xr-linux/xr
py=${1:-python3}
repo=$(git rev-parse --show-toplevel) || exit 2
if ! git -C "$repo" cat-file -e "$commit^{commit}" 2>/dev/null; then
  echo "[frozen] commit $commit is not in this repository; fetch it first" >&2
  exit 2
fi
if ! git -C "$repo" diff --quiet "$commit" HEAD -- "$pkg"; then
  echo "[frozen] $pkg at HEAD differs from $commit: not a frozen package any more" >&2
  exit 2
fi
wt=$(mktemp -d "${TMPDIR:-/tmp}/frozen-xr-linux-XXXXXX")
rmdir "$wt"
git -C "$repo" worktree add -q --detach "$wt" "$commit" || exit 2
trap 'git -C "$repo" worktree remove --force "$wt"' EXIT
echo "[frozen] $pkg at $(git -C "$wt" rev-parse HEAD), driver sha256" \
     "$(shasum -a 256 "$wt/2d-unfolding/unfold_2d_omnifold_unbinned.py" | cut -c1-64)"
cd "$wt" || exit 2
export OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
rc=0
"$py" "$pkg/xr_admit.py" manifest --check || rc=1
"$py" -m unittest discover -s "$pkg/tests" -t "$pkg/tests" -p test_xr.py || rc=1
echo "[frozen] xr-linux rc=$rc"
exit $rc
