"""Derive connect-null.sh from rerun129/connect-rerun129.sh (0fb2f282, the approved rerun connect) by explicit
replacements, each matching exactly once. Writes connect-null.sh beside this file.
    python3 -I make_null_connect.py
"""
import hashlib
from pathlib import Path

H = Path(__file__).resolve().parent
SRC = H.parent / "rerun129" / "connect-rerun129.sh"
s = SRC.read_text()
assert hashlib.sha256(s.encode()).hexdigest().startswith("0fb2f282"), "the rerun connect is not 0fb2f282"
lines = s.split("\n")
EXP = {"g18": ("ec363fd10db805005306e12955bc8651a02a340d5e53b8e81097bc53cb0e1e01", 227),
       "ar23": ("923681b295f1226360ca9ba9ee73c783ad7d9e2d559abd0106bc20d6320f3a93", 227)}


def rep(old: str, new: str) -> None:
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"{n} matches for: {old[:100]!r}")
    s = s.replace(old, new)


# 1. header (the rerun connect's lines 2-13)
rep("\n".join(lines[1:13]) + "\n", """# LL5D section 11 step 7: the null at G18 and AR23 (ll5d_b.py null, one call per truth, both readings and both
# matrices inside), DRAFT for the director's review. The director's ruling (a), 2026-11-14: run as bound; the
# products_digest moves are the declared deviation of LL5D-DECLARATION.md:672-673. At 4231b14d null_step opens the
# products through the atime watch (ll5d_b.py:499 remade, _x :366-368), and only then hashes them with a plain open
# (:502 products_digest, :477; s5c_unfold.py:87-89). So each call's record should list exactly those products in
# atime.moved and exit 8 with verdict PASS. That expected set is fixed here before the run: the job recomputes it from
# the bound module and must reproduce EXP_<T>_SHA256 (227 paths per truth: central T, seed T, 175 blocks, stat 1-50),
# or it stops before any call. CLEAN per truth = rc exactly 8, verdict PASS, atime.moved set-equal to the fixed set.
# Anything else (rc 0, 13, any extra or missing path) is NOT-CLEAN and goes to the director unrepaired.
# ONE job (-N 1 --exclusive, --time 01:00:00, 1.0 node-h) on a FRESH deploy clone at M that no other job reads; its
# single start check (sha256sum -c) runs before both calls, which run one after the other, so no plain read of a
# watched file runs while a call is in flight (B1). Writes only under $W; $U is read. Nothing to CFS. Not under set -u.
""")
# 2. namespaces, inputs, price
rep("W=$P/ll5d-rerun129-r1; DD=$W/deploy; U=$P/ll5d-unfolds-r2; PW=$P/ll5d-pilot-r2   # $U is read-only here (names)\n"
    "UO=$P/ll5d-unfolds-rerun129-r1   # the rerun's fresh out directory (refused if it exists)\n"
    "BW=$P/ll5d-bulk-r1               # the bulk's namespace: its pinned bulk-lanes.tsv is read (plainly; not an LL5D input)\n",
    "W=$P/ll5d-null-r1; DD=$W/deploy; U=$P/ll5d-unfolds-r2; PW=$P/ll5d-pilot-r2   # $U: the bulk's 1662 products, read\n"
    "STAGED=$P/fd-1b-inv-20261101/i0/in   # --staged (setup reads s1/s1_assembly.npz through via_noatime)\n"
    "CONSTRAINT=$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt\n"
    "CMODELSHA=3cfdc6a5b8c6cea5f99b4678e27f6ca5f7973ee57a79b9d139798f0751cfcd60   # nd-unfolding/pv-ladder/readouts/cmodel_5d.json at M\n")
rep('CAP=148.0; THIS=2.5; TL=02:30:00; NODES="01"   # 4 lanes of 5: 5 x 1,062 s = 5,310 s + setup < 9,000 s',
    'CAP=148.0; THIS=1.0; TL=01:00:00; NODES="01"   # two null calls, one after the other, on one node')
rep('for v in "$G18GATE" "$AR23GATE" "$WALLSSHA" "$CLIPSHA" "$CTLSHA" "$L5" "$LANESHA"; do',
    'for v in "$G18GATE" "$AR23GATE" "$WALLSSHA" "$CLIPSHA" "$CTLSHA" "$L5" "$CMODELSHA"; do')
rep("LANESHA=315f004bb6869345400dd87f3bee2d31f380713492e33ce3c5a7582a6c41ede7\n", "")
rep('exec >> "$W/logs/connect-rerun129.log" 2>&1', 'exec >> "$W/logs/connect-null.log" 2>&1')
rep('[ -e "$UO" ] && stop "$UO exists"\n', "")
# 3. drop the rerun's row split and its G2R overlap block (from the partition pin to the end of the OVL heredoc)
p0 = s.index('[ "$(sha256sum "$BW/bulk-lanes.tsv"')
p1 = s.index("\nOVL\n", p0) + len("\nOVL\n")
s = s[:p0] + s[p1:]
# 4. after the bound blobs: the cmodel json at M, and $U's names (ls: names only, nothing opened)
rep('(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"\ncat > "$W/sbatch-ll5d-rerun129.sh" <<\'JOB\'',
    '(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"\n'
    '[ "$(sha256sum "$DD/nd-unfolding/pv-ladder/readouts/cmodel_5d.json" | cut -d\' \' -f1)" = "$CMODELSHA" ] || stop "cmodel_5d.json is not M\'s"\n'
    'echo "cmodel_5d.json $CMODELSHA OK"\n'
    'ls "$U" > "$W/u-names.txt" || stop "ls \\$U"\n'
    'echo "u-names $(awk \'END {print NR}\' "$W/u-names.txt") lines sha256 $(sha256sum "$W/u-names.txt" | cut -d\' \' -f1)"\n'
    'cat > "$W/sbatch-ll5d-null.sh" <<\'JOB\'')
# 5. the job script: replace the rerun's body (from its first comment line to `exit $urc`)
j0 = s.index("# ll5d_rerun129_01's job:")
j1 = s.index("exit $urc\nJOB\n") + len("exit $urc\n")
JOB = f"""# ll5d_null_01's job: the deploy at M with porcelain 0 and the bound blobs, checked ONCE here, before both calls; the
# expected moved set recomputed from the bound module and pinned; then ll5d_b.py null for g18, then for ar23, one after
# the other; after each, its record checked against the fixed set. Not under set -u. Writes only under $W.
DD=$1; M=$2; W=$3; U=$4; NODE=$5
P=/pscratch/sd/j/josephrb; STAGED=$P/fd-1b-inv-20261101/i0/in
CONSTRAINT=$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
EXP_g18_SHA256={EXP['g18'][0]}; EXP_g18_N={EXP['g18'][1]}
EXP_ar23_SHA256={EXP['ar23'][0]}; EXP_ar23_N={EXP['ar23'][1]}
stop() {{ echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }}
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
    opened |= {{b.product_name(T, "central", "T"), b.product_name(T, "seed", "T")}}
    opened |= {{b.product_name(T, "block", f"{{band}}_{{i}}") for band in b.bands_of(rd) for i in range(b.sa.EXPECT[band])}}
    opened |= {{b.product_name(T, "stat", str(x)) for x in b.STAT_REPLICAS}}
dig = {{n for n in names if n.startswith(f"{{b.TAG}}_{{T}}_") and n.endswith(".npz") and ".partial-" not in n
        and n.split("_")[2] in b.BLOCK_ROLES}}
body = "".join(f"{{U}}/{{n}}\\n" for n in sorted(opened & dig))
open(sys.argv[5], "w").write(body)
print(f"expected {{T}}: opened {{len(opened)}} digested {{len(dig)}} absent {{len(opened - set(names))}} moved {{len(opened & dig)}} "
      f"sha256 {{hashlib.sha256(body.encode()).hexdigest()}}")
sys.exit(1 if opened - set(names) else 0)
EXPECT
  eval "want=\\$EXP_${{T}}_SHA256; wn=\\$EXP_${{T}}_N"
  [ "$(sha256sum "$W/expected_moved_$T.txt" | cut -d' ' -f1)" = "$want" ] && [ "$(awk 'END {{print NR}}' "$W/expected_moved_$T.txt")" = "$wn" ] \\
    || stop "the expected moved set at $T is not the fixed one ($want, $wn paths)"
  echo "expected moved $T: $wn paths, sha256 $want (fixed)"
done
urc=0
for T in g18 ar23; do
  /usr/bin/time -v python3 -B "$DD/nd-unfolding/ll5d_b.py" null --staged "$STAGED" \\
    --definition "$DD/nd-unfolding/pv-ladder/readouts/h2_definition.json" --unfolds "$U" \\
    --cmodel-json "$DD/nd-unfolding/pv-ladder/readouts/cmodel_5d.json" --flux-constraint "$CONSTRAINT" \\
    --truth "$T" --out "$W/null-$T.json" < /dev/null > "$W/null-$T.out" 2> "$W/null-$T.time"; s=$?
  echo "null $T rc=$s: $(tail -1 "$W/null-$T.out")"
  python3 -B - "$W/null-$T.json" "$W/null-$T.invalid.json" "$W/expected_moved_$T.txt" "$s" "$T" <<'CHECK'
import json, os, sys
rec_p, inv_p, exp_p, rc, T = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
exp = sorted(l for l in open(exp_p).read().splitlines() if l)
p = rec_p if os.path.exists(rec_p) else inv_p if os.path.exists(inv_p) else None
if p is None:
    print(f"NULL-EXIT {{T}} NOT-CLEAN rc={{rc}}: no record; to the director unrepaired"); sys.exit(1)
rec = json.load(open(p))
moved = sorted(rec.get("atime", {{}}).get("moved", []))
extra, missing = sorted(set(moved) - set(exp)), sorted(set(exp) - set(moved))
print(f"null {{T}}: record {{os.path.basename(p)}} verdict {{rec.get('verdict')}} moved {{len(moved)}} expected {{len(exp)}} "
      f"extra {{len(extra)}} {{extra[:5]}} missing {{len(missing)}} {{missing[:5]}}")
ok = rc == 8 and p == rec_p and rec.get("verdict") == "PASS" and not extra and not missing
print(f"NULL-EXIT {{T}} " + ("CLEAN: rc 8, verdict PASS, moved == the fixed set (the declared deviation)" if ok else
      f"NOT-CLEAN rc={{rc}}: to the director unrepaired; nothing is read from this null"))
sys.exit(0 if ok else 1)
CHECK
  c=$?; urc=$((urc | c))
done
sha256sum "$W"/null-*.json "$W"/null-*.out "$W"/expected_moved_*.txt 2>/dev/null
grep -h -E "Elapsed|Maximum resident|Exit status" "$W"/null-*.time
echo "null checks rc=$urc"
echo "end=$(date -u +%FT%TZ)"
exit $urc
"""
s = s[:j0] + JOB + s[j1:]
rep('echo "job script sha256 $(sha256sum "$W/sbatch-ll5d-rerun129.sh" | cut -d\' \' -f1)"',
    'echo "job script sha256 $(sha256sum "$W/sbatch-ll5d-null.sh" | cut -d\' \' -f1)"')
# 6. after atime-pre: the declared-input coverage check (the null's declared inputs, not a directory walk)
rep('echo "atime-pre $(wc -l < "$W/atime-pre.tsv") files at $(date -u +%FT%TZ)"\n',
    'echo "atime-pre $(wc -l < "$W/atime-pre.tsv") files at $(date -u +%FT%TZ)"\n'
    'python3 - "$W/atime-pre.tsv" "$STAGED" "$CONSTRAINT" "$DD" "$U" "$W/u-names.txt" <<\'COVER\' || stop "a declared protected input is not in atime-pre"\n'
    '# The null\'s declared inputs (ll5d_b.setup, remade, made_from at 4231b14d): the staged S1 assembly and the flux\n'
    '# constraint (protected: each must be in atime-pre), the deploy\'s definition and cmodel json, and the $U products\n'
    '# of the two truths\' central/seed/block/stat roles (LL5D\'s own outputs). Classified by path against atime-pre.\n'
    'import os, sys\n'
    'pre = {l.split("\\t", 1)[1] for l in open(sys.argv[1]).read().splitlines()}\n'
    'staged, constraint, dd, U = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5].rstrip("/")\n'
    'prot = [f"{staged}/s1/s1_assembly.npz", constraint]\n'
    'deploy = [f"{dd}/nd-unfolding/pv-ladder/readouts/h2_definition.json", f"{dd}/nd-unfolding/pv-ladder/readouts/cmodel_5d.json"]\n'
    'prods = [f"{U}/{n}" for n in open(sys.argv[6]).read().split() if n.split("_")[1:2] in (["g18"], ["ar23"])\n'
    '         and n.split("_")[2:3] and n.split("_")[2] in ("central", "seed", "block", "stat") and n.endswith(".npz")]\n'
    'missing = [p for p in prot + deploy if not os.path.exists(p)]\n'
    'print(f"declared inputs: protected {len(prot)} (in atime-pre: {sum(p in pre for p in prot)}), deploy {len(deploy)} "\n'
    '      f"(in atime-pre: {sum(p in pre for p in deploy)}), products {len(prods)} (in atime-pre: {sum(p in pre for p in prods)}), missing {missing}")\n'
    'sys.exit(0 if all(p in pre for p in prot) and not missing and not any(p in pre for p in deploy + prods) else 1)\n'
    'COVER\n')
# 7. submission
rep('-J "ll5d_rerun129_$NN" \\\n    -o "$W/logs/%x_%j.out" "$W/sbatch-ll5d-rerun129.sh" "$DD" "$M" "$W" "$UO" "$NN")',
    '-J "ll5d_null_$NN" \\\n    -o "$W/logs/%x_%j.out" "$W/sbatch-ll5d-null.sh" "$DD" "$M" "$W" "$U" "$NN")')
s = s.replace('stop "sbatch for ll5d_rerun129_$NN returned no id', 'stop "sbatch for ll5d_null_$NN returned no id')
s = s.replace('(ll5d_rerun129_$NN)"', '(ll5d_null_$NN)"')
rep('[ "$tl" = "TimeLimit=02:30:00" ] || { scancel "${ids[@]}"; stop "ll5d_rerun129_$NN\'s time limit parsed as ${tl#TimeLimit=}, not 02:30:00: cancelled ${ids[*]}"; }',
    '[ "$tl" = "TimeLimit=01:00:00" ] || { scancel "${ids[@]}"; stop "ll5d_null_$NN\'s time limit parsed as ${tl#TimeLimit=}, not 01:00:00: cancelled ${ids[*]}"; }')
rep("squeue --me -h -o '%i %j %T %l %D' | grep ll5d_rerun129_", "squeue --me -h -o '%i %j %T %l %D' | grep ll5d_null_")
for bad in ("rerun129", "$UO", "$BW", "LANESHA"):
    assert bad not in s, f"{bad} survives"
(H / "connect-null.sh").write_text(s)
print("wrote", H / "connect-null.sh", hashlib.sha256(s.encode()).hexdigest())
