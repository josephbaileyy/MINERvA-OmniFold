#!/bin/bash
# LL5D bulk: the rc-129 rerun (the director's ruling 2, 2026-11-14, under LL5D-DECLARATION.md:70), DRAFT for the
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
M=4231b14de5ea693e92cb31b1358a816b5c2f6625         # M_A1b.1 (LL5D-BINDING-3.md addendum A1b.1): the merge that carries ll5d_ctl.py
L5=2b0224c6fe52c5bb2d3fe64d461ac9edb80ebd191b0ab2f892dec605a0b56a14        # ll5d.py's sha256 at M
P=/pscratch/sd/j/josephrb; ND=$P/MINERvA-OmniFold/nd-unfolding
W=$P/ll5d-rerun129-r1; DD=$W/deploy; U=$P/ll5d-unfolds-r2; PW=$P/ll5d-pilot-r2   # $U is read-only here (names)
UO=$P/ll5d-unfolds-rerun129-r1   # the rerun's fresh out directory (refused if it exists)
BW=$P/ll5d-bulk-r1               # the bulk's namespace: its pinned bulk-lanes.tsv is read (plainly; not an LL5D input)
FIGMARK=$P/note-figstyle-20261114/RUNNING   # director-helper-2's group C figure connects hold this while they run
G18W=$P/ll5d-gate-2-g18-20261110; AR23W=$P/ll5d-gate-2-ar23-20261110
G18GATE=a5d66b7e506a98d5a0b555dbe171aa6c1e931eb93df793c3e515d7d44466fc70   # sha256 of gate-g18.json (receipts-ll5d/gate-2-g18/node-sha256.txt)
AR23GATE=35a20c471cb06f428c49daaaebfc6646babb7f7fb060039d4c63139da51d0a4c  # sha256 of gate-ar23.json (receipts-ll5d/gate-2-ar23/node-sha256.txt)
WALLSSHA=9377977cc9ea330522291363899e6a9a7f233ef71469f46fca184421bbe81e48  # sha256 of the pilot's walls.json (#1123, ll5d_pilot_61184880.out.txt)
CLIPSHA=9632540ecd0d25e2223eedb480b96078459a6e6d75128b4e4132ea1bf644d3aa   # sha256 of the pilot's clipcheck.json (#1123)
CTLSHA=82cc5858263164d7f5dc5977730484c385d960a1bb135208bd5b1f208e9cf2ec    # sha256 of the pilot's controls.json (#1123; amendment A1b.1, ll5d_ctl.py)
AUDITACK=https://github.com/josephbaileyy/MINERvA-OmniFold/pull/1123#issuecomment-6840388077   # coverage-5b-audit's GO (2026-11-13T00:48:18Z)
LANESHA=315f004bb6869345400dd87f3bee2d31f380713492e33ce3c5a7582a6c41ede7
CAP=148.0; THIS=2.5; TL=02:30:00; NODES="01"   # 4 lanes of 5: 5 x 1,062 s = 5,310 s + setup < 9,000 s
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
for v in "$G18GATE" "$AR23GATE" "$WALLSSHA" "$CLIPSHA" "$CTLSHA" "$L5" "$LANESHA"; do [[ $v =~ ^[0-9a-f]{64}$ ]] || { echo "STOP a placeholder is not filled"; exit 2; }; done
[[ $M =~ ^[0-9a-f]{40}$ ]] || { echo "STOP M is not filled"; exit 2; }
[[ $AUDITACK =~ ^https://github\.com/josephbaileyy/MINERvA-OmniFold/pull/[0-9]+#issuecomment-[0-9]+$ ]] || { echo "STOP the audit's acknowledgement is not filled"; exit 2; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir -p "$W/logs" || exit 2
exec >> "$W/logs/connect-rerun129.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ audit_ack=$AUDITACK"
echo "squeue: [$(squeue --me -h -o '%i %j %T %l %D' | tr '\n' ';')]"
[ "$(squeue --me -h -o %j | grep -c '^ll5d_')" = "0" ] || stop "an ll5d_ job is queued or running"
[ "$(squeue --me -h -o %j | grep -c '^cov2dg2r-')" = "0" ] || stop "a cov2dg2r- job is queued or running"
[ -e "$FIGMARK" ] && stop "a group C figure connect is running (or left its marker): $(head -c 300 "$FIGMARK")"
echo "group C marker absent: $FIGMARK"
[ -e "$UO" ] && stop "$UO exists"
[ "$(squeue --me -h -o %j | grep -cE '^(rsn_|e96data|rdx_)')" = "0" ] || stop "an rsn_, e96data or rdx_ job is queued or running"
# ^cov2d but not ^cov2dg2r-: COV2D-G2R reads no LL5D input outside O_NOATIME (overlap-fence.diff.txt); COV2D proper still refuses
cv=$(sacct -X -n -P -S 2026-11-04 -u josephrb -o JobID,JobName,State | awk -F'|' '$2 ~ /^cov2d/ && $2 !~ /^cov2dg2r-/ && $3 !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)/')
[ -z "$cv" ] || stop "a cov2d job is unended: $cv"
echo "== iris"; row=$(iris 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}'); [ -n "$bal" ] || stop "could not read the m3246 balance"
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') cap=$CAP"
awk -v b=$bal -v c=$CAP 'BEGIN{exit !(c <= b/2)}' || stop "the cap $CAP is above half the balance $bal: to Joseph"
charged=$(sacct -X -n -P -S 2026-11-08 -u josephrb -o JobName,State,ElapsedRaw,NNodes | awk -F'|' '$1 ~ /^ll5d_/ && $2 !~ /^(PENDING|RUNNING|REQUEUED|SUSPENDED)/ {s += $3 * $4} END {printf "%.3f", s / 3600}')
held=$(squeue --me -h -o '%j|%l|%D' | awk -F'|' '$1 ~ /^ll5d_/ {split($2, t, /[-:]/); n = length(t); s = (n == 4 ? t[1]*86400 + t[2]*3600 + t[3]*60 + t[4] : n == 3 ? t[1]*3600 + t[2]*60 + t[3] : t[1]*60 + t[2]); h += s * $3} END {printf "%.3f", h / 3600}')
proj=$(awk -v a=$charged -v b=$held -v c=$THIS 'BEGIN{printf "%.3f", a + b + c}')
echo "projection charged=$charged held=$held this=$THIS total=$proj cap=$CAP"
awk -v p=$proj -v c=$CAP 'BEGIN{exit !(p <= c)}' || stop "the projection $proj passes the cap $CAP"
# Section 11 step 6's preconditions, each by the receipted digest; only the named verdict fields are read.
for T in g18 ar23; do
  if [ $T = g18 ]; then GW=$G18W; GS=$G18GATE; else GW=$AR23W; GS=$AR23GATE; fi
  [ "$(sha256sum "$GW/gate-$T.json" | cut -d' ' -f1)" = "$GS" ] || stop "gate-$T.json's digest is not the receipt's"
  python3 -c 'import json,sys; g=json.load(open(sys.argv[1])); ok=g.get("truth")==sys.argv[2] and g.get("verdict")=="PASS"; print("gate", sys.argv[2], "truth=%s verdict=%s" % (g.get("truth"), g.get("verdict"))); sys.exit(0 if ok else 1)' "$GW/gate-$T.json" "$T" || stop "gate $T is not PASS"
done
for f in "walls.json|$WALLSSHA|PASS" "controls.json|$CTLSHA|PASS" "clipcheck.json|$CLIPSHA|PROCEED"; do
  IFS='|' read -r name want verdict <<< "$f"
  [ "$(sha256sum "$PW/$name" | cut -d' ' -f1)" = "$want" ] || stop "the pilot's $name digest is not the receipt's"
  python3 -c 'import json,sys; v=json.load(open(sys.argv[1])).get("verdict"); print(sys.argv[1], "verdict=%s" % v); sys.exit(0 if v==sys.argv[2] else 1)' "$PW/$name" "$verdict" || stop "the pilot's $name is not $verdict"
done
k=$(ls "$U" | grep -c '\.npz$'); echo "products in \$U: $k"
[ "$k" = "1662" ] || stop "\$U does not hold the bulk's 1662 products"
[ "$(sha256sum "$BW/bulk-lanes.tsv" | cut -d' ' -f1)" = "$LANESHA" ] || stop "the bulk's bulk-lanes.tsv is not the pinned partition"
awk -F'\t' '$1 == "09" && $2 == "4"' "$BW/bulk-lanes.tsv" > "$W/bulk-09-4.tsv"
[ "$(awk 'END {print NR}' "$W/bulk-09-4.tsv")" = "1" ] || stop "bulk-lanes.tsv does not hold exactly one node 09 lane 4 row"
# the director's split: consecutive slices of 5 in the row's own order (items 1-5, 6-10, 11-15, 16-20) -> lanes 0-3
awk -F'\t' '{n = split($5, a, ","); if (n != 20) exit 3; for (l = 0; l < 4; l++) {s = a[5*l+1]; for (j = 2; j <= 5; j++) s = s "," a[5*l+j]; print "01\t" l "\t" $3 "\t" $4 "\t" s}}' \
  "$W/bulk-09-4.tsv" > "$W/rerun-lanes.tsv" || stop "the node 09 lane 4 row does not hold 20 items"
[ "$(awk 'END {print NR}' "$W/rerun-lanes.tsv")" = "4" ] || stop "the split did not give 4 lanes"
[ "$(cut -f5 "$W/rerun-lanes.tsv" | paste -sd, -)" = "$(cut -f5 "$W/bulk-09-4.tsv")" ] || stop "the 4 slices, joined in order, are not the row"
[ "$(cut -f5 "$W/rerun-lanes.tsv" | tr ',' '\n' | sort -u | awk 'END {print NR}')" = "20" ] || stop "the 4 slices are not 20 distinct items"
while IFS=$'\t' read -r nd l t r its; do echo "rerun lane: $nd $l $t $r items=$(echo "$its" | tr ',' '\n' | awk 'END {print NR}') $its"; done < "$W/rerun-lanes.tsv"
n20=0; for it in $(cut -f5 "$W/rerun-lanes.tsv" | tr ',' ' '); do
  [ -e "$U/ll5d_ar23_toy_$it.npz" ] || stop "$U/ll5d_ar23_toy_$it.npz is not there"; n20=$((n20 + 1)); done
[ "$n20" = "20" ] || stop "the lanes hold $n20 items, not 20"
echo "the 20 items are in \$U (names only; nothing there is opened)"
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
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M" || stop clone
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
cat > "$W/bound.sha256" <<SUMS
$L5  nd-unfolding/ll5d.py
522d7edd71643df61d0c5ef5a7488834e664eb36d20c3e0c0b46e10a5808f02f  nd-unfolding/fd_1b_c2.py
936e1957d330e24d3eaab5f6c53d30b5be42a96f76daac07d527be97c0af30e2  nd-unfolding/fd_1b_mc.py
869a65c3bcce1a3b56ecd197ecdf3b6cf2741e0611f91b582c3064f67967bc08  nd-unfolding/fd_1b_toys.py
71b3903aa1329807af7e48b29b4ffd3336ad637d4b8c7e43ae0a6cbe28bcdf1f  nd-unfolding/fd_1b_inv.py
b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7  nd-unfolding/s1_assemble.py
805a00063a6136e25c6f8f57d228ec996c85a9bc997981632643baeee6c13d80  nd-unfolding/s5p_universe.py
c6c9a45fa93c6590c4fdf0d9b7d29f01cccf97b281e469fa29a3d2f34b4618fd  nd-unfolding/fd_1b_score.py
b95c562916091b910a5ca8d874d83296035690cb8784db3d318b2f07fed28182  docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/clip/clip_probe2.py
76cbceba395bc6bbf8fc5cce9cf44fc0f21354dff8591cbdee578e0fddcaf8ed  2d-unfolding/cov2d/cov2d.py
3a50f502b5a425bc4d116245c36f79bbc279cbd876b87aa72bd0298b001b5031  docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt
b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89  nd-unfolding/pv-ladder/readouts/h2_definition.json
ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48  setup_salloc_env.sh
bda8c48ce2365e173bbba083b18233d6f6b7c2dfbab5179156073860c8281ec7  nd-unfolding/s5e_candidate.py
6726ff99c7787d1ee6dff7fa5d08df88f9df76285d98c4c462f964ac6164779f  nd-unfolding/s5e_deform.py
24312ca86f9e70ed86699772d634c19d9bcacb2bb87bff5aaa8c9f7c2661f3cb  nd-unfolding/ll5d_b.py
ec1402db5cbb5ca3002d7e45a714319d90a8b93654005d688b304a69caab4d38  nd-unfolding/fd_1b_null.py
8981f97b96b418cfe46f1e940cb120f174053d7d3429f3b0b01a229c6c02ee6c  nd-unfolding/s5n_pseudo.py
7ad8ca0f73989128b783b59d55670687c293d186b2643ea799a3e67c047bf185  nd-unfolding/s5p_numerics.py
24f87f119073c4f125c2f753310507d4375b6f8a1b7751e59d3615dd50e90582  nd-unfolding/omnifold_nn_core.py
fc95f53459a5caafea4aa05a24a406535968e25b0bcca52567a38caf4caf3de5  2d-unfolding/uq/coverage_fixed_truth/score_coverage.py
a9f09557ec1b6022b1205f14e8d2241257336d9028b166061a3b33118243a936  nd-unfolding/ll5d_ctl.py
SUMS
[ "$(sha256sum "$W/bound.sha256" | cut -d' ' -f1)" = "7540b2de8f2de64f25d62497abe91a6a04fc7cf6cb18379e624422afb32c52b3" ] || stop "bound.sha256 is not the bulk's 22-line list 7540b2de"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
cat > "$W/sbatch-ll5d-rerun129.sh" <<'JOB'
#!/bin/bash
# ll5d_rerun129_01's job: 4 lanes of 5 items, each an srun step (32 CPUs, 56G, --threads 32); the deploy at M with
# porcelain 0 and the bound blobs, checked ONCE here, before all 4 calls; the lanes asserted against ll5d_b; 4 ll5d_b.py
# unfold calls (ar23 toy, 5 items each, the 20 between them). Not under set -u. Writes only under $W and $UO (passed as the 4th argument).
DD=$1; M=$2; W=$3; U=$4; NODE=$5   # here U is $UO, the fresh out directory
P=/pscratch/sd/j/josephrb; ND=$P/MINERvA-OmniFold/nd-unfolding
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
echo "host=$(hostname) job=$SLURM_JOB_ID node=$NODE start=$(date -u +%FT%TZ)"
h=$(git -C "$DD" rev-parse HEAD); n=$(git -C "$DD" status --porcelain | wc -l); echo "deploy head=$h porcelain_lines=$n"
[ "$h" = "$M" ] && [ "$n" = "0" ] || stop "deploy not clean at M"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
source "$DD/setup_salloc_env.sh" > "$W/logs/env-job-$NODE.log" 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# The unfolds run as 1B staged ran them, and as S1 made the controls' references (meta threads 32): each lane one srun
# step with 32 CPUs and 56G (section 9's 8 lanes; the RSS limit is 75 % of 56 GiB), --threads 32. The one-thread rule
# is the gate's and the calibration's (section 9, 936-C2), not the unfolds'.
echo "lanes 4 x (srun --exact -n1 -c 32 --mem 56G) --threads 32"
python3 -B - "$DD/nd-unfolding" "$W/rerun-lanes.tsv" <<'PY' || stop "the row is not the bulk's node 09 lane 4"
import sys
from collections import Counter
sys.path.insert(0, sys.argv[1])
import ll5d_b
rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[2]) if l.strip() and not l.startswith("#")]
got = [(t, r, i) for _, _, t, r, its in rows for i in its.split(",")]
per_lane = Counter((nd, ln) for nd, ln, t, r, its in rows for i in its.split(","))
want = {(t, r, i) for t in ll5d_b.TRUTHS for r, i in ll5d_b.items(t)} - set(ll5d_b.PILOT)
print(f"items={len(got)} unique={len(set(got))} in_section9_bulk={set(got) <= want} lanes={len(per_lane)} truth_role={sorted({(t, r) for t, r, _ in got})}")
sys.exit(0 if len(got) == 20 and len(set(got)) == 20 and set(got) <= want and len(per_lane) == 4 and set(per_lane.values()) == {5}
         and {(t, r) for t, r, _ in got} == {("ar23", "toy")} else 1)
PY
WORLD=(--npz "$ND/of_inputs_5d.npz" --bkg "$P/s5c-20260924/runs/p2/bkg_dump.npz" --bank "$ND/bank_sweep_5d_bkgaware"
  --detector-dir "$P/s5p-20260926/bank_detector" --pins "$P/fd-1b-20261030/pins.json"
  --expect-pins-sha256 5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248
  --flux-constraint "$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"
  --flux-table "$P/fd-1b-staged-20261102/stage1/in/flux_universes.npz"
  --expect-flux-table-sha256 cdc3da788c385da72826b2a74b1987320bbe399af212722826914df4d2fe15a5
  --prep "$P/fd-f1-20261027/f1b3/prep"
  --manifest "$DD/docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt"
  --expect-manifest-sha256 3a50f502b5a425bc4d116245c36f79bbc279cbd876b87aa72bd0298b001b5031)
mkdir -p "$W/lanes" || stop mkdir
lane() {
  local L=$1 rc=0 nd l t r its
  while IFS=$'\t' read -r -u 3 nd l t r its; do   # the table on fd 3, never stdin (the pilot r1 STOP)
    [ "$nd" = "$NODE" ] && [ "$l" = "$L" ] || continue
    srun --exact -n1 -c 32 --mem 56G --job-name "lane$L" /usr/bin/time -v python3 -B "$DD/nd-unfolding/ll5d_b.py" unfold "${WORLD[@]}" --truth "$t" --role "$r" --items "$its" \
      --out "$U" --threads 32 < /dev/null >> "$W/lanes/node$NODE-lane$L.out" 2>> "$W/lanes/node$NODE-lane$L.time"
    s=$?; echo "node $NODE lane $L $t $r rc=$s" >> "$W/lanes/node$NODE-lane$L.out"; rc=$((rc | s))
  done 3< <(grep -v '^#' "$W/rerun-lanes.tsv")
  return $rc
}
pids=(); for L in 0 1 2 3; do lane $L & pids+=($!); done
urc=0; for k in 0 1 2 3; do wait ${pids[$k]}; s=$?; echo "lane $k rc=$s"; urc=$((urc | s)); done
echo "unfold lanes rc=$urc"
case "$urc" in
  0) echo "RERUN-EXIT clean rc=0" ;;
  8) echo "RERUN-EXIT rc=8: ll5d_b's atime sidecar lists a move; to the director with the sidecar, nothing graded until explained" ;;
  *) echo "RERUN-EXIT NOT-CLEAN rc=$urc: to the director unrepaired; nothing graded even if the comparison is equal" ;;
esac
grep -h "rc=" "$W"/lanes/node$NODE-lane*.out
grep -h -E "Elapsed|Maximum resident|Exit status" "$W"/lanes/node$NODE-lane*.time
echo "end=$(date -u +%FT%TZ)"
exit $urc
JOB
echo "job script sha256 $(sha256sum "$W/sbatch-ll5d-rerun129.sh" | cut -d' ' -f1)"
find "$ND/of_inputs_5d.npz" "$P/s5c-20260924/runs/p2/bkg_dump.npz" "$ND/bank_sweep_5d_bkgaware" "$P/s5p-20260926/bank_detector" \
  "$P/fd-1b-20261030/pins.json" "$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt" \
  "$P/fd-1b-staged-20261102/stage1/in/flux_universes.npz" "$P/fd-f1-20261027/f1b3/prep" "$P/fd-1b-inv-20261101/i0/in" \
  -type f -printf "%A@\t%p\n" | sort -k2 > "$W/atime-pre.tsv" || stop "atime snapshot"
echo "atime-pre $(wc -l < "$W/atime-pre.tsv") files at $(date -u +%FT%TZ)"
ids=()
for NN in $NODES; do
  jid=$(sbatch --parsable -A m3246 -q regular -C cpu -N 1 --exclusive --no-requeue -t "$TL" -J "ll5d_rerun129_$NN" \
    -o "$W/logs/%x_%j.out" "$W/sbatch-ll5d-rerun129.sh" "$DD" "$M" "$W" "$UO" "$NN")
  jid=${jid%%;*}
  [ -n "$jid" ] || { [ ${#ids[@]} -gt 0 ] && scancel "${ids[@]}"; stop "sbatch for ll5d_rerun129_$NN returned no id: cancelled ${ids[*]}"; }
  ids+=("$jid"); echo "Submitted batch job $jid (ll5d_rerun129_$NN)"
  tl=$(scontrol show job "$jid" | grep -oE "TimeLimit=[^ ]*"); echo "$tl"
  [ "$tl" = "TimeLimit=02:30:00" ] || { scancel "${ids[@]}"; stop "ll5d_rerun129_$NN's time limit parsed as ${tl#TimeLimit=}, not 02:30:00: cancelled ${ids[*]}"; }
done
squeue --me -h -o '%i %j %T %l %D' | grep ll5d_rerun129_
echo "end=$(date -u +%FT%TZ)"
