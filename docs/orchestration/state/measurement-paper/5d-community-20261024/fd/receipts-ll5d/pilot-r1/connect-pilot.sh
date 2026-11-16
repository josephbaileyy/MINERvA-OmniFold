#!/bin/bash
# LL5D section 11 step 5: ll5d_pilot, DRAFT for the director's review (binding 3 ruling 4; A1b section 5). Runs only
# after BOTH gate-2 jobs read PASS (binding 3 ruling 4; the pilot's clipmeans need both truths' sealed clip-prep files)
# and their receipts are merged; every placeholder refuses until filled from those merged receipts by git.
# One exclusive regular CPU node, --time 01:00:00 (section 9: 1.0 node-h reserved, about 0.4 expected), 8 lanes, each
# an srun step of 32 CPUs and 56G at --threads 32 (as 1B staged). The pilot's 13 items (ll5d_b.PILOT, asserted in the job) are unfolded into the shared products
# directory $U, then, in the same job, ll5d_b.py walls (section 9's REPRICE trigger), ll5d_ctl.py (amendment A1b.1:
# the four procedure controls bitwise against S1's committed products) and clipcheck (section 5.3; TO_JOSEPH goes to
# Joseph before any bulk). The sealed clip-prep files are read only inside ll5d_b.read_clip_prep, by
# the sha256 each gate record carries (binding 3 ruling 3); this connect hashes neither and opens neither.
# The fence, iris, the projection gate with this job's 1.0, a fresh clone at M_A1b.1 with the bound blobs, the job
# script and an atime snapshot, sbatch, TimeLimit. Nothing to CFS. Not under set -u.
J=ll5d_pilot
M=4231b14de5ea693e92cb31b1358a816b5c2f6625         # M_A1b.1 (LL5D-BINDING-3.md addendum A1b.1): the merge that carries ll5d_ctl.py
L5=2b0224c6fe52c5bb2d3fe64d461ac9edb80ebd191b0ab2f892dec605a0b56a14        # ll5d.py's sha256 at M
P=/pscratch/sd/j/josephrb; ND=$P/MINERvA-OmniFold/nd-unfolding
W=$P/ll5d-pilot-r1; DD=$W/deploy; U=$P/ll5d-unfolds-r1
G18W=$P/ll5d-gate-2-g18-20261110; AR23W=$P/ll5d-gate-2-ar23-20261110
G18GATE=a5d66b7e506a98d5a0b555dbe171aa6c1e931eb93df793c3e515d7d44466fc70   # sha256 of gate-g18.json (node-sha256.txt of the merged receipt)
AR23GATE=35a20c471cb06f428c49daaaebfc6646babb7f7fb060039d4c63139da51d0a4c  # sha256 of gate-ar23.json
G18CP=76154b205691bcd5e19b0c0e2274f35615dec4dd857a6033b976aaf2f30aacba     # the SEALED line's sha256 of gate-g18.clipprep.npz
AR23CP=c567183d94d9b0be9b1d7ec1513cdb58db14bcffa5ef6eb630c7b77d4c5ff6d1    # the SEALED line's sha256 of gate-ar23.clipprep.npz
CAP=148.0; THIS=1.0; TL=01:00:00
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
for v in "$G18GATE" "$AR23GATE" "$G18CP" "$AR23CP" "$L5"; do [[ $v =~ ^[0-9a-f]{64}$ ]] || { echo "STOP a placeholder is not filled"; exit 2; }; done
[[ $M =~ ^[0-9a-f]{40}$ ]] || { echo "STOP M is not filled"; exit 2; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
[ -e "$U" ] && { echo "STOP $U exists (the pilot makes it)"; exit 2; }
mkdir -p "$W/logs" || exit 2
exec >> "$W/logs/connect-pilot.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
echo "squeue: [$(squeue --me -h -o '%i %j %T %l %D' | tr '\n' ';')]"
[ "$(squeue --me -h -o %j | grep -c '^ll5d_')" = "0" ] || stop "an ll5d_ job is queued or running (the gates must have ended)"
# the director's queue order (2026-11-12): no atime-snapshot connect while another lane's reader of our inputs is queued or running
[ "$(squeue --me -h -o %j | grep -cE '^(rsn_|e96data|rdx_)')" = "0" ] || stop "an rsn_, e96data or rdx_ job is queued or running"
cv=$(sacct -X -n -P -S 2026-11-04 -u josephrb -o JobID,JobName,State | awk -F'|' '$2 ~ /^cov2d/ && $3 !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)/')
[ -z "$cv" ] || stop "a cov2d job is unended: $cv"   # ^cov2d, not ^cov2d-: it also matches COV2D-G2R's cov2dg2r-<job> names
echo "== iris"; row=$(iris 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}'); [ -n "$bal" ] || stop "could not read the m3246 balance"
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') cap=$CAP"
awk -v b=$bal -v c=$CAP 'BEGIN{exit !(c <= b/2)}' || stop "the cap $CAP is above half the balance $bal: to Joseph"
charged=$(sacct -X -n -P -S 2026-11-08 -u josephrb -o JobName,State,ElapsedRaw,NNodes | awk -F'|' '$1 ~ /^ll5d_/ && $2 !~ /^(PENDING|RUNNING|REQUEUED|SUSPENDED)/ {s += $3 * $4} END {printf "%.3f", s / 3600}')
held=$(squeue --me -h -o '%j|%l|%D' | awk -F'|' '$1 ~ /^ll5d_/ {split($2, t, /[-:]/); n = length(t); s = (n == 4 ? t[1]*86400 + t[2]*3600 + t[3]*60 + t[4] : n == 3 ? t[1]*3600 + t[2]*60 + t[3] : t[1]*60 + t[2]); h += s * $3} END {printf "%.3f", h / 3600}')
proj=$(awk -v a=$charged -v b=$held -v c=$THIS 'BEGIN{printf "%.3f", a + b + c}')
echo "projection charged=$charged held=$held this=$THIS total=$proj cap=$CAP"
awk -v p=$proj -v c=$CAP 'BEGIN{exit !(p <= c)}' || stop "the projection $proj passes the cap $CAP"
# The precondition (binding 3 ruling 4; A1b section 3f): each gate record is the receipted one, reads PASS, and names
# the clip-prep digest the receipt gives. Only verdict, truth and clip_prep.sha256 are read here.
for T in g18 ar23; do
  if [ $T = g18 ]; then GW=$G18W; GS=$G18GATE; CS=$G18CP; else GW=$AR23W; GS=$AR23GATE; CS=$AR23CP; fi
  [ "$(sha256sum "$GW/gate-$T.json" | cut -d' ' -f1)" = "$GS" ] || stop "gate-$T.json's digest is not the receipt's"
  python3 -c 'import json,sys; g=json.load(open(sys.argv[1])); ok=g.get("truth")==sys.argv[2] and g.get("verdict")=="PASS" and (g.get("clip_prep") or {}).get("sha256")==sys.argv[3]; print("gate", sys.argv[2], "truth=%s verdict=%s clip_prep_sha256_matches=%s" % (g.get("truth"), g.get("verdict"), ok)); sys.exit(0 if ok else 1)' "$GW/gate-$T.json" "$T" "$CS" || stop "gate $T is not PASS, or its clip-prep digest is not the receipt's"
  [ -e "$GW/gate-$T.clipprep.npz" ] || stop "gate-$T.clipprep.npz is missing"
done
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
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
# The pilot's lanes: at most two items a lane (2 x 1,062 s under the 0.9 line 3,240 s). The job asserts that the union
# is exactly ll5d_b.PILOT, with no item twice.
cat > "$W/pilot-lanes.tsv" <<'LANES'
# lane	truth	role	items (LL5D pilot: ll5d_b.PILOT's 13 items over 8 lanes)
0	data	control	setA_b1
0	ar23	stat	1
1	data	control	MaRES_0
2	data	control	Flux_0
3	data	control	GEANT_Pion_0
4	g18	central	T
4	g18	toy	minus2_4751000
5	ar23	central	T
5	g18	toy	all_4751000
6	g18	clipmean	minus2,all
7	ar23	clipmean	minus2,all
LANES
cat > "$W/sbatch-ll5d-pilot.sh" <<'JOB'
#!/bin/bash
# ll5d_pilot's job: 8 lanes, each an srun step (32 CPUs, 56G, --threads 32); the deploy at M with porcelain 0 and the bound blobs; the lanes
# (ll5d_b.py unfold, one truth and role per call), then walls, the controls (ll5d_ctl.py, A1b.1) and clipcheck. Not under set -u. Writes only under $W, $U.
DD=$1; M=$2; W=$3; U=$4; G18CP=$5; AR23CP=$6; G18W=$7; AR23W=$8
P=/pscratch/sd/j/josephrb; ND=$P/MINERvA-OmniFold/nd-unfolding
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
echo "host=$(hostname) job=$SLURM_JOB_ID start=$(date -u +%FT%TZ)"
h=$(git -C "$DD" rev-parse HEAD); n=$(git -C "$DD" status --porcelain | wc -l); echo "deploy head=$h porcelain_lines=$n"
[ "$h" = "$M" ] && [ "$n" = "0" ] || stop "deploy not clean at M"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
source "$DD/setup_salloc_env.sh" > "$W/logs/env-job.log" 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# The unfolds run as 1B staged ran them, and as S1 made the controls' references (meta threads 32): each lane one srun
# step with 32 CPUs and 56G (section 9's 8 lanes; the RSS limit is 75 % of 56 GiB), --threads 32. The one-thread rule
# is the gate's and the calibration's (section 9, 936-C2), not the unfolds'.
echo "lanes 8 x (srun --exact -n1 -c 32 --mem 56G) --threads 32"
python3 -B - "$DD/nd-unfolding" "$W/pilot-lanes.tsv" <<'PY' || stop "the lanes are not exactly ll5d_b.PILOT"
import sys
sys.path.insert(0, sys.argv[1])
import ll5d_b
rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[2]) if l.strip() and not l.startswith("#")]
got = [(t, r, i) for _, t, r, its in rows for i in its.split(",")]
print(f"lanes={len({x[0] for x in rows})} items={len(got)} unique={len(set(got))} pilot={len(ll5d_b.PILOT)}")
sys.exit(0 if len(got) == len(set(got)) and set(got) == set(ll5d_b.PILOT) else 1)
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
mkdir -p "$U" "$W/lanes" || stop mkdir
lane() {
  local L=$1 rc=0 t r its cp
  while IFS=$'\t' read -r l t r its; do
    [ "$l" = "$L" ] || continue
    cp=()
    if [ "$r" = clipmean ]; then
      if [ "$t" = g18 ]; then cp=(--clip-prep "$G18W/gate-g18.clipprep.npz" --expect-clip-prep-sha256 "$G18CP")
      else cp=(--clip-prep "$AR23W/gate-ar23.clipprep.npz" --expect-clip-prep-sha256 "$AR23CP"); fi
    fi
    srun --exact -n1 -c 32 --mem 56G --job-name "lane$L" /usr/bin/time -v python3 -B "$DD/nd-unfolding/ll5d_b.py" unfold "${WORLD[@]}" --truth "$t" --role "$r" --items "$its" \
      --out "$U" --threads 32 "${cp[@]}" >> "$W/lanes/lane$L.out" 2>> "$W/lanes/lane$L.time"
    s=$?; echo "lane $L $t $r rc=$s" >> "$W/lanes/lane$L.out"; rc=$((rc | s))
  done < <(grep -v '^#' "$W/pilot-lanes.tsv")
  return $rc
}
pids=(); for L in 0 1 2 3 4 5 6 7; do lane $L & pids+=($!); done
urc=0; for k in 0 1 2 3 4 5 6 7; do wait ${pids[$k]}; s=$?; echo "lane $k rc=$s"; urc=$((urc | s)); done
echo "unfold lanes rc=$urc"
grep -h "rc=" "$W"/lanes/lane*.out
grep -h -E "Elapsed|Maximum resident|Exit status" "$W"/lanes/lane*.time
cd "$W" || stop cd
python3 -B "$DD/nd-unfolding/ll5d_b.py" walls --unfolds "$U" --out "$W/walls.json" > "$W/walls.out" 2>&1; wrc=$?
echo "walls rc=$wrc"; cat "$W/walls.out"
python3 -B "$DD/nd-unfolding/ll5d_ctl.py" --unfolds "$U" --repo "$DD" --out "$W/controls.json" > "$W/controls.out" 2>&1; krc=$?
echo "controls rc=$krc"; cat "$W/controls.out"
python3 -B "$DD/nd-unfolding/ll5d_b.py" clipcheck --staged "$P/fd-1b-inv-20261101/i0/in" \
  --definition "$DD/nd-unfolding/pv-ladder/readouts/h2_definition.json" --unfolds "$U" --out "$W/clipcheck.json" \
  --truths g18 ar23 --clip-prep "$G18W/gate-g18.clipprep.npz" "$AR23W/gate-ar23.clipprep.npz" \
  --expect-clip-prep-sha256 "$G18CP" "$AR23CP" > "$W/clipcheck.out" 2>&1; crc=$?
echo "clipcheck rc=$crc"; cat "$W/clipcheck.out"
sha256sum "$W"/walls*.json "$W"/controls*.json "$W"/clipcheck*.json "$W"/walls.out "$W"/controls.out "$W"/clipcheck.out "$U"/*.npz 2>/dev/null
echo "end=$(date -u +%FT%TZ)"
exit $((urc | wrc | krc | crc))
JOB
echo "job script sha256 $(sha256sum "$W/sbatch-ll5d-pilot.sh" | cut -d' ' -f1)"
echo "lanes sha256 $(sha256sum "$W/pilot-lanes.tsv" | cut -d' ' -f1)"
find "$ND/of_inputs_5d.npz" "$P/s5c-20260924/runs/p2/bkg_dump.npz" "$ND/bank_sweep_5d_bkgaware" "$P/s5p-20260926/bank_detector" \
  "$P/fd-1b-20261030/pins.json" "$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt" \
  "$P/fd-1b-staged-20261102/stage1/in/flux_universes.npz" "$P/fd-f1-20261027/f1b3/prep" "$P/fd-1b-inv-20261101/i0/in" \
  -type f -printf "%A@\t%p\n" | sort -k2 > "$W/atime-pre.tsv" || stop "atime snapshot"
echo "atime-pre $(wc -l < "$W/atime-pre.tsv") files at $(date -u +%FT%TZ)"
jid=$(sbatch --parsable -A m3246 -q regular -C cpu -N 1 --exclusive --no-requeue -t "$TL" -J "$J" -o "$W/logs/%x_%j.out" \
  "$W/sbatch-ll5d-pilot.sh" "$DD" "$M" "$W" "$U" "$G18CP" "$AR23CP" "$G18W" "$AR23W") || stop sbatch
jid=${jid%%;*}; echo "Submitted batch job $jid"
tl=$(scontrol show job "$jid" | grep -oE "TimeLimit=[^ ]*"); echo "$tl"
[ "$tl" = "TimeLimit=01:00:00" ] || { scancel "$jid"; stop "the time limit parsed as ${tl#TimeLimit=}, not 01:00:00: cancelled $jid"; }
scontrol show job "$jid" | grep -oE "(JobName|JobState|TimeLimit|Partition|QOS|NumNodes|Account|OverSubscribe)=[^ ]*" | tr '\n' ' '; echo
echo "end=$(date -u +%FT%TZ)"
