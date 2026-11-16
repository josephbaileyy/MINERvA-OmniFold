#!/bin/bash
# LL5D section 11 step 4: ll5d_gate_<T> for ONE truth (argument 1: g18 or ar23), LL5D BINDING 2, A1a.1 at M_A1a.1. One
# exclusive regular CPU node, --time 31:00:00 (31.0 node-h reserved, section 9, A1a section 5a; the job's own 0.9 line
# 100,440 s), one BLAS thread. The calibration is ll5d_calib's, by the digests below (filled from its receipt before
# this connect's sha256 goes to the director; the placeholders refuse). Steps as connect-calib.sh: the fence (refusing on
# an unended cov2d-* or this truth's gate already queued), iris against the cap, section 9's projection gate with
# this job's 31.0, a fresh clone at M_A1a.1 with the bound blobs, the job script and an atime snapshot, sbatch, TimeLimit.
# The gate writes gate-<T>.json, gate-<T>.receipt.npz and the SEALED gate-<T>.clipprep.npz (A1a section 5j: its path,
# size and sha256 only; no one opens or summarizes it before binding 3). Nothing to CFS. Not under set -u.
T=$1
case "$T" in g18) J=ll5d_gate_G18 ;; ar23) J=ll5d_gate_AR23 ;; *) echo "STOP truth '$T' is not g18 or ar23"; exit 2 ;; esac
M=a95cc39f7437170af0b65ba042934fad079e0ee2
P=/pscratch/sd/j/josephrb; ND=$P/MINERvA-OmniFold/nd-unfolding
W=$P/ll5d-gate-$T-20261108; DD=$W/deploy
CAL=$P/ll5d-calib-2-20261109/calibration.json
CALSHA=ea039893e8ec98a9cd3da15dd7811a82a99563da8fbb253e6fc0766eb960fb17
CALNPZSHA=b31ddd12d050163396b4811705777fc1fa28f77757575af73c8dc5976b3c1a7c
CAP=148.0; THIS=31.0; TL=31:00:00; TLS=111600
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
case "$CALSHA$CALNPZSHA" in *FILL*) echo "STOP the calibration digests are not filled"; exit 2 ;; esac
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir -p "$W/logs" || exit 2
exec >> "$W/logs/connect-gate-$T.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ truth=$T"
echo "squeue: [$(squeue --me -h -o '%i %j %T %l %D' | tr '\n' ';')]"
[ "$(squeue --me -h -o %j | grep -cx "$J")" = "0" ] || stop "$J is already queued"
cv=$(sacct -X -n -P -S 2026-11-04 -u josephrb -o JobID,JobName,State | awk -F'|' '$2 ~ /^cov2d-/ && $3 !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)/')
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
[ "$(sha256sum "$CAL" | cut -d' ' -f1)" = "$CALSHA" ] || stop "the calibration's digest differs"
[ "$(sha256sum "${CAL%.json}.npz" | cut -d' ' -f1)" = "$CALNPZSHA" ] || stop "the calibration npz's digest differs"
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M" || stop clone
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
cat > "$W/bound.sha256" <<SUMS
b49f5d5f793265ef0cf569abe1912838cce9280e692f4dd61100d05c133aec1f  nd-unfolding/ll5d.py
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
SUMS
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
cat > "$W/sbatch-ll5d-gate.sh" <<'JOB'
#!/bin/bash
# ll5d_gate_<T>'s job: one BLAS thread, asserted; the deploy at M with porcelain 0 and the bound blobs; ll5d.py gate.
# The sealed clip-prep file is hashed and sized here, never read. Not under set -u. Writes only under $W.
DD=$1; M=$2; W=$3; T=$4; CAL=$5; CALSHA=$6; CALNPZSHA=$7; TLS=$8
P=/pscratch/sd/j/josephrb; ND=$P/MINERvA-OmniFold/nd-unfolding
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
echo "host=$(hostname) job=$SLURM_JOB_ID truth=$T start=$(date -u +%FT%TZ)"
h=$(git -C "$DD" rev-parse HEAD); n=$(git -C "$DD" status --porcelain | wc -l); echo "deploy head=$h porcelain_lines=$n"
[ "$h" = "$M" ] && [ "$n" = "0" ] || stop "deploy not clean at M"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
source "$DD/setup_salloc_env.sh" > "$W/logs/env-job.log" 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
echo "threads OMP=$OMP_NUM_THREADS OPENBLAS=$OPENBLAS_NUM_THREADS MKL=$MKL_NUM_THREADS NUMEXPR=$NUMEXPR_NUM_THREADS"
cd "$W" || stop cd
/usr/bin/time -v python3 -B "$DD/nd-unfolding/ll5d.py" gate --truth "$T" \
  --npz "$ND/of_inputs_5d.npz" --bkg "$P/s5c-20260924/runs/p2/bkg_dump.npz" --bank "$ND/bank_sweep_5d_bkgaware" \
  --detector-dir "$P/s5p-20260926/bank_detector" --pins "$P/fd-1b-20261030/pins.json" \
  --expect-pins-sha256 5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248 \
  --flux-constraint "$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt" \
  --flux-table "$P/fd-1b-staged-20261102/stage1/in/flux_universes.npz" \
  --expect-flux-table-sha256 cdc3da788c385da72826b2a74b1987320bbe399af212722826914df4d2fe15a5 \
  --definition "$DD/nd-unfolding/pv-ladder/readouts/h2_definition.json" --prep "$P/fd-f1-20261027/f1b3/prep" \
  --manifest "$DD/docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt" \
  --expect-manifest-sha256 3a50f502b5a425bc4d116245c36f79bbc279cbd876b87aa72bd0298b001b5031 \
  --staged "$P/fd-1b-inv-20261101/i0/in" --calibration "$CAL" --expect-calibration-sha256 "$CALSHA" \
  --expect-calibration-npz-sha256 "$CALNPZSHA" --time-limit-seconds "$TLS" \
  --out "$W/gate-$T.json" > "$W/gate.out" 2> "$W/gate.time"
rc=$?
echo "gate rc=$rc"
cat "$W/gate.out"
grep -E "Elapsed|Maximum resident|Percent of CPU|Exit status" "$W/gate.time"
sha256sum "$W/gate-$T.json" "$W/gate-$T.receipt.npz" "$W"/gate.out "$W"/gate.time "$W"/gate-$T.*.json 2>/dev/null
[ -e "$W/gate-$T.clipprep.npz" ] && echo "SEALED gate-$T.clipprep.npz bytes=$(stat -c %s "$W/gate-$T.clipprep.npz") sha256=$(sha256sum "$W/gate-$T.clipprep.npz" | cut -d' ' -f1)"
echo "end=$(date -u +%FT%TZ)"
exit $rc      # A1a.1 round: sacct's state is the step's (run 1 read COMPLETED 0:0 on rc 1)
JOB
echo "job script sha256 $(sha256sum "$W/sbatch-ll5d-gate.sh" | cut -d' ' -f1)"
find "$ND/of_inputs_5d.npz" "$P/s5c-20260924/runs/p2/bkg_dump.npz" "$ND/bank_sweep_5d_bkgaware" "$P/s5p-20260926/bank_detector" \
  "$P/fd-1b-20261030/pins.json" "$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt" \
  "$P/fd-1b-staged-20261102/stage1/in/flux_universes.npz" "$P/fd-f1-20261027/f1b3/prep" "$P/fd-1b-inv-20261101/i0/in" \
  -type f -printf "%A@\t%p\n" | sort -k2 > "$W/atime-pre.tsv" || stop "atime snapshot"
echo "atime-pre $(wc -l < "$W/atime-pre.tsv") files at $(date -u +%FT%TZ)"
jid=$(sbatch --parsable -A m3246 -q regular -C cpu -N 1 --exclusive -t "$TL" -J "$J" -o "$W/logs/%x_%j.out" \
  "$W/sbatch-ll5d-gate.sh" "$DD" "$M" "$W" "$T" "$CAL" "$CALSHA" "$CALNPZSHA" "$TLS") || stop sbatch
jid=${jid%%;*}; echo "Submitted batch job $jid"
tl=$(scontrol show job "$jid" | grep -oE "TimeLimit=[^ ]*"); echo "$tl"
[ "$tl" = "TimeLimit=1-07:00:00" ] || { scancel "$jid"; stop "the time limit parsed as ${tl#TimeLimit=}, not 1-07:00:00 (31 h): cancelled $jid"; }
scontrol show job "$jid" | grep -oE "(JobName|JobState|TimeLimit|Partition|QOS|NumNodes|Account|OverSubscribe)=[^ ]*" | tr '\n' ' '; echo
echo "end=$(date -u +%FT%TZ)"
