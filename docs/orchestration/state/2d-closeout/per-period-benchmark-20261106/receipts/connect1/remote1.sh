C1=/pscratch/sd/j/josephrb/per-period-benchmark-20261106/connect1
TAR_SHA=bb1e00e4ed9c8ef27b9681a9daf47078b9d89d5559937104f778afd5c06c716e
D=docs/orchestration/state/2d-closeout/per-period-benchmark-20261106
PINS="9bc3921bc86b62813d8297e66012f1e941398ce641a67fc5f46fe6fa6cdd5961  docs/orchestration/state/2d-closeout/per-period-benchmark-20261106/DECLARATION.md
94fc5a3d23ffcdf6c16629aef328979f1940cfbc373cc0790761be75d331d70b  docs/orchestration/state/2d-closeout/per-period-benchmark-20261106/per_period_benchmark.py
8f3ccf8aa052d377e6a84e797a61efea4df2b0f8645c64bcc003ab1ea9ef68c0  docs/orchestration/state/2d-closeout/per-period-benchmark-20261106/test_per_period_benchmark.py
9c05e5e1aa3d12d6782a23c0b5625ea63de429071667761b026366d92b6a3be0  docs/orchestration/state/2d-closeout/per-period-benchmark-20261106/INPUTS.sha256"
echo "== remote $(date -u +%FT%TZ) $(hostname)"
cd "$C1" || { echo "STOP: no $C1"; exit 10; }
got=$(sha256sum code-M.tar | awk '{print $1}')
[ "$got" = "$TAR_SHA" ] || { echo "STOP: archive digest $got != $TAR_SHA"; exit 11; }
echo "archive digest equal: $got"
mkdir code R || exit 12
tar -xf code-M.tar -C code || { echo "STOP: untar"; exit 12; }
printf '%s\n' "$PINS" > R/pins.sha256
(cd code && sha256sum -c ../R/pins.sha256) > R/pins.check 2>&1; rc=$?
cat R/pins.check
[ $rc -eq 0 ] || { echo "STOP: remote pins differ"; exit 13; }
squeue -u josephrb -h -o '%i|%j|%T' > R/squeue.txt 2>R/squeue.err; rc=$?
echo "squeue rc $rc, rows $(wc -l < R/squeue.txt)"
[ $rc -eq 0 ] || { echo "STOP: squeue failed; the fence cannot be checked"; exit 14; }
if grep -q '|cov2d-' R/squeue.txt; then echo "STOP: a cov2d-* job is queued or running"; grep '|cov2d-' R/squeue.txt; exit 15; fi
echo "fence: no cov2d-* job"
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; exit 16; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
PY=$(command -v python3)
{ echo "python $PY"; "$PY" -c 'import sys,numpy,matplotlib,ROOT; print(sys.version); print("numpy",numpy.__version__,"matplotlib",matplotlib.__version__,"ROOT",ROOT.gROOT.GetVersion())'; } > R/env.txt 2>&1; rc=$?
cat R/env.txt
[ $rc -eq 0 ] || { echo "STOP: environment imports failed"; exit 17; }
cd "code/$D" || exit 18
nice -n 19 ionice -c 3 "$PY" -B -m unittest -v test_per_period_benchmark > "$C1/R/suite.log" 2>&1; suite_rc=$?
ran=$(grep -E '^Ran [0-9]+ tests? in' "$C1/R/suite.log")
last=$(tail -n 1 "$C1/R/suite.log")
echo "suite rc $suite_rc; $ran; last line '$last'"
cat > "$C1/R/smoke.py" <<'PYEOF'
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np
import per_period_benchmark as P
out = {"stage": "smoke"}
m = P.import_reused()
rows = P.read_inputs()
pick = [r for r in rows if P.Path(r[1]).name.startswith("cov_ptpl_") or P.Path(r[1]).parent.name == "pu_PA_b01"]
assert len(pick) == 2, pick
dest = sys.argv[1]
os.makedirs(dest)
at = {}
for _, src in pick:
    st0 = os.stat(src)
    P.noatime_copy(src, os.path.join(dest, P.copy_name(src)))
    st1 = os.stat(src)
    at[src] = {"atime_before": st0.st_atime_ns, "atime_after": st1.st_atime_ns, "equal": st0.st_atime_ns == st1.st_atime_ns}
out["source_atimes"] = at
ver = P.verify_copies(dest, pick)
out["verify"] = ver
if ver["verdict"] != "PASS" or not all(v["equal"] for v in at.values()):
    out["verdict"] = "FAIL"
    print(json.dumps(out, indent=1)); sys.exit(3)
cov = os.path.join(dest, P.copy_name([s for _, s in pick if "cov_ptpl" in s][0]))
prod = os.path.join(dest, P.copy_name([s for _, s in pick if "pu_PA_b01" in s][0]))
roles = {"published": cov, "E_R": prod, "CTRL": prod,
         "groups": {g: {"s42": prod, "s43": prod, "boot": {r: prod for r in range(1, 11)}} for g in P.GROUPS}}
pub, prods = P.load_all(m, roles)
mask = np.diag(pub["stat"]) > 0
x = prods["PA_b01"]
txt = np.zeros(224)
with open(os.path.join(str(P.REPO), "2d-unfolding/minerva_paper_anc/data_result_ptpl_2D_minerva_inclusive_6GeV.txt")) as fh:
    next(fh)
    for line in fh:
        if line.strip():
            pz, pt, xs = line.split(",")[:3]
            txt[(int(pt) - 1) * 16 + (int(pz) - 1)] = float(xs)
rel_txt = float(np.max(np.abs(pub["p"][mask] - txt[mask]) / np.abs(txt[mask])))
cells = P.ctl_cells(m.reported_cells, np.flatnonzero(mask), {"PA_b01": x})
checks = {
    "published_shapes": [list(pub["p"].shape), list(pub["total"].shape), list(pub["stat"].shape)],
    "n_reported": int(mask.sum()),
    "total_symmetric_max_abs": float(np.max(np.abs(pub["total"] - pub["total"].T))),
    "published_vs_text_release_max_rel_reported_cells": rel_txt,
    "product_shape": list(x.shape), "product_finite": bool(np.all(np.isfinite(x))),
    "product_positive_cells": int((x > 0).sum()), "cells_control": cells,
    "n_products_loaded": len(prods),
}
ok = (checks["published_shapes"] == [[224], [224, 224], [224, 224]] and checks["n_reported"] == 205
      and rel_txt <= 5e-3 * (1 + 1e-9)
      and checks["product_finite"] and cells["verdict"] == "PASS" and len(prods) == 38)
# total_symmetric_max_abs is printed only: exact symmetry of the published TMatrix is not a declared property
out["checks"] = checks
out["verdict"] = "PASS" if ok else "FAIL"
print(json.dumps(out, indent=1))
sys.exit(0 if ok else 3)
PYEOF
nice -n 19 ionice -c 3 "$PY" -B "$C1/R/smoke.py" "$C1/smoke-copies" > "$C1/R/smoke.json" 2> "$C1/R/smoke.err"; smoke_rc=$?
echo "smoke rc $smoke_rc"; tail -n 3 "$C1/R/smoke.json"
cd "$C1/R" && sha256sum * > ../SHA256SUMS.R && mv ../SHA256SUMS.R SHA256SUMS
if [ $suite_rc -eq 0 ] && [ "${ran%% in*}" = "Ran 51 tests" ] && [ "$last" = "OK" ] && [ $smoke_rc -eq 0 ]; then
  echo "CONNECT1 PASS"; exit 0
fi
echo "CONNECT1 FAIL"; exit 20
