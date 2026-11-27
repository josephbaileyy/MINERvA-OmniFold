#!/bin/bash
# test_fence_omnifiles.sh: p0e1's overlap fence lists the 12 RDX omnifiles that p0 stages (C-JOIN part 2), so one placed
# under a cov2d protected path STOPs. Real config and a clone at S; then one mutant (the omnifile loop removed), which
# must not pass the same cases.
# usage: bash test_fence_omnifiles.sh CLONE_AT_S        (local only; MAT_PYTHON is this python3 -I -B)
HERE=$(cd "$(dirname "$0")" && pwd)
PKG="$HERE/.."
CLONE=${1:?a checkout of this repository detached at 2415e8d6}
[ "$(git -C "$CLONE" rev-parse HEAD)" = 2415e8d66d1a9160e724d426eaeb54d458d4b4f7 ] || { echo "SETUP: clone is not at S"; exit 9; }
T=$(mktemp -d "${TMPDIR:-/tmp}/p0e1-fence.XXXXXX") || exit 9
trap 'rm -rf -- "$T"' EXIT
fails=0
check() {  # check NAME WANT_RC WANT_TEXT FENCE CONFIG
  local out rc
  out=$(python3 -I -B "$4" "$5" "$CLONE" 2>&1); rc=$?
  if [ "$rc" = "$2" ] && printf '%s\n' "$out" | grep -qF -- "$3"; then echo "ok   $1"; return 0; fi
  echo "FAIL $1 (rc $rc, wanted $2 and '$3')"; printf '%s\n' "$out" | sed 's/^/     /'; return 1
}
cases() {  # cases FENCE -> number of failed cases
  local bad=0
  check "real config: 70 originals (flux4's 58 + 12 omnifiles), CLEAR" 0 "FENCE staged originals 70" "$1" "$PKG/production-config.ready.json" || bad=$((bad + 1))
  check "the omnifiles' directory protected: STOP (omnifile 1M under it)" 3 "(c) omnifile 1M" "$1" "$T/omni-protected.json" || bad=$((bad + 1))
  check "omnifile 1A equal to a protected path: STOP" 3 "(c) omnifile 1A" "$1" "$T/omni-equal.json" || bad=$((bad + 1))
  return $bad
}
python3 -I -B - "$PKG/production-config.ready.json" "$T" <<'EOF'
import json, sys
config = json.load(open(sys.argv[1]))
out = sys.argv[2]
a = json.loads(json.dumps(config))
a["cov2d_protected_paths"].append("/pscratch/sd/j/josephrb/rdx-20261112b/out/evloop")
json.dump(a, open(f"{out}/omni-protected.json", "w"))
b = json.loads(json.dumps(config))
b["cov2d_protected_paths"].append(b["true_energy"]["omnifiles"]["1A"]["path"])
json.dump(b, open(f"{out}/omni-equal.json", "w"))
EOF
cases "$PKG/tools/fence_overlap.py" || fails=$((fails + $?))
# The mutant: the fence without the omnifile loop (the two lines gen_p0e1.py adds).
sed '/for playlist, spec in sorted(config\["true_energy"\]\["omnifiles"\]/,+1d' "$PKG/tools/fence_overlap.py" > "$T/mutant.py"
[ "$(wc -l < "$PKG/tools/fence_overlap.py")" -eq $(( $(wc -l < "$T/mutant.py") + 2 )) ] || { echo "SETUP: the mutant did not drop two lines"; exit 9; }
if cases "$T/mutant.py" > "$T/mutant.out" 2>&1; then
  echo "SURVIVED omnifile-loop-dropped"; fails=$((fails + 1))
else
  echo "KILLED   omnifile-loop-dropped ($(grep -c '^FAIL' "$T/mutant.out") cases)"
fi
echo "FENCE-OMNIFILES :: $( [ "$fails" -eq 0 ] && echo PASS || echo "FAIL ($fails)")"
[ "$fails" -eq 0 ]
