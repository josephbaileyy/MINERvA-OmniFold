#!/bin/bash
# Band diagnosis, P4: the readout (FD-1B-BAND-DIAGNOSIS-DECLARATION.md sections 4.4-4.7 and 5; BINDING-1 rulings 2, 5
# and 6). Login node, nice 19, 0 node-h, no Slurm job, after P3's post. Every step stamped to the second. In order:
#   1. the fence (A1): every josephrb job must be named fd1b_bdg_*, ll5d_* or prr_*, and no fd1b_bdg_* job may be
#      queued (P3 must have ended);
#   2. P2's deploy $W/deploy is still M with no tracked change, the module still 658ca918, and the clone's Part 1
#      readout.json (8e05ca9b) and I0's i0.json (9a4142d3) gated on sha256; P3's post must have counted 126 products;
#   3. thread variables as Part 1's P4 and this campaign's P1: nothing exported; recorded as inherited and in Python;
#   4. section 5: the 73 sources re-stat'd into $W/p4/stat-before-readout.txt and compared byte for byte with P1's
#      stat-before.txt (7986e2bf); any difference is a STOP and the readout does not run;
#   5. `fd_1b_band_diag.py readout` on $V/stage, $V/unf, $W/unf, the deploy's i0.json and readout.json, writing
#      $W/p4/readout.json (the module refuses to overwrite). It validates all 126 products (identity, the one-code keys
#      less estimator_seed, the estimator at each product's seed), requires seed 42's F_src and resolved cells to equal
#      Part 1's, and gives sections 4.4-4.6's readings. It reads only through O_NOATIME. A refusal (rc 4) is reported
#      unrepaired;
#   6. the 73 sources re-stat'd again into $W/p4/stat-after-readout.txt and compared; any difference is a STOP (rc 4);
#   7. readout.json, its stdout and the two stats printed with their sha256.
# Nothing is deleted or written under $V. Launched from a /dev/shm copy of itself ($1), which it deletes.
SELF=$1
M=83ac32fb5024026ac6c51c0621d5ae9ff9073370
W=/pscratch/sd/j/josephrb/fd-1b-band-diag-20261109
V=/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
MOD_SHA=658ca91849a8151a4fb801e41004102f0ba621c367f1c23146a8fc3a580484df
RO_SHA=8e05ca9bc2d0f2142b5c8d2bff28f05176c48f27454218390f09658344cea7b0
I0_SHA=9a4142d348f591134ba4912a2197ca958ea387ec58b095622bce5f206d007021
BASE_SHA=7986e2bf31aac583c03273f96804c2adaac85bcfdde5bd4b3da5b0f834c95b22
RO=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/precheck-fd/p4/records/p4/readout.json
I0=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/inv/i0/i0.json
ts() { date -u +%FT%TZ; }
finish() { echo "== bdg-p4 rc=$1 $(ts)"; rm -f -- "$SELF"; exit "$1"; }
restat() {
  env -u PYTHONPATH "$PY" -B -c 'import sys; [print(l.rsplit("|", 1)[1]) for l in open(sys.argv[1]).read().splitlines()]' "$W/stat-before.txt" \
    | while read -r f; do stat -c '%F|%i|%h|%s|%Y|%X|%Z|%n' "$f" 2>&1; done > "$1"
}
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; finish 9 ;; esac
echo "node $(hostname) $(ts)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
[ "$(sha256sum "$W/stat-before.txt" | cut -d' ' -f1)" = "$BASE_SHA" ] || { echo "STOP: stat-before.txt is not 7986e2bf"; finish 9; }
[ ! -e "$W/p4" ] || { echo "STOP: $W/p4 already exists"; finish 9; }
echo "== 1. fence $(ts)"
out=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l'); frc=$?
echo "squeue rc=$frc; rows:"; printf '%s\n' "$out"; echo "-- end rows"
bad=$(printf '%s\n' "$out" | awk -F'|' 'NF && ($2 !~ /^(fd1b_bdg_|ll5d_|prr_)/ || $2 ~ /^fd1b_bdg_/)')
echo "refusing rows: [$bad]"
[ "$frc" -eq 0 ] && [ -z "$bad" ] || { echo "STOP: the fence is not clear, or an fd1b_bdg_* job is still queued"; finish 3; }
echo "FENCE: clear"
echo "== 2. the deploy and the committed inputs $(ts)"
head=$(git -C "$W/deploy" rev-parse HEAD); porc=$(git -C "$W/deploy" status --porcelain --untracked-files=no | wc -l)
echo "deploy HEAD $head; tracked porcelain $porc"
[ "$head" = "$M" ] && [ "$porc" -eq 0 ] || { echo "STOP: the deploy is not M clean"; finish 5; }
for pair in "nd-unfolding/fd_1b_band_diag.py:$MOD_SHA" "$RO:$RO_SHA" "$I0:$I0_SHA"; do
  f=${pair%%:*}; want=${pair##*:}; got=$(sha256sum "$W/deploy/$f" | cut -d' ' -f1)
  echo "sha256 $got (bound $want) $f"
  [ "$got" = "$want" ] || { echo "STOP: $f is not the bound file"; finish 5; }
done
np=$(find "$W/unf" -maxdepth 1 -type f -name '*.npz' | wc -l); echo "products in $W/unf: $np"
[ "$np" -eq 126 ] || { echo "STOP: $np products, not 126"; finish 6; }
mkdir -m 700 "$W/p4" || finish 9
cd "$W/deploy/nd-unfolding" || finish 5
export PYTHONDONTWRITEBYTECODE=1
echo "== 3. thread variables as inherited (none exported): OMP_NUM_THREADS=${OMP_NUM_THREADS-<unset>} OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS-<unset>} MKL_NUM_THREADS=${MKL_NUM_THREADS-<unset>} NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS-<unset>}"
nice -n 19 env -u PYTHONPATH "$PY" -B -c 'import os, numpy as np; print("thread variables (python):", {k: os.environ.get(k, "<unset>") for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")}, "numpy", np.__version__)'
echo "== 4. section 5: the 73 sources against P1's stat-before.txt $(ts)"
restat "$W/p4/stat-before-readout.txt"
echo "stat-before-readout.txt: $(wc -l < "$W/p4/stat-before-readout.txt") lines; sha256 $(sha256sum "$W/p4/stat-before-readout.txt" | cut -d' ' -f1)"
if cmp -s "$W/stat-before.txt" "$W/p4/stat-before-readout.txt"; then echo "sources: byte-identical to P1's stat-before"; else echo "STOP: a source's stat moved; the readout does not run:"; diff "$W/stat-before.txt" "$W/p4/stat-before-readout.txt" | head -40; finish 4; fi
echo "== 5. the readout $(ts)"
nice -n 19 env -u PYTHONPATH "$PY" -B fd_1b_band_diag.py readout --staged "$V/stage" --part1-unfolds "$V/unf" --unfolds "$W/unf" \
  --i0 "$W/deploy/$I0" --readout "$W/deploy/$RO" --out "$W/p4/readout.json" > "$W/p4/readout.stdout" 2> "$W/p4/readout.stderr"
r=$?
echo "readout rc=$r $(ts)"
cat "$W/p4/readout.stdout"; cat "$W/p4/readout.stderr"
echo "== 6. section 5: the 73 sources after the readout $(ts)"
restat "$W/p4/stat-after-readout.txt"
echo "stat-after-readout.txt: $(wc -l < "$W/p4/stat-after-readout.txt") lines; sha256 $(sha256sum "$W/p4/stat-after-readout.txt" | cut -d' ' -f1)"
moved=0
if cmp -s "$W/stat-before.txt" "$W/p4/stat-after-readout.txt"; then echo "sources: byte-identical to P1's stat-before"; else echo "STOP: a source's stat moved during the readout:"; diff "$W/stat-before.txt" "$W/p4/stat-after-readout.txt" | head -40; moved=1; fi
echo "== 7. records"
for f in readout.json readout.stdout readout.stderr stat-before-readout.txt stat-after-readout.txt; do [ -f "$W/p4/$f" ] && echo "sha256 $(sha256sum "$W/p4/$f" | cut -d' ' -f1) p4/$f"; done
echo "== readout.json"; [ -f "$W/p4/readout.json" ] && cat "$W/p4/readout.json" || echo "(not written)"
echo "== end of records"
[ "$moved" -eq 0 ] || finish 4
finish "$r"
