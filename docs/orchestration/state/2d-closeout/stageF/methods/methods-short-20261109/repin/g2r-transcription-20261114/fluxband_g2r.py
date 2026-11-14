#!/usr/bin/env python3
"""\\fluxBand under C_new (#981 re-pin row RP38): the median per-cell relative sigma of the rebuilt Flux band, from
committed files only. Run from the top of a checkout: python3 fluxband_g2r.py. Writes nothing. Requires numpy.

The computation, as RE-2's budget defines \\fluxBand (re2c_build_q.py: budget["bands"]["Flux"] = metrics(...), whose
median_pct is float(100 * np.median(np.sqrt(np.maximum(np.diag(C), 0)) / x))):
  C_Flux = wcov(X_Flux, w_flux), where
  - X_Flux is the 100 Flux universe rows of transcription/g2r_bands.csv (data_g2r.npz's band__Flux, rebuilt by G2R);
  - w_flux is the 100 per-universe Flux weights committed in COV2D's readout blocks (blocks_G18.npz, blocks_AR23.npz,
    member w_flux, written from re2c_rollup.flux_weights(), the function G2R's data phase calls);
  - wcov is build_repair.py's weighted covariance, the one re2c_rollup.band_cov calls, executed from its committed
    source;
  - x is the 205 reported cells' cross section, c2a's cov2d_x.csv.
Checks before the number is printed:
  1. every input's sha256 equals its pin;
  2. w_flux is bitwise equal in the two blocks files, and its sum and n_eff = sum^2 / sum(w^2) equal those G2R's data
     phase logged ("weights_equal_vl175_build_json", readout/data/connect.log.txt) exactly;
  3. the 38 band covariances, Flux weighted by w_flux and every other band unweighted, summed in sorted band order,
     equal g2r_C_univ_new.csv to 1e-15 of its largest entry. That validates the weights and the formula against the
     block G2R built.
"""
import ast
import csv
import hashlib
import subprocess
import sys

import numpy as np

HERE = "docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109/repin/g2r-transcription-20261114"
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d"
PINS = {
    f"{HERE}/transcription/g2r_bands.csv": "8caa9ed6eee9f360a60edcdd800230f27cce2f37286b0f302ed4cf0fb7572613",
    f"{HERE}/transcription/g2r_C_univ_new.csv": "28216af51712932a305f576c58976c7fcc6631cfd046603c1d135c5d7d6a6103",
    f"{FD}/readout/G18/blocks_G18.npz": "7eb657b82ae953bdf0584eda27264c52a64bcb48baea52dfc194f5efe440ea3d",
    f"{FD}/readout/AR23/blocks_AR23.npz": "abaebaeae6c9cb075dcb974a420dbf148809d01b2cabc8deda31f318bf6715ee",
    "docs/orchestration/state/2d-closeout/c04-repair/scripts/build_repair.py":
        "b5363a948bd2816442a95be6a4cd25f34797386aee90b34534286321b0e389d5",
}
C2A_X = ("origin/pkg/methods-result-20261109", "docs/orchestration/state/2d-closeout/stageF/methods/"
         "result-package-20261109/receipts/c2a-20261109/transcription/cov2d_x.csv",
         "f0612bcc3bc432e90b6a1546a106043a7c525d4cae69e29ebdcec6a4505df723")
LOGGED = (211.01200325082078, 19.060534772246488)   # readout/data/connect.log.txt:14
TOL = 1e-15


def read(path, want, ref=None):
    b = (subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, check=True).stdout if ref
         else open(path, "rb").read())
    got = hashlib.sha256(b).hexdigest()
    if got != want:
        raise SystemExit(f"FLUXBAND: {path} has sha256 {got}, pinned {want}")
    return b


def main():
    raw = {p: read(p, s) for p, s in PINS.items()}
    xr = list(csv.reader(read(C2A_X[1], C2A_X[2], C2A_X[0]).decode().splitlines()))
    ids = [int(r[0]) for r in xr[1:]]
    x = np.array([float(r[1]) for r in xr[1:]], dtype=np.float64)
    print("1. inputs: every sha256 equals its pin")

    import io
    w = [np.load(io.BytesIO(raw[f"{FD}/readout/{t}/blocks_{t}.npz"]), allow_pickle=False)["w_flux"]
         for t in ("G18", "AR23")]
    same = w[0].dtype == np.float64 and w[0].shape == (100,) and w[0].tobytes() == w[1].tobytes()
    s, neff = float(w[0].sum()), float(w[0].sum() ** 2 / (w[0] ** 2).sum())
    print(f"2. w_flux: shape {w[0].shape}, bitwise equal in G18 and AR23: {same}; sum {s!r}, n_eff {neff!r}; "
          f"logged by G2R {LOGGED[0]!r}, {LOGGED[1]!r}")
    if not same or (s, neff) != LOGGED:
        raise SystemExit("FLUXBAND: the Flux weights do not match")
    w = w[0]

    tree = ast.parse(raw["docs/orchestration/state/2d-closeout/c04-repair/scripts/build_repair.py"].decode())
    fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "wcov"]
    if len(fn) != 1:
        raise SystemExit("FLUXBAND: build_repair.py has no single wcov")
    ns = {"np": np}
    exec(compile(ast.Module(fn, []), "build_repair.wcov", "exec"), ns)
    wcov = ns["wcov"]

    rows = list(csv.reader(raw[f"{HERE}/transcription/g2r_bands.csv"].decode().splitlines()))
    if [int(v) for v in rows[0][2:]] != ids:
        raise SystemExit("FLUXBAND: g2r_bands.csv's ids differ from c2a's")
    bands = {}
    for r in rows[1:]:
        bands.setdefault(r[0], []).append([float(v) for v in r[2:]])
    bands = {k: np.array(v, dtype=np.float64) for k, v in bands.items()}
    ur = list(csv.reader(raw[f"{HERE}/transcription/g2r_C_univ_new.csv"].decode().splitlines()))
    un = np.array([[float(v) for v in r[1:]] for r in ur[1:]], dtype=np.float64)
    tot = np.zeros((205, 205))
    for b in sorted(bands):
        tot += wcov(bands[b], w if b == "Flux" else np.ones(bands[b].shape[0]))
    res = float(np.max(np.abs(tot - un)) / np.max(np.abs(un)))
    print(f"3. {len(bands)} band covariances ({sum(v.shape[0] for v in bands.values())} universes; Flux has "
          f"{bands['Flux'].shape[0]}) summed: largest |residual| / max|C_univ_new| = {res:.3e} (tolerance {TOL:g})")
    if bands["Flux"].shape[0] != 100 or not res <= TOL:
        raise SystemExit("FLUXBAND: the band sum does not reproduce C_univ_new")

    C = wcov(bands["Flux"], w)
    med = float(100 * np.median(np.sqrt(np.maximum(np.diag(C), 0)) / x))
    print(f"FLUXBAND :: PASS  Flux band median relative sigma under C_new = {med!r} %  (printed {med:.2f}; "
          f"RE-2's value under the current covariance is 3.7124503352159897, printed 3.71)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
