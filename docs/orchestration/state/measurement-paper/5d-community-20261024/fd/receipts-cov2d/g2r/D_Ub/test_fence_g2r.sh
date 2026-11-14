#!/bin/bash
# The D_Ub fence: connect-g2r-D_Ub.sh's fence block (from "# --- the fence" to "# --- iris") and launch-g2r.sh's fence
# script plus its unended-cov2d refusal, run against stand-in squeue/sacct. COV2D-G2R's own cov2dg2r-* jobs are admitted;
# every other refused family (rsn_, e96data, rdx_, t2a, cov2d-*) still stops, queued or unended. No ssh, no cluster.
#     bash test_fence_g2r.sh [connect] [launcher]
set -u
H=$(cd "$(dirname "$0")" && pwd)
CONN=${1:-$H/connect-g2r-D_Ub.sh}; LAUN=${2:-$H/launch-g2r.sh}
T=$(mktemp -d "${TMPDIR:-/tmp}/tfence.XXXXXX"); mkdir -p "$T/bin"
cat > "$T/bin/squeue" <<'EOF'
#!/usr/bin/env bash
# squeue [--me|-u josephrb] -h -o FMT: one line per "name state" row of $SQ, in FMT's fields (%i %j %T %l %D)
fmt=${@: -1}; i=100
while read -r name state; do
    [ -n "$name" ] || continue; i=$((i + 1))
    out=$fmt; out=${out//%i/$i}; out=${out//%j/$name}; out=${out//%T/$state}; out=${out//%l/8:54:00}; out=${out//%D/1}
    printf '%s\n' "$out"
done < "$SQ"
EOF
cat > "$T/bin/sacct" <<'EOF'
#!/usr/bin/env bash
# sacct ... -o JobID,JobName,State: the "name state" rows of $SA as JobID|JobName|State
i=200; while read -r name state; do [ -n "$name" ] || continue; i=$((i + 1)); echo "$i|$name|$state"; done < "$SA"
EOF
chmod +x "$T/bin/"*
cblk=$(awk '/^# --- the fence$/ {on = 1; next} /^# --- iris/ {exit} on' "$CONN")
lfence=$(awk "/^cat > \"\\\$OUT\\/fence.sh\" <<'FENCE'\$/ {on = 1; next} /^FENCE\$/ {exit} on" "$LAUN")
lrefuse=$(awk '/^\[ "\$\(sed -n .\/\^sacct unended cov2d:/ {on = 1} on {print} on && /REFUSED: a cov2d/ {exit}' "$LAUN")
echo "connect fence: $(printf '%s\n' "$cblk" | wc -l | tr -d ' ') lines; launcher fence: $(printf '%s\n' "$lfence" | wc -l | tr -d ' ') lines, refusal: $(printf '%s\n' "$lrefuse" | wc -l | tr -d ' ') lines"
[ -n "$cblk" ] && [ -n "$lfence" ] && [ "$(printf '%s\n' "$lrefuse" | wc -l | tr -d ' ')" = 2 ] || { echo "BLOCKS NOT FOUND"; exit 1; }
fail=0
case_() {  # case_ <name> <want connect: pass|stop> <want launcher: clear|refused> <squeue rows> <sacct rows>
    printf '%b' "$4" > "$T/sq"; printf '%b' "$5" > "$T/sa"
    { printf 'stop() { echo "STOP $*"; exit 2; }\n'; printf '%s\n' "$cblk"; echo 'echo FENCE-PASSED'; } > "$T/c.sh"
    PATH=$T/bin:$PATH SQ=$T/sq SA=$T/sa bash "$T/c.sh" > "$T/c.out" 2>&1; crc=$?
    { printf 'OUT=%q\n' "$T"; printf '%s\n' "$lfence" > "$T/fence.sh"; echo 'bash "$OUT/fence.sh" > "$OUT/fence.txt" 2>&1'
      printf '%s\n' "$lrefuse"; echo 'echo FENCE_CLEAR'; } > "$T/l.sh"
    PATH=$T/bin:$PATH SQ=$T/sq SA=$T/sa bash "$T/l.sh" > "$T/l.out" 2>&1; lrc=$?
    local cg lg; [ "$crc" = 0 ] && grep -q FENCE-PASSED "$T/c.out" && cg=pass || { grep -q '^STOP ' "$T/c.out" && cg=stop || cg=other; }
    [ "$lrc" = 0 ] && grep -q FENCE_CLEAR "$T/l.out" && lg=clear || { grep -q '^REFUSED: a cov2d (not cov2dg2r-) job is unended' "$T/l.out" && lg=refused || lg=other; }
    if [ "$cg" = "$2" ] && [ "$lg" = "$3" ]; then echo "PASS $1 connect=$cg launcher=$lg"
    else echo "FAIL $1 connect=$cg (want $2) launcher=$lg (want $3)"; sed 's/^/    c: /' "$T/c.out"; sed 's/^/    l: /' "$T/l.out"; fail=1; fi
}
case_ d_ua-running pass clear "ll5d_bulk_05 RUNNING\ncov2dg2r-D_Ua RUNNING\n" "cov2dg2r-D_Ua RUNNING\ncov2dg2r-prepare COMPLETED\n"
case_ nothing pass clear "" ""
case_ g2r-pending pass clear "cov2dg2r-D_Ua PENDING\n" "cov2dg2r-D_Ua PENDING\n"
case_ cov2d-queued stop refused "cov2d-pilot PENDING\n" "cov2d-pilot PENDING\n"
case_ cov2d-unended-only stop refused "" "cov2d-null RUNNING\n"
case_ cov2d-ended pass clear "" "cov2d-null COMPLETED\ncov2d-x CANCELLED by 1\n"
case_ rdx stop clear "rdx_s1 RUNNING\n" ""
case_ rsn stop clear "rsn_a PENDING\n" ""
case_ e96data stop clear "e96data_1 RUNNING\n" ""
case_ t2a stop clear "t2a_x RUNNING\n" ""
case_ g2r-and-cov2d stop refused "cov2dg2r-D_Ua RUNNING\ncov2d-s RUNNING\n" "cov2dg2r-D_Ua RUNNING\ncov2d-s RUNNING\n"
grep -q '^cov2dg2r queued or running: \[' "$T/c.out" || { echo "FAIL the connect does not print its cov2dg2r line"; fail=1; }
rm -f "$T"/bin/* "$T"/sq "$T"/sa "$T"/c.sh "$T"/c.out "$T"/l.sh "$T"/l.out "$T"/fence.sh "$T"/fence.txt; rmdir "$T/bin" "$T"
[ "$fail" = 0 ] && echo "FENCE-G2R TEST PASS" || echo "FENCE-G2R TEST FAILED"
exit $fail
