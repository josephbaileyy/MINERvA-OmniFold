#!/bin/bash
# REF-C2C1 step two, stage 3b: the READ, second run (REF-C2C1-BINDING-2.md ruling 2.3; the director's rulings of
# 2026-11-06, #825, and on C-PUB's operand, #839 and #842: the read is bound at M' = af70e9c4, re-run in a fresh
# directory $O/read-2 with the stopped read's $O/read left as it is, cells.root copied from $O/read by O_NOATIME and
# required to be f06e4a26), on a login node, 0 node-h, under the binding's fixed conditional sequence. It refuses
# unless (a) stage 2 passed: CENTRALS-DONE is the accepted record, and (the director's ruling of 2026-11-06 on the four
# TIMEOUT jobs) in a fresh clone, `git fetch origin main`, the committed REPLICAS-TIMEOUT-j0..3 (units-replicas/timeout/)
# and REPLICAS-DONE-j4 (units-replicas/completion/) each hash equal to the pscratch record; each TIMEOUT record has
# watch_moved 0 and porcelain 0, and DONE-j4 has every unit PASS, rcs 0, watch_moved 0, porcelain 0, concurrent 1;
# the five records' unit sets (the TIMEOUT pass_units, DONE-j4's unit_list) are disjoint, their union is the 350 of
# lanes.tsv (7b737d0c), and every unit in it has a PASS done-marker (O_NOATIME reads); and (b) 3a's cells file is on
# main: the committed fd/receipts-ref-c2c1/step2/cells/cells.root hashes to f06e4a26..., equal to the read directory's.
# Then,
# from that clone checked out at M (porcelain --ignored 0, the binding's 8 blobs):
#   ref_c2c1_read.py read --run $O/units --cells $R/cells.root --cells-sha256 f06e4a26... --out $R/readout.json
# in root_6_28, nice 19, idle I/O, 4 threads. The read stages E_R's central and replicas and the publication through
# O_NOATIME into $R/inputs/ (which must not exist) under its guards. The 303 COV2D inputs are stat'd (no read) before and
# after: a moved atime is a STOP. The reader's stdout (it prints the readings) goes to read.stdout, not read.log. The
# fence is a recorded line. Porcelain --ignored before and after. Writes only under $R and $O/deploy-read. No set -u.
# Launched from a /dev/shm copy of itself (its path is $1), which it deletes at exit.
SELF=$1
O=/pscratch/sd/j/josephrb/ref-c2c1-20261106
R=$O/read-2
D=$O/deploy-read-2
M=af70e9c4685acdf2d64e30d812942bea1e7ccb0c
CELLS_SHA=f06e4a26efc3085eac71d80fce5f806f17dc04cb89bfcc51ee2c939332aed743
CELLS_PATH=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ref-c2c1/step2/cells/cells.root
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
LANES_SHA=7b737d0c4bb5e547adae0376f9c50da00cc1ec9a08d7dc2c892804e0b968524c
UP=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ref-c2c1/step2/units-replicas
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in login*) ;; *) bail ;; esac
[ -s "$O/read/cells.root" ] && [ ! -e "$R" ] && [ -d "$O/units" ] && [ -x "$PY" ] && [ -s "$O/logs-replicas/cov2d-watch-paths.txt" ] && [ -s "$O/logs-replicas/lanes.tsv" ] || bail
for x in readout.json STOP.json inputs read.log read.stdout read.done read.time logs-read; do [ ! -e "$R/$x" ] || bail; done
[ ! -e "$D" ] || bail
LR=$R/logs-read
mkdir -p "$LR" || bail
exec > "$R/read.log" 2>&1
finish() { echo "ref-c2c1 read rc=$1"; date -u +%FT%TZ; echo "$1" > "$R/read.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "read script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
dd if="$O/read/cells.root" iflag=noatime status=none of="$R/cells.root" || { echo "STOP: copying cells.root"; finish 4; }
echo "cells.root copied from $O/read by O_NOATIME: sha256 $(sha256sum "$R/cells.root" | cut -d' ' -f1) (required $CELLS_SHA)"
[ "$(sha256sum "$R/cells.root" | cut -d' ' -f1)" = "$CELLS_SHA" ] || { echo "STOP: the copied cells.root is not f06e4a26"; finish 4; }
cp "$SELF" "$LR/refc2c1_read_login.sh"
echo "fence, recorded: squeue -u josephrb at $(date -u +%FT%TZ):"; squeue -u josephrb -h -o '%i|%j|%T|%M|%l' | sed 's/^/  /'
cd_rec=$(cat "$O/CENTRALS-DONE"); echo "gate: CENTRALS-DONE $cd_rec"
[ "$cd_rec" = '{"job": "60889566", "rcs": "0 0 0", "pass_markers": 3, "porcelain_after": 0}' ] || { echo "STOP: CENTRALS-DONE is not the accepted record"; finish 4; }
lc=$(dd if="$R/cells.root" iflag=noatime status=none | sha256sum | cut -d' ' -f1)
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$LR/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" fetch -q origin main >> "$LR/clone.log" 2>&1 || { echo "STOP: fetch origin main"; finish 3; }
echo "origin/main $(git -C "$D" rev-parse origin/main)"
for rec in timeout/REPLICAS-TIMEOUT-j0 timeout/REPLICAS-TIMEOUT-j1 timeout/REPLICAS-TIMEOUT-j2 timeout/REPLICAS-TIMEOUT-j3 completion/REPLICAS-DONE-j4; do
  ms=$(git -C "$D" show "origin/main:$UP/$rec" 2>/dev/null | sha256sum | cut -d' ' -f1)
  ps=$(dd if="$O/${rec#*/}" iflag=noatime status=none | sha256sum | cut -d' ' -f1)
  echo "gate: ${rec#*/} origin/main $ms; pscratch $ps"
  [ "$ms" = "$ps" ] && [ "$ms" != e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 ] || { echo "STOP: ${rec#*/} is not on main (the read waits for the merge)"; finish 4; }
done
"$PY" -B -I - "$O" "$LANES_SHA" <<'PYEOF'
import hashlib, json, os, sys
O, lanes_sha = sys.argv[1:3]
def rd(p):
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    with os.fdopen(fd, "rb") as f: return f.read()
lanes = rd(os.path.join(O, "logs-replicas", "lanes.tsv"))
if hashlib.sha256(lanes).hexdigest() != lanes_sha: print("STOP: lanes.tsv is not the reviewed one"); sys.exit(4)
declared = [ln.split("\t")[2].replace(":", "_b") for ln in lanes.decode().splitlines() if ln.strip() and not ln.startswith("#")]
bad, sets = [], []
for j in range(4):
    r = json.loads(rd(os.path.join(O, f"REPLICAS-TIMEOUT-j{j}")))
    if not (r["state"] == "TIMEOUT" and r["watch_moved"] == 0 and r["porcelain_after"] == 0 and r["pass_markers"] == len(r["pass_units"])):
        bad.append(f"REPLICAS-TIMEOUT-j{j}")
    sets.append(r["pass_units"])
r = json.loads(rd(os.path.join(O, "REPLICAS-DONE-j4")))
if not (r["index"] == 4 and r["units"] == r["pass_markers"] == len(r["unit_list"]) and r["watch_moved"] == 0
        and r["porcelain_after"] == 0 and r["concurrent"] == 1 and set(r["rcs"].split()) == {"0"}):
    bad.append("REPLICAS-DONE-j4")
sets.append(r["unit_list"])
union = set().union(*sets)
disjoint = sum(map(len, sets)) == len(union)
notpass = [u for u in sorted(union) if json.loads(rd(os.path.join(O, "units", u + ".done"))).get("verdict") != "PASS"]
print(f"gate: records failing their fields {bad}; unit sets {[len(x) for x in sets]}, disjoint {disjoint}, union {len(union)}, "
      f"equal to the {len(set(declared))} of lanes.tsv {union == set(declared)}; without a PASS marker {notpass}")
ok = not bad and disjoint and len(declared) == len(set(declared)) == 350 and union == set(declared) and not notpass
sys.exit(0 if ok else 4)
PYEOF
[ $? -eq 0 ] || { echo "STOP: stage 2 did not pass (the five records' unit sets are not the 350, each PASS)"; finish 4; }
mc=$(git -C "$D" show "origin/main:$CELLS_PATH" 2>/dev/null | sha256sum | cut -d' ' -f1)
echo "cells: origin/main $(git -C "$D" rev-parse origin/main) $mc; read directory $lc; expected $CELLS_SHA"
[ "$mc" = "$CELLS_SHA" ] && [ "$lc" = "$CELLS_SHA" ] || { echo "STOP: 3a's cells file is not on main (the read waits for the merge)"; finish 4; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
128b4e00505f82153d1d400a482b7b1a5a3d56be 2d-unfolding/ref_c2c1/ref_c2c1.py
1baf74b5163ff36e22fb66c4b13dc17c6a92d400 2d-unfolding/ref_c2c1/ref_c2c1_read.py
f27545e9ca70382a318eb284a0c9ea01cc0e5891 2d-unfolding/ref_c2c1/config.json
4633f384392cbb7d18e159d72bffbe81aca19a8d 2d-unfolding/ref_c2c1/test_ref_c2c1.py
a2ce6e48a0d3b65b3d7467bd7b72dfd0cf436817 2d-unfolding/ref_c2c1/ref_c2c1_mutation.py
f2711d4ea81141205f6ef8a450707051713faf20 2d-unfolding/ref_c2c1/run_suite.py
1d3f971f2b2a3a0cc9cf477b6f11061d8f35f07e 2d-unfolding/ref_c2c1/run_tests.sh
990ec7894a982709298ce3550ffa3fa1e73fe1b9 2d-unfolding/ref_c2c1/test_run_suite.py
BLOBS
echo "bound blobs: 8 checked, $bad mismatches"; [ "$bad" -eq 0 ] || { echo "STOP: bound bytes"; finish 9; }
xargs -d '\n' stat -c '%U %a %X %s %n' < "$O/logs-replicas/cov2d-watch-paths.txt" > "$LR/watch-before.txt" 2>&1
echo "COV2D inputs stat'd before: $(wc -l < "$LR/watch-before.txt"); not owned by josephrb: $(awk '$1 != "josephrb"' "$LR/watch-before.txt" | wc -l)"
(
  eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
  conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; exit 2; }
  export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
  echo "interpreter $PY: $("$PY" -c 'import sys; print(sys.version.replace(chr(10), " "))'); threads 4; nice 19; ionice idle"
  cd "$D" && nice -n 19 ionice -c3 /usr/bin/time -v -o "$R/read.time" "$PY" -B 2d-unfolding/ref_c2c1/ref_c2c1_read.py read \
      --run "$O/units" --cells "$R/cells.root" --cells-sha256 "$lc" --out "$R/readout.json" > "$R/read.stdout"
)
rc=$?
echo "read rc=$rc"
grep -E 'Elapsed|Maximum resident' "$R/read.time"
[ -s "$R/readout.json" ] && echo "readout.json sha256 $(sha256sum "$R/readout.json" | cut -d' ' -f1)"
[ -e "$R/STOP.json" ] && echo "STOP.json written: sha256 $(sha256sum "$R/STOP.json" | cut -d' ' -f1)"
echo "staged into inputs/: $(ls "$R/inputs" 2>/dev/null | wc -l) files"
echo "reader stdout (the readings; not echoed here) is $R/read.stdout"
xargs -d '\n' stat -c '%U %a %X %s %n' < "$O/logs-replicas/cov2d-watch-paths.txt" > "$LR/watch-after.txt" 2>&1
if cmp -s "$LR/watch-before.txt" "$LR/watch-after.txt"; then echo "COV2D inputs: no atime moved"; else echo "STOP: a COV2D input's stat changed:"; diff "$LR/watch-before.txt" "$LR/watch-after.txt" | head -20; fi
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
git -C "$D" status --porcelain --ignored | head -10
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
cmp -s "$LR/watch-before.txt" "$LR/watch-after.txt" || finish 8
finish $rc
