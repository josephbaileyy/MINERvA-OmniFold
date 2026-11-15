#!/bin/bash
# Stand-in test of connect-rerun129.sh's new block (from `k=$(ls "$U"` to the end of the OVL heredoc): the 1662-product
# count of $U, the bulk partition's pin, the node 09 lane 4 row split into 4 lanes of 5 (consecutive, in order), the
# 20 names in $U, and the WORLD x G2R overlap check.
# P, ND, U, BW and W point into a fresh mktemp tree; LANESHA is the connect's own value; the partition is the real
# bulk-lanes.tsv (315f004b). Cases: pass; $U one short; one of the 20 missing; the partition altered; a planted
# overlap (a WORLD dir that resolves to the G2R inputs' directory). Exit 0 only if every case behaves.
#     bash test_connect_rerun129.sh connect-rerun129.sh ../bulk-lanes.tsv
set -u
CONN=$1; LANES=$2
blk=$(awk '/^k=\$\(ls "\$U" \| grep -c/ {on = 1} on {print} on && /^OVL$/ {exit}' "$CONN")
LANESHA=$(sed -n 's/^LANESHA=\([0-9a-f]\{64\}\)$/\1/p' "$CONN")
echo "block: $(printf '%s\n' "$blk" | wc -l | tr -d ' ') lines; LANESHA=$LANESHA"
T=$(mktemp -d "${TMPDIR:-/tmp}/tcr129.XXXXXX")
fail=0; n=0
setup() {
    n=$((n + 1)); R=$T/c$n; P=$R/p; ND=$P/MINERvA-OmniFold/nd-unfolding; U=$P/ll5d-unfolds-r2; BW=$P/ll5d-bulk-r1; W=$P/ll5d-rerun129-r1
    mkdir -p "$ND" "$U" "$BW" "$W" "$P/MINERvA-OmniFold/2d-unfolding/baseline_flux"
    cp "$LANES" "$BW/bulk-lanes.tsv"
    items=$(awk -F'\t' '$1 == "09" && $2 == "4" {print $5}' "$LANES" | tr ',' ' ')
    for it in $items; do : > "$U/ll5d_ar23_toy_$it.npz"; done
    i=0; while [ "$(ls "$U" | grep -c '\.npz$')" -lt 1662 ]; do i=$((i + 1)); : > "$U/ll5d_x_$i.npz"; done
}
run() {
    { printf 'P=%q; ND=%q; U=%q; BW=%q; W=%q; LANESHA=%s\n' "$P" "$ND" "$U" "$BW" "$W" "$LANESHA"
      printf 'stop() { echo "STOP $*"; exit 2; }\n'; printf '%s\n' "$blk"; echo 'echo REACHED-END'; } > "$R/case.sh"
    (cd "$R" && bash case.sh) > "$R/out" 2>&1; echo $? > "$R/rc"
}
check() {
    local rc; rc=$(cat "$R/rc")
    if [ "$rc" = "$2" ] && grep -qE "$3" "$R/out"; then echo "PASS $1 rc=$rc"
    else echo "FAIL $1 rc=$rc (want $2, /$3/)"; sed 's/^/    /' "$R/out"; fail=1; fi
}
setup; run; check pass 0 'REACHED-END'
grep -qx 'products in \$U: 1662' "$R/out" && [ "$(grep -c '^rerun lane: 01 [0-3] ar23 toy items=5 ' "$R/out")" = 4 ] \
  && grep -q '^overlap check: 8 WORLD paths x 18 G2R inputs, hits \[\]$' "$R/out" && echo "PASS pass-lines" || { echo "FAIL pass-lines"; sed 's/^/    /' "$R/out"; fail=1; }
[ "$(cut -f2 "$W/rerun-lanes.tsv" | paste -sd' ' -)" = "0 1 2 3" ] \
  && [ "$(cut -f5 "$W/rerun-lanes.tsv" | paste -sd, -)" = "$(awk -F'\t' '$1 == "09" && $2 == "4" {print $5}' "$LANES")" ] \
  && [ "$(cut -f5 "$W/rerun-lanes.tsv" | tr ',' '\n' | sort -u | wc -l | tr -d ' ')" = 20 ] \
  && echo "PASS lanes-0-3-slices-join-to-bulk-09-4-and-are-disjoint" || { echo "FAIL lanes"; cat "$W/rerun-lanes.tsv"; fail=1; }
awk -F'\t' '{print "    lane " $2 ": " $5}' "$W/rerun-lanes.tsv"
setup; rm -f "$U/ll5d_x_1.npz"; run; check u-one-short 2 '^STOP .*does not hold the bulk.s 1662 products'
setup; rm -f "$U/ll5d_ar23_toy_all_4761071.npz"; : > "$U/ll5d_x_extra.npz"; run; check one-of-20-missing 2 '^STOP .*ll5d_ar23_toy_all_4761071.npz is not there'
setup; printf '# altered\n' >> "$BW/bulk-lanes.tsv"; run; check partition-altered 2 '^STOP the bulk.s bulk-lanes.tsv is not the pinned partition'
setup; mkdir -p "$P/s5p-20260926"; ln -s "$P/MINERvA-OmniFold/2d-unfolding" "$P/s5p-20260926/bank_detector"; run
check overlap-planted 2 '^STOP a WORLD path overlaps a G2R input'
grep -q "hits \[('$P/s5p-20260926/bank_detector'" "$R/out" && echo "PASS overlap-detector-fired" || { echo "FAIL overlap-detector-fired"; fail=1; }
find "$T" -type l -exec rm -f {} +; find "$T" -type f -exec rm -f {} +; find "$T" -depth -type d -exec rmdir {} \;
[ -e "$T" ] && echo "left: $T"
[ "$fail" = 0 ] && echo "CONNECT-RERUN129 BLOCK TEST PASS" || echo "CONNECT-RERUN129 BLOCK TEST FAILED"
exit $fail
