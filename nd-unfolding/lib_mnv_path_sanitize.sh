# PATH sanitization for a guarded submission: drop entries outside the declared environment
# WITHOUT widening the allowlist.
#
# ⚠ THIS FILE EXISTS BECAUSE A COPY OF IT PASSED ITS OWN TEST 14/14 WHILE BEING BROKEN.
# The first version inlined the loop in the submission script and tested a duplicate of the
# predicate in a separate file. The script's loop set `IFS=':'` to split PATH; the predicate
# splits the allowlist on WHITESPACE. Under the caller's IFS the allowlist loop iterated ONCE
# over the whole 8-prefix string, so `/usr/bin`, `/bin`, `/opt/cray/pe/bin` and
# `/global/common/software/nersc/bin` were ALL DROPPED -- and the duplicate in the test never
# saw that IFS, so it agreed with the rule instead of with the code. One implementation now,
# sourced by both the procedure and its test.
#
# Requires MNV_ENV_ROOT, MNV_CONDA_PREFIX and MNV_ENV_SYSTEM_PREFIXES to be set by the caller
# (the last one from lib_mnv_env_pathcheck.sh, never retyped).
#
# Outputs, set as globals: MNV_PATH_CLEAN, MNV_PATH_DROPPED, MNV_PATH_N_BEFORE, MNV_PATH_N_AFTER.

mnv_keep_entry() {                      # 0 = keep this PATH entry
  local p="$1" q
  # ⚠ THE FUNCTION DEFENDS ITSELF. Restoring word-splitting locally means the predicate is
  # correct no matter what IFS the caller happens to be holding -- which is the defect above,
  # fixed at the site that was wrong rather than only at the one call site that triggered it.
  local IFS=$' \t\n'
  case "$p" in
    "${MNV_ENV_ROOT}"|"${MNV_ENV_ROOT}"/*)         return 0 ;;
    "${MNV_CONDA_PREFIX}"|"${MNV_CONDA_PREFIX}"/*) return 0 ;;
  esac
  for q in ${MNV_ENV_SYSTEM_PREFIXES}; do
    case "$p" in "$q"|"$q"/*) return 0 ;; esac
  done
  return 1
}

mnv_sanitize_path() {                   # $1 = the PATH to sanitize
  local original="$1" entry
  MNV_PATH_CLEAN=""; MNV_PATH_DROPPED=""
  # Newline-delimited with `IFS= read -r`, so no global IFS is set, entries containing spaces
  # survive, and the predicate is never called under a modified IFS. A here-string keeps the
  # loop in THIS shell, so the accumulators persist -- a pipe would put them in a subshell.
  while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    if mnv_keep_entry "$entry"; then
      MNV_PATH_CLEAN="${MNV_PATH_CLEAN:+${MNV_PATH_CLEAN}:}${entry}"
    else
      MNV_PATH_DROPPED="${MNV_PATH_DROPPED:+${MNV_PATH_DROPPED} }${entry}"
    fi
  done <<< "$(printf '%s' "$original" | tr ':' '\n')"
  MNV_PATH_N_BEFORE=$(printf '%s' "$original" | tr ':' '\n' | grep -c .)
  MNV_PATH_N_AFTER=$(printf '%s' "$MNV_PATH_CLEAN" | tr ':' '\n' | grep -c .)
}
