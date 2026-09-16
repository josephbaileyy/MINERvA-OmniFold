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

echo "=== 1. the PROCEDURE uses this library, and holds no competing inline loop ==="
[ -f "$PROC" ] || { echo "  FAIL  procedure not found at $PROC"; exit 1; }
if grep -q 'lib_mnv_path_sanitize.sh' "$PROC"; then ok; else bad "procedure does not reference the sanitizer library"; fi
if grep -q 'mnv_sanitize_path "\$PATH_ORIG"' "$PROC"; then ok; else bad "procedure does not call mnv_sanitize_path on PATH_ORIG"; fi
# A live IFS assignment anywhere in the procedure is the defect class; comments are fine.
if grep -qE '^[^#]*IFS=' "$PROC"; then bad "procedure contains a LIVE IFS assignment"; else ok; fi
if grep -qE '^[^#]*for _p in \$PATH' "$PROC"; then bad "procedure still has an inline PATH loop"; else ok; fi

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
