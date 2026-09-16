#!/bin/bash
# Exercise THE ACTUAL SANITIZER THE SUBMISSION PROCEDURE USES, by sourcing the same library
# the procedure sources -- not a copy of the predicate.
#
# ⚠ WHY THIS FILE IS SHAPED THIS WAY. Its first version copied the predicate into itself and
# tested the copy. It reported 14 passed / 0 failed while the production code was BROKEN: the
# procedure's PATH loop set `IFS=':'`, the predicate splits the allowlist on WHITESPACE, so the
# allowlist loop iterated ONCE over the whole 8-prefix string and `/usr/bin`, `/bin`,
# `/opt/cray/pe/bin` and `/global/common/software/nersc/bin` were ALL DROPPED. The copy never
# saw the caller's IFS, so it agreed with the rule instead of with the code.
#
# Two consequences, both enforced below: the loop lives in the library and is called from here
# exactly as the procedure calls it (section 2-4), and the PROCEDURE is asserted to use that
# library with no competing inline loop (section 1).
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ND="$(cd "${HERE}/.." && pwd)"
PROC="${ND}/submit_z_pilot_a5.sh"
LIB="${ND}/lib_mnv_path_sanitize.sh"
pass=0; fail=0
ok()   { pass=$((pass+1)); }
bad()  { fail=$((fail+1)); echo "  FAIL  $*"; }

echo "=== 1. the PROCEDURE actually sanitizes, and EXPORTS WHAT IT SANITIZED ==="
[ -f "$PROC" ] || { echo "  FAIL  procedure not found at $PROC"; exit 1; }
# ⚠ STRIP COMMENTS FIRST. Review found 14 of 14 procedure mutants surviving this section.
# Two causes: a bare `grep -q` let the sanitize call be COMMENTED OUT and still match, and
# `grep -E '^[^#]*IFS='` has a false negative on GNU grep whenever any `#` precedes the
# assignment on the same line. Both are gone once the greps run over comment-free text.
STRIPPED="$(mktemp)"; trap 'rm -f "$STRIPPED"' EXIT
sed 's/#.*//' "$PROC" > "$STRIPPED"
pgrep_live() { grep -qE "$1" "$STRIPPED"; }

if pgrep_live 'lib_mnv_path_sanitize\.sh'; then ok; else bad "procedure does not source the sanitizer library"; fi
if pgrep_live 'mnv_sanitize_path[[:space:]]+"\$PATH_ORIG"'; then ok; else bad "procedure does not call mnv_sanitize_path on PATH_ORIG"; fi
# THE POINT OF THE WHOLE EXERCISE: the value exported must be the value produced. Mutants
# M1 (export the unsanitized PATH) and M13 (sanitize one variable, export another) both
# survived every assertion this section used to make.
if pgrep_live 'CLEAN="\$MNV_PATH_CLEAN"'; then ok; else bad "procedure does not take CLEAN from MNV_PATH_CLEAN"; fi
if pgrep_live 'export[[:space:]]+PATH="\$CLEAN"'; then ok; else bad "procedure does not export exactly \$CLEAN"; fi
if grep -qE 'export[[:space:]]+PATH="\$PATH_ORIG"|export[[:space:]]+PATH="\$CLEAN:' "$STRIPPED"; then
  bad "procedure exports an unsanitized or augmented PATH"; else ok; fi
# F1: the ambient allowlist must be discarded, not trusted.
if pgrep_live 'unset[[:space:]]+MNV_ENV_SYSTEM_PREFIXES'; then ok; else bad "procedure does not unset an ambient MNV_ENV_SYSTEM_PREFIXES"; fi
if pgrep_live 'ALLOW_EXPECTED'; then ok; else bad "procedure does not compare the allowlist against the library default"; fi
# no live IFS assignment, and no resurrected inline loop of any spelling
# The `IFS`-blank-read form is a COMMAND PREFIX: scoped to that one command, it is the safe idiom and is
# how the library itself splits. What must not appear is an assignment that changes the
# SHELL's IFS for subsequent commands -- which is the defect that dropped every system path.
# This distinction was found by this assertion firing on a legitimate `while IFS= read`.
# Scanned on the RAW file, excluding only lines that BEGIN with `#`. Stripping comments with
# `sed 's/#.*//'` hides `say "step #1"; IFS=":"` -- a live assignment after a quoted hash --
# and `^[^#]*IFS=` never matches it either. A full-line comment is still allowed, so prose
# about this defect must not write the token followed by `=`.
_bad_ifs="$(grep -nE 'IFS=' "$PROC" | grep -vE '^[0-9]+:[[:space:]]*#' \
            | grep -vE 'IFS=[^[:space:]]*[[:space:]]+read' || true)"
if [ -n "${_bad_ifs}" ]; then bad "procedure has a shell-wide IFS assignment: ${_bad_ifs}"; else ok; fi
if grep -qE 'for[[:space:]]+[A-Za-z_]+[[:space:]]+in[[:space:]]+\$\{?PATH' "$STRIPPED"; then
  bad "procedure has an inline PATH loop"; else ok; fi
# F3: non-acceptance must not be asserted blind
if pgrep_live 'sbatch_exit_status'; then ok; else bad "procedure does not record the sbatch exit status"; fi
# F5: both log paths verified
if pgrep_live 'StdErr='; then ok; else bad "procedure does not verify StdErr"; fi

# THE IMPLEMENTATION UNDER TEST. Sourced, never copied.
MNV_ENV_ROOT=/pscratch/sd/j/josephrb/k0env
MNV_CONDA_PREFIX=/global/u2/j/josephrb/.conda/envs/root_6_28
MNV_ENV_SYSTEM_PREFIXES="/usr /bin /sbin /lib /lib64 /etc /opt /global/common/software"
source "$LIB" || { echo "  FAIL  cannot source $LIB"; exit 1; }

expect() {   # expect <want keep|drop> <entry>
  local want="$1" entry="$2" got
  mnv_sanitize_path "$entry"
  if [ -n "$MNV_PATH_CLEAN" ]; then got=keep; else got=drop; fi
  if [ "$got" = "$want" ]; then ok; else bad "$entry  want=$want got=$got"; fi
}

echo "=== 2. POSITIVE CONTROLS: one required system path per allowlist prefix must SURVIVE ==="
for d in /usr/bin /bin/ls-dir /sbin/foo /lib/x /lib64/y /etc/z /opt/cray/pe/bin \
         /global/common/software/nersc/bin /usr /opt; do
  expect keep "$d"
done
expect keep "${MNV_ENV_ROOT}/unbinned_unfolding/build"
expect keep "${MNV_CONDA_PREFIX}/bin"

echo "=== 3. the entries that actually refused job 58403564 must be DROPPED ==="
expect drop /global/homes/j/josephrb/.local/bin
expect drop /global/homes/j/josephrb/.nvm/versions/node/v24.18.0/bin
expect drop /global/homes/j/josephrb/bin

echo "=== 4. PREFIX LOOKALIKES must be dropped (anchored, not substring) ==="
expect drop /usrlocal/bin
expect drop /global/common/software-evil/bin
expect drop "${MNV_ENV_ROOT}il/bin"
expect drop /optimism/bin

echo "=== 5. THE IFS REGRESSION -- the bug this file missed, under every hostile IFS ==="
REAL='/pscratch/sd/j/josephrb/k0env/bin:/usr/bin:/bin:/opt/cray/pe/bin:/global/common/software/nersc/bin:/global/homes/j/josephrb/.local/bin'
for hostile in ':' $'\n' '' ' ' ':x'; do
  ( IFS="$hostile"
    mnv_sanitize_path "$REAL"
    # all five declared entries must survive and the one home entry must not
    miss=""
    for need in /usr/bin /bin /opt/cray/pe/bin /global/common/software/nersc/bin \
                /pscratch/sd/j/josephrb/k0env/bin; do
      case ":${MNV_PATH_CLEAN}:" in *":${need}:"*) ;; *) miss="${miss} ${need}" ;; esac
    done
    case ":${MNV_PATH_CLEAN}:" in
      *":/global/homes/j/josephrb/.local/bin:"*) miss="${miss} LEAKED-HOME-ENTRY" ;;
    esac
    if [ -n "$miss" ]; then echo "  FAIL  IFS=$(printf %q "$hostile") lost/leaked:${miss}"; exit 1; fi
    exit 0
  ) && ok || bad "IFS=$(printf %q "$hostile") regression"
done

echo "=== 7. EXECUTE the procedure's REAL PATH block -- text assertions cannot see a value ==="
# ⚠ SECTIONS 1-6 ARE TEXT CHECKS, AND TWO FAITHFUL MUTANTS SURVIVED THEM ALL.
#   M13: corrupt MNV_PATH_CLEAN between mnv_sanitize_path and CLEAN="$MNV_PATH_CLEAN".
#        Every spelling assertion still matched -- a grep cannot see a VALUE.
#   M4 : `say "step #1"; IFS=":"` -- a LIVE shell-wide IFS after a quoted `#` on the same
#        line. The comment-strip removes from the `#` onward, and `^[^#]*IFS=` never
#        matches, so the assignment is invisible to BOTH forms of text check.
# So the block is extracted from the real file and RUN. That is the only check here that
# constrains behaviour rather than spelling.
BLOCK="$(awk '/^PATH_ORIG="\$PATH"$/,/^export PATH="\$CLEAN"$/' "$PROC")"
case "$BLOCK" in
  *mnv_sanitize_path*export*) ok ;;
  *) bad "could not extract the procedure's PATH block (anchors moved?)" ;;
esac

got="$(
  env -u IFS MNV_ENV_ROOT="$MNV_ENV_ROOT" MNV_CONDA_PREFIX="$MNV_CONDA_PREFIX" \
      MNV_ENV_SYSTEM_PREFIXES="$MNV_ENV_SYSTEM_PREFIXES" \
  bash -c '
    say(){ :; }
    die(){ printf "DIE:%s\n" "$1"; exit 1; }
    source "'"$LIB"'"
    PATH="/usr/bin:/global/homes/j/josephrb/.local/bin:/bin:'"$MNV_ENV_ROOT"'/x:/global/homes/j/josephrb/bin"
    '"$BLOCK"'
    printf "%s" "$PATH"
  ' 2>&1
)"
for need in /usr/bin /bin "${MNV_ENV_ROOT}/x"; do
  case ":${got}:" in *":${need}:"*) ok ;; *) bad "executed block lost required entry ${need} (PATH=${got})" ;; esac
done
for forbid in /global/homes/j/josephrb/.local/bin /global/homes/j/josephrb/bin; do
  case ":${got}:" in *":${forbid}:"*) bad "executed block EXPORTED an undeclared entry ${forbid}" ;; *) ok ;; esac
done

echo "=== 6. NEGATIVE CONTROL ON THIS HARNESS: a wrong expectation must be reported ==="
before=$fail
expect drop /usr/bin          # deliberately wrong
if [ "$fail" -eq "$((before+1))" ]; then
  fail=$before; pass=$((pass+1))
  echo "  harness is live: it reported the deliberate error (that FAIL line is expected)"
else
  fail=$((fail+1)); echo "  FAIL  harness did NOT report a deliberately wrong expectation"
fi

echo
echo "  RESULT: ${pass} passed, ${fail} failed"
[ "$fail" -eq 0 ] || exit 1
