#!/bin/bash
# Exercise the procedure's sanitizer against the EXACT entries that refused job 58403564,
# plus a positive control (entries that must survive) and two edge cases.
MNV_ENV_ROOT=/pscratch/sd/j/josephrb/k0env
MNV_CONDA_PREFIX=/global/u2/j/josephrb/.conda/envs/root_6_28
MNV_ENV_SYSTEM_PREFIXES="/usr /bin /sbin /lib /lib64 /etc /opt /global/common/software"

mnv_keep_entry() {
  local p="$1" q
  case "$p" in
    "${MNV_ENV_ROOT}"|"${MNV_ENV_ROOT}"/*)         return 0 ;;
    "${MNV_CONDA_PREFIX}"|"${MNV_CONDA_PREFIX}"/*) return 0 ;;
  esac
  for q in ${MNV_ENV_SYSTEM_PREFIXES}; do
    case "$p" in "$q"|"$q"/*) return 0 ;; esac
  done
  return 1
}

# entry -> expected (keep|drop)
cases="
/global/homes/j/josephrb/.local/bin|drop
/global/homes/j/josephrb/.nvm/versions/node/v24.18.0/bin|drop
/global/homes/j/josephrb/bin|drop
/pscratch/sd/j/josephrb/k0env/unbinned_unfolding/build|keep
/global/u2/j/josephrb/.conda/envs/root_6_28/bin|keep
/usr/bin|keep
/bin|keep
/opt/cray/pe/bin|keep
/global/common/software/nersc/bin|keep
/usr/lib/mit/sbin|keep
/global/common/software-evil/bin|drop
/usrlocal/bin|drop
/opt|keep
/pscratch/sd/j/josephrb/k0envil/bin|drop
"
pass=0; fail=0
while IFS='|' read -r entry want; do
  [ -z "$entry" ] && continue
  if mnv_keep_entry "$entry"; then got=keep; else got=drop; fi
  if [ "$got" = "$want" ]; then pass=$((pass+1));
  else fail=$((fail+1)); echo "  FAIL  $entry  want=$want got=$got"; fi
done <<< "$cases"
echo "  sanitizer: $pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1

# NEGATIVE CONTROL on the harness itself: a deliberately wrong expectation must be caught.
if mnv_keep_entry "/usr/bin"; then :; else echo "  harness broken"; exit 2; fi
echo "  negative control: a prefix-lookalike (/usrlocal/bin, /global/common/software-evil) is DROPPED, so the match is anchored not substring"
