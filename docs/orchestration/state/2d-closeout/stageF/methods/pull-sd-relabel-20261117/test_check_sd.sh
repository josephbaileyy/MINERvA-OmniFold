#!/bin/bash
# Tests of check_sd.py, on the laptop (no cluster access, no ROOT). The three arms are drawn here by toy_pull.py, which
# runs the deploy's own plotting block (compare_to_paper_fullcov.py, "# Summary plot." to the save) on run-a2's captured
# pull map and values, through boxes.py and the restyle's capture.py, as the connect runs the real producer:
#   before  the installed figure's producer, git archive db5276148 (technote_style.py, 2d-unfolding), --style
#   off     the package's producer (this worktree), --style          after  the same, --style --sd-label
# The "installed" figure is the toy's "before" PDF (the real run uses fd84d992). The clean run must PASS every check;
# each mutant must FAIL the check named (its FAIL line asserted), with rc 1.
#   bash test_check_sd.sh <repo worktree> <python with numpy, matplotlib, PIL>
set -u
REPO=$(cd "$1" && pwd); PY=$2
H=$(cd "$(dirname "$0")" && pwd); T0=$(mktemp -d "${TMPDIR:-/tmp}/tsd.XXXXXX"); fail=0
ok() { echo "PASS $1"; }; bad() { echo "FAIL $1"; fail=1; }
export MPLCONFIGDIR=$T0/mpl PYTHONDONTWRITEBYTECODE=1; unset TECHNOTE_DARK
"$PY" -I -c "import matplotlib.font_manager" > /dev/null 2>&1   # one font cache for every arm, built before the first
mkdir -p "$T0/base" && git -C "$REPO" archive db5276148d0097665800d3992f918d2f4e5e98b0 technote_style.py 2d-unfolding \
  | tar -x -C "$T0/base" || { bad "base deploy"; exit 1; }
[ "$(shasum -a 256 "$T0/base/2d-unfolding/compare_to_paper_fullcov.py" | cut -d' ' -f1)" = \
  1dd5ff52d0c140921a3bcc411bd4108337dbe756c43bffc2c707eb2a8f633314 ] || { bad "base producer is not 1dd5ff52"; exit 1; }
printf 'stand-in for E_R\n' > "$T0/x.root"; printf 'another E_R\n' > "$T0/y.root"
arm() {  # arm <dir> <deploy> <input> [producer args...]; TOY_MUT from the environment
  local d=$T0/$1 dep=$2 x=$3; shift 3
  mkdir -p "$d/out" "$d/logs"
  (cd "$d" && "$PY" -I -B "$H/boxes.py" "$d/capture/pull_full" "$dep" "$H/toy_pull.py" --ours "$x" \
     --out-prefix "$d/out/MEFHC_5iter" --style restyle-2026-10 "$@" > "$d/logs/pull_full.log" 2>&1) \
     || { bad "arm $1 rc $?"; cat "$d/logs/pull_full.log"; }
}
arm before "$T0/base" "$T0/x.root"; arm off "$REPO" "$T0/x.root"; arm after "$REPO" "$T0/x.root" --sd-label
INST=$T0/before/out/MEFHC_5iter_pull_full.pdf; ISHA=$(shasum -a 256 "$INST" | cut -d' ' -f1)
check() {  # check <name> <after dir> [<off dir>] [extra check_sd args]; output in $T0/<name>.out, rc in $T0/<name>.rc
  local name=$1 af=$2 of=${3:-$T0/off}; shift 3 2>/dev/null || shift $#
  "$PY" -I "$H/check_sd.py" --before "$T0/before" --off "$of" --after "$af" --installed "$INST" --installed-sha "$ISHA" \
    --deploy "$REPO" --strip "$T0/before=RUN" --strip "$af=RUN" --strip "$of=RUN" "$@" > "$T0/$name.out" 2>&1
  echo $? > "$T0/$name.rc"
}
check clean "$T0/after" "$T0/off"
n=$(grep -c '^PASS K' "$T0/clean.out")
[ "$(cat "$T0/clean.rc")" = 0 ] && [ "$n" = 16 ] && ! grep -q '^FAIL' "$T0/clean.out" && grep -q '^CHECK_SD :: PASS$' "$T0/clean.out" \
  && ok "clean: $n checks PASS, rc 0 ($(grep '^PASS K6 pixels: changed' "$T0/clean.out" | cut -c1-90))" \
  || { bad "clean (rc $(cat "$T0/clean.rc"), $n PASS)"; cat "$T0/clean.out"; }
mutant() {  # mutant <name> <regex of the FAIL line that must appear> <check args...>
  local name=$1 re=$2; shift 2
  check "$name" "$@"
  grep -qE "^FAIL $re" "$T0/$name.out" && [ "$(cat "$T0/$name.rc")" = 1 ] \
    && ok "mutant $name: $(grep -E "^FAIL $re" "$T0/$name.out" | head -1 | cut -c1-110)" \
    || { bad "mutant $name (rc $(cat "$T0/$name.rc"))"; grep -E '^(PASS|FAIL)' "$T0/$name.out"; }
}
TOY_MUT=ulp arm m-ulp "$REPO" "$T0/x.root" --sd-label
mutant ulp "K3 data, log and inputs: before vs after" "$T0/m-ulp"
TOY_MUT=log arm m-log "$REPO" "$T0/x.root" --sd-label
mutant log "K3 data, log and inputs: before vs after" "$T0/m-log"
arm m-input "$REPO" "$T0/y.root" --sd-label
mutant input "K3 data, log and inputs: before vs after" "$T0/m-input"
TOY_MUT=xlabel arm m-xlabel "$REPO" "$T0/x.root" --sd-label
mutant xlabel "K4 text: after changes the label alone" "$T0/m-xlabel"
arm m-noflag "$REPO" "$T0/x.root"
mutant noflag "K4 text: after changes the label alone" "$T0/m-noflag"
TOY_MUT=move arm m-move "$REPO" "$T0/x.root" --sd-label
mutant move "K5 layout: after moves nothing" "$T0/m-move"
mutant move-pixels "K6 pixels: changed only inside" "$T0/m-move"
arm m-offflag "$REPO" "$T0/x.root" --sd-label
mutant offflag "K2 identity off" "$T0/after" "$T0/m-offflag"
check wrong-installed "$T0/after" "$T0/off" --installed-sha 0000000000000000000000000000000000000000000000000000000000000000
grep -q '^FAIL K1 installed figure' "$T0/wrong-installed.out" && [ "$(cat "$T0/wrong-installed.rc")" = 1 ] \
  && ok "mutant wrong-installed: $(grep '^FAIL K1' "$T0/wrong-installed.out" | cut -c1-90)" || bad "mutant wrong-installed"
# the full words, as item 16 first put them: the label box reaches the zero bin's bar (why the package says "SD")
mkdir -p "$T0/long/2d-unfolding" && cp "$REPO/technote_style.py" "$T0/long/" \
  && cp "$REPO/2d-unfolding/compare_to_paper_fullcov.py" "$REPO/2d-unfolding/restyle_2026_10.py" "$T0/long/2d-unfolding/"
"$PY" -I - "$T0/long/2d-unfolding/compare_to_paper_fullcov.py" <<'PYS'
import sys
p = sys.argv[1]; s = open(p).read(); a = "{'SD = ' if args.sd_label else 'rms ='}"
assert s.count(a) == 1, a
open(p, "w").write(s.replace(a, "{'standard deviation = ' if args.sd_label else 'rms ='}"))
PYS
arm m-long "$T0/long" "$T0/x.root" --sd-label
mutant long-words "K7 overlap gate \(after\)" "$T0/m-long" "$T0/off" --new-label "standard deviation = "
find "$T0" -type f -exec rm -f {} + 2>/dev/null; find "$T0" -type l -exec rm -f {} + 2>/dev/null; find "$T0" -depth -type d -exec rmdir {} \; 2>/dev/null
[ -e "$T0" ] && echo "left: $T0"
[ "$fail" = 0 ] && echo "CHECK_SD TEST PASS" || echo "CHECK_SD TEST FAILED"
exit $fail
