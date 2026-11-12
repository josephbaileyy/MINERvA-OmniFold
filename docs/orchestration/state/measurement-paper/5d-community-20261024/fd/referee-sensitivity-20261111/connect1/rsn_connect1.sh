#!/bin/bash
# RSN connect 1 (RSN-BINDING-1 rulings 3 and 4; RSN-DECLARATION.md rev 3 §6 step 3), on one Perlmutter login node in
# the foreground of a detached session, at 0 node-h. It runs only on the director's go for this script's sha256 and
# the launcher's. It does NOT write fence.txt and does NOT submit anything: the director announces the rsn_ family to
# every fenced lane first, and fence.txt and J1 are a later connect.
#   1 a fresh clone of the repository at M_RSN into $D (the deploy every RSN job will name): HEAD = M_RSN, no modified
#     or untracked file, and the nine §7 files at their bound sha256s;
#   2 the four NC-R inputs staged into $OUT/stage by os.open(O_RDONLY | O_NOATIME) copies: each copy's sha256 must
#     equal its pin, and the source's size, mtime and atime must be unchanged by the copy. The flux constraint file is
#     an input of the running LL5D gates, whose atime-post check STOPped cov2d's AR23 attempt 1 when that file's atime
#     moved; the other three are staged the same way so that no shared input is read plainly. The bound code reads
#     only the copies (same bytes, so its own sha256 pins hold);
#   3 rsn_prep.py --ratios $PVL_PREP/ratios/L-5D-PV --out $OUT/prep, as declared (pv-ladder's frozen prep is not a gate
#     input and is archived on HPSS, #1085); its stdout is the rsn-prep-SHA256SUMS to commit;
#   4 the NC-R gate: rsn_regrade.py --nominal-only on the staged table, S1, cpl block and flux file -> $OUT/nc_r.json;
#   5 ruling 4 (audit low r1): nc_r.json's recorded code_sha256 of rsn_regrade.py is printed beside the deployed file's
#     sha256, and the two must be equal (they must also equal the bound 661608d8...);
#   6 every product is printed in full (prep.json, the sums, nc_r.json) for the receipt PR.
# Any failure is a STOP: nothing is repaired, retried or deleted except this script's own /dev/shm copy and $B/tmp.
# It refuses before writing anything if: the host is not loginNN; a Slurm job is set; $B exists; an input is missing;
# an rsn_ job is queued or running. Threads 1, nice 19. No set -u. Launched from a /dev/shm copy of itself ($1).
SELF=$1
PIN=af7112989417f180e846573c31d101e44e6b02f9
P=/pscratch/sd/j/josephrb
B=$P/rsn-20261112
D=$B/deploy
OUT=$B/out
PVL_PREP=$P/pv-ladder-20261024/prep
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
REPO=https://github.com/josephbaileyy/MINERvA-OmniFold.git
INPUTS="table $P/fd-f1-20261027/grade/fd_f1_experiments.npz 997c7dae34ef9703291baece51eed05f3dd7d38a043630cac9667efaad2775bc
s1_npz $P/s1-20261024/s1_assembly.npz db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4
extra_block $P/fd-ct-5b-addition-20261031/with/block/cpl_block.npz d9aa32fdb64357760348c9ccbc32fbea81d517f0f0786eedf17ab4946eaca59f
flux $P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2"
BOUND="7b0fc567776d2016897173b1f8ab723fd99daedd34454537b36cd42bd03194be nd-unfolding/rsn/rsn_prep.py
5796bb6043a0ff646043206ef3ef623cbaf19d003875331da54a5642454e3690 nd-unfolding/rsn/rsn_unfold.py
ab63292122bffbc30e5d85efc2a5ae3f96c7f917891a856c48e2d26414848a48 nd-unfolding/rsn/rsn_cmodel.py
661608d81ccf7ca0ab08aee853f5934d4c0dab89677e82f8292239fee60b7652 nd-unfolding/rsn/rsn_regrade.py
4dd37197f6aa6c7f013b3ffea5558fd8d8fd1bc124047f761269adafce87e484 nd-unfolding/rsn/rsn_read.py
f889a0cf4de4a78aa7096bc01341ab6f3e6cdb41438267918519da7a527051d6 nd-unfolding/rsn/sbatch_rsn.sh
354bd16dd4d8b9dd5462f1daf6114e7beb467be3ab80e28b8ff212f51ea55616 nd-unfolding/rsn/rsn_tasks.tsv
887dbccd648e8648c03810e8d7ef335e09e5dfc7d97d4098c608db8de7bcaf29 nd-unfolding/rsn/test_rsn.py
8075fe8c9befed9184924fbab614ed81bf8c46bcfa112c7420a8c1a34d33f483 nd-unfolding/rsn/rsn_mutation.py"
REGRADE_SHA=661608d81ccf7ca0ab08aee853f5934d4c0dab89677e82f8292239fee60b7652

bail() { echo "REFUSED (nothing written): $*"; rm -f -- "$SELF"; exit 9; }
case "$(hostname -s)" in login[0-9][0-9]) ;; *) bail "host $(hostname -s) is not a login node" ;; esac
[ -z "$SLURM_JOB_ID" ] || bail "a Slurm job is set ($SLURM_JOB_ID)"
[ -x "$PY" ] || bail "no $PY"
[ ! -e "$B" ] || bail "$B exists"
[ -d "$PVL_PREP/ratios/L-5D-PV" ] || bail "no $PVL_PREP/ratios/L-5D-PV"
while read -r key path sha; do [ -f "$path" ] || bail "no $key input $path"; done <<< "$INPUTS"
q=$(squeue --me -h -o '%i|%j|%T') || bail "squeue failed"
printf '%s\n' "$q" | awk -F'|' '$2 ~ /^rsn_/ {f=1} END {exit !f}' && bail "an rsn_ job is queued or running: $q"

mkdir -p "$OUT/stage" "$OUT/logs" "$B/tmp" || bail "mkdir rc=$?"
exec > >(tee -a "$OUT/logs/connect1.log") 2>&1
finish() {
  rm -rf -- "$B/tmp"; echo "== rsn connect 1 rc=$1 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; sleep 1; exit "$1"
}
stop() { echo "STOP: $*"; finish 8; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export TMPDIR="$B/tmp" PYTHONDONTWRITEBYTECODE=1
RUNPY=(env -u PYTHONPATH nice -n 19 "$PY" -I -B)
echo "node $(hostname) $(date -u +%FT%TZ) slurm_job='$SLURM_JOB_ID'; connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "squeue --me:"; printf '%s\n' "$q"
echo "python $("$PY" -V 2>&1); numpy $(env -u PYTHONPATH "$PY" -I -B -c 'import numpy; print(numpy.__version__)')"

echo "== 1 clone at $PIN into $D"
git clone --quiet --filter=blob:none --no-checkout "$REPO" "$D" || stop "clone failed"
git -C "$D" -c advice.detachedHead=false checkout --quiet "$PIN" || stop "checkout failed"
head=$(git -C "$D" rev-parse HEAD)
porc=$(git -C "$D" status --porcelain --untracked-files=all | wc -l)
echo "HEAD $head; porcelain lines (untracked included) $porc"
[ "$head" = "$PIN" ] && [ "$porc" -eq 0 ] || stop "the deploy is not $PIN clean"
while read -r want rel; do
  got=$(sha256sum "$D/$rel" | cut -d' ' -f1); echo "sha256 $got $rel"
  [ "$got" = "$want" ] || stop "$rel is not at its bound sha256 $want"
done <<< "$BOUND"

echo "== 2 stage the NC-R inputs by O_NOATIME copy into $OUT/stage"
printf '%s\n' "$INPUTS" > "$B/tmp/inputs.txt"
"${RUNPY[@]}" - "$OUT/stage" "$B/tmp/inputs.txt" <<'PY' || stop "staging failed"
import hashlib, os, sys
stage, lst = sys.argv[1:3]
for line in open(lst).read().splitlines():
    key, src, pin = line.split()
    s0 = os.stat(src)
    dst = os.path.join(stage, os.path.basename(src))
    if os.path.exists(dst):
        print(f"STAGE STOP {key}: {dst} exists"); sys.exit(8)
    h, n = hashlib.sha256(), 0
    fi = os.open(src, os.O_RDONLY | os.O_NOATIME)          # EPERM raises here; there is no plain retry
    with open(dst, "wb") as fo:
        while True:
            b = os.read(fi, 1 << 24)
            if not b:
                break
            h.update(b); fo.write(b); n += len(b)
    os.close(fi)
    s1 = os.stat(src)
    if (s0.st_size, s0.st_mtime_ns, s0.st_atime_ns) != (s1.st_size, s1.st_mtime_ns, s1.st_atime_ns):
        print(f"STAGE STOP {key}: {src}: size, mtime or atime changed by the copy"); sys.exit(8)
    if n != s0.st_size or os.path.getsize(dst) != s0.st_size:
        print(f"STAGE STOP {key}: {src}: {n} bytes read, copy {os.path.getsize(dst)}, size {s0.st_size}"); sys.exit(8)
    if h.hexdigest() != pin:
        print(f"STAGE STOP {key}: {src}: sha256 {h.hexdigest()} is not its pin {pin}"); sys.exit(8)
    os.chmod(dst, 0o444)
    print(f"STAGE OK {key}: {src} -> {dst}: {n} bytes, sha256 {pin}, size/mtime/atime unchanged "
          f"({s0.st_size} {s0.st_mtime_ns} {s0.st_atime_ns})")
PY
st() { echo "$OUT/stage/$(basename "$(printf '%s\n' "$INPUTS" | awk -v k="$1" '$1 == k {print $2}')")"; }

echo "== 3 rsn_prep"
( cd "$B" && timeout 900 "${RUNPY[@]}" "$D/nd-unfolding/rsn/rsn_prep.py" --ratios "$PVL_PREP/ratios/L-5D-PV" \
    --out "$OUT/prep" > "$OUT/logs/rsn_prep.out" 2> "$OUT/logs/rsn_prep.err" )
r=$?; echo "rsn_prep rc=$r"; cat "$OUT/logs/rsn_prep.err"
[ $r = 0 ] || stop "rsn_prep rc=$r"
grep -E '^[0-9a-f]{64}  \./' "$OUT/logs/rsn_prep.out" > "$OUT/rsn-prep-SHA256SUMS"
echo "rsn_prep stdout: $(wc -l < "$OUT/logs/rsn_prep.out") lines, $(wc -l < "$OUT/rsn-prep-SHA256SUMS") of the sums form"
echo "== FILE rsn-prep-SHA256SUMS sha256 $(sha256sum "$OUT/rsn-prep-SHA256SUMS" | cut -d' ' -f1)"
cat "$OUT/rsn-prep-SHA256SUMS"; echo "== END rsn-prep-SHA256SUMS"
echo "== check: every listed file exists under $OUT/prep at its listed sha256, and every file but prep.json is listed"
( cd "$OUT/prep" && sha256sum -c --strict --quiet "$OUT/rsn-prep-SHA256SUMS" ) || stop "the prep's files do not match its sums"
nfiles=$(cd "$OUT/prep" && find . -type f ! -name prep.json | wc -l)
[ "$nfiles" -eq "$(wc -l < "$OUT/rsn-prep-SHA256SUMS")" ] && [ "$nfiles" -gt 0 ] \
  || stop "$nfiles files under $OUT/prep but $(wc -l < "$OUT/rsn-prep-SHA256SUMS") listed"
echo "== FILE prep.json sha256 $(sha256sum "$OUT/prep/prep.json" | cut -d' ' -f1)"
cat "$OUT/prep/prep.json"; echo "== END prep.json"

echo "== 4 NC-R gate"
( cd "$B" && timeout 900 "${RUNPY[@]}" "$D/nd-unfolding/rsn/rsn_regrade.py" --nominal-only \
    --table "$(st table)" --s1-npz "$(st s1_npz)" --extra-block "$(st extra_block)" --flux-constraint "$(st flux)" \
    --out "$OUT/nc_r.json" > "$OUT/logs/nc_r.out" 2> "$OUT/logs/nc_r.err" )
r=$?; echo "rsn_regrade --nominal-only rc=$r"; cat "$OUT/logs/nc_r.out" "$OUT/logs/nc_r.err"
[ $r = 0 ] || stop "NC-R rc=$r"
[ -f "$OUT/nc_r.json" ] || stop "no $OUT/nc_r.json"
echo "== FILE nc_r.json sha256 $(sha256sum "$OUT/nc_r.json" | cut -d' ' -f1)"
cat "$OUT/nc_r.json"; echo "== END nc_r.json"
grep -q '"schema": "rsn-nc-r/1"' "$OUT/nc_r.json" && grep -q '"verdict": "PASS"' "$OUT/nc_r.json" \
  || stop "nc_r.json records no rsn-nc-r/1 PASS"

echo "== 5 ruling 4 (r1): nc_r.json's recorded rsn_regrade.py sha256 beside the deployed file's"
rec=$("$PY" -I -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["code_sha256"]["rsn_regrade.py"])' "$OUT/nc_r.json")
dep=$(sha256sum "$D/nd-unfolding/rsn/rsn_regrade.py" | cut -d' ' -f1)
echo "recorded $rec"; echo "deployed $dep"; echo "bound    $REGRADE_SHA"
[ "$rec" = "$dep" ] && [ "$dep" = "$REGRADE_SHA" ] || stop "r1: the recorded, deployed and bound sha256s are not all equal"
echo "R1 EQUAL"

porc=$(git -C "$D" status --porcelain --untracked-files=all | wc -l)
echo "deploy porcelain after (untracked included) $porc"
[ "$porc" -eq 0 ] || stop "the deploy is no longer clean"
echo "fence.txt present: $([ -e "$OUT/fence.txt" ] && echo yes || echo no) (connect 1 never writes it)"
echo "CONNECT 1 PASS: deploy clean at $PIN; prep built; NC-R PASS; r1 equal. fence.txt and J1 wait for the director."
finish 0
