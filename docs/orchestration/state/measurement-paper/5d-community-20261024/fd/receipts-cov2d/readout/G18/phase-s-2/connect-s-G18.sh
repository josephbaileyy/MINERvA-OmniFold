#!/bin/bash
# COV2D connect S-<T>: addendum A4's phase S (COV2D-ADDENDUM-A4.md section 4), `cov2d_readout.py score --truth T
# --null-digest D`, for one truth, after its null record is merged to main (COV2D-BINDING-2 addendum A4, ruling 1).
# Login node, 0 node-h (A4 section 9), at M_A5 = b1d56e4f (A5's M line; was ac25b665). The same template as connect-n.sh (phase N, receipted in
# readout/<T>/): a fresh clone at M in /dev/shm, the MAT pin before and after sourcing, the MnvH1D preflight, nice 19,
# taskset -c 8-11, threads 1, porcelain before and after, the clone removed at the end (logged).
# The gate is the driver's (section 9.7): origin/main's null_<T>.json must hash to D, name this M, this truth and PASS;
# the blocks npz and the re-hashed inventory must match; only then is a toy opened. Before running, this script records
# origin/main's sha and the sha256 of `git show origin/main:<null record>` (the driver still does its own check).
# Verdict: COVERS or UNDER-COVERS (rc 0, "COV2D-SCORE <T> COVERS|UNDER-COVERS"); REFUSED (rc 2, the gate);
# STOP or INVALID from the driver (rc 3, "COV2D-SCORE <T> STOP|INVALID"); else INVALID (connect). A section 9.9 INVALID
# goes to the director unrepaired, with the mechanism named (binding A4, ruling 2).
# A5 (M line rulings 1-3): a grade refusal is rc 3 "COV2D-SCORE <T> INVALID (grade refused, <grade>: <text>)" with
# score_<T>.invalid.json. Ruling 3's reading rule is applied here after the run and printed per grade (A5-READING):
# for each grade (cholesky_check = C_T, cholesky_check_minus = C_T-) whose compared ndf is 205, kappa2, tol and
# max_rel_diff must be finite, max_rel_diff <= tol, and the tol the grade used (compared.tol) must be the recorded
# tol; a grade with no compared values also fails. If it fails, the PHASE-S line reads INVALID (A5 reading rule),
# whatever the driver printed; the records are left as written.
# connect-s-<T>.sh is this file with T and D set; nothing else differs.
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-s-<T>.sh >/dev/null 2>&1 </dev/null &
M=b1d56e4f08e62983784e34b2278f38a09a68eca0   # M_A5 (#900's merge; bound by #911)
T=G18
D=6bd5259d61b062af7b3a8b09af78fc544e3eba48e35a062a28fdcd923b90f6e0   # null_G18.json of phase-n-2 (#914)
READOUT_SHA=0c3ad137be128691cce7bbe3ec72493b76791e761e6cd897f75aaf0a4fc7444f   # cov2d_readout.py at M_A5
W=/dev/shm/josephrb-cov2d-s-$T; DD=$W/deploy
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold   # the shared checkout with the MAT build (setup_salloc_env.sh)
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
RUN="nice -n 19 taskset -c 8-11"
cleanup() { echo "removal: host=$(hostname) $(date -u +%FT%TZ) $(du -sh "$DD" 2>/dev/null | cut -f1) $DD"; rm -rf "$DD" "$W/tmp"; echo "rc=$?"; ls -d "$DD" "$W/tmp" 2>&1; }
stop() { echo "STOP $*"; cleanup; echo "PHASE-S INVALID (connect)"; echo "end=$(date -u +%FT%TZ)"; echo DONE; exit 2; }
case "$T" in G18|AR23) ;; *) echo "STOP T is not set"; exit 2 ;; esac
case "$D" in *[!0-9a-f]*|"") echo "STOP D is not set"; exit 2 ;; esac
[ ${#D} = 64 ] || { echo "STOP D is not a sha256"; exit 2; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" "$W/tmp" "$W/out" || exit 2
exec >> "$W/connect-s-$T.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" -c advice.detachedHead=false checkout --quiet --detach "$M" || stop clone
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "porcelain_before_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
got=$(sha256sum "$DD/2d-unfolding/cov2d/cov2d_readout.py" | cut -c1-64)
[ "$got" = "$READOUT_SHA" ] && echo "READOUT-SHA OK $got" || stop "cov2d_readout.py is $got"
(cd "$DD" && git ls-tree -r HEAD 2d-unfolding/cov2d | grep -v __pycache__) > "$W/blobs.before"
NR=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/readout/$T/null_$T.json
echo "origin/main=$(git -C "$DD" rev-parse origin/main)"
g=$(git -C "$DD" show "origin/main:$NR" | sha256sum | cut -c1-64)
[ "$g" = "$D" ] && echo "NULL-ON-MAIN OK $g" || stop "origin/main null_$T.json is $g, not $D"
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
  cd "$DD/2d-unfolding/cov2d" && $RUN /usr/bin/time -v python -B cov2d_readout.py score --truth "$T" --null-digest "$D" --out "$W/out"
) > "$W/score_$T.log" 2>&1; rc=$?
grep -v '^Warning in <TInterpreter::ReadRootmapFile>' "$W/score_$T.log" | tail -40
L=$(grep "^COV2D-SCORE $T " "$W/score_$T.log" | tail -1)
case "$rc:$L" in
  "0:COV2D-SCORE $T COVERS"|"0:COV2D-SCORE $T UNDER-COVERS") V=${L#COV2D-SCORE $T } ;;
  "2:COV2D-SCORE $T REFUSED "*) V=REFUSED ;;
  "3:COV2D-SCORE $T STOP"|"3:COV2D-SCORE $T INVALID") V=${L#COV2D-SCORE $T } ;;
  "3:COV2D-SCORE $T INVALID (grade refused, "*) V=${L#COV2D-SCORE $T } ;;
  *) V="INVALID (connect: rc=$rc, no matching verdict line)" ;;
esac
# A5 M line ruling 3: the reading rule, per grade, from whichever score record was written
SR=""; for f in "$W/out/score_$T.json" "$W/out/score_$T.invalid.json"; do [ -f "$f" ] && SR="$SR $f"; done
if [ -n "$SR" ]; then
  "$PY310" -B - $SR <<'A5R'; a5=$?
import json, math, sys
ok = True
for p in sys.argv[1:]:
    rec = json.load(open(p))
    for key, grade in (("cholesky_check", "C_T"), ("cholesky_check_minus", "C_T_minus")):
        cc = rec.get(key) or {}
        cmp = cc.get("compared") or {}
        k, tol, mrd, ndf = cc.get("kappa2"), cc.get("tol"), cmp.get("max_rel_diff"), cmp.get("ndf")
        fin = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)
        if not cmp:
            good = False; why = "no compared values"
        elif ndf != 205:
            good = True; why = f"ndf {ndf}: the rule applies at ndf 205 only"
        else:
            good = fin(k) and fin(tol) and fin(mrd) and mrd <= tol and cmp.get("tol") == tol
            why = ("finite, max_rel_diff <= tol, the grade used the recorded tol" if good
                   else "not finite, or max_rel_diff > tol, or the grade's tol is not the recorded tol")
        ok &= good
        print(f"A5-READING {p.rsplit('/', 1)[-1]} {grade} ndf={ndf} kappa2={k!r} tol={tol!r} cmp_tol={cmp.get('tol')!r} "
              f"max_rel_diff={mrd!r} {'OK' if good else 'FAIL'} ({why})")
print("A5-READING-RULE " + ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 8)
A5R
  [ "$a5" = 0 ] || V="INVALID (A5 reading rule; the driver printed: $V)"
else
  echo "A5-READING-RULE NOT-CHECKED (no score record written; verdict $V)"
fi
echo "PHASE-S $T $V rc=$rc"
(cd "$W/out" && sha256sum * 2>&1)
n=$(git -C "$DD" status --porcelain | wc -l); echo "porcelain_after_lines=$n head=$(git -C "$DD" rev-parse HEAD)"
git -C "$DD" status --porcelain | head -20
(cd "$DD" && git ls-tree -r HEAD 2d-unfolding/cov2d | grep -v __pycache__) > "$W/blobs.after"
cmp -s "$W/blobs.before" "$W/blobs.after" && echo "blobs unchanged" || echo "blobs CHANGED"
cleanup
echo "end=$(date -u +%FT%TZ)"
echo DONE
