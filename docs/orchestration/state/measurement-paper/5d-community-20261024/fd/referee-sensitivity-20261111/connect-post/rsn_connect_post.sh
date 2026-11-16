#!/bin/bash
# RSN post-run connect (RSN-DECLARATION.md rev 3 §6 step 5), on one Perlmutter login node, at 0 node-h. It runs only on
# the director's go for this script's sha256 and the launcher's, after J2 (61170759) and J3 (61170761) have ended.
#   1 refusals before anything is written: the host is not loginNN; a Slurm job is set; an rsn_ job is queued or
#     running; sacct does not show J2 as rsn_J2 and J3 as rsn_J3, each COMPLETED 0:0; a job log lacks its rc=0 line,
#     or a product's sha256 line, or a product on disk differs from it (J2's eight, J3's four); nc.json records no
#     rsn-nc/1 PASS; the deploy $D is not clean at M_P1 or a bound file is not at its sha256; a staged NC-R input in
#     $OUT/stage is not at its pin; $OUT/cmodel, $OUT/regrade.json or $OUT/rsn_readout.json exists;
#   2 rsn_cmodel.py build -> $OUT/cmodel/rsn_cmodel.{json,npz};
#   3 rsn_regrade.py on the staged inputs and the arm file -> $OUT/regrade.json;
#   4 rsn_read.py -> $OUT/rsn_readout.json;
#   5 each output is printed in full, with its sha256, for the receipt PR; then the read log.
# The guard's self-test opens a name that does not exist under a denied root (cov2d-run-20261104), so a guard that
# failed to refuse would touch no file.
# THE READ SET (the director's ruling of 2026-11-12: E96D's runs atime-check of_inputs_5d.npz and the s5c p2
# bkg_dump.npz, and may be running when this runs). The three tools read only:
#   - the deploy $D at M_P1 (the code, and the committed records it reads by repository path);
#   - RSN's own files under $OUT: products/ (J1-J3), prep/, nc.json, cmodel/ (written by step 2), and stage/, the
#     four NC-R inputs connect 1 copied there by O_NOATIME (fd_f1_experiments.npz, s1_assembly.npz, cpl_block.npz
#     and the NuE constraint file);
#   - pv-ladder's frozen products, $P/pv-ladder-20261024/products (rsn_cmodel.py build's frozen shifts; no E96D or
#     LL5D input);
#   - the python environment.
# This is enforced, not only stated: each tool runs under guard.py, a sys.addaudithook wrapper. On every "open" event,
# before the file is opened, it refuses (PermissionError, so the tool fails and the step STOPs) any path equal to or
# under DENY: of_inputs_5d.npz, bkg_dump.npz, the original NuE constraint file and prologue5's eight
# cov2d_protected_paths, compared after realpath. It logs every path opened, and the connect prints that log and
# STOPs if any opened path lies outside the read set above.
# Any failure is a STOP: nothing is repaired or retried. Threads 1, nice 19. No set -u. Launched from a /dev/shm copy
# of itself ($1), deleted at exit.
SELF=$1
PIN=5e43e509d08d9b294594988f2c21e50e281e7ad8
P=/pscratch/sd/j/josephrb
B=$P/rsn-20261112
D=$B/deploy-p1
OUT=$B/out
T=$B/tmp-post
J2_JOB=61170759; J3_JOB=61170761
J2_TASKS="G6_gibuu SM_genie_mec SM_nuwro SM_gibuu WR_data WR_closure_tune_v1 WR_closure_nuwro TR_data"
J3_TASKS="WR_closure_gibuu WR_closure_q3 WU_closure_gibuu WU_closure_q3"
PVL_PRODUCTS=$P/pv-ladder-20261024/products
P5_REL=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-f1/run/cluster/f1b3/prep/k1_p5_rerun.npz
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
STAGED="fd_f1_experiments.npz 997c7dae34ef9703291baece51eed05f3dd7d38a043630cac9667efaad2775bc
s1_assembly.npz db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4
cpl_block.npz d9aa32fdb64357760348c9ccbc32fbea81d517f0f0786eedf17ab4946eaca59f
sorted_NuEConstraint_FHC_RHC_IMD.txt e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2"
DENY="$P/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
$P/s5c-20260924/runs/p2/bkg_dump.npz
$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
$P/2d-closeout-re2-20261023/partb/out
$P/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root
$P/cov2d-run-20261104
$P/MINERvA-OmniFold/2d-unfolding/baseline_flux
$P/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root
/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root"
BOUND="7b0fc567776d2016897173b1f8ab723fd99daedd34454537b36cd42bd03194be nd-unfolding/rsn/rsn_prep.py
5796bb6043a0ff646043206ef3ef623cbaf19d003875331da54a5642454e3690 nd-unfolding/rsn/rsn_unfold.py
ab63292122bffbc30e5d85efc2a5ae3f96c7f917891a856c48e2d26414848a48 nd-unfolding/rsn/rsn_cmodel.py
661608d81ccf7ca0ab08aee853f5934d4c0dab89677e82f8292239fee60b7652 nd-unfolding/rsn/rsn_regrade.py
4dd37197f6aa6c7f013b3ffea5558fd8d8fd1bc124047f761269adafce87e484 nd-unfolding/rsn/rsn_read.py
f889a0cf4de4a78aa7096bc01341ab6f3e6cdb41438267918519da7a527051d6 nd-unfolding/rsn/sbatch_rsn.sh
354bd16dd4d8b9dd5462f1daf6114e7beb467be3ab80e28b8ff212f51ea55616 nd-unfolding/rsn/rsn_tasks.tsv
887dbccd648e8648c03810e8d7ef335e09e5dfc7d97d4098c608db8de7bcaf29 nd-unfolding/rsn/test_rsn.py
8075fe8c9befed9184924fbab614ed81bf8c46bcfa112c7420a8c1a34d33f483 nd-unfolding/rsn/rsn_mutation.py"

bail() { echo "REFUSED (nothing written): $*"; rm -f -- "$SELF"; exit 9; }
stop() { echo "STOP: $*"; rm -rf -- "$T"; echo "== rsn connect post rc=8 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit 8; }
case "$(hostname -s)" in login[0-9][0-9]) ;; *) bail "host $(hostname -s) is not a login node" ;; esac
[ -z "$SLURM_JOB_ID" ] || bail "a Slurm job is set ($SLURM_JOB_ID)"
[ -x "$PY" ] || bail "no $PY"
q=$(squeue --me -h -o '%i|%j|%T') || bail "squeue failed"
hit=$(printf '%s\n' "$q" | awk -F'|' '$2 ~ /^rsn_/')
[ -z "$hit" ] || bail "rsn_ jobs are queued or running: $hit"
acct=$(sacct -X -n -P -j "$J2_JOB,$J3_JOB" -o JobID,JobName,State,ExitCode,Elapsed) || bail "sacct failed"
for jj in "$J2_JOB rsn_J2" "$J3_JOB rsn_J3"; do
  set -- $jj
  printf '%s\n' "$acct" | awk -F'|' -v j="$1" -v n="$2" '$1 == j && $2 == n && $3 == "COMPLETED" && $4 == "0:0" {f=1} END {exit !f}' \
    || bail "$1 is not $2 COMPLETED 0:0 ($acct)"
done
for jt in "J2 $J2_JOB $J2_TASKS" "J3 $J3_JOB $J3_TASKS"; do
  set -- $jt; j=$1; id=$2; shift 2
  LOG="$OUT/logs/rsn_${j}_$id.out"
  grep -q "^\[rsn\] job=$j rc=0 " "$LOG" 2>/dev/null || bail "$LOG has no '[rsn] job=$j rc=0' line"
  for t in "$@"; do
    f="$OUT/products/$t.npz"
    psha=$(awk -v f="$f" '$2 == f && $1 ~ /^[0-9a-f]{64}$/ {print $1}' "$LOG")
    [ -n "$psha" ] || bail "$LOG has no sha256 line for $f"
    [ "$(sha256sum "$f" 2>/dev/null | cut -d' ' -f1)" = "$psha" ] || bail "$f on disk is not $j's logged $psha"
  done
done
grep -q '"schema": "rsn-nc/1"' "$OUT/nc.json" 2>/dev/null && grep -q '"verdict": "PASS"' "$OUT/nc.json" \
  || bail "$OUT/nc.json records no rsn-nc/1 PASS"
head=$(git -C "$D" rev-parse HEAD 2>/dev/null)
porc=$(git -C "$D" status --porcelain --untracked-files=all 2>/dev/null | wc -l)
[ "$head" = "$PIN" ] && [ "$porc" -eq 0 ] || bail "the deploy is not $PIN clean (HEAD=$head, $porc porcelain lines)"
while read -r want rel; do
  [ "$(sha256sum "$D/$rel" | cut -d' ' -f1)" = "$want" ] || bail "$rel is not at its bound sha256"
done <<< "$BOUND"
while read -r name want; do
  [ "$(sha256sum "$OUT/stage/$name" 2>/dev/null | cut -d' ' -f1)" = "$want" ] || bail "staged $name is not at its pin"
done <<< "$STAGED"
for f in "$OUT/cmodel" "$OUT/regrade.json" "$OUT/rsn_readout.json" "$T"; do [ ! -e "$f" ] || bail "$f exists"; done

mkdir -p "$T" || bail "mkdir $T"
echo "node $(hostname) $(date -u +%FT%TZ) slurm_job='$SLURM_JOB_ID'; connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "squeue --me:"; printf '%s\n' "$q"
echo "sacct:"; printf '%s\n' "$acct"
echo "J2's 8 and J3's 4 products: logged = on disk; nc.json PASS; deploy $head clean, bound shas; 4 staged inputs at pins"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export TMPDIR="$T" PYTHONDONTWRITEBYTECODE=1
printf '%s\n' "$DENY" > "$T/deny.txt"
printf '%s\n' "$D" "$OUT/products" "$OUT/prep" "$OUT/nc.json" "$OUT/cmodel" "$OUT/stage" "$OUT/regrade.json" \
  "$OUT/rsn_readout.json" "$PVL_PRODUCTS" "$T" > "$T/readset.txt"
cat > "$T/guard.py" <<'GUARD'
# guard.py <deny file> <open log> <script> [args]: runs <script> as __main__ under an audit hook that refuses, before
# the open, any path equal to or under a DENY entry (both sides realpath'd), and records every path opened.
import atexit, os, runpy, sys
deny_file, log_file, script = sys.argv[1:4]
DENY = [os.path.realpath(x) for x in open(deny_file).read().split("\n") if x.strip()]
seen, live = set(), [True]
def under(p, roots):
    return any(p == r or p.startswith(r.rstrip("/") + "/") for r in roots)
def hook(event, args):
    if event != "open" or not live[0]:
        return
    path = args[0]
    if isinstance(path, int) or path is None:
        return
    p = os.path.realpath(os.fsdecode(path))
    if under(p, DENY):
        raise PermissionError(f"RSN read-set guard: refusing to open {p}")
    seen.add(p)
def dump():
    live[0] = False
    with open(log_file, "w") as fo:
        fo.write("".join(f"{p}\n" for p in sorted(seen)))
atexit.register(dump)
sys.addaudithook(hook)
sys.argv = [script] + sys.argv[4:]
runpy.run_path(script, run_name="__main__")
GUARD
echo "guard.py sha256 $(sha256sum "$T/guard.py" | cut -d' ' -f1)"
G() { local tag=$1; shift; ( cd "$B" && timeout 1800 env -u PYTHONPATH nice -n 19 "$PY" -I -B "$T/guard.py" "$T/deny.txt" "$T/open-$tag.txt" "$@" ); }
echo "== 0 the guard refuses a denied path (self-test on a name that does not exist under a denied root)"
printf 'try:\n    open(%s)\nexcept PermissionError as e:\n    print("GUARD REFUSED:", e); raise SystemExit(0)\nexcept OSError as e:\n    print("GUARD DID NOT REFUSE:", e); raise SystemExit(1)\nprint("GUARD DID NOT REFUSE"); raise SystemExit(1)\n' \
  "'$P/cov2d-run-20261104/rsn-guard-selftest-absent'" > "$T/selftest.py"
G selftest "$T/selftest.py"; r=$?; echo "guard self-test rc=$r"
[ $r = 0 ] || stop "the guard did not refuse a denied path"

echo "== 2 rsn_cmodel.py build"
G build "$D/nd-unfolding/rsn/rsn_cmodel.py" build --rsn-products "$OUT/products" \
  --rsn-prep-sums "$D/nd-unfolding/rsn/rsn-prep-SHA256SUMS" --products "$PVL_PRODUCTS" --p5 "$D/$P5_REL" \
  --out-json "$OUT/cmodel/rsn_cmodel.json" --out-npz "$OUT/cmodel/rsn_cmodel.npz" > "$T/build.out" 2> "$T/build.err"
r=$?; echo "rsn_cmodel.py build rc=$r"; cat "$T/build.out" "$T/build.err"
[ $r = 0 ] || stop "rsn_cmodel.py build rc=$r"
echo "== 3 rsn_regrade.py"
G regrade "$D/nd-unfolding/rsn/rsn_regrade.py" --table "$OUT/stage/fd_f1_experiments.npz" \
  --s1-npz "$OUT/stage/s1_assembly.npz" --extra-block "$OUT/stage/cpl_block.npz" \
  --flux-constraint "$OUT/stage/sorted_NuEConstraint_FHC_RHC_IMD.txt" --rsn-cmodel "$OUT/cmodel/rsn_cmodel.npz" \
  --rsn-cmodel-json "$OUT/cmodel/rsn_cmodel.json" --out "$OUT/regrade.json" > "$T/regrade.out" 2> "$T/regrade.err"
r=$?; echo "rsn_regrade.py rc=$r"; cat "$T/regrade.out" "$T/regrade.err"
[ $r = 0 ] || stop "rsn_regrade.py rc=$r"
echo "== 4 rsn_read.py"
G read "$D/nd-unfolding/rsn/rsn_read.py" --prep "$OUT/prep/prep.json" --cmodel "$OUT/cmodel/rsn_cmodel.json" \
  --regrade "$OUT/regrade.json" --out "$OUT/rsn_readout.json" > "$T/read.out" 2> "$T/read.err"
r=$?; echo "rsn_read.py rc=$r"; cat "$T/read.out" "$T/read.err"
[ $r = 0 ] || stop "rsn_read.py rc=$r"

echo "== 5 the outputs"
echo "== FILE cmodel/rsn_cmodel.npz sha256 $(sha256sum "$OUT/cmodel/rsn_cmodel.npz" | cut -d' ' -f1)"
for f in cmodel/rsn_cmodel.json regrade.json rsn_readout.json; do
  [ -f "$OUT/$f" ] || stop "no $OUT/$f"
  echo "== FILE $f sha256 $(sha256sum "$OUT/$f" | cut -d' ' -f1)"; cat "$OUT/$f"; echo "== END $f"
done
echo "== the read log (every path the three tools opened, realpath; the interpreter's own prefixes and /usr, /proc,"
echo "   /sys, /dev, /etc are counted but not listed)"
bad=0
for tag in build regrade read; do
  echo "-- $tag: $(wc -l < "$T/open-$tag.txt") paths"
  "$PY" -I -B - "$T/open-$tag.txt" "$T/readset.txt" "$PY" <<'CHK' || bad=1
import os, sys
log, rs, py = sys.argv[1:4]
roots = [os.path.realpath(x) for x in open(rs).read().split("\n") if x.strip()]
envs = sorted({os.path.realpath(x) for x in (sys.prefix, sys.base_prefix, sys.exec_prefix)})
sysroots = ["/usr", "/proc", "/sys", "/dev", "/etc"]
roots += envs + sysroots
out = []
for p in open(log).read().split("\n"):
    if not p:
        continue
    ok = any(p == r or p.startswith(r.rstrip("/") + "/") for r in roots)
    if not any(p.startswith(r.rstrip("/") + "/") for r in envs + sysroots):
        print(("  " if ok else "  OUTSIDE ") + p)
    if not ok:
        out.append(p)
sys.exit(1 if out else 0)
CHK
done
[ $bad = 0 ] || stop "a tool opened a path outside the declared read set (listed OUTSIDE above)"
echo "READ SET HELD: every opened path is under the deploy, RSN's own out/, the frozen products or the environment"
porc=$(git -C "$D" status --porcelain --untracked-files=all | wc -l)
echo "deploy porcelain after (untracked included) $porc"
[ "$porc" -eq 0 ] || stop "the deploy is no longer clean"
rm -rf -- "$T"
echo "POST PASS: cmodel build, regrade and read written under $OUT"
echo "== rsn connect post rc=0 $(date -u +%FT%TZ)"
rm -f -- "$SELF"; exit 0
