#!/bin/bash
# FD-PRR: the PRR read (FD-PRR BINDING 1 addendum A4 ruling 1: the read runs from M_A4; addendum A2 section 6: from a
# fresh clone), on a Perlmutter login node, after the director's go, once prr_ibu attempt 3 (61057142) has completed.
# It runs M_A4's prr_read.py unchanged, `prr_read.main(["--run", $OUT, "--repo", $D, "--out", $OUT/read])`, with nice 19,
# ionice idle, every thread cap at 1, -I -B and no bytecode. The call is wrapped in REF-G1's read guard
# (ref_g1.read_guards at M_A4): a plain Python read under /pscratch or /global/cfs outside the deploy and $OUT is
# refused, so the read cannot touch s5p-20260926 or any other shared tree. prr_read is the only code called.
# In order, each failure a final stop before the read:
#   preconditions: the five jobs' DONE (dry, iter, cap, misc, ibu) exist with no STOP or FAILED beside them; sacct shows
#     61057142 COMPLETED; $OUT/read and $OUT/deploy-read and this connect's log and done are absent; no prr_* job queued
#     or running (squeue --me; fails closed);
#   a fresh clone at M_A4 into $OUT/deploy-read, clean (porcelain --ignored 0), the six FD-PRR files, the declaration,
#     addendums A1-A4 and BINDING 1 at their bound sha256 (BINDING 1 at origin/main);
#   the route-2 products at log-ibu/SHA256SUMS (prr_read checks its own committed inputs, INPUT_PINS, at :428).
# Then the read. prr_read writes only $OUT/read/ (readout.json and readout.txt, or STOP). This connect writes only
# $OUT/deploy-read, $OUT/read and its own log and done. The record comes to the director before any reading is quoted.
# No set -u. Any stop is final. Launched from a /dev/shm copy of itself (its path is $1), which it deletes at exit.
SELF=$1
TAG=read
M=cb13a6443a457bd3887d1c421723dfcdb1909ec8
OUT=/pscratch/sd/j/josephrb/fd-prr-20261108
D=$OUT/deploy-$TAG
RO=$OUT/read
JOB=61057142
PY=$HOME/.conda/envs/root_6_28/bin/python3
DECL_SHA=5be1e19cb8db67064cb0f90382ed7ac2365a2ed4841d9b498f323ed2761b64ce
A1_SHA=ca6b8457e74c9323fcb985766a88f404038f6f16c3e822a67bf2606af223f38b
A2_SHA=41e53237ceacb99e7310f922bc70df777dd9c0a04cb005e2aafa7a0c75a73a73
A3_SHA=48641cf9ba6a6e30856dc3447412cca777bcc0b75f84566db9f4463d9e646db1
A4_SHA=3ba2f47ba0d9b40155d6840ca22f665051a4f6cdaf15fd0efe24564929bdc6a8
BIND_SHA=634cded38a1780286d24941ce567c174ff17ccc1b6af640f24129c5e6275b613   # FD-PRR-BINDING-1.md at main, with A4 bound
bail() { rm -f -- "$SELF"; exit 9; }                # a precondition failed: nothing written
[ -d "$OUT" ] && [ -x "$PY" ] || bail
for j in dry iter cap misc ibu; do
  [ -s "$OUT/log-$j/DONE" ] && [ ! -e "$OUT/log-$j/STOP" ] && [ ! -e "$OUT/log-$j/FAILED" ] || bail
done
for p in "$RO" "$D" "$OUT/logs/connect-$TAG.log" "$OUT/logs/connect-$TAG.done"; do [ ! -e "$p" ] || bail; done
case "$(sacct -j "$JOB" -X -n -P -o State | head -1)" in COMPLETED) ;; *) bail ;; esac
q=$(squeue --me -h -o '%j') || bail                 # fails closed
[ -z "$(printf '%s\n' "$q" | grep -E '^prr_')" ] || bail
LOG=$OUT/logs/connect-$TAG.log
exec > "$LOG" 2>&1
finish() { echo "prr $TAG rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect-$TAG.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/prr_${TAG}.sh"
echo "squeue --me:"; squeue --me -h -o "%i %j %T"
echo "prr_ibu attempt 3: $(sacct -j "$JOB" -X -n -P -o JobID,JobName,State,ExitCode,ElapsedRaw,NNodes | head -1)"
for j in dry iter cap misc ibu; do echo "log-$j/DONE: $(dd if="$OUT/log-$j/DONE" iflag=noatime status=none)"; done

# ---- the deploy: a fresh clone at M_A4, clean, the bound bytes
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$OUT/logs/clone-$TAG.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M_A4"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
( cd "$D/nd-unfolding/prior_retention" && sha256sum -c ) <<SUMS || { echo "STOP: the FD-PRR files are not the bound ones"; finish 9; }
f87ee90c58d2b8904fe881931edc61966a6adda8be7eb503da6644797a3d1232  prr_probe.py
fa91394507c0e6a32486af25fa52f7e162135cf6483519ccf15510e1c9473cb0  prr_ibu.py
d7c7c2c0d6cbe4a13d445a779335699de3d5275c4bcd3efc9f4e84a166868fbe  prr_read.py
4493aad5dff0a8a0316c0f8b4d159c8f08c7666856474b5cf9c4c963a3a7e975  sbatch_prr.sh
fad928d85c9183ac525ffabcd809d6968afab6aead4a2ad2aa13202b788eef40  test_prr.py
e088406cd47ef88c8e47b988e7f684f8c29b74a620fa65d101ac790ca7892d5f  prr_mutation.py
SUMS
S=$D/docs/orchestration/state/measurement-paper/5d-community-20261024
for pair in "FD-PRR-DECLARATION.md $DECL_SHA" "FD-PRR-ADDENDUM-A1.md $A1_SHA" "FD-PRR-ADDENDUM-A2.md $A2_SHA" \
            "FD-PRR-ADDENDUM-A3.md $A3_SHA" "FD-PRR-ADDENDUM-A4.md $A4_SHA"; do
  set -- $pair; got=$(sha256sum "$S/$1" | cut -d' ' -f1); echo "$1 sha256 $got"
  [ "$got" = "$2" ] || { echo "STOP: $1 is not the bound one"; finish 9; }
done
bmain=$(git -C "$D" show origin/main:docs/orchestration/state/measurement-paper/5d-community-20261024/FD-PRR-BINDING-1.md | sha256sum | cut -d' ' -f1)
echo "FD-PRR-BINDING-1.md at origin/main $(git -C "$D" rev-parse origin/main) sha256 $bmain"
[ "$bmain" = "$BIND_SHA" ] || { echo "STOP: BINDING 1 on main is not the one this connect was made against: to the director"; finish 9; }
# the route-2 products at the job's own record
( cd "$OUT" && sha256sum -c log-ibu/SHA256SUMS ) || { echo "STOP: route 2's products are not log-ibu/SHA256SUMS's"; finish 9; }

# ---- the read: M_A4's prr_read.main, unchanged, inside REF-G1's read guard
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONHASHSEED=0
echo "threads: OMP=1 OPENBLAS=1 MKL=1 NUMEXPR=1 VECLIB=1; nice 19; ionice idle; python $("$PY" -c 'import sys; print(sys.version.split()[0])')"
( cd "$D" && nice -n 19 ionice -c3 env -u PYTHONPATH "$PY" -I -B -c '
import sys
from pathlib import Path
D, OUT, RO = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
for p in ("nd-unfolding/prior_retention", "nd-unfolding", "nd-unfolding/ref_g1"):
    sys.path.insert(0, str(D / p))
import prr_read, ref_g1
with ref_g1.read_guards(ref_g1.PROTECTED, (D, OUT), root=False):
    rc = prr_read.main(["--run", str(OUT), "--repo", str(D), "--out", str(RO)])
print("prr_read rc", rc, flush=True)
sys.exit(rc)
' "$D" "$OUT" "$RO" )
rc=$?
echo "read rc=$rc"
ls -la "$RO" 2>&1
for f in readout.json readout.txt STOP; do
  [ -e "$RO/$f" ] && echo "$f sha256 $(dd if="$RO/$f" iflag=noatime status=none | sha256sum | cut -d' ' -f1) bytes $(stat -c %s "$RO/$f")"
done
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
finish $rc
