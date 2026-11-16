"""Derive connect-rerun129.sh from connect-bulk.sh (163c6269, the bulk connect that ran) by explicit replacements.
Each replacement must match exactly once; the item list is never retyped (the job takes it from the bulk's pinned
bulk-lanes.tsv, node 09 lane 4). Writes connect-rerun129.sh next to this file.
    python3 -I make_connect.py
"""
import hashlib
from pathlib import Path

H = Path(__file__).resolve().parent
SRC = H.parent / "connect-bulk.sh"
s = SRC.read_text()
assert hashlib.sha256(s.encode()).hexdigest().startswith("163c6269"), "connect-bulk.sh is not 163c6269"
lines = s.split("\n")


def rep(old: str, new: str) -> None:
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"{n} matches for: {old[:90]!r}")
    s = s.replace(old, new)


# 1. header (lines 2-13 of the bulk connect)
head_old = "\n".join(lines[1:13]) + "\n"
head_new = """# LL5D bulk: the rc-129 rerun (the director's ruling 2, 2026-11-14, under LL5D-DECLARATION.md:70), DRAFT for the
# director's review. ll5d_bulk_09's lane 4 (ar23 toy all_4761060 ... all_4761079) exited 129: its 20 products were
# written, then ROOT segfaulted while Python exited. This reruns that call's 20 items once, unchanged: ONE job (-N 1 --exclusive,
# --time 02:30:00, 2.5 node-h) of 4 lanes of 5 items (the director's revision: the bulk ran 8 such lanes a node), each
# lane one srun step (32 CPUs, 56G, --threads 32), the same bound code (M, bound.sha256) and the
# same WORLD inputs, on a FRESH deploy clone at M that no other job reads, into a FRESH out directory $UO outside $U.
# The 20 items are taken from the bulk's pinned partition (bulk-lanes.tsv, node 09 lane 4), never retyped, and must
# be exactly the 20 names already in $U. Nothing under $U is written, moved or deleted. One job means its single start
# check (sha256sum -c) runs before all 4 calls, so the bulk's rc-8 mechanism (a later job's start check moving the
# deploy manifest under a running call) cannot occur. The comparison with $U's 20 products is a separate step
# (compare_rerun.py), after the job ends. Submitted only after the director's go on this file's sha256. Nothing to CFS.
# Not under set -u.
"""
rep(head_old, head_new)
# 2. namespaces and price
rep("W=$P/ll5d-bulk-r1; DD=$W/deploy; U=$P/ll5d-unfolds-r2; PW=$P/ll5d-pilot-r2   # the pilot's r2 namespace",
    "W=$P/ll5d-rerun129-r1; DD=$W/deploy; U=$P/ll5d-unfolds-r2; PW=$P/ll5d-pilot-r2   # $U is read-only here (names)\n"
    "UO=$P/ll5d-unfolds-rerun129-r1   # the rerun's fresh out directory (refused if it exists)\n"
    "BW=$P/ll5d-bulk-r1               # the bulk's namespace: its pinned bulk-lanes.tsv is read (plainly; not an LL5D input)\n"
    "FIGMARK=$P/note-figstyle-20261114/RUNNING   # director-helper-2's group C figure connects hold this while they run")
rep('CAP=148.0; THIS=80.0; TL=08:00:00; NODES="01 02 03 04 05 06 07 08 09 10"',
    'CAP=148.0; THIS=2.5; TL=02:30:00; NODES="01"   # 4 lanes of 5: 5 x 1,062 s = 5,310 s + setup < 9,000 s')
# 3. fence additions, after the bulk's ll5d_ line
rep("""[ "$(squeue --me -h -o %j | grep -c '^ll5d_')" = "0" ] || stop "an ll5d_ job is queued or running"\n""",
    """[ "$(squeue --me -h -o %j | grep -c '^ll5d_')" = "0" ] || stop "an ll5d_ job is queued or running"
[ "$(squeue --me -h -o %j | grep -c '^cov2dg2r-')" = "0" ] || stop "a cov2dg2r- job is queued or running"
[ -e "$FIGMARK" ] && stop "a group C figure connect is running (or left its marker): $(head -c 300 "$FIGMARK")"
echo "group C marker absent: $FIGMARK"
[ -e "$UO" ] && stop "$UO exists"
""")
# 4. products: $U holds the bulk's 1662, the 20 among them; no count-13 check
rep("""k=$(ls "$U" | grep -c '\\.npz$'); echo "products before the bulk: $k"
[ "$k" = "13" ] || stop "the products directory does not hold exactly the pilot's 13 products"
""", """k=$(ls "$U" | grep -c '\\.npz$'); echo "products in \\$U: $k"
[ "$k" = "1662" ] || stop "\\$U does not hold the bulk's 1662 products"
[ "$(sha256sum "$BW/bulk-lanes.tsv" | cut -d' ' -f1)" = "$LANESHA" ] || stop "the bulk's bulk-lanes.tsv is not the pinned partition"
awk -F'\\t' '$1 == "09" && $2 == "4"' "$BW/bulk-lanes.tsv" > "$W/bulk-09-4.tsv"
[ "$(awk 'END {print NR}' "$W/bulk-09-4.tsv")" = "1" ] || stop "bulk-lanes.tsv does not hold exactly one node 09 lane 4 row"
# the director's split: consecutive slices of 5 in the row's own order (items 1-5, 6-10, 11-15, 16-20) -> lanes 0-3
awk -F'\\t' '{n = split($5, a, ","); if (n != 20) exit 3; for (l = 0; l < 4; l++) {s = a[5*l+1]; for (j = 2; j <= 5; j++) s = s "," a[5*l+j]; print "01\\t" l "\\t" $3 "\\t" $4 "\\t" s}}' \\
  "$W/bulk-09-4.tsv" > "$W/rerun-lanes.tsv" || stop "the node 09 lane 4 row does not hold 20 items"
[ "$(awk 'END {print NR}' "$W/rerun-lanes.tsv")" = "4" ] || stop "the split did not give 4 lanes"
[ "$(cut -f5 "$W/rerun-lanes.tsv" | paste -sd, -)" = "$(cut -f5 "$W/bulk-09-4.tsv")" ] || stop "the 4 slices, joined in order, are not the row"
[ "$(cut -f5 "$W/rerun-lanes.tsv" | tr ',' '\\n' | sort -u | awk 'END {print NR}')" = "20" ] || stop "the 4 slices are not 20 distinct items"
while IFS=$'\\t' read -r nd l t r its; do echo "rerun lane: $nd $l $t $r items=$(echo "$its" | tr ',' '\\n' | awk 'END {print NR}') $its"; done < "$W/rerun-lanes.tsv"
n20=0; for it in $(cut -f5 "$W/rerun-lanes.tsv" | tr ',' ' '); do
  [ -e "$U/ll5d_ar23_toy_$it.npz" ] || stop "$U/ll5d_ar23_toy_$it.npz is not there"; n20=$((n20 + 1)); done
[ "$n20" = "20" ] || stop "the lanes hold $n20 items, not 20"
echo "the 20 items are in \\$U (names only; nothing there is opened)"
# the overlap check: none of the 18 G2R inputs is, or lies under, a WORLD path (realpath and device:inode)
python3 - "$ND" "$P" <<'OVL' || stop "a WORLD path overlaps a G2R input"
import os, sys
nd, p = sys.argv[1], sys.argv[2]
world = [f"{nd}/of_inputs_5d.npz", f"{p}/s5c-20260924/runs/p2/bkg_dump.npz", f"{nd}/bank_sweep_5d_bkgaware",
         f"{p}/s5p-20260926/bank_detector", f"{p}/fd-1b-20261030/pins.json",
         f"{p}/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt",
         f"{p}/fd-1b-staged-20261102/stage1/in/flux_universes.npz", f"{p}/fd-f1-20261027/f1b3/prep"]
d2 = f"{p}/MINERvA-OmniFold/2d-unfolding"
g2r = [f"{d2}/runEventLoopOmniFold_{x}_universes_full.root" for x in
       ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P", "MEFHC")]
g2r += [f"{d2}/baseline_flux/runEventLoopMC_MEFHC.root", f"{d2}/baseline_flux/flux_integral_universes_MEFHC.root",
        f"{p}/cov2d-g2r-20261112/prepare/g2r_map.npz", f"{p}/cov2d-run-20261104/pseudo/G18/b/data_5721000.root",
        f"{p}/cov2d-run-20261104/pseudo/AR23-a2/b/data_5731000.root"]
assert len(world) == 8 and len(g2r) == 18
ino = lambda x: (os.stat(x).st_dev, os.stat(x).st_ino)
hits = []
for w in world:
    rw = os.path.realpath(w)
    for g in g2r:
        rg = os.path.realpath(g)
        if rg == rw or rg.startswith(rw.rstrip("/") + "/") or (os.path.isfile(w) and os.path.exists(g) and ino(w) == ino(g)):
            hits.append((w, g))
print(f"overlap check: {len(world)} WORLD paths x {len(g2r)} G2R inputs, hits {hits}")
sys.exit(1 if hits else 0)
OVL
""")
# 5. partition: no embedded full partition (the rerun row comes from the bulk's pinned file above)
p0 = s.index("""cat > "$W/bulk-lanes.tsv" <<'LANES'\n""")
p1 = s.index("""[ "$(sha256sum "$W/bulk-lanes.tsv" | cut -d' ' -f1)" = "$LANESHA" ] || stop "bulk-lanes.tsv is not the pinned partition"\n""")
p1e = s.index("\n", p1) + 1
s = s[:p0] + s[p1e:]
# 6. the job script
rep("""cat > "$W/sbatch-ll5d-bulk.sh" <<'JOB'""", """cat > "$W/sbatch-ll5d-rerun129.sh" <<'JOB'""")
rep("""# ll5d_bulk_<NN>'s job: 8 lanes, each an srun step (32 CPUs, 56G, --threads 32); the deploy at M with porcelain 0 and the bound blobs; the
# partition asserted against ll5d_b; this node's 8 lanes (ll5d_b.py unfold, one truth and role per call). Not under
# set -u. Writes only under $W and $U.
DD=$1; M=$2; W=$3; U=$4; NODE=$5""",
    """# ll5d_rerun129_01's job: 4 lanes of 5 items, each an srun step (32 CPUs, 56G, --threads 32); the deploy at M with
# porcelain 0 and the bound blobs, checked ONCE here, before all 4 calls; the lanes asserted against ll5d_b; 4 ll5d_b.py
# unfold calls (ar23 toy, 5 items each, the 20 between them). Not under set -u. Writes only under $W and $UO (passed as the 4th argument).
DD=$1; M=$2; W=$3; U=$4; NODE=$5   # here U is $UO, the fresh out directory""")
rep('echo "lanes 8 x (srun --exact -n1 -c 32 --mem 56G) --threads 32"',
    'echo "lanes 4 x (srun --exact -n1 -c 32 --mem 56G) --threads 32"')
rep("""python3 -B - "$DD/nd-unfolding" "$W/bulk-lanes.tsv" <<'PY' || stop "the partition is not section 9's bulk\"""",
    """python3 -B - "$DD/nd-unfolding" "$W/rerun-lanes.tsv" <<'PY' || stop "the row is not the bulk's node 09 lane 4\"""")
rep("""want = {(t, r, i) for t in ll5d_b.TRUTHS for r, i in ll5d_b.items(t)} - set(ll5d_b.PILOT)
print(f"items={len(got)} unique={len(set(got))} want={len(want)} lanes={len(per_lane)} max_per_lane={max(per_lane.values())}")
sys.exit(0 if len(got) == len(set(got)) and set(got) == want and max(per_lane.values()) <= 22 and len(per_lane) == 80 else 1)""",
    """want = {(t, r, i) for t in ll5d_b.TRUTHS for r, i in ll5d_b.items(t)} - set(ll5d_b.PILOT)
print(f"items={len(got)} unique={len(set(got))} in_section9_bulk={set(got) <= want} lanes={len(per_lane)} truth_role={sorted({(t, r) for t, r, _ in got})}")
sys.exit(0 if len(got) == 20 and len(set(got)) == 20 and set(got) <= want and len(per_lane) == 4 and set(per_lane.values()) == {5}
         and {(t, r) for t, r, _ in got} == {("ar23", "toy")} else 1)""")
rep("""  done 3< <(grep -v '^#' "$W/bulk-lanes.tsv")""", """  done 3< <(grep -v '^#' "$W/rerun-lanes.tsv")""")
rep("""pids=(); for L in 0 1 2 3 4 5 6 7; do lane $L & pids+=($!); done
urc=0; for k in 0 1 2 3 4 5 6 7; do wait ${pids[$k]}; s=$?; echo "lane $k rc=$s"; urc=$((urc | s)); done
echo "unfold lanes rc=$urc\"""",
    """pids=(); for L in 0 1 2 3; do lane $L & pids+=($!); done
urc=0; for k in 0 1 2 3; do wait ${pids[$k]}; s=$?; echo "lane $k rc=$s"; urc=$((urc | s)); done
echo "unfold lanes rc=$urc"
case "$urc" in
  0) echo "RERUN-EXIT clean rc=0" ;;
  8) echo "RERUN-EXIT rc=8: ll5d_b's atime sidecar lists a move; to the director with the sidecar, nothing graded until explained" ;;
  *) echo "RERUN-EXIT NOT-CLEAN rc=$urc: to the director unrepaired; nothing graded even if the comparison is equal" ;;
esac""")
rep('exec >> "$W/logs/connect-bulk.log" 2>&1', 'exec >> "$W/logs/connect-rerun129.log" 2>&1')
rep("""SUMS
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
""", """SUMS
[ "$(sha256sum "$W/bound.sha256" | cut -d' ' -f1)" = "7540b2de8f2de64f25d62497abe91a6a04fc7cf6cb18379e624422afb32c52b3" ] || stop "bound.sha256 is not the bulk's 22-line list 7540b2de"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
""")
# 7. submission
rep('''echo "job script sha256 $(sha256sum "$W/sbatch-ll5d-bulk.sh" | cut -d' ' -f1)"''',
    '''echo "job script sha256 $(sha256sum "$W/sbatch-ll5d-rerun129.sh" | cut -d' ' -f1)"''')
rep('''  jid=$(sbatch --parsable -A m3246 -q regular -C cpu -N 1 --exclusive --no-requeue -t "$TL" -J "ll5d_bulk_$NN" \\
    -o "$W/logs/%x_%j.out" "$W/sbatch-ll5d-bulk.sh" "$DD" "$M" "$W" "$U" "$NN")''',
    '''  jid=$(sbatch --parsable -A m3246 -q regular -C cpu -N 1 --exclusive --no-requeue -t "$TL" -J "ll5d_rerun129_$NN" \\
    -o "$W/logs/%x_%j.out" "$W/sbatch-ll5d-rerun129.sh" "$DD" "$M" "$W" "$UO" "$NN")''')
s = s.replace('stop "sbatch for ll5d_bulk_$NN returned no id', 'stop "sbatch for ll5d_rerun129_$NN returned no id')
s = s.replace('(ll5d_bulk_$NN)"', '(ll5d_rerun129_$NN)"')
rep('''  [ "$tl" = "TimeLimit=08:00:00" ] || { scancel "${ids[@]}"; stop "ll5d_bulk_$NN's time limit parsed as ${tl#TimeLimit=}, not 08:00:00: cancelled ${ids[*]}"; }''',
    '''  [ "$tl" = "TimeLimit=02:30:00" ] || { scancel "${ids[@]}"; stop "ll5d_rerun129_$NN's time limit parsed as ${tl#TimeLimit=}, not 02:30:00: cancelled ${ids[*]}"; }''')
rep("""squeue --me -h -o '%i %j %T %l %D' | grep ll5d_bulk_""", """squeue --me -h -o '%i %j %T %l %D' | grep ll5d_rerun129_""")
assert "ll5d_bulk_" not in s.split("cat > \"$W/sbatch-ll5d-rerun129.sh\"")[1], "a bulk job name survives after the job script"
(H / "connect-rerun129.sh").write_text(s)
print("wrote", H / "connect-rerun129.sh", hashlib.sha256(s.encode()).hexdigest())
