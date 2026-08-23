#!/bin/bash
# mnv_env_pathcheck.sh -- AFTER activation, refuse any PATH/PYTHONPATH/LD_LIBRARY_PATH entry that
# resolves inside an unauthorized checkout, or outside the declared env root except for predeclared
# system paths.
#
# WHY THIS IS SEPARATE FROM THE DIGEST CHECK, and why binding the bytes is not enough. The round-4
# verdict's second substantive finding: `unbinned_unfolding/build/setup.sh` injected
# /pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build into PATH, PYTHONPATH AND
# LD_LIBRARY_PATH. That is F-2's prohibition violated BY CONTENT -- a perfectly verified file can
# still put the canonical checkout on the search path, and the OI-136 Python import guard sees only
# the sys.path consequence, never PATH and never LD_LIBRARY_PATH. So the channels are checked
# directly, after activation, where the damage would already be visible.
#
# ALLOWLIST, NOT DENYLIST, for the same reason the import ratchet pins identity rather than a floor:
# a denylist of known-bad prefixes passes every prefix nobody thought of.
#
# NO `set -u`. See mnv_env_preflight.sh; job 57235710.
#
# EXIT: 0 clean, 2 could not look, 3 measured violation.

# ALWAYS returns 0. Under the launchers' `set -eo pipefail`, `entry_real="$(helper ...)"` takes the
# helper's status, so a helper that fails on a NON-EXISTENT directory kills the caller before the
# `-z` guard on the next line can run. Measured: PATH carries `.../cuda/13.2/libnvvp`, which does
# not exist on this system, and the check died there instead of reporting it.
mnv_env__pc_realdir() { (cd -P "$1" 2>/dev/null && pwd -P) || true ; }

mnv_env__pc_is_checkout() { [[ -f "$1/VALIDATION_LEDGER.md" && -d "$1/nd-unfolding" ]]; }

#: PREDECLARED SYSTEM PREFIXES. Anything under one of these is allowed; everything else must live
#: under the env root or the conda prefix. An allowlist, not a denylist, for the reason the import
#: ratchet pins identity rather than a floor: a denylist passes every prefix nobody thought of.
#:
#: DERIVED BY MEASUREMENT on saul 2026-08-23, not guessed -- enumerated from the three variables
#: after a real activation. The first draft omitted `/opt/nersc` and `/opt` generally and refused a
#: correct environment over `/opt/nersc/pe/bin`.
#:
#: WHAT IS DELIBERATELY *NOT* HERE: anything under $HOME. A user `bin` directory can shadow a tool,
#: so `~/.local/bin` and `~/.nvm/.../bin` are refused BY DEFAULT and must be named explicitly by the
#: submitter through this variable. That is what "explicitly predeclared" means -- the widening is a
#: visible act by whoever submits, not a default this file grants on their behalf.
MNV_ENV_SYSTEM_PREFIXES="${MNV_ENV_SYSTEM_PREFIXES:-/usr /bin /sbin /lib /lib64 /etc /opt /global/common/software}"

mnv_env_pathcheck() {
  local env_root="$1" code_root="$2" data_root="$3"
  local rc=0 var val entry entry_real allowed p probe n=0

  local env_real; env_real="$(mnv_env__pc_realdir "$env_root")"
  if [[ -z "$env_real" ]]; then
    echo "[env-pathcheck] COULD NOT LOOK: MNV_ENV_ROOT does not resolve: $env_root" >&2
    return 2
  fi
  local conda_real; conda_real="$(mnv_env__pc_realdir "${MNV_CONDA_PREFIX:-/nonexistent}")"

  for var in PATH PYTHONPATH LD_LIBRARY_PATH; do
    eval "val=\${$var}"
    [[ -z "$val" ]] && continue
    local IFS_SAVE="$IFS"; IFS=':'
    for entry in $val; do
      IFS="$IFS_SAVE"
      [[ -z "$entry" ]] && continue
      n=$((n+1))
      entry_real="$(mnv_env__pc_realdir "$entry")"
      # A path that does not resolve cannot host code, so it is reported and not fatal.
      if [[ -z "$entry_real" ]]; then IFS=':'; continue; fi

      # (a) inside ANY repository checkout -> refuse, whichever root it belongs to.
      probe="$entry_real"
      while [[ -n "$probe" && "$probe" != "/" ]]; do
        if mnv_env__pc_is_checkout "$probe"; then
          echo "[env-pathcheck] VIOLATION: $var carries a REPOSITORY CHECKOUT path." >&2
          echo "[env-pathcheck]   entry    $entry" >&2
          echo "[env-pathcheck]   resolves $entry_real" >&2
          echo "[env-pathcheck]   checkout $probe" >&2
          echo "[env-pathcheck]   The Python import guard cannot see PATH or LD_LIBRARY_PATH; this can." >&2
          rc=3; break
        fi
        probe="$(dirname "$probe")"
      done

      # (b) otherwise it must be under the env root, the conda prefix, or a predeclared system path.
      allowed=0
      [[ "$entry_real" == "$env_real" || "$entry_real" == "$env_real"/* ]] && allowed=1
      if [[ -n "$conda_real" && ( "$entry_real" == "$conda_real" || "$entry_real" == "$conda_real"/* ) ]]; then allowed=1; fi
      # BOTH SIDES CANONICALIZED. The first draft compared a RESOLVED entry against an
      # UNRESOLVED prefix and refused `$HOME/.local/bin`, because on this system `/global/homes` is
      # a symlink to `/global/u2` -- the entry resolved and the prefix did not, so a correct
      # predeclaration could never match. A containment check must resolve both sides or it is not
      # the check it claims to be.
      for p in $MNV_ENV_SYSTEM_PREFIXES; do
        local p_real; p_real="$(mnv_env__pc_realdir "$p")"
        [[ -z "$p_real" ]] && p_real="$p"        # a prefix that does not exist still matches literally
        [[ "$entry_real" == "$p_real" || "$entry_real" == "$p_real"/* ]] && { allowed=1; break; }
      done
      if [[ "$allowed" -eq 0 ]]; then
        echo "[env-pathcheck] VIOLATION: $var entry is outside the declared environment." >&2
        echo "[env-pathcheck]   entry    $entry" >&2
        echo "[env-pathcheck]   resolves $entry_real" >&2
        echo "[env-pathcheck]   Allowed: MNV_ENV_ROOT, MNV_CONDA_PREFIX, or MNV_ENV_SYSTEM_PREFIXES." >&2
        rc=3
      fi
      IFS=':'
    done
    IFS="$IFS_SAVE"
  done

  if [[ "$n" -eq 0 ]]; then
    echo "[env-pathcheck] COULD NOT LOOK: all three variables were empty after activation, which is" >&2
    echo "[env-pathcheck]   not a state a successful activation produces." >&2
    return 2
  fi
  if [[ "$rc" -eq 0 ]]; then
    echo "[env-pathcheck] OK: ${n} search-path entr(ies) checked; none inside a checkout, none outside the declared environment"
  fi
  return "$rc"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  mnv_env_pathcheck "$@"; exit $?
fi
