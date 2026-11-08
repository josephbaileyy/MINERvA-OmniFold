#!/bin/bash
# COV2D connect N5-G18: G18's phase N rerun at M_A5 (COV2D-BINDING-2, "Addendum A5, the M line", ruling 2: ruling 5 as
# amended), so that phase S at M_A5 passes A4's gate (the null record's M must be the deploy's HEAD). The same template
# as connect-n.sh (readout/G18/connect-n-G18.sh, c9b3e929), the same /dev/shm path (the record's `modules` holds the
# clone's paths), plus the field-equality control against origin/main's committed null_G18.json (ecdb4be2...):
#   EXCEPTED, named before the run (the CMP block's EXCEPT):
#     M    the record's only code-identity field (c.deploy_head of the clone); it must equal M_A5;
#     utc  the run's clock (time.gmtime at Run start), not a content field.
#   COMPARED, everything else, by exact JSON equality at full depth, including `code` (the toys' driverSha256 and
#   omnifoldHelperSha256 under section 9.9, a provenance of the inputs, not of this deploy) and `host` (the launcher
#   pins login02). blocks_G18.npz must be byte-equal, or equal in every array.
# Any other difference is NULL-EQUALITY DIFFERS: a STOP to the director, unrepaired; phase S does not follow.
# Verdict: PASS and EQUAL (rc 0), else STOP/INVALID as connect-n.sh, or NULL-EQUALITY DIFFERS.
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-n-<T>.sh >/dev/null 2>&1 </dev/null &
M=b1d56e4f08e62983784e34b2278f38a09a68eca0   # M_A5 (#900's merge; bound by #911)
T=G18
READOUT_SHA=0c3ad137be128691cce7bbe3ec72493b76791e761e6cd897f75aaf0a4fc7444f   # cov2d_readout.py at M_A5 (the M line's table)
W=/dev/shm/josephrb-cov2d-n-$T; DD=$W/deploy
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold   # the shared checkout with the MAT build (setup_salloc_env.sh)
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
RUN="nice -n 19 taskset -c 8-11"
cleanup() { echo "removal: host=$(hostname) $(date -u +%FT%TZ) $(du -sh "$DD" 2>/dev/null | cut -f1) $DD"; rm -rf "$DD" "$W/tmp"; echo "rc=$?"; ls -d "$DD" "$W/tmp" 2>&1; }
stop() { echo "STOP $*"; cleanup; echo "PHASE-N INVALID (connect)"; echo "end=$(date -u +%FT%TZ)"; echo DONE; exit 2; }
case "$T" in G18|AR23) ;; *) echo "STOP T is not set"; exit 2 ;; esac
case "$M" in *[!0-9a-f]*|"") echo "STOP M is not set"; exit 2 ;; esac
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" "$W/tmp" "$W/out" || exit 2
exec >> "$W/connect-n-$T.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" -c advice.detachedHead=false checkout --quiet --detach "$M" || stop clone
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "porcelain_before_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
got=$(sha256sum "$DD/2d-unfolding/cov2d/cov2d_readout.py" | cut -c1-64)
[ "$got" = "$READOUT_SHA" ] && echo "READOUT-SHA OK $got" || stop "cov2d_readout.py is $got"
(cd "$DD" && git ls-tree -r HEAD 2d-unfolding/cov2d | grep -v __pycache__) > "$W/blobs.before"
(
  "$PY310" -B -c "import sys; sys.path.insert(0, '$DD/nd-unfolding'); import fd_rpd_inputs as r; r.run_check_mat_setup(None)" || exit 7
  source "$A/setup_salloc_env.sh" > /dev/null 2>&1 || exit 3
  export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
  echo "python=$(command -v python) TMPDIR=$TMPDIR"
  python -c "import sys, numpy, ROOT; print(sys.version.split()[0], 'numpy', numpy.__version__, 'ROOT', ROOT.gROOT.GetVersion())" || exit 4
  python - <<'PYEOF' || exit 5
import hashlib, os, ROOT
src = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_1A.root"
fd = os.open(src, os.O_RDONLY | os.O_NOATIME); data = b""
while True:
  b = os.read(fd, 1 << 24)
  if not b: break
  data += b
os.close(fd)
print("MAT preflight file:", src, "sha256", hashlib.sha256(data).hexdigest())
dst = os.path.join(os.environ["TMPDIR"], "mat_preflight.root"); open(dst, "wb").write(data)
f = ROOT.TFile.Open(dst); h = f.Get("pTmu_reweightedflux_integrated")
print("MAT preflight:", type(h).__name__, h.ClassName(), h.GetNbinsX(), "bins")
assert h.ClassName().startswith("PlotUtils::MnvH1D"), h.ClassName()
os.remove(dst)
PYEOF
  cd "$DD/2d-unfolding/cov2d" && $RUN /usr/bin/time -v python -B cov2d_readout.py null --truth "$T" --out "$W/out"
) > "$W/null_$T.log" 2>&1; rc=$?
grep -v '^Warning in <TInterpreter::ReadRootmapFile>' "$W/null_$T.log" | tail -40
if [ "$rc" = 0 ] && grep -q "^COV2D-NULL $T PASS" "$W/null_$T.log"; then V=PASS
elif [ "$rc" = 3 ] && grep -q "^COV2D-NULL $T STOP" "$W/null_$T.log"; then V=STOP
else V=INVALID; fi
echo "PHASE-N $T $V rc=$rc"
(cd "$W/out" && sha256sum * 2>&1)
# the director's control: equal in content to the committed null except the named fields; blocks byte- or array-equal
NR=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/readout/$T
echo "origin/main=$(git -C "$DD" rev-parse origin/main)"
git -C "$DD" show "origin/main:$NR/null_$T.json" > "$W/committed_null_$T.json"; g1=$?
git -C "$DD" show "origin/main:$NR/blocks_$T.npz" > "$W/committed_blocks_$T.npz"; g2=$?
echo "committed: git show rc=$g1/$g2 $(sha256sum "$W/committed_null_$T.json" "$W/committed_blocks_$T.npz" | tr '\n' ' ')"
if [ "$V" = PASS ] && [ "$g1" = 0 ] && [ "$g2" = 0 ]; then
  "$PY310" -B - "$W/out/null_$T.json" "$W/committed_null_$T.json" "$W/out/blocks_$T.npz" "$W/committed_blocks_$T.npz" "$M" <<'CMP'
import hashlib, json, sys
import numpy as np
new_p, old_p, newz_p, oldz_p, m = sys.argv[1:6]
new, old = json.load(open(new_p)), json.load(open(old_p))
EXCEPT = {"M", "utc"}   # named before the run: see the header
keys = sorted(set(new) | set(old))
diff = [k for k in keys if k not in EXCEPT and new.get(k, "<absent>") != old.get(k, "<absent>")]
print("NULL-FIELDS compared", len([k for k in keys if k not in EXCEPT]), "excepted", sorted(EXCEPT & set(keys)),
      "differing", diff)
print("NULL-M new", new.get("M"), "old", old.get("M"), "new M is this M:", new.get("M") == m)
print("NULL-UTC new", new.get("utc"), "old", old.get("utc"))
# diagnostic only (the verdict is the top-level test above): the leaf paths that differ, first 40
def leaves(a, b, p=""):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            yield from leaves(a.get(k, "<absent>"), b.get(k, "<absent>"), f"{p}.{k}" if p else k)
    elif a != b:
        yield p
paths = [q for k in diff for q in leaves(new.get(k, "<absent>"), old.get(k, "<absent>"), k)]
print("NULL-LEAVES differing", len(paths), paths[:40])
nb, ob = open(newz_p, "rb").read(), open(oldz_p, "rb").read()
byte_equal = nb == ob
zn, zo = np.load(newz_p), np.load(oldz_p)
arr_diff = sorted(set(zn.files) ^ set(zo.files)) + [k for k in sorted(set(zn.files) & set(zo.files))
                                                       if zn[k].dtype != zo[k].dtype or not np.array_equal(zn[k], zo[k])]
print("BLOCKS byte_equal", byte_equal, "arrays", len(zn.files), "differing", arr_diff,
      "sha new", hashlib.sha256(nb).hexdigest(), "old", hashlib.sha256(ob).hexdigest())
ok = not diff and new.get("M") == m and (byte_equal or not arr_diff)
print("NULL-EQUALITY " + ("EQUAL" if ok else "DIFFERS"))
sys.exit(0 if ok else 9)
CMP
  echo "equality rc=$?"
else
  echo "NULL-EQUALITY NOT-CHECKED (verdict $V, git show $g1/$g2)"
fi
n=$(git -C "$DD" status --porcelain | wc -l); echo "porcelain_after_lines=$n head=$(git -C "$DD" rev-parse HEAD)"
git -C "$DD" status --porcelain | head -20
(cd "$DD" && git ls-tree -r HEAD 2d-unfolding/cov2d | grep -v __pycache__) > "$W/blobs.after"
cmp -s "$W/blobs.before" "$W/blobs.after" && echo "blobs unchanged" || echo "blobs CHANGED"
cleanup
echo "end=$(date -u +%FT%TZ)"
echo DONE
