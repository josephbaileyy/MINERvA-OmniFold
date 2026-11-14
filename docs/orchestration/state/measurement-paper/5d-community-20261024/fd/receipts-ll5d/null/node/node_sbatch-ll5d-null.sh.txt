#!/bin/bash
# ll5d_null_01's job: the deploy at M with porcelain 0 and the bound blobs, checked ONCE here, before both calls; the
# expected moved set recomputed from the bound module and pinned; then ll5d_b.py null for g18, then for ar23, one after
# the other; after each, its record checked against the fixed set. Not under set -u. Writes only under $W.
DD=$1; M=$2; W=$3; U=$4; NODE=$5
P=/pscratch/sd/j/josephrb; STAGED=$P/fd-1b-inv-20261101/i0/in
CONSTRAINT=$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
EXP_g18_SHA256=ec363fd10db805005306e12955bc8651a02a340d5e53b8e81097bc53cb0e1e01; EXP_g18_N=227
EXP_ar23_SHA256=923681b295f1226360ca9ba9ee73c783ad7d9e2d559abd0106bc20d6320f3a93; EXP_ar23_N=227
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
echo "host=$(hostname) job=$SLURM_JOB_ID node=$NODE start=$(date -u +%FT%TZ)"
h=$(git -C "$DD" rev-parse HEAD); n=$(git -C "$DD" status --porcelain | wc -l); echo "deploy head=$h porcelain_lines=$n"
[ "$h" = "$M" ] && [ "$n" = "0" ] || stop "deploy not clean at M"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
source "$DD/setup_salloc_env.sh" > "$W/logs/env-job-$NODE.log" 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# the expected moved set (the director's ruling (a)): remade's opened products (bands_of, sa.EXPECT, STAT_REPLICAS,
# product_name over READINGS) intersected with products_digest's set (TAG, BLOCK_ROLES) applied to $U's names
for T in g18 ar23; do
  python3 -B - "$DD/nd-unfolding" "$W/u-names.txt" "$U" "$T" "$W/expected_moved_$T.txt" <<'EXPECT' || stop "expected set $T"
import hashlib, sys
sys.path.insert(0, sys.argv[1])
import ll5d, ll5d_b as b
names = [l.strip() for l in open(sys.argv[2]) if l.strip()]
U, T = sys.argv[3].rstrip("/"), sys.argv[4]
opened = set()
for rd in ll5d.READINGS:
    opened |= {b.product_name(T, "central", "T"), b.product_name(T, "seed", "T")}
    opened |= {b.product_name(T, "block", f"{band}_{i}") for band in b.bands_of(rd) for i in range(b.sa.EXPECT[band])}
    opened |= {b.product_name(T, "stat", str(x)) for x in b.STAT_REPLICAS}
dig = {n for n in names if n.startswith(f"{b.TAG}_{T}_") and n.endswith(".npz") and ".partial-" not in n
        and n.split("_")[2] in b.BLOCK_ROLES}
body = "".join(f"{U}/{n}\n" for n in sorted(opened & dig))
open(sys.argv[5], "w").write(body)
print(f"expected {T}: opened {len(opened)} digested {len(dig)} absent {len(opened - set(names))} moved {len(opened & dig)} "
      f"sha256 {hashlib.sha256(body.encode()).hexdigest()}")
sys.exit(1 if opened - set(names) else 0)
EXPECT
  eval "want=\$EXP_${T}_SHA256; wn=\$EXP_${T}_N"
  [ "$(sha256sum "$W/expected_moved_$T.txt" | cut -d' ' -f1)" = "$want" ] && [ "$(awk 'END {print NR}' "$W/expected_moved_$T.txt")" = "$wn" ] \
    || stop "the expected moved set at $T is not the fixed one ($want, $wn paths)"
  echo "expected moved $T: $wn paths, sha256 $want (fixed)"
done
urc=0
for T in g18 ar23; do
  /usr/bin/time -v python3 -B "$DD/nd-unfolding/ll5d_b.py" null --staged "$STAGED" \
    --definition "$DD/nd-unfolding/pv-ladder/readouts/h2_definition.json" --unfolds "$U" \
    --cmodel-json "$DD/nd-unfolding/pv-ladder/readouts/cmodel_5d.json" --flux-constraint "$CONSTRAINT" \
    --truth "$T" --out "$W/null-$T.json" < /dev/null > "$W/null-$T.out" 2> "$W/null-$T.time"; s=$?
  echo "null $T rc=$s: $(tail -1 "$W/null-$T.out")"
  python3 -B - "$W/null-$T.json" "$W/null-$T.invalid.json" "$W/expected_moved_$T.txt" "$s" "$T" <<'CHECK'
import json, os, sys
rec_p, inv_p, exp_p, rc, T = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
exp = sorted(l for l in open(exp_p).read().splitlines() if l)
p = rec_p if os.path.exists(rec_p) else inv_p if os.path.exists(inv_p) else None
if p is None:
    print(f"NULL-EXIT {T} NOT-CLEAN rc={rc}: no record; to the director unrepaired"); sys.exit(1)
rec = json.load(open(p))
moved = sorted(rec.get("atime", {}).get("moved", []))
extra, missing = sorted(set(moved) - set(exp)), sorted(set(exp) - set(moved))
print(f"null {T}: record {os.path.basename(p)} verdict {rec.get('verdict')} moved {len(moved)} expected {len(exp)} "
      f"extra {len(extra)} {extra[:5]} missing {len(missing)} {missing[:5]}")
ok = rc == 8 and p == rec_p and rec.get("verdict") == "PASS" and not extra and not missing
print(f"NULL-EXIT {T} " + ("CLEAN: rc 8, verdict PASS, moved == the fixed set (the declared deviation)" if ok else
      f"NOT-CLEAN rc={rc}: to the director unrepaired; nothing is read from this null"))
sys.exit(0 if ok else 1)
CHECK
  c=$?; urc=$((urc | c))
done
sha256sum "$W"/null-*.json "$W"/null-*.out "$W"/expected_moved_*.txt 2>/dev/null
grep -h -E "Elapsed|Maximum resident|Exit status" "$W"/null-*.time
echo "null checks rc=$urc"
echo "end=$(date -u +%FT%TZ)"
exit $urc
