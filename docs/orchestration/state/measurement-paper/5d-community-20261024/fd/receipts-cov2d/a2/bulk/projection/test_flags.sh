#!/bin/bash
# Both-direction test of flags.py (the director's triggers, 2026-11-06). Inputs: the 15:22:02Z snapshot out.txt and
# projection proj.txt; the 15:24:51Z snapshot out-1524.txt and projection proj-1524.txt. Every case must give its rc.
cd "$(dirname "$0")"; T=$(mktemp -d "${TMPDIR:-/tmp}/flagtest.XXXXXX"); fail=0
c() { local want=$1 name=$2 pat=$3; shift 3; python3 -I -B flags.py "$@" > $T/o; local rc=$?
      if [ "$rc" = "$want" ] && { [ -z "$pat" ] || grep -q "$pat" $T/o; }; then echo "ok   $name rc=$rc"; else echo "FAIL $name rc=$rc want=$want"; cat $T/o; fail=1; fi; }
c 0 "silent: baseline vs itself"              ""                 proj.txt out.txt proj.txt out.txt
c 0 "silent: 15:24 snapshot, all 3 triggers"  ""                 proj-1524.txt out-1524.txt proj.txt out.txt
c 3 "fires: over-max vs the 15:22 max"        "RUN-OVER-MAX"     proj.txt out-1524.txt
sed "s/('G18', 'B') 252 0.742 0.124 0.612 0.838 1.245/('G18', 'B') 252 0.742 0.124 0.612 0.838 1.244/" proj.txt > $T/max.txt
c 3 "fires: lowered G18 B max on baseline"     "B_G18_004"        $T/max.txt out.txt
sed 's/^\(G18_Uc    60895578  RUNNING     4.82 | 5.43 \/ 5.66 \/ \)5.76/\13.00/' proj.txt > $T/slip.txt
c 3 "fires: G18_Uc p90 lowered to 3.00 h"      "END-SLIP cov2d-G18_Uc" $T/slip.txt out.txt
sed "s/('G18', 'T') 229 0.784/('G18', 'T') 229 0.700/" proj.txt > $T/mean.txt
c 3 "fires: G18 T fixed mean lowered to 0.700" "OVER-1.3MEAN G18_Tc T_G18_5720275" proj-1524.txt out-1524.txt $T/mean.txt out.txt
# regressions (2026-11-07): G18_C's rows crashed the class lookup (KeyError ('G18','C')), and Python's crash rc 1 read
# as "fired"; flags now exit 3, so a crash is neither 0 nor 3. Ended jobs are checked against their sacct End.
awk '{print} /^== WALLS/ {print "walls.G18_C.1.tsv\tL_G18_BeamAngleX_0\t1793990000\t1793991100\t0"; print "walls.G18_C.1.tsv\tX_G18\t1793991100\t1793991680\t0"}' out-1524.txt > $T/gc.txt
c 0 "silent: G18_C rows at normal ratios"       ""                 proj-1524.txt $T/gc.txt proj.txt out.txt
awk '{print} /^== WALLS/ {print "walls.G18_C.2.tsv\tT_G18_5720000\t1793990000\t1793991200\t0"}' out-1524.txt > $T/gcslow.txt
c 3 "fires: a slow G18_C T row (1200/866 s)"    "OVER-1.3MEAN G18_C T_G18_5720000" proj-1524.txt $T/gcslow.txt proj.txt out.txt
sed 's/^\(60895578|cov2d-G18_Uc|\)RUNNING|17341|1|534|\(2026-11-06T01:08:15|2026-11-06T02:33:01\)|Unknown/\1COMPLETED|36000|1|534|\2|2026-11-06T12:33:01/' out.txt > $T/late.txt
c 3 "fires: G18_Uc ended 10 h after start"      "END-SLIP cov2d-G18_Uc 60895578 ended" proj.txt $T/late.txt
printf 'NOW 2026-11-06T15:22:02Z\n== SACCT\n== WALLS\nwalls.G18_Ua.1.tsv\tU_G18_Flux_2\t1\n== RUNS\n' > $T/bad.txt
python3 -I -B flags.py proj.txt $T/bad.txt > /dev/null 2>&1; rc=$?
if [ "$rc" != 0 ] && [ "$rc" != 3 ]; then echo "ok   crash is neither 0 nor 3 (rc=$rc)"; else echo "FAIL crash rc=$rc"; fail=1; fi
rm -r "$T"; [ "$fail" = 0 ] && echo "ALL PASS" || { echo "FAILED"; exit 1; }
