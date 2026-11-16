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
