#!/bin/bash
# The D_Ua connect's new block (connect-g2r-D_Ua.sh, from "PR=" to the constraint line: the prepare record's PASS, the
# map's O_NOATIME sha256 against the record's map_npz_sha256, the input stats and the constraint stat), run against
# stand-ins: git show serves a fixture record, and stat/date/python3 are shims for macOS (python3 gets O_NOATIME = 0
# where os lacks it; on Linux the connect uses the real flag). Every other line of the connect is 233f8cd2's, with the
# name, THIS and LOG substitutions the diff shows. No ssh, no cluster path. Exit 0 only if every case behaves.
#     bash test_connect_dua.sh [path/to/connect-g2r-D_Ua.sh]
set -u
H=$(cd "$(dirname "$0")" && pwd)
CONN=${1:-$H/connect-g2r-D_Ua.sh}
REALPY=$(command -v python3)
T=$(mktemp -d "${TMPDIR:-/tmp}/tcdua.XXXXXX")
mkdir -p "$T/bin" "$T/fix"
cat > "$T/bin/git" <<'EOF'
#!/usr/bin/env bash
# git -C <dir> show origin/main:<path>: the fixture record if present, else git's own failure
[ "$1" = -C ] && [ "$3" = show ] || { echo "stub git: unexpected $*" >&2; exit 99; }
f=$FIX/record.json; [ -e "$f" ] && exec cat "$f"; echo "fatal: path does not exist" >&2; exit 128
EOF
cat > "$T/bin/py.py" <<'EOF'
import os, sys
if not hasattr(os, "O_NOATIME"):
    os.O_NOATIME = 0
assert sys.argv[1] == "-c", sys.argv
code = sys.argv[2]; sys.argv = ["-c"] + sys.argv[3:]
exec(compile(code, "<connect -c>", "exec"), {"__name__": "__main__"})
EOF
printf '#!/usr/bin/env bash\nexec "%s" "%s" "$@"\n' "$REALPY" "$T/bin/py.py" > "$T/bin/python3"
cat > "$T/bin/stat" <<EOF
#!/usr/bin/env bash
# stat --printf FMT FILE for FMT '%s %X' or '%X'
[ "\$1" = --printf ] || exit 99
exec "$REALPY" -c 'import os, sys
fmt, f = sys.argv[1], sys.argv[2]
try: s = os.stat(f)
except OSError: sys.exit(1)
sys.stdout.write(fmt.replace("%s", str(s.st_size)).replace("%X", str(int(s.st_atime))))' "\$2" "\$3"
EOF
cat > "$T/bin/date" <<EOF
#!/usr/bin/env bash
# date -u -d @N +%FT%TZ
[ "\$1" = -u ] && [ "\$2" = -d ] || exit 99
exec "$REALPY" -c 'import sys, datetime
n = sys.argv[1].lstrip("@")
if not n.isdigit(): sys.exit(1)
print(datetime.datetime.utcfromtimestamp(int(n)).strftime("%Y-%m-%dT%H:%M:%SZ"))' "\$3"
EOF
printf '#!/usr/bin/env bash\nshasum -a 256 "$@"\n' > "$T/bin/sha256sum"
chmod +x "$T/bin/"*

blk=$(awk '/^PR=docs\/orchestration/ {on = 1} on {print} /^echo "ll5d constraint / {exit}' "$CONN")
nl=$(printf '%s\n' "$blk" | wc -l | tr -d ' ')
first=$(printf '%s\n' "$blk" | head -1 | cut -c1-12); last=$(printf '%s\n' "$blk" | tail -1 | cut -c1-20)
echo "block: $nl lines, from '$first' to '$last'"
[ "$nl" -ge 15 ] || { echo "BLOCK NOT FOUND"; exit 1; }

A=$T/A; O=$T/O
mkdir -p "$A/2d-unfolding/baseline_flux" "$A/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints" "$O/prepare"
mk() { printf '%s' "$2" > "$1"; }
reset() {
    rm -f "$T/fix/record.json"
    mk "$A/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root" uni
    mk "$A/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root" mc
    mk "$A/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root" fluxu
    mk "$O/prepare/g2r_map.npz" "the map bytes"
    mk "$A/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt" con
}
mapsha() { shasum -a 256 "$O/prepare/g2r_map.npz" | cut -c1-64; }
rec() { printf '{"verdict": "%s"%s}\n' "$1" "${2:+, \"map_npz_sha256\": \"$2\"}" > "$T/fix/record.json"; }
run() {
    { printf 'set -u\nA=%q; O=%q; C=%q\n' "$A" "$O" "$T/deploy"
      printf 'stop() { echo "STOP $*"; echo DONE; exit 2; }\n'
      printf '%s\n' "$blk"
      printf 'echo REACHED-SUBMIT\n'; } > "$T/case.sh"
    PATH=$T/bin:$PATH FIX=$T/fix bash "$T/case.sh" > "$T/out" 2>&1; echo $? > "$T/rc"
}
fail=0
check() {  # check <name> <want rc> <want pattern>
    local rc; rc=$(cat "$T/rc")
    if [ "$rc" = "$2" ] && grep -qE "$3" "$T/out"; then echo "PASS $1 rc=$rc"
    else echo "FAIL $1 rc=$rc (want $2, /$3/)"; sed 's/^/    /' "$T/out"; fail=1; fi
}
reset; rec PASS "$(mapsha)"; run; check pass 0 'REACHED-SUBMIT'
grep -qE '^map .* sha256=[0-9a-f]{64} \(O_NOATIME\)$' "$T/out" && grep -c '^input ' "$T/out" | grep -qx 4 \
    && grep -qE '^ll5d constraint .* atime_epoch=[0-9]+ ' "$T/out" && grep -q 'verdict=PASS map_npz_sha256=' "$T/out" \
    && echo "PASS pass-lines (record, map, 4 inputs, constraint)" || { echo "FAIL pass-lines"; sed 's/^/    /' "$T/out"; fail=1; }
reset; rec STOP "$(mapsha)"; run; check record-stop 2 "^STOP the prepare's PASS is not committed"
reset; run; check record-absent 2 "^STOP the prepare's PASS is not committed"
reset; printf 'not json' > "$T/fix/record.json"; run; check record-garbled 2 "^STOP the prepare's PASS is not committed"
reset; rec PASS; run; check record-no-mapsha 2 "^STOP the map's sha256 is not the committed"
reset; rec PASS "$(printf '0%.0s' $(seq 64))"; run; check map-mismatch 2 "^STOP the map's sha256 is not the committed"
reset; rec PASS "$(mapsha)"; rm -f "$O/prepare/g2r_map.npz"; run; check map-missing 2 "^STOP the map's sha256 is not the committed"
reset; rec PASS "$(mapsha)"; rm -f "$A/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"; run
check input-missing 2 "^STOP .*runEventLoopMC_MEFHC.root is missing"
reset; rec PASS "$(mapsha)"; rm -f "$A/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"
run; check constraint-missing-no-stop 0 'atime_epoch=missing.*REACHED-SUBMIT|REACHED-SUBMIT'
grep -q 'atime_epoch=missing' "$T/out" || { echo "FAIL constraint-missing printed no 'missing'"; fail=1; }
rm -f "$T"/A/2d-unfolding/*.root "$T"/A/2d-unfolding/baseline_flux/*.root "$T"/O/prepare/g2r_map.npz "$T"/fix/record.json \
    "$T"/A/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/*.txt "$T"/bin/* "$T"/case.sh "$T"/out "$T"/rc
find "$T" -depth -type d -exec rmdir {} \;
[ -e "$T" ] && echo "left: $T"
[ "$fail" = 0 ] && echo "CONNECT-DUA BLOCK TEST PASS" || echo "CONNECT-DUA BLOCK TEST FAILED"
exit $fail
