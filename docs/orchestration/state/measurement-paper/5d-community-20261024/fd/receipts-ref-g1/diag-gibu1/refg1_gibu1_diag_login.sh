#!/bin/bash
# REF-G1 G-IBU1 diagnosis (the director's request of 2026-11-05, after the read's STOP, #792): on a login node, 0 node-h,
# read-only. Compares the batch's gibu1.npz (sha256 70bb60d0...) with IBU-1's D_N.npz (a160dbea...), each read once
# with O_NOATIME into memory and its sha256 checked before np.load. For ks, F_fold and F_sub: shape and dtype of each,
# the number of differing elements (NaN equal to NaN), max|a-b|, max|b|, max|a-b|/max|b|, the largest difference in
# units of b's float spacing, and max|a-b| per K row. Also each file's key list and stored meta, and numpy's build
# configuration (np.show_config) and threadpoolctl's report, if importable, in root_6_28. Forms no Delta, loads no
# other product, runs no unfolding. Writes only under a NEW $X: diag.json, diag.log, diag.done and this script's copy.
# Launched from a /dev/shm copy of itself (its path is $1), which it deletes at exit. No set -u.
SELF=$1
X=/pscratch/sd/j/josephrb/ref-g1-20261105/diag-gibu1
A=/pscratch/sd/j/josephrb/ref-g1-20261105/batch/units/gibu1.npz
B=/pscratch/sd/j/josephrb/ibu1-20261022/run/products/D_N.npz
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
bail() { rm -f -- "$SELF"; exit 9; }
case "$(hostname)" in login*) ;; *) bail ;; esac
[ ! -e "$X" ] && [ -x "$PY" ] && [ -f "$A" ] && [ -f "$B" ] || bail
mkdir -p "$X" || bail
exec > "$X/diag.log" 2>&1
finish() { echo "gibu1 diag rc=$1"; date -u +%FT%TZ; echo "$1" > "$X/diag.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "diag script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$X/refg1_gibu1_diag_login.sh"
echo "atime before (stat): $(stat -c '%X %n' "$A" "$B" | tr '\n' ' ')"
(
  eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
  conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; exit 2; }
  export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
  cd "$X" && nice -n 19 "$PY" -I -B - "$A" "$B" "$X/diag.json" <<'PYEOF'
import contextlib, hashlib, io, json, os, sys, time
import numpy as np
A, B, OUT = sys.argv[1:4]
WANT = {A: "70bb60d0c928822ee17494343226c35055f54a38d2dfb17bce60f0ad20a78741",
        B: "a160dbea95006f552f3f724302d30c0da852bf7747907268e712a2251ccf593b"}
def noatime(p):
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    with os.fdopen(fd, "rb") as f:
        return f.read()
def npz(p):
    raw = noatime(p)
    sha = hashlib.sha256(raw).hexdigest()
    if sha != WANT[p]:
        print(f"STOP: {p} sha256 {sha} is not {WANT[p]}"); sys.exit(4)
    with np.load(io.BytesIO(raw), allow_pickle=False) as z:
        arrays = {k: np.asarray(z[k]) for k in z.files}
    meta = json.loads(str(arrays.pop("meta"))) if "meta" in arrays else None
    return sha, len(raw), arrays, meta
sa, na, a, ma = npz(A)
sb, nb, b, mb = npz(B)
rec = {"schema": "ref-g1-gibu1-diag/1", "a": {"path": A, "sha256": sa, "bytes": na, "keys": sorted(a), "meta": ma},
       "b": {"path": B, "sha256": sb, "bytes": nb, "keys": sorted(b), "meta": mb}, "arrays": {}}
for k in ("ks", "F_fold", "F_sub"):
    r = {"a": {"present": k in a}, "b": {"present": k in b}}
    if k in a: r["a"].update(shape=list(a[k].shape), dtype=str(a[k].dtype))
    if k in b: r["b"].update(shape=list(b[k].shape), dtype=str(b[k].dtype))
    if k in a and k in b and a[k].shape == b[k].shape:
        x, y = np.asarray(a[k]), np.asarray(b[k])
        r["array_equal"] = bool(np.array_equal(x, y))
        if x.dtype.kind in "fc" or y.dtype.kind in "fc":
            xf, yf = x.astype(np.float64), y.astype(np.float64)
            same = (xf == yf) | (np.isnan(xf) & np.isnan(yf))
            d = np.where(same, 0.0, np.abs(xf - yf))
            fin = np.isfinite(d)
            mb_ = float(np.nanmax(np.abs(yf))) if yf.size else 0.0
            md = float(np.max(d[fin])) if fin.any() else None
            r.update(n_elements=int(x.size), n_differ=int((~same).sum()), n_nonfinite_a=int((~np.isfinite(xf)).sum()),
                     n_nonfinite_b=int((~np.isfinite(yf)).sum()), max_abs_diff=md, max_abs_b=mb_,
                     max_abs_diff_over_max_abs_b=(md / mb_ if md is not None and mb_ > 0 else None),
                     max_diff_in_b_spacings=float(np.max(d[fin] / np.spacing(np.abs(yf[fin])))) if fin.any() else None,
                     note="max_abs_diff and max_diff_in_b_spacings are over the finite differences; a pair with a "
                          "non-finite value counts in n_differ and n_nonfinite_*")
            if x.ndim >= 2:
                r["max_abs_diff_per_row"] = [float(np.max(d[i][np.isfinite(d[i])])) if np.isfinite(d[i]).any() else None
                                             for i in range(x.shape[0])]
        else:
            r.update(n_elements=int(x.size), n_differ=int((x != y).sum()))
            r["values_a"], r["values_b"] = x.tolist(), y.tolist()
    rec["arrays"][k] = r
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    np.show_config()
rec["numpy"] = {"version": np.__version__, "show_config": buf.getvalue()}
try:
    import threadpoolctl
    rec["threadpoolctl"] = threadpoolctl.threadpool_info()
except Exception as e:
    rec["threadpoolctl"] = f"unavailable: {type(e).__name__}: {e}"
rec["interpreter"] = {"executable": sys.executable, "version": sys.version}
rec["written_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
with open(OUT, "w") as f:
    f.write(json.dumps(rec, indent=1) + "\n")
for k, r in rec["arrays"].items():
    print(k, json.dumps({kk: v for kk, v in r.items() if kk not in ("max_abs_diff_per_row", "values_a", "values_b")}))
print(rec["numpy"]["show_config"])
PYEOF
)
rc=$?
echo "diag rc=$rc"
echo "atime after (stat): $(stat -c '%X %n' "$A" "$B" | tr '\n' ' ')"
[ -s "$X/diag.json" ] && echo "diag.json sha256 $(sha256sum "$X/diag.json" | cut -d' ' -f1)"
finish $rc
