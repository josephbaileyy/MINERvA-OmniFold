#!/bin/bash
# COV2D connect FLUX: step B's flux read on the real file (the auditor's suggestion, the director's go, 2026-11-04).
# Step B (cov2d_pseudo_write.py) calls re2_driver.load_flux_bins on runEventLoopMC_MEFHC.root's
# pTmu_reweightedflux_integrated, and its tests used TH1D fixtures, which cannot show whether that object needs MAT.
# Here, on one pinned O_NOATIME copy of the real 5,143-byte file:
#   1. plain root_6_28 (activated by prefix): load_flux_bins, recording the object's class and either the bins or the
#      exception;
#   2. the pinned MAT environment (RPD's standard: fd_rpd_inputs.run_check_mat_setup before sourcing setup_salloc_env.sh,
#      mat_environment after): load_flux_bins must return the bins; their equality with step 1's is recorded.
# Descriptive: both outcomes go in the record. A login node, 0 node-h, nice 19, taskset -c 8-11, threads 1. A fresh
# clone at M in /dev/shm; the driver (97f26a1d) and fd_rpd_inputs (7c2e018f) blobs asserted; everything removed after.
# Run on login02: setsid nohup bash /dev/shm/josephrb-cov2d-flux.sh >/dev/null 2>&1 </dev/null &
M=13927a0ed8f28fbb3149786dbb007e9bd6909b76
W=/dev/shm/josephrb-cov2d-flux; DD=$W/deploy
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold
MC=$A/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root
MC_SHA=d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
CONDA=/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda
RUN="nice -n 19 taskset -c 8-11"
finish() { echo "removal: host=$(hostname) $(date -u +%FT%TZ) $(du -sh "$DD" 2>/dev/null | cut -f1)"; rm -rf "$DD" "$W/mc.root"; echo "rc=$?"; ls -d "$DD" "$W/mc.root" 2>&1; echo "end=$(date -u +%FT%TZ)"; echo DONE; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" "$W/tmp" || exit 2
exec >> "$W/connect-flux.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M" \
    || { echo "STOP clone"; finish; exit 2; }
echo "head=$(git -C "$DD" rev-parse HEAD) porcelain=$(git -C "$DD" status --porcelain | wc -l)"
(cd "$DD" && git ls-tree HEAD 2d-unfolding/re2/re2_driver.py nd-unfolding/fd_rpd_inputs.py) | tee "$W/blobs"
grep -q " 97f26a1d03be8cf14cdb6e0ce05e794f66f9b571	" "$W/blobs" && grep -q " 7c2e018f1169a9be0c5642daab991c664acbefcf	" "$W/blobs" \
    || { echo "STOP blobs"; finish; exit 2; }
"$PY310" -B - "$MC" "$MC_SHA" "$W/mc.root" <<'PYEOF' || { echo "STOP copy"; finish; exit 2; }
import hashlib, os, sys
src, want, dst = sys.argv[1:4]
a0 = os.stat(src).st_atime_ns
fd = os.open(src, os.O_RDONLY | os.O_NOATIME); data = os.read(fd, 1 << 26); os.close(fd)
got = hashlib.sha256(data).hexdigest()
print("copy:", len(data), "bytes sha256", got, "atime unchanged", os.stat(src).st_atime_ns == a0)
assert got == want, "not the pinned file"
open(dst, "wb").write(data)
PYEOF
PROBE='
import json, sys
sys.path.insert(0, sys.argv[1] + "/2d-unfolding/re2")
import ROOT
ROOT.gROOT.SetBatch(True)
import re2_driver as d
f = ROOT.TFile.Open(sys.argv[2]); key = f.GetKey("pTmu_reweightedflux_integrated")
out = {"env": sys.argv[3], "key_class": key.GetClassName() if key else None}
f.Close()
try:
    bins, _ = d.load_flux_bins(sys.argv[2], "pTmu_reweightedflux_integrated", d.PT_EDGES)
    out.update(ok=True, bins=[float(x) for x in bins])
except Exception as e:
    out.update(ok=False, error=f"{type(e).__name__}: {e}")
print("PROBE " + json.dumps(out))
'
echo "== 1. plain root_6_28"
(
  eval "$("$CONDA" shell.bash hook)" && conda activate "$HOME/.conda/envs/root_6_28" || exit 3
  $RUN python -B -c "$PROBE" "$DD" "$W/mc.root" plain_root_6_28
) > "$W/plain.log" 2>&1; echo "plain rc=$?"; grep "^PROBE\|Error\|error" "$W/plain.log" | head -5
echo "== 2. the pinned MAT environment"
(
  "$PY310" -B -c "import sys; sys.path.insert(0, '$DD/nd-unfolding'); import fd_rpd_inputs as r; r.run_check_mat_setup(None)" || exit 7
  source "$A/setup_salloc_env.sh" > /dev/null 2>&1 || exit 3
  export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
  $RUN python -B -c "import sys, json; sys.path.insert(0, '$DD/nd-unfolding'); import fd_rpd_inputs as r; m = r.mat_environment(); print('MAT ' + json.dumps({'mapped': m['mapped_mat_files'], 'dictionary': m['plotutils_mnvh1d_dictionary']}))" || exit 8
  $RUN python -B -c "$PROBE" "$DD" "$W/mc.root" pinned_mat
) > "$W/mat.log" 2>&1; echo "mat rc=$?"; grep "^PROBE\|^MAT\|Error\|error" "$W/mat.log" | head -5
python3 - "$W/plain.log" "$W/mat.log" <<'PYEOF'
import json, sys
p = [json.loads(l[6:]) for f in sys.argv[1:3] for l in open(f) if l.startswith("PROBE ")]
if len(p) == 2:
    print("key class:", p[0]["key_class"], "| plain ok:", p[0]["ok"], "| MAT ok:", p[1]["ok"],
          "| bins equal:", p[0].get("bins") == p[1].get("bins") if p[0]["ok"] and p[1]["ok"] else "n/a")
    print("FLUX-CHECK", "PASS" if p[1]["ok"] else "FAIL", "(step B needs MAT:", "no" if p[0]["ok"] else "yes", ")")
else:
    print("FLUX-CHECK INVALID: a probe printed no record")
PYEOF
finish
