#!/bin/bash
# REF-G1 step two, the batch connect (REF-G1-BINDING-2.md rulings 2, 3, 5 and 6; #786, main 87ae7102; code at M =
# 609d8f24), on a login node, detached: the 233 declared units, priced from the timing unit (job 60849625, receipts
# fd/receipts-ref-g1/timing/, #788). In order:
#   the projection from the timing record (its unit.log seconds and unit.time wall, read O_NOATIME): setup = wall -
#   unit seconds; projected node-h = (setup + 30 units x unit seconds) / 3600 on one node, the longest lane of 8 (30,
#   29 x 7). It STOPS, unshrunk, if the projection exceeds the 5.0 cap less the timing charge (0.0211), or 2.00 (the
#   --time below), and reports;
#   the iris half-balance check at the price 2.0; a fresh clean clone at M into $O/deploy-M, porcelain --ignored 0 and
#   the 5 bound blobs; the lane table (lanes.tsv, ed3abdcf...) and the job script (refg1_batch_job.sbatch,
#   f4651380...) written from this file and refused unless they are those bytes; one sbatch, --time=02:00:00 (at most
#   2.0 node-h); scontrol's TimeLimit must read 02:00:00, else scancel, rc 6.
# Writes only under $O. No set -u. Any stop is final. Launched from a /dev/shm copy of itself ($1).
SELF=$1
O=/pscratch/sd/j/josephrb/ref-g1-20261105/batch
T=/pscratch/sd/j/josephrb/ref-g1-20261105/timing
D=$O/deploy-M
M=609d8f24ea2229fa4b3540627aa8c31acfcc0a54
TLIMIT=02:00:00
PRICE=2.0
CAPLEFT=4.9789
LANES_SHA=ed3abdcf5048bae3c9786f2e43359779577ba5c26590a024f506e5f064148f51
JOB_SHA=f4651380a896ea29af47f15de8b59dac5c8092810cdd9a0788c142463ee3c687
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in login*) ;; *) bail ;; esac
[ ! -e "$O" ] && [ -s "$T/unit.log" ] && [ -s "$T/unit.time" ] || bail
[ -z "$(squeue --me -h -n fd_refg1_timing,fd_refg1 -o %i)" ] || bail
mkdir -p "$O/logs" || bail
exec > "$O/logs/connect.log" 2>&1
finish() { echo "refg1 batch submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$O/logs/connect.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$O/logs/refg1_batch_submit.sh"
# ---- the projection, from the timing record
us=$(dd if="$T/unit.log" iflag=noatime status=none | sed -n 's/.*"seconds": \([0-9.]*\).*/\1/p' | head -1)
wl=$(dd if="$T/unit.time" iflag=noatime status=none | sed -n 's/.*Elapsed (wall clock) time (h:mm:ss or m:ss): //p' | awk -F: '{if (NF==3) print $1*3600+$2*60+$3; else print $1*60+$2}')
echo "timing unit: seconds=$us wall=$wl"
[ -n "$us" ] && [ -n "$wl" ] || { echo "STOP: the timing record is unreadable"; finish 9; }
proj=$(awk -v u=$us -v w=$wl 'BEGIN{printf "%.4f", ((w - u) + 30 * u) / 3600}')
echo "projected_node_h=$proj (setup $(awk -v u=$us -v w=$wl 'BEGIN{printf "%.1f", w-u}') s + 30 units x $us s, 1 node, 8 lanes) cap_left=$CAPLEFT limit_node_h=$PRICE"
awk -v p=$proj -v c=$CAPLEFT 'BEGIN{exit !(p <= c)}' || { echo "STOP: the projection $proj exceeds the cap's remainder $CAPLEFT (unshrunk; to the director)"; finish 4; }
awk -v p=$proj -v c=$PRICE 'BEGIN{exit !(p <= c)}' || { echo "STOP: the projection $proj exceeds the limit $PRICE (to the director)"; finish 4; }
echo "== iris"; row=$(timeout 120 iris < /dev/null 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') price=$PRICE"
awk -v b=$bal -v c=$PRICE 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the price is above half the balance: to Joseph"; finish 9; }
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$O/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
cfe089d466fa8cb1926d6665fbae65b5d269eaeb nd-unfolding/ref_g1/ref_g1.py
e49ab974598ea3d15663f61da538fad3c9c8f12a nd-unfolding/ref_g1/ref_g1_read.py
2a14b22f169b9a5e616a5498dcba79c682d6766b nd-unfolding/ref_g1/config.json
c68198177807a39d41114c8286edd3d23bc6ab18 nd-unfolding/ref_g1/test_ref_g1.py
4ad3b92570b2196737df57944f94300a90d9ecc5 nd-unfolding/ref_g1/ref_g1_mutation.py
BLOBS
echo "bound blobs: 5 checked, $bad mismatches"; [ "$bad" -eq 0 ] || { echo "STOP: bound bytes"; finish 9; }
cat > "$O/lanes.tsv" <<'LANESEOF'
# lane	unit (REF-G1 batch: the 233 declared units, round-robin over 8 lanes, from config.json at M 609d8f24)
0	gibu1
0	replica:7
0	replica:15
0	replica:23
0	replica:31
0	replica:39
0	replica:47
0	closure:tune_v1
0	universe:AhtBY:1
0	universe:CV2uBY:1
0	universe:Flux:13
0	universe:Flux:20
0	universe:Flux:28
0	universe:Flux:35
0	universe:Flux:42
0	universe:Flux:5
0	universe:Flux:57
0	universe:Flux:64
0	universe:Flux:71
0	universe:Flux:79
0	universe:Flux:86
0	universe:Flux:93
0	universe:FrAbs_N:1
0	universe:FrElas_N:1
0	universe:FrPiProd_pi:1
0	universe:HighQ2:1
0	universe:MaCCQE:1
0	universe:MvRES:1
0	universe:Rvn1pi:1
0	universe:VecFFCCQEshape:1
1	central
1	replica:8
1	replica:16
1	replica:24
1	replica:32
1	replica:40
1	replica:48
1	universe:CV
1	universe:BhtBY:0
1	universe:EtaNCEL:0
1	universe:Flux:14
1	universe:Flux:21
1	universe:Flux:29
1	universe:Flux:36
1	universe:Flux:43
1	universe:Flux:50
1	universe:Flux:58
1	universe:Flux:65
1	universe:Flux:72
1	universe:Flux:8
1	universe:Flux:87
1	universe:Flux:94
1	universe:FrAbs_pi:0
1	universe:FrElas_pi:0
1	universe:GEANT_Neutron:0
1	universe:LowQ2:0
1	universe:MaNCEL:0
1	universe:NormDISCC:0
1	universe:Rvn2pi:0
2	replica:1
2	replica:9
2	replica:17
2	replica:25
2	replica:33
2	replica:41
2	replica:49
2	universe:2p2h:0
2	universe:BhtBY:1
2	universe:EtaNCEL:1
2	universe:Flux:15
2	universe:Flux:22
2	universe:Flux:3
2	universe:Flux:37
2	universe:Flux:44
2	universe:Flux:51
2	universe:Flux:59
2	universe:Flux:66
2	universe:Flux:73
2	universe:Flux:80
2	universe:Flux:88
2	universe:Flux:95
2	universe:FrAbs_pi:1
2	universe:FrElas_pi:1
2	universe:GEANT_Neutron:1
2	universe:LowQ2:1
2	universe:MaNCEL:1
2	universe:NormDISCC:1
2	universe:Rvn2pi:1
3	replica:2
3	replica:10
3	replica:18
3	replica:26
3	replica:34
3	replica:42
3	replica:50
3	universe:2p2h:1
3	universe:CCQEPauliSupViaKF:0
3	universe:Flux:0
3	universe:Flux:16
3	universe:Flux:23
3	universe:Flux:30
3	universe:Flux:38
3	universe:Flux:45
3	universe:Flux:52
3	universe:Flux:6
3	universe:Flux:67
3	universe:Flux:74
3	universe:Flux:81
3	universe:Flux:89
3	universe:Flux:96
3	universe:FrCEx_N:0
3	universe:FrInel_N:0
3	universe:GEANT_Pion:0
3	universe:MFP_N:0
3	universe:MaRES:0
3	universe:NormNCRES:0
3	universe:Rvp2pi:0
4	replica:3
4	replica:11
4	replica:19
4	replica:27
4	replica:35
4	replica:43
4	vertex:genie_mec
4	universe:2p2h:2
4	universe:CCQEPauliSupViaKF:1
4	universe:Flux:1
4	universe:Flux:17
4	universe:Flux:24
4	universe:Flux:31
4	universe:Flux:39
4	universe:Flux:46
4	universe:Flux:53
4	universe:Flux:60
4	universe:Flux:68
4	universe:Flux:75
4	universe:Flux:82
4	universe:Flux:9
4	universe:Flux:97
4	universe:FrCEx_N:1
4	universe:FrInel_N:1
4	universe:GEANT_Pion:1
4	universe:MFP_N:1
4	universe:MaRES:1
4	universe:NormNCRES:1
4	universe:Rvp2pi:1
5	replica:4
5	replica:12
5	replica:20
5	replica:28
5	replica:36
5	replica:44
5	vertex:nuwro
5	universe:AGKYxF1pi:0
5	universe:CV1uBY:0
5	universe:Flux:10
5	universe:Flux:18
5	universe:Flux:25
5	universe:Flux:32
5	universe:Flux:4
5	universe:Flux:47
5	universe:Flux:54
5	universe:Flux:61
5	universe:Flux:69
5	universe:Flux:76
5	universe:Flux:83
5	universe:Flux:90
5	universe:Flux:98
5	universe:FrCEx_pi:0
5	universe:FrPiProd_N:0
5	universe:GEANT_Proton:0
5	universe:MFP_pi:0
5	universe:MinosEfficiency:0
5	universe:RDecBR1gamma:0
5	universe:Theta_Delta2Npi:0
6	replica:5
6	replica:13
6	replica:21
6	replica:29
6	replica:37
6	replica:45
6	vertex:gibuu
6	universe:AGKYxF1pi:1
6	universe:CV1uBY:1
6	universe:Flux:11
6	universe:Flux:19
6	universe:Flux:26
6	universe:Flux:33
6	universe:Flux:40
6	universe:Flux:48
6	universe:Flux:55
6	universe:Flux:62
6	universe:Flux:7
6	universe:Flux:77
6	universe:Flux:84
6	universe:Flux:91
6	universe:Flux:99
6	universe:FrCEx_pi:1
6	universe:FrPiProd_N:1
6	universe:GEANT_Proton:1
6	universe:MFP_pi:1
6	universe:MinosEfficiency:1
6	universe:RDecBR1gamma:1
6	universe:Theta_Delta2Npi:1
7	replica:6
7	replica:14
7	replica:22
7	replica:30
7	replica:38
7	replica:46
7	closure:nuwro
7	universe:AhtBY:0
7	universe:CV2uBY:0
7	universe:Flux:12
7	universe:Flux:2
7	universe:Flux:27
7	universe:Flux:34
7	universe:Flux:41
7	universe:Flux:49
7	universe:Flux:56
7	universe:Flux:63
7	universe:Flux:70
7	universe:Flux:78
7	universe:Flux:85
7	universe:Flux:92
7	universe:FrAbs_N:0
7	universe:FrElas_N:0
7	universe:FrPiProd_pi:0
7	universe:HighQ2:0
7	universe:MaCCQE:0
7	universe:MvRES:0
7	universe:Rvn1pi:0
7	universe:VecFFCCQEshape:0
LANESEOF
cat > "$O/refg1_batch_job.sbatch" <<'JOBEOF'
#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
# REF-G1 step two, the batch (REF-G1-BINDING-2.md rulings 2, 3 and 6): the 233 declared units by the bound driver at
# M from a fresh clean clone, with -B, under the exact interpreter ruling 2 names, 8 lanes of 32 threads (config.json
# resources.max_threads_per_task), each lane ONE driver invocation over its units of <O>/lanes.tsv (the driver loads its
# inputs once per invocation). Products go to <O>/units, outside the deploy. A unit refused or failing a control gives a
# nonzero lane rc and is reported to the director unrepaired; nothing is rerun here. Porcelain, with --ignored, is
# recorded before and after. Arguments: <deploy> <O>. Writes only under <O>.
set -o pipefail   # NOT set -u
C="${1:?deploy}"; O="${2:?out}"
M=609d8f24ea2229fa4b3540627aa8c31acfcc0a54
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
[ "$O" = /pscratch/sd/j/josephrb/ref-g1-20261105/batch ] || { echo "[refg1b] refusing: O is $O"; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { echo "[refg1b] refusing: deploy HEAD is not M"; exit 2; }
nb=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[refg1b] porcelain --ignored lines before: $nb"
[ "$nb" -eq 0 ] || { echo "[refg1b] refusing: the deploy is not clean"; exit 2; }
[ "$(grep -vc '^#' "$O/lanes.tsv")" -eq 233 ] || { echo "[refg1b] refusing: lanes.tsv is not 233 units"; exit 2; }
echo "[refg1b] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname) nproc=$(nproc)"
source "$C/setup_salloc_env.sh" > "$O/env.log" 2>&1   # root_6_28, as the s5p and RE-2 jobs source it
export TMPDIR=$O/tmp PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=32 MKL_NUM_THREADS=32 OPENBLAS_NUM_THREADS=32 NUMEXPR_NUM_THREADS=32
mkdir -p "$TMPDIR" "$O/units" "$O/lanes"
echo "[refg1b] interpreter $PY: $("$PY" -c 'import sys; print(sys.version.replace(chr(10), " "))')"
pids=""
for l in 0 1 2 3 4 5 6 7; do
    args=(); while IFS=$'\t' read -r ln u; do [ "$ln" = "$l" ] && args+=(--unit "$u"); done < <(grep -v '^#' "$O/lanes.tsv")
    ( /usr/bin/time -v -o "$O/lanes/lane$l.time" "$PY" -B "$C/nd-unfolding/ref_g1/ref_g1.py" "${args[@]}" \
          --out "$O/units" --threads 32 > "$O/lanes/lane$l.log" 2>&1
      echo "$?" > "$O/lanes/lane$l.rc" ) &
    pids="$pids $!"
done
for p in $pids; do wait "$p"; done
echo "[refg1b] lanes done $(date -u +%FT%TZ)"
for l in 0 1 2 3 4 5 6 7; do
    echo "[refg1b] lane $l rc=$(cat "$O/lanes/lane$l.rc") units=$(grep -c "^$l	" "$O/lanes.tsv") $(grep -E 'Elapsed|Maximum resident' "$O/lanes/lane$l.time" | tr -s ' \t' ' ' | tr '\n' ' ')"
done
npass=$(cat "$O"/units/*.done 2>/dev/null | grep -c '"verdict": "PASS"'); ndone=$(ls "$O"/units/*.done 2>/dev/null | wc -l)
echo "[refg1b] done-markers: $ndone, PASS: $npass, of 233"
( cd "$O/units" && sha256sum *.npz ) > "$O/SHA256SUMS"
echo "[refg1b] products listed: $(wc -l < "$O/SHA256SUMS")"
na=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[refg1b] porcelain --ignored lines after: $na"
git -C "$C" status --porcelain --ignored | head -10
bad=0; for l in 0 1 2 3 4 5 6 7; do [ "$(cat "$O/lanes/lane$l.rc")" = 0 ] || bad=1; done
[ "$bad" -eq 0 ] && [ "$npass" -eq 233 ] || { echo "[refg1b] STOP: a lane failed or a unit is not PASS (to the director, unrepaired)"; exit 1; }
echo "{\"units\": 233, \"pass\": $npass, \"job\": \"$SLURM_JOB_ID\", \"porcelain_after\": $na}" > "$O/DONE"
echo "[refg1b] done"
JOBEOF
l=$(sha256sum "$O/lanes.tsv" | cut -d' ' -f1); j=$(sha256sum "$O/refg1_batch_job.sbatch" | cut -d' ' -f1)
echo "lanes.tsv sha256 $l; refg1_batch_job.sbatch sha256 $j"
[ "$l" = "$LANES_SHA" ] && [ "$j" = "$JOB_SHA" ] || { echo "STOP: the lane table or the job script is not the reviewed one"; finish 9; }
echo "squeue --me before:"; squeue --me -h -o "%i %j %T"
date -u +%FT%TZ
cd "$O" || finish 9
sbatch --time=$TLIMIT --job-name=fd_refg1 --output="$O/logs/%x_%j.out" "$O/refg1_batch_job.sbatch" "$D" "$O" > "$O/logs/submit.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$O/logs/submit.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$O/logs/submit.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "batch job $job"; echo "$job" > "$O/logs/batch.jobid"
tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
echo "scontrol TimeLimit=$tl (declared $TLIMIT)"
if [ "$tl" != "$TLIMIT" ]; then
  scancel "$job"; echo "STOP: TimeLimit $tl is not $TLIMIT; job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a"
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after submission: $n"
finish 0
