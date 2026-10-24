#!/usr/bin/env python3
"""5D design Stage 0c (STAGE0-PARTA-DECLARATION.md): re-derive the GiBUU/GENIE E_avail shape ratio behind vertex D1
and the s5e GiBUU truth, from the flux-repaired 5D predictions (KNOWN_ISSUES 83).

frac[k] = sum over fine cells in E_avail bin k of xsec x cell volume, normalized over the bins (the s5n-eavail-ratio/1
definition, "content x width, normalized", applied to the 5D prediction's E_avail marginal); shape_ratio = num / den.

CONTROL first: the same construction on the UNREPAIRED 5D predictions must reproduce the committed s5n ratio
(state/s5n/eavail-ratio-gibuu-over-genie.json) to max |r / r_s5n - 1| <= 0.02 in every bin. The s5n ratio came from
the Stage-A 3D files; gen5d was built from a different GENIE sample (the work_seed sample,
state/s5p/gen5d/README-gen5d-build.md), so the control tests that the two constructions agree in E_avail shape, not
that they are identical. 0.02 is a declared choice, not derived from the record. If the control fails, the rebuild would
change more than the flux and the tool STOPS (exit 3) without writing the new ratio. Any non-positive E_avail bin
also STOPS, as in s5n_eavail_ratio.py.

Usage: python3 -I stage0c_ratio.py --s5n-ratio JSON --old-num NPZ --old-den NPZ --new-num NPZ --new-den NPZ --out JSON
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

TOL = 0.02


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def eavail_fractions(path: Path) -> tuple[np.ndarray, np.ndarray]:
    z = np.load(path, allow_pickle=False)
    shape = tuple(int(v) for v in z["shape"])
    e = [np.asarray(z[f"edges_{ax}"], float) for ax in ("pt", "pz", "eavail", "q3", "W")]
    w = [np.diff(x) for x in e]
    vol = w[0][:, None, None, None, None] * w[1][None, :, None, None, None] * w[2][None, None, :, None, None] \
        * w[3][None, None, None, :, None] * w[4][None, None, None, None, :]
    x = np.asarray(z["xsec_flat"], float).reshape(shape, order="C")
    m = (x * vol).sum(axis=(0, 1, 3, 4))
    if np.any(m <= 0):
        raise SystemExit(f"STOP: {path}: a non-positive E_avail bin {m.tolist()}")
    return e[2], m / m.sum()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    for k in ("s5n-ratio", "old-num", "old-den", "new-num", "new-den", "out"):
        ap.add_argument(f"--{k}", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    ref = json.loads(a.s5n_ratio.read_text())
    e_old, fn_old = eavail_fractions(a.old_num)
    _, fd_old = eavail_fractions(a.old_den)
    if not np.allclose(e_old, ref["eavail_edges"]):
        print("STOP: E_avail edges differ from the s5n ratio's", e_old, ref["eavail_edges"])
        return 3
    r_old = fn_old / fd_old
    dev = np.abs(r_old / np.asarray(ref["shape_ratio"], float) - 1.0)
    ctl = {"max_abs_rel_dev": float(dev.max()), "per_bin": dev.tolist(), "tol": TOL, "pass": bool(dev.max() <= TOL),
           "r_old_5d": r_old.tolist(), "r_s5n": ref["shape_ratio"]}
    print("CONTROL", json.dumps(ctl), flush=True)
    if not ctl["pass"]:
        a.out.with_suffix(".control.json").write_text(json.dumps(ctl, indent=1) + "\n")
        print("STOP: the unrepaired 5D marginal does not reproduce the s5n ratio")
        return 3
    e, fn = eavail_fractions(a.new_num)
    _, fd = eavail_fractions(a.new_den)
    if not np.allclose(e, e_old):
        print("STOP: repaired predictions use different E_avail edges")
        return 3
    out = {"schema": "s5n-eavail-ratio/1",
           "label": "GiBUU over GENIE CV E_avail shape, from the flux-repaired 5D predictions (5D design Stage 0c)",
           "definition": "shape_ratio[k] = frac_numerator[k] / frac_denominator[k], frac = the 5D prediction's E_avail "
                         "marginal (xsec x cell volume summed over pt, pz, q3, W), normalized over the bins",
           "eavail_edges": e.tolist(), "shape_ratio": (fn / fd).tolist(),
           "frac_numerator": fn.tolist(), "frac_denominator": fd.tolist(),
           "numerator": {"path": str(a.new_num), "sha256": sha256(a.new_num)},
           "denominator": {"path": str(a.new_den), "sha256": sha256(a.new_den)},
           "control": dict(ctl, old_numerator={"path": str(a.old_num), "sha256": sha256(a.old_num)},
                           old_denominator={"path": str(a.old_den), "sha256": sha256(a.old_den)},
                           s5n_ratio={"path": str(a.s5n_ratio), "sha256": sha256(a.s5n_ratio)}),
           "code_sha256": sha256(Path(__file__).resolve())}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print("WROTE", a.out, "shape_ratio", [round(v, 4) for v in out["shape_ratio"]], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
