#!/bin/bash
# setup_salloc_env.sh for a generation-two DATA root.
#
# ============================================================================================
# ROUTED 2026-08-23. THIS TEMPLATE'S DIAGNOSIS IS NOW THE k=0 CONTRACT, AND THERE IS ONLY ONE.
#
# Everything below was written for the Gate-5 path and was referenced by NOTHING on the k=0 path.
# The round-4 Gate-1 verdict then re-derived it from scratch, at the cost of a failed gate: the
# three SCRIPT_DIR references ("the failure list is three long, not one"), absence-by-construction
# ("NO git worktree or frozen deployment will ever contain them"), the FILE-vs-DIRECTORY symlink
# distinction, the `set -u` job kill (57235710), and the fix itself -- "a separate GATE5_ENV_ROOT".
#
# THE k=0 IMPLEMENTATION OF THAT FIX IS `MNV_ENV_ROOT`, and it is the SAME CONTRACT under a
# path-agnostic name, so that two environment-root conventions cannot drift apart:
#
#   mandatory, no default             ->  ENV_ROOT="${MNV_ENV_ROOT:?...}" in all eight launchers
#   resolved outside every checkout   ->  nd-unfolding/mnv_env_preflight.sh, on the CANONICAL target
#   the closure bound, not the shim   ->  nd-unfolding/mnv_env_manifest.tsv, 14 members, two hops
#   no checkout on the search paths   ->  nd-unfolding/mnv_env_pathcheck.sh, all three channels
#   no `set -u`                       ->  unchanged, and for the reason recorded below
#
# GATE-5 USERS: this shim remains correct for a generation-two data root and is NOT superseded as a
# mechanism. What is superseded is the idea that the environment root is a Gate-5-only concern. If
# this template is ever extended, extend `MNV_ENV_ROOT` instead and point here -- do not fork a
# second contract. The reverse is also true: a change to the k=0 contract that invalidates the
# reasoning below should update this header rather than leave the two disagreeing.
# ============================================================================================
#
# WHY THIS IS A SHIM AND NOT A SYMLINK, and it is the diagnosis rather than a workaround.
#
# The real activator computes `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` and then
# resolves THREE paths against it:
#     :18  source "${SCRIPT_DIR}/unbinned_unfolding/build/setup.sh"
#     :20  export MINERVA_PREFIX="${SCRIPT_DIR}/MINERvA101/opt"
#     :21  source "${SCRIPT_DIR}/MINERvA101/opt/bin/setup.sh"
# `BASH_SOURCE[0]` is the path AS SOURCED, so symlinking that file into a bare data root makes SCRIPT_DIR
# the DATA root -- and all three resolve into a directory that has none of them. Patching only the path
# that appeared in the .err would have failed again at :21; the failure list is three long, not one.
#
# AND BOTH TREES ARE UNTRACKED: `git ls-files unbinned_unfolding/build/setup.sh MINERvA101/opt/bin/setup.sh`
# returns 0, so NO git worktree or frozen deployment will ever contain them. Sourcing the activator from the
# deployment instead of the data root is therefore not an option either -- it is unavailable by construction.
#
# THE REAL DEFECT IS A CONFLATION: `GATE5_DATA_ROOT` names both WHERE THE DATA IS and WHERE THE SOFTWARE
# ENVIRONMENT IS. Generation one never exposed it because those were the same directory. Every SCRIPT_DIR
# use in the activator is SOFTWARE (`unbinned_unfolding/build`, `MINERvA101/opt`) and none is data -- so the
# right long-term fix is a separate `GATE5_ENV_ROOT` in both launchers, and this shim is the small correct
# version of it: sourcing the real file makes `BASH_SOURCE[0]` the real path, so SCRIPT_DIR becomes the
# environment tree and all three references resolve where they actually live.
# *** NO `set -u` HERE, AND THAT IS NOT AN OVERSIGHT. ***
#
# The first version of this shim had it, for hygiene, and it killed 57235710 in 10 seconds -- 50/50, exactly
# like the failure it was written to fix. The activator this sources reaches conda's
# `activate-binutils_linux-64.sh`, which references `ADDR2LINE` unbound; under `set -u` that is FATAL to the
# whole shell, and `source` runs in the caller's shell, so the task dies before its first line of work.
#
# MEASURED, not reasoned: `bash -c 'set -eo pipefail; source <shim>'` produces nothing and dies, while
# `bash -c 'set -eo pipefail; source <real activator>'` prints OK. The shim was the only difference.
#
# AND I HAD ALREADY LEARNED THIS TWICE TODAY, in the pre-submit checker, where adding `-u` made the CHECK
# stricter than the JOB and produced two false failures. I then wrote it into production code. The launcher
# uses `set -eo pipefail` and NOT `-u` (line 15); anything sourced into that shell must tolerate the same.
# `${VAR:-default}` below needs no `-u` to be safe.
GATE5_ENV_ROOT="${GATE5_ENV_ROOT:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}"
if [ ! -r "${GATE5_ENV_ROOT}/setup_salloc_env.sh" ]; then
  echo "[g2-env] no activator at ${GATE5_ENV_ROOT}/setup_salloc_env.sh -- refusing to continue with a" >&2
  echo "[g2-env] half-built environment, which is how a task dies 40 lines later for the wrong reason" >&2
  return 1 2>/dev/null || exit 1
fi
# shellcheck disable=SC1090
source "${GATE5_ENV_ROOT}/setup_salloc_env.sh"
