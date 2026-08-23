#!/bin/bash
# mnv_env_preflight.sh -- verify the COMPLETE transitive activation closure BEFORE anything is sourced.
#
# WHY THIS EXISTS. Gate-1 round 4 failed F-2(a) because `setup_salloc_env.sh` sourced files that are
# ABSENT from any tree satisfying A-2 -- .gitignore excludes `unbinned_unfolding/**` and
# `MINERvA101/**`, so a clone or worktree at a named sha NECESSARILY lacks them and every launcher
# died at the activator with exit 1 before any preflight tool, guard or science invocation ran. The
# repair is a third root plus a digest manifest: git structurally cannot bind these bytes, so the
# MECHANISM is substituted rather than the check relocated -- the same move PR-02 made for the
# interpreter.
#
# WHY PURE BASH AND NO PYTHON. This runs BEFORE the activator, and the activator is what provides a
# modern interpreter. Measured on saul: the pre-conda /usr/bin/python3 is 3.6.15 and every tool in
# this package uses `from __future__ import annotations` (3.7+) or `list[str]`. `sha256sum` is in
# coreutils on the cluster and present on macOS too, with `shasum -a 256` as the fallback.
#
# WHAT IT REFUSES, all fail-closed: a missing entry, a digest mismatch, an EXTRA file in a bound
# directory, an env root that resolves inside any checkout, and a manifest it cannot read. A check
# that could not run is never a check that passed.
#
# NO `set -u` ANYWHERE ON THIS PATH, AND THAT IS NOT AN OVERSIGHT: the closure reaches conda's
# activate-binutils_linux-64.sh, which references ADDR2LINE unbound. Under `set -u` that is fatal to
# the caller's shell -- it killed job 57235710 in 10 seconds.
#
# EXIT: 0 verified, 2 could not look, 3 measured violation.

mnv_env__sha256() {
  # returns empty (not nonzero) on a missing file; the caller reports it
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" 2>/dev/null | cut -d' ' -f1
  elif command -v shasum   >/dev/null 2>&1; then shasum -a 256 "$1" 2>/dev/null | cut -d' ' -f1
  else return 2; fi
}

# `cd -P` so the recorded root is the CANONICAL target. A directory symlink is allowed; what must
# satisfy the separation rule is where it POINTS.
# ALWAYS returns 0 -- see the note in mnv_env_pathcheck.sh: under `set -e` a failing command
# substitution in an assignment kills the caller before the emptiness guard can run.
mnv_env__realdir() { (cd -P "$1" 2>/dev/null && pwd -P) || true ; }

mnv_env__is_checkout() {
  # The guard's own definition of a checkout: VALIDATION_LEDGER.md AND nd-unfolding/ both present.
  [[ -f "$1/VALIDATION_LEDGER.md" && -d "$1/nd-unfolding" ]]
}

mnv_env_preflight() {
  local manifest="$1" env_root="$2" code_root="$3" data_root="$4"
  local rc=0 line role base rel want got abs n_checked=0 n_extra=0

  if [[ -z "$manifest" || -z "$env_root" || -z "$code_root" ]]; then
    echo "[env-preflight] COULD NOT LOOK: usage: mnv_env_preflight <manifest> <env_root> <code_root> [data_root]" >&2
    return 2
  fi
  if [[ ! -r "$manifest" ]]; then
    echo "[env-preflight] COULD NOT LOOK: unreadable manifest: $manifest" >&2
    return 2
  fi
  local env_real; env_real="$(mnv_env__realdir "$env_root")"
  if [[ -z "$env_real" ]]; then
    echo "[env-preflight] COULD NOT LOOK: MNV_ENV_ROOT does not resolve: $env_root" >&2
    return 2
  fi

  # ---- SEPARATION, on the CANONICAL target ------------------------------------------------------
  # A directory symlink is permitted; a target inside a checkout is not. Checked before any digest,
  # because a perfectly-matching manifest inside the canonical checkout is the failure this repair
  # exists to prevent.
  local d
  for d in "$code_root" "$data_root"; do
    [[ -z "$d" ]] && continue
    local dr; dr="$(mnv_env__realdir "$d")"
    [[ -z "$dr" ]] && continue
    if [[ "$env_real" == "$dr" || "$env_real" == "$dr"/* ]]; then
      echo "[env-preflight] VIOLATION: MNV_ENV_ROOT resolves INSIDE another declared root." >&2
      echo "[env-preflight]   env  -> $env_real" >&2
      echo "[env-preflight]   root -> $dr" >&2
      rc=3
    fi
  done
  # ... and inside no repository checkout at all, walking upward.
  local probe="$env_real"
  while [[ -n "$probe" && "$probe" != "/" ]]; do
    if mnv_env__is_checkout "$probe"; then
      echo "[env-preflight] VIOLATION: MNV_ENV_ROOT resolves inside a repository checkout: $probe" >&2
      echo "[env-preflight]   A shared env tree must be a real copy OUTSIDE every checkout; a view" >&2
      echo "[env-preflight]   onto the canonical tree resolves back into it." >&2
      rc=3
    fi
    probe="$(dirname "$probe")"
  done

  # ---- DIGESTS over the declared closure ---------------------------------------------------------
  # The manifest is line-oriented on purpose: no JSON parser exists in bash, and a parser written
  # here would be a second thing to trust. Format: `role<TAB>base<TAB>relpath<TAB>sha256`.
  while IFS=$'\t' read -r role base rel want; do
    [[ -z "$role" || "${role:0:1}" == "#" ]] && continue
    case "$base" in
      env_root)     abs="${env_real}/${rel}" ;;
      conda_prefix) abs="${MNV_CONDA_PREFIX:?set MNV_CONDA_PREFIX to the conda env whose activate.d scripts the manifest binds}/${rel}" ;;
      *) echo "[env-preflight] COULD NOT LOOK: unknown base '$base' for $rel" >&2; return 2 ;;
    esac
    if [[ ! -f "$abs" ]]; then
      echo "[env-preflight] VIOLATION: MISSING closure member ($role): $abs" >&2
      rc=3; continue
    fi
    got="$(mnv_env__sha256 "$abs")"
    if [[ -z "$got" ]]; then
      echo "[env-preflight] COULD NOT LOOK: no sha256 tool for $abs" >&2; return 2
    fi
    if [[ "$got" != "$want" ]]; then
      echo "[env-preflight] VIOLATION: DIGEST MISMATCH ($role) $rel" >&2
      echo "[env-preflight]   want $want" >&2
      echo "[env-preflight]   got  $got" >&2
      rc=3
    fi
    n_checked=$((n_checked+1))
  done < "$manifest"

  if [[ "$n_checked" -eq 0 ]]; then
    echo "[env-preflight] COULD NOT LOOK: the manifest bound ZERO entries. An empty manifest and a" >&2
    echo "[env-preflight]   clean closure are the two states this exists to separate." >&2
    return 2
  fi

  # ---- EXTRA files, but ONLY where every member EXECUTES ------------------------------------------
  # SCOPED DELIBERATELY, and the first draft of this check was wrong in a way worth recording: it
  # flagged any unbound `.sh` sitting in a directory that merely CONTAINS a closure member, and so
  # refused a correct environment over `MINERvA101/opt/bin/runTransWarp.sh` and three siblings --
  # real scripts that nothing in the closure sources. A shared `bin/` is not a closure.
  #
  # `etc/conda/activate.d` IS different in kind: conda activation GLOBS that directory and runs
  # every `.sh` in it, so a file appearing there executes without anything referencing it by name.
  # That is the only place where "extra" is itself the defect, so it is the only place checked here.
  # Growth of the SOURCED closure is caught by a different instrument -- mnv_env_manifest.py walks
  # the actual `source` lines and reports any member the declared list does not name.
  local ad="${MNV_CONDA_PREFIX}/etc/conda/activate.d"
  local f bn
  if [[ -d "$ad" ]]; then
    for f in "$ad"/*.sh; do
      [[ -e "$f" ]] || continue
      bn="etc/conda/activate.d/$(basename "$f")"
      if ! awk -F'\t' -v want="$bn" '$1!~/^#/ && $2=="conda_prefix" && $3==want {found=1} END{exit !found}' "$manifest"; then
        echo "[env-preflight] VIOLATION: EXTRA unbound activate.d script -- conda GLOBS this" >&2
        echo "[env-preflight]   directory and will EXECUTE it: $bn" >&2
        rc=3; n_extra=$((n_extra+1))
      fi
    done
  fi

  if [[ "$rc" -eq 0 ]]; then
    echo "[env-preflight] OK: ${n_checked} closure member(s) verified against ${manifest##*/}; env root ${env_real}"
  else
    echo "[env-preflight] REFUSING to source an unverified activation closure." >&2
  fi
  return "$rc"
}

# Runnable as a script as well as sourceable, so a grader can exercise it without a launcher.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  mnv_env_preflight "$@"; exit $?
fi
