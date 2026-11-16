"""Derive connect-readout.sh from ../null/connect-null.sh (87aa0b65, the approved null connect) by explicit
replacements, each matching exactly once. Writes connect-readout.sh beside this file.
    python3 -I make_readout_connect.py
"""
import hashlib
from pathlib import Path

H = Path(__file__).resolve().parent
SRC = H.parent / "null" / "connect-null.sh"
s = SRC.read_text()
assert hashlib.sha256(s.encode()).hexdigest().startswith("87aa0b65"), "the null connect is not 87aa0b65"
lines = s.split("\n")
NULL = {"g18": "73dbaf9517374646c719ff589015cb12c1a6a2eafd5579e1074ef700bde703c2",
        "ar23": "a0544ab9f6f0ec55c9866bee689d2563b13c9d07f4b3fdc37ce4762718a23933"}
PDIG = {"g18": "c16e9ce045ed255dda49c8031ca6769cf4285d25fd8f5b3fe86d5a2f8d8508a9",
        "ar23": "b716657b59b0169d50cf5ea2283c353fb4f7b9228ba041d5b54d2c40af796b43"}


def rep(old: str, new: str) -> None:
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"{n} matches for: {old[:100]!r}")
    s = s.replace(old, new)


# 1. header (the null connect's lines 2-13)
rep("\n".join(lines[1:13]) + "\n", """# LL5D section 11 step 7: the readout at G18 and AR23 (ll5d_b.py readout, one call per truth, both readings inside),
# DRAFT for the director's review. Inputs, each pinned: the null records of job 61271235 (null-<T>.json, sha256 below;
# receipts-ll5d/null), the pilot's clipcheck.json (CLIPSHA), each truth's gate-2 record (G18GATE, AR23GATE), and the
# bulk's products in $U, unchanged since the null (1662, no partials, 300 toys per reading per truth). At 4231b14d the
# readout's only plain reads are products_digest (ll5d_b.py:660, BEFORE its first watched product open at :670) and the
# deploy's definition and cmodel json, which are not watched; every watched read goes through O_NOATIME. So the expected
# atime-moved set is EMPTY. CLEAN per truth = rc 0, the record readout-<T>.json (not .invalid.json), and atime.moved == [].
# Anything else is NOT-CLEAN and goes to the director unrepaired. The :660 check refuses unless the products' digest
# equals the null's products_sha256 (g18 c16e9ce0…, ar23 b716657b…). ONE job (-N 1 --exclusive, --time 01:00:00,
# 1.0 node-h) on a FRESH deploy clone at M; its single start check runs before both calls, which run one after the
# other (B1). Writes only under $W; $U, the null records, clipcheck and the gate records are read. Not under set -u.
""")
# 2. namespaces and pins
rep("W=$P/ll5d-null-r1; DD=$W/deploy; U=$P/ll5d-unfolds-r2; PW=$P/ll5d-pilot-r2   # $U: the bulk's 1662 products, read\n",
    "W=$P/ll5d-readout-r1; DD=$W/deploy; U=$P/ll5d-unfolds-r2; PW=$P/ll5d-pilot-r2   # $U: the bulk's 1662 products, read\n"
    f"NW=$P/ll5d-null-r1   # the null's namespace: null-g18.json, null-ar23.json (job 61271235)\n"
    f"NULLG18={NULL['g18']}   # null-g18.json (receipts-ll5d/null)\n"
    f"NULLAR23={NULL['ar23']}  # null-ar23.json\n")
rep('for v in "$G18GATE" "$AR23GATE" "$WALLSSHA" "$CLIPSHA" "$CTLSHA" "$L5" "$CMODELSHA"; do',
    'for v in "$G18GATE" "$AR23GATE" "$WALLSSHA" "$CLIPSHA" "$CTLSHA" "$L5" "$CMODELSHA" "$NULLG18" "$NULLAR23"; do')
rep('exec >> "$W/logs/connect-null.log" 2>&1', 'exec >> "$W/logs/connect-readout.log" 2>&1')
# 3. after the products count: $U unchanged since the null (no partials; the toys complete), the null records pinned
rep('[ "$k" = "1662" ] || stop "\\$U does not hold the bulk\'s 1662 products"\n',
    '[ "$k" = "1662" ] || stop "\\$U does not hold the bulk\'s 1662 products"\n'
    '[ "$(ls "$U" | grep -c \'\\.partial-\')" = "0" ] || stop "partial products are present in \\$U"\n'
    'for T in g18 ar23; do for RD in all minus2; do\n'
    '  nt=$(ls "$U" | grep -c "^ll5d_${T}_toy_${RD}_[0-9]*\\.npz$"); echo "toys $T/$RD: $nt"\n'
    '  [ "$nt" = "300" ] || stop "$T/$RD holds $nt toy products, not 300"; done; done\n'
    '[ "$(sha256sum "$NW/null-g18.json" | cut -d\' \' -f1)" = "$NULLG18" ] || stop "null-g18.json is not the receipted record"\n'
    '[ "$(sha256sum "$NW/null-ar23.json" | cut -d\' \' -f1)" = "$NULLAR23" ] || stop "null-ar23.json is not the receipted record"\n'
    'echo "null records OK: g18 $NULLG18 ar23 $NULLAR23"\n')
rep("cat > \"$W/sbatch-ll5d-null.sh\" <<'JOB'", "cat > \"$W/sbatch-ll5d-readout.sh\" <<'JOB'")
# 4. the job script body
j0 = s.index("# ll5d_null_01's job:")
j1 = s.index("exit $urc\nJOB\n") + len("exit $urc\n")
JOB = f"""# ll5d_readout_01's job: the deploy at M with porcelain 0 and the bound blobs, checked ONCE here, before both calls; then
# ll5d_b.py readout for g18, then for ar23, one after the other; after each, its record checked (rc 0, no atime move).
# Not under set -u. Writes only under $W.
DD=$1; M=$2; W=$3; U=$4; NODE=$5
P=/pscratch/sd/j/josephrb; STAGED=$P/fd-1b-inv-20261101/i0/in; NW=$P/ll5d-null-r1; PW=$P/ll5d-pilot-r2
CONSTRAINT=$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
NULL_g18={NULL['g18']}; NULL_ar23={NULL['ar23']}
GATE_g18=a5d66b7e506a98d5a0b555dbe171aa6c1e931eb93df793c3e515d7d44466fc70; GW_g18=$P/ll5d-gate-2-g18-20261110
GATE_ar23=35a20c471cb06f428c49daaaebfc6646babb7f7fb060039d4c63139da51d0a4c; GW_ar23=$P/ll5d-gate-2-ar23-20261110
CLIPSHA=9632540ecd0d25e2223eedb480b96078459a6e6d75128b4e4132ea1bf644d3aa
stop() {{ echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }}
echo "host=$(hostname) job=$SLURM_JOB_ID node=$NODE start=$(date -u +%FT%TZ)"
h=$(git -C "$DD" rev-parse HEAD); n=$(git -C "$DD" status --porcelain | wc -l); echo "deploy head=$h porcelain_lines=$n"
[ "$h" = "$M" ] && [ "$n" = "0" ] || stop "deploy not clean at M"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
source "$DD/setup_salloc_env.sh" > "$W/logs/env-job-$NODE.log" 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
urc=0
for T in g18 ar23; do
  eval "ns=\\$NULL_$T; gs=\\$GATE_$T; gw=\\$GW_$T"
  /usr/bin/time -v python3 -B "$DD/nd-unfolding/ll5d_b.py" readout --staged "$STAGED" \\
    --definition "$DD/nd-unfolding/pv-ladder/readouts/h2_definition.json" --unfolds "$U" \\
    --cmodel-json "$DD/nd-unfolding/pv-ladder/readouts/cmodel_5d.json" --flux-constraint "$CONSTRAINT" --truth "$T" \\
    --null "$NW/null-$T.json" --expect-null-sha256 "$ns" --clipcheck "$PW/clipcheck.json" --expect-clipcheck-sha256 "$CLIPSHA" \\
    --gate "$gw/gate-$T.json" --expect-gate-sha256 "$gs" --out "$W/readout-$T.json" < /dev/null > "$W/readout-$T.out" 2> "$W/readout-$T.time"; s=$?
  echo "readout $T rc=$s: $(tail -1 "$W/readout-$T.out")"
  python3 -B - "$W/readout-$T.json" "$W/readout-$T.invalid.json" "$s" "$T" <<'CHECK'
import json, os, sys
rec_p, inv_p, rc, T = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
p = rec_p if os.path.exists(rec_p) else inv_p if os.path.exists(inv_p) else None
if p is None:
    print(f"READOUT-EXIT {{T}} NOT-CLEAN rc={{rc}}: no record; to the director unrepaired"); sys.exit(1)
rec = json.load(open(p))
moved = rec.get("atime", {{}}).get("moved", [])
print(f"readout {{T}}: record {{os.path.basename(p)}} verdicts {{rec.get('verdicts')}} moved {{len(moved)}} {{moved[:5]}}")
ok = rc == 0 and p == rec_p and moved == [] and "evaluations" in rec
print(f"READOUT-EXIT {{T}} " + ("CLEAN: rc 0, record written, atime.moved []" if ok else
      f"NOT-CLEAN rc={{rc}}: to the director unrepaired"))
sys.exit(0 if ok else 1)
CHECK
  c=$?; urc=$((urc | c))
done
sha256sum "$W"/readout-*.json "$W"/readout-*.out 2>/dev/null
grep -h -E "Elapsed|Maximum resident|Exit status" "$W"/readout-*.time
echo "readout checks rc=$urc"
echo "end=$(date -u +%FT%TZ)"
exit $urc
"""
s = s[:j0] + JOB + s[j1:]
rep('echo "job script sha256 $(sha256sum "$W/sbatch-ll5d-null.sh" | cut -d\' \' -f1)"',
    'echo "job script sha256 $(sha256sum "$W/sbatch-ll5d-readout.sh" | cut -d\' \' -f1)"')
# 5. the declared-input coverage check: the readout's inputs are the null's plus the toys, the null records,
#    clipcheck and the gate records (none protected)
rep('python3 - "$W/atime-pre.tsv" "$STAGED" "$CONSTRAINT" "$DD" "$U" "$W/u-names.txt" <<\'COVER\' || stop "a declared protected input is not in atime-pre"\n',
    'python3 - "$W/atime-pre.tsv" "$STAGED" "$CONSTRAINT" "$DD" "$U" "$W/u-names.txt" "$NW" "$PW" "$G18W" "$AR23W" <<\'COVER\' || stop "a declared protected input is not in atime-pre"\n')
rep("# The null's declared inputs (ll5d_b.setup, remade, made_from at 4231b14d): the staged S1 assembly and the flux\n"
    "# constraint (protected: each must be in atime-pre), the deploy's definition and cmodel json, and the $U products\n"
    "# of the two truths' central/seed/block/stat roles (LL5D's own outputs). Classified by path against atime-pre.\n",
    "# The readout's declared inputs (ll5d_b.readout, setup, remade, toy_errors, gate_ratios at 4231b14d): the staged S1\n"
    "# assembly and the flux constraint (protected: each must be in atime-pre); the deploy's definition and cmodel json;\n"
    "# the $U products of the two truths' central/seed/block/stat AND toy roles; the null records, clipcheck and the gate\n"
    "# records. Only the first two may be in atime-pre. Classified by path against atime-pre.\n")
rep('deploy = [f"{dd}/nd-unfolding/pv-ladder/readouts/h2_definition.json", f"{dd}/nd-unfolding/pv-ladder/readouts/cmodel_5d.json"]\n',
    'deploy = [f"{dd}/nd-unfolding/pv-ladder/readouts/h2_definition.json", f"{dd}/nd-unfolding/pv-ladder/readouts/cmodel_5d.json"]\n'
    'nw, pw, g18w, ar23w = sys.argv[7:11]\n'
    'deploy += [f"{nw}/null-g18.json", f"{nw}/null-ar23.json", f"{pw}/clipcheck.json", f"{g18w}/gate-g18.json", f"{ar23w}/gate-ar23.json"]\n')
rep('n.split("_")[2] in ("central", "seed", "block", "stat") and n.endswith(".npz")]\n',
    'n.split("_")[2] in ("central", "seed", "block", "stat", "toy") and n.endswith(".npz")]\n')
# 6. submission
rep('-J "ll5d_null_$NN" \\\n    -o "$W/logs/%x_%j.out" "$W/sbatch-ll5d-null.sh" "$DD" "$M" "$W" "$U" "$NN")',
    '-J "ll5d_readout_$NN" \\\n    -o "$W/logs/%x_%j.out" "$W/sbatch-ll5d-readout.sh" "$DD" "$M" "$W" "$U" "$NN")')
s = s.replace('stop "sbatch for ll5d_null_$NN returned no id', 'stop "sbatch for ll5d_readout_$NN returned no id')
s = s.replace('(ll5d_null_$NN)"', '(ll5d_readout_$NN)"')
rep('[ "$tl" = "TimeLimit=01:00:00" ] || { scancel "${ids[@]}"; stop "ll5d_null_$NN\'s time limit',
    '[ "$tl" = "TimeLimit=01:00:00" ] || { scancel "${ids[@]}"; stop "ll5d_readout_$NN\'s time limit')
rep("squeue --me -h -o '%i %j %T %l %D' | grep ll5d_null_", "squeue --me -h -o '%i %j %T %l %D' | grep ll5d_readout_")
for bad in ("ll5d_null_", "connect-null.log", "sbatch-ll5d-null", "EXP_g18", "expected_moved"):
    assert bad not in s, f"{bad} survives"
(H / "connect-readout.sh").write_text(s)
print("wrote", H / "connect-readout.sh", hashlib.sha256(s.encode()).hexdigest())
