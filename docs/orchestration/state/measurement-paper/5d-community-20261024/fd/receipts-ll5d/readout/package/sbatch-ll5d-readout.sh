#!/bin/bash
# ll5d_readout_01's job: the deploy at M with porcelain 0 and the bound blobs, checked ONCE here, before both calls; then
# ll5d_b.py readout for g18, then for ar23, one after the other; after each, its record checked (rc 0, no atime move).
# Not under set -u. Writes only under $W.
DD=$1; M=$2; W=$3; U=$4; NODE=$5
P=/pscratch/sd/j/josephrb; STAGED=$P/fd-1b-inv-20261101/i0/in; NW=$P/ll5d-null-r1; PW=$P/ll5d-pilot-r2
CONSTRAINT=$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
NULL_g18=73dbaf9517374646c719ff589015cb12c1a6a2eafd5579e1074ef700bde703c2; NULL_ar23=a0544ab9f6f0ec55c9866bee689d2563b13c9d07f4b3fdc37ce4762718a23933
GATE_g18=a5d66b7e506a98d5a0b555dbe171aa6c1e931eb93df793c3e515d7d44466fc70; GW_g18=$P/ll5d-gate-2-g18-20261110
GATE_ar23=35a20c471cb06f428c49daaaebfc6646babb7f7fb060039d4c63139da51d0a4c; GW_ar23=$P/ll5d-gate-2-ar23-20261110
CLIPSHA=9632540ecd0d25e2223eedb480b96078459a6e6d75128b4e4132ea1bf644d3aa
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
echo "host=$(hostname) job=$SLURM_JOB_ID node=$NODE start=$(date -u +%FT%TZ)"
h=$(git -C "$DD" rev-parse HEAD); n=$(git -C "$DD" status --porcelain | wc -l); echo "deploy head=$h porcelain_lines=$n"
[ "$h" = "$M" ] && [ "$n" = "0" ] || stop "deploy not clean at M"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
source "$DD/setup_salloc_env.sh" > "$W/logs/env-job-$NODE.log" 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
urc=0
for T in g18 ar23; do
  eval "ns=\$NULL_$T; gs=\$GATE_$T; gw=\$GW_$T"
  /usr/bin/time -v python3 -B "$DD/nd-unfolding/ll5d_b.py" readout --staged "$STAGED" \
    --definition "$DD/nd-unfolding/pv-ladder/readouts/h2_definition.json" --unfolds "$U" \
    --cmodel-json "$DD/nd-unfolding/pv-ladder/readouts/cmodel_5d.json" --flux-constraint "$CONSTRAINT" --truth "$T" \
    --null "$NW/null-$T.json" --expect-null-sha256 "$ns" --clipcheck "$PW/clipcheck.json" --expect-clipcheck-sha256 "$CLIPSHA" \
    --gate "$gw/gate-$T.json" --expect-gate-sha256 "$gs" --out "$W/readout-$T.json" < /dev/null > "$W/readout-$T.out" 2> "$W/readout-$T.time"; s=$?
  echo "readout $T rc=$s: $(tail -1 "$W/readout-$T.out")"
  python3 -B - "$W/readout-$T.json" "$W/readout-$T.invalid.json" "$s" "$T" <<'CHECK'
import json, os, sys
rec_p, inv_p, rc, T = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
p = rec_p if os.path.exists(rec_p) else inv_p if os.path.exists(inv_p) else None
if p is None:
    print(f"READOUT-EXIT {T} NOT-CLEAN rc={rc}: no record; to the director unrepaired"); sys.exit(1)
rec = json.load(open(p))
moved = rec.get("atime", {}).get("moved", [])
print(f"readout {T}: record {os.path.basename(p)} verdicts {rec.get('verdicts')} moved {len(moved)} {moved[:5]}")
ok = rc == 0 and p == rec_p and moved == [] and "evaluations" in rec
print(f"READOUT-EXIT {T} " + ("CLEAN: rc 0, record written, atime.moved []" if ok else
      f"NOT-CLEAN rc={rc}: to the director unrepaired"))
sys.exit(0 if ok else 1)
CHECK
  c=$?; urc=$((urc | c))
done
sha256sum "$W"/readout-*.json "$W"/readout-*.out 2>/dev/null
grep -h -E "Elapsed|Maximum resident|Exit status" "$W"/readout-*.time
echo "readout checks rc=$urc"
echo "end=$(date -u +%FT%TZ)"
exit $urc
