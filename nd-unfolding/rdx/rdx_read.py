#!/usr/bin/env python3
"""RDX readings (RDX-DECLARATION.md §4): NC-X, then R1p, R1, R2, R3, R4 and the outcome, on the fifteen S3a/S3b
products. Numpy only; it runs on the laptop, in a clean clone at the bound sha, on products fetched by O_NOATIME copy.

    rdx_read.py --products <dir of the 15 .npz> --log-s3a <rdx_s3_a job log> --log-s3b <rdx_s3_b job log> \
                --out <readout.json>

Refusals, each before anything is written ([FAIL], exit status nonzero):
  - the task table is not the bound one (rdx_tasks.tsv, sha256 TASKS_SHA256; fifteen unique rows), or a sums manifest
    repeats a key;
  - the product directory holds any .npz other than the fifteen;
  - a job log has a malformed product line (any line naming /products/ that is not `<sha256>  <path>/products/<task>.npz`),
    names an undeclared task, prints a task twice, prints a task in the other job's log, or misses a task;
  - a product whose sha256 is not the one its own job printed (sbatch_rdx_arms.sh prints `sha256sum` of every product
    it wrote);
  - a product that is not the producer's (pvl_unfold.py, rdx_unfold.py): its arrays (xsec_flat float64 of the fine
    grid's size, shape equal to the fine grid's, xtrue_flat on exactly the closures, all finite), or its meta (rung,
    arm, features, closure, the tune_v1 ratio, seed 42, 5 iterations, 32 threads, its input and background pins, X0's
    estimator and refinement parameters, present; the RDX options; the instrumented fit and predict counts; the weight
    sums; the A7 hypothesis pin; the transfer records' schema, with iterations 0-4 in order and 16 finite-or-None cells);
  - NC-X: X0's and X0_lat's product arrays (xsec_flat and shape, the arrays a product carries besides its meta, which
    differs by the declared input pins) must be bitwise equal: dtype, shape and bytes. "If NC-X fails, nothing is read";
  - a closure family whose truth references differ: X0c, X1c, X1pc and X1wc share the prior's closure, X0g and X1g the
    A7 GiBUU hybrid's, X0q and X1q the q3 tilt's (§4's "the same closure"), compared bitwise;
  - phi_c or sigma_c that are not 16 finite positive values; a cell integral that is not 16 finite values; a reference
    that is not positive; any non-finite result.
phi_c and sigma_c are read only from their committed records, through RSN's bound reader (rsn_read.py): phi_c is
i0.json's data jitter over cmodel_5d.json's P5 integrals, reproduced at its printed precision; sigma_c is the committed
F1 readout's reported relative sigma. The W and T classes are RSN's (rsn_read.wr_class, rsn_read.transfer_class).

MEASURES: classification of the declared differences between recorded products. CANNOT AUTHORIZE: a paper or note
sentence, a change to the unfolding, or any statement outside MP-1's chain. Any note-facing text goes to a side branch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ND = _HERE.parent
_ROOT = _ND.parent
_PVL = _ND / "pv-ladder"
for _p in (str(_ND / "rsn"), str(_PVL), str(_ND), str(_ROOT / "2d-unfolding" / "pv2d"),
           str(_ROOT / "2d-unfolding" / "pv2d" / "cmodel")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import rsn_read as RR  # noqa: E402

TASKS = _HERE / "rdx_tasks.tsv"
TASKS_SHA256 = "3ec5069127f5f937c84b4efdb34bdcc99d8acc4b20891f1b26b25e32d27f75b9"  # RDX-DECLARATION.md:240
TASK_NAMES = ("X0", "X0_lat", "X1", "X1p", "X1w", "X1t", "X0c", "X1c", "X1pc", "X1wc", "X0t", "X0g", "X1g", "X0q", "X1q")
JOBS = ("S3a", "S3b")
SUMS = _HERE / "rdx-inputs-SHA256SUMS"
PVL_SUMS = _PVL / "prep-SHA256SUMS"
DEFINITION = _PVL / "readouts" / "h2_definition.json"
STAGE1 = _ROOT / "docs/orchestration/state/s5p/stage1/stage1_inspect.json"
RATIO_KEY = "./ratios/L-5D-PV/tune_v1.json"
AXES5 = ["pt", "pz", "eavail", "q3", "W"]
SEED, ITERS, THREADS = 42, 5, 32
N_DECILES = 10  # rsn_unfold.py:65
A7_HYPOTHESIS_SHA256 = "0080495c911143be29bbd780063a85b2890cd30d10c1e5b29f1f5cdb71013a77"  # rsn_unfold.py:60
TRANSFER_KEYS = {"iteration", "n_masked", "rel_bias", "rel_rms", "cell_bias", "acceptance_edges",
                 "acceptance_decile_rel_bias"}  # rsn_unfold.summarize
FAMILIES = {"prior": ("X0c", "X1c", "X1pc", "X1wc"), "gibuu": ("X0g", "X1g"), "q3": ("X0q", "X1q")}
SHA_LINE = re.compile(r"^([0-9a-f]{64})  \S*/products/([A-Za-z0-9_-]+)\.npz$")
CELLS = [f"R{c:02d}" for c in range(16)]
# §4, RDX-DECLARATION.md:497-507, in its own characters
SENTENCE = ("in MP-1's chain, adding E_ν, the true vertex and the leading-proton KE to the misses regressor moves the "
            "unfolded result by no more than half the reported σ in any cell, beyond the refit null")
SILENT = "It is silent on any quantity not added."
REFIT_W2 = ("the refit alone moves the result in the named cells. R1 is not attributable, and that is reported with no "
            "claim about the three quantities.")
SENSITIVITY = ("a stated sensitivity, with the cells named. Whether the unfolding changes is a separate decision for "
               "Joseph.")
# Where §4 leaves the reader a choice, the choice made here; each is put to the audit and to J7.
INTERPRETATIONS = [
    "1. R1's attributable excess e_c = |delta1_c| - |deltap_c| is compared with 0.5 sigma_c per cell; a cell is named "
    "when e_c > 0.5 sigma_c, and equality stays on the licensed side (§4: 'max_c e_c <= 0.5 sigma_c' licenses, 'some "
    "e_c > 0.5 sigma_c' does not)",
    "2. R4 reads each closure against its family's common truth: b = X / X_true - 1 on the 16 cells (RSN rev 3 §3.3), "
    "and a change is the difference of two such biases; the reader refuses a family whose truths differ",
    "3. R4 at the prior: the attributable change is max(0, |b(X1c) - b(X0c)| - |b(X1pc) - b(X0c)|) per cell, R1's "
    "excess applied to the closures, W-classed; the clipped vector is the one stored and classed",
    "4. R4 at the A7 GiBUU hybrid and the q3 tilt: no refit null was declared there, so the change b(X1) - b(X0) is read "
    "in full as the attributable change",
    "5. R4's X1wc - X1c (the weight at the prior) is reported and W-classed beside R2, as a qualifier; it is not one of "
    "the outcome's 'attributable changes at all three truths'",
    "6. R3's difference is t_c(X1t) - t_c(X0t) at the last iteration, T-classed as each transfer is; a cell with no "
    "masked rows in either is None and fails T0 and T1, as in RSN",
]


class RdxReadError(SystemExit):
    pass


def fail(msg: str):
    raise RdxReadError(f"[FAIL] {msg}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sums(path: Path) -> dict:
    out = {}
    for ln in Path(path).read_text().splitlines():
        if not ln.strip():
            continue
        sha, name = ln.split()
        if name in out:
            fail(f"{path}: the key {name} appears twice")
        out[name] = sha
    return out


def tasks(path: Path = TASKS, expect_sha: str | None = TASKS_SHA256) -> dict:
    if expect_sha is not None and sha256(path) != expect_sha:
        fail(f"{path}: sha256 is not the bound task table's {expect_sha}")
    out = {}
    for ln in Path(path).read_text().splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        task, job, features, permute, weight, truth, transfer, closure, inputs, _ = ln.split("\t")
        if task in out:
            fail(f"{path}: the task {task} appears twice")
        if job not in JOBS:
            fail(f"{path}: {task}'s job {job!r} is not one of {JOBS}")
        out[task] = {"job": job, "features": features, "permute": None if permute == "-" else int(permute),
                     "weight": weight, "truth": truth, "transfer": transfer == "yes", "closure": closure == "yes",
                     "inputs": inputs}
    if tuple(out) != TASK_NAMES:
        fail(f"{path}: the tasks are {list(out)}, not §4's fifteen")
    return out


def log_shas(logs: dict, spec: dict) -> dict:
    """{task: sha256} from each job's `sha256sum` lines; logs = {job: path}."""
    seen: dict = {}
    for job, p in logs.items():
        for ln in Path(p).read_text(errors="replace").splitlines():
            s = ln.strip()
            m = SHA_LINE.match(s)
            if not m:
                if "/products/" in s:
                    fail(f"{p}: a malformed product line: {s[:120]!r}")
                continue
            sha, task = m.groups()
            if task not in spec:
                fail(f"{p}: the log names a product {task} that is not a declared task")
            if spec[task]["job"] != job:
                fail(f"{p}: {task} is {spec[task]['job']}'s product, printed in {job}'s log")
            if task in seen:
                fail(f"the logs print {task}'s sha256 more than once")
            seen[task] = sha
    missing = sorted(set(spec) - set(seen))
    if missing:
        fail(f"the logs print no sha256 for {missing}")
    return seen


def load(path: Path) -> tuple:
    """(meta, xsec_flat, xtrue_flat or None, shape), the arrays as stored, unconverted."""
    z = np.load(path, allow_pickle=False)
    for k in ("meta", "xsec_flat", "shape"):
        if k not in z.files:
            fail(f"{path.name}: no {k}")
    extra = set(z.files) - {"meta", "xsec_flat", "shape", "xtrue_flat"}
    if extra:
        fail(f"{path.name}: unexpected arrays {sorted(extra)}")
    meta = json.loads(str(z["meta"]))
    return meta, np.asarray(z["xsec_flat"]), (np.asarray(z["xtrue_flat"]) if "xtrue_flat" in z.files else None), \
        np.asarray(z["shape"])


def finite(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def transfer_problems(recs) -> list:
    """rsn_unfold.summarize's records, one per iteration, iterations 0..4 in order (rdx_unfold: k = len(fits))."""
    if not isinstance(recs, list) or len(recs) != ITERS:
        return ["a transfer step must carry one transfer record per iteration"]
    bad = []
    if [r.get("iteration") if isinstance(r, dict) else None for r in recs] != list(range(ITERS)):
        bad.append("the transfer records' iterations are not 0..4 in order")
    for r in recs:
        if not isinstance(r, dict) or set(r) != TRANSFER_KEYS:
            bad.append("a transfer record does not have summarize's fields")
            continue
        cb, dec, edges = r["cell_bias"], r["acceptance_decile_rel_bias"], r["acceptance_edges"]
        if not (isinstance(r["n_masked"], int) and r["n_masked"] > 0 and finite(r["rel_bias"]) and finite(r["rel_rms"])):
            bad.append(f"iteration {r['iteration']}: n_masked, rel_bias or rel_rms is not valid")
        if not isinstance(cb, list) or len(cb) != 16 or not all(v is None or finite(v) for v in cb):
            bad.append(f"iteration {r['iteration']}: cell_bias is not 16 finite values or None")
        if not isinstance(dec, list) or len(dec) != N_DECILES or not all(v is None or finite(v) for v in dec):
            bad.append(f"iteration {r['iteration']}: acceptance_decile_rel_bias is not {N_DECILES} values")
        if not isinstance(edges, list) or len(edges) != N_DECILES + 1 or not all(finite(v) for v in edges):
            bad.append(f"iteration {r['iteration']}: acceptance_edges is not {N_DECILES + 1} values")
    return bad


def identity_problems(meta: dict, spec: dict, pins: dict, ref: dict | None) -> list:
    """The declared task's identity; ref is X0's meta, for what must not change across the fifteen."""
    bad = []
    lat = spec["inputs"] == "lat_zero"
    ident = {"schema": "pvl-unfold/1", "rung": "L-5D-PV", "arm": "e", "features": AXES5, "closure": spec["closure"],
             "ratio_sha256": pins["ratio"], "estimator_seed": SEED, "iters": ITERS, "threads": THREADS,
             "input_npz_sha256": pins["lat_zero.npz" if lat else "lat_RDX_ALL.npz"],
             "bkg_dump_sha256": pins["lat_zero_bkg.npz" if lat else "lat_RDX_ALL_bkg.npz"]}
    for k, v in ident.items():
        if meta.get(k) != v:
            bad.append(f"{k} {meta.get(k)!r} != {v!r}")
    params = meta.get("estimator_params")
    if not params or not isinstance(params, (dict, list)):
        bad.append("estimator_params are absent")
    refine = meta.get("refinement") or {}
    if spec["closure"]:
        if refine.get("ran") is not False:
            bad.append("a closure must record that the refinement did not run")
    else:
        if refine.get("ran") is not True:
            bad.append("the refinement must have run")
        if not refine.get("classifier_params") or not isinstance(refine.get("classifier_params"), dict):
            bad.append("the refinement's classifier_params are absent")
    if ref is not None:
        if params != ref.get("estimator_params"):
            bad.append("estimator_params differ from X0's")
        if not spec["closure"] and refine.get("classifier_params") != (ref.get("refinement") or {}).get("classifier_params"):
            bad.append("refinement parameters differ from X0's")
    r = meta.get("rdx")
    if not isinstance(r, dict):
        return bad + ["no rdx record"]
    wide = spec["features"] == "wide"
    want = {"regressor_features": spec["features"], "regressor_weight": spec["weight"], "truth": spec["truth"],
            "transfer": spec["transfer"], "truthx_permute": spec["permute"],
            "truthx_sidecar_sha256": pins["truthx_RDX_ALL.npz"] if wide else None}
    for k, v in want.items():
        if r.get(k) != v:
            bad.append(f"rdx.{k} {r.get(k)!r} != {v!r}")
    instrumented = wide or spec["weight"] != "none" or spec["transfer"]
    if instrumented:
        if r.get("fit_calls") != ITERS or r.get("predict_calls") != ITERS:
            bad.append(f"rdx.fit_calls {r.get('fit_calls')!r} or predict_calls {r.get('predict_calls')!r} != {ITERS}")
        if not (isinstance(r.get("rows"), int) and r["rows"] > 0):
            bad.append("rdx.rows is not a positive count")
        ws = r.get("weight_sums")
        if spec["weight"] != "none":
            if not isinstance(ws, list) or len(ws) != ITERS or not all(finite(v) and v > 0 for v in ws):
                bad.append("a weighted step must record five positive weight sums")
        elif ws is not None:
            bad.append("an unweighted step must record no weight sums")
    else:
        for k in ("fit_calls", "predict_calls", "rows", "weight_sums"):
            if r.get(k) is not None:
                bad.append(f"an uninstrumented step must not record rdx.{k}")
    if spec["transfer"]:
        bad += transfer_problems(r.get("transfer_records"))
    elif "transfer_records" in r:
        bad.append("a step without the transfer diagnostic carries transfer records")
    if spec["truth"] == "a7_gibuu":
        if r.get("a7_hypothesis_sha256") != A7_HYPOTHESIS_SHA256:
            bad.append("rdx.a7_hypothesis_sha256 is not the A7 hypothesis pin")
    elif "a7_hypothesis_sha256" in r:
        bad.append("only an A7 GiBUU step carries the A7 hypothesis pin")
    return bad


def array_problems(x, xt, shp, closure: bool, n_fine: int, fine_shape: tuple) -> list:
    bad = []
    for name, a in (("xsec_flat", x), ("xtrue_flat", xt)):
        if a is None:
            continue
        if a.dtype != np.float64 or a.ndim != 1 or a.size != n_fine:
            bad.append(f"{name} is {a.dtype} {a.shape}, not float64 ({n_fine},)")
        elif not np.all(np.isfinite(a)):
            bad.append(f"{name} has non-finite values")
    if (xt is not None) != closure:
        bad.append("a truth reference is carried exactly by the closures")
    if shp.dtype.kind not in "iu" or tuple(int(v) for v in shp.ravel()) != tuple(fine_shape):
        bad.append(f"shape {shp.tolist()} is not the fine grid {list(fine_shape)}")
    return bad


def same_bits(a, b) -> bool:
    return a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()


def rel(a, b) -> np.ndarray:
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != (16,) or b.shape != (16,):
        fail("a relative difference needs two 16-cell vectors")
    if np.any(b <= 0) or not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        fail("a relative difference needs finite values and a positive reference in every cell")
    with np.errstate(over="raise", invalid="raise"):
        return a / b - 1.0


def excess_class(e, phi, sigma) -> tuple[str, list]:
    return RR.wr_class(e, phi, sigma)


def all_finite(obj) -> bool:
    if isinstance(obj, float):
        return math.isfinite(obj)
    if isinstance(obj, dict):
        return all(all_finite(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return all(all_finite(v) for v in obj)
    return True


def read(prod: dict, integ, phi, sigma) -> dict:
    """prod: {task: (meta, xsec_flat, xtrue_flat or None, shape)}, arrays as stored, already sha-, array- and
    identity-checked; integ: xsec -> the 16 cell integrals."""
    phi, sigma = np.asarray(phi, float), np.asarray(sigma, float)
    for name, v in (("phi_c", phi), ("sigma_c", sigma)):
        if v.shape != (16,) or not np.all(np.isfinite(v)) or np.any(v <= 0):
            fail(f"{name} must be 16 finite positive values")
    x0, xl = prod["X0"], prod["X0_lat"]
    if not (same_bits(x0[1], xl[1]) and same_bits(x0[3], xl[3])):
        fail("NC-X: X0's product arrays (xsec_flat, shape) are not bitwise X0_lat's; nothing is read")
    for fam, members in FAMILIES.items():
        t0 = prod[members[0]][2]
        for t in members:
            if prod[t][2] is None or not same_bits(prod[t][2], t0):
                fail(f"the {fam} closure family's truth references differ ({members[0]} vs {t})")

    def cells(x):
        c = np.asarray(integ(np.asarray(x, float)), float)
        if c.shape != (16,) or not np.all(np.isfinite(c)):
            fail("a cell integral is not 16 finite values")
        return c

    X = {t: cells(v[1]) for t, v in prod.items()}

    def bias(t):
        return rel(X[t], cells(prod[t][2]))

    dp = rel(X["X1p"], X["X0"])
    d1 = rel(X["X1"], X["X0"])
    e = np.abs(d1) - np.abs(dp)
    e_cells = [CELLS[c] for c in np.flatnonzero(e > RR.HALF_SIGMA * sigma)]
    c1p, cells1p = RR.wr_class(dp, phi, sigma)
    c1, cells1 = RR.wr_class(d1, phi, sigma)
    d2 = rel(X["X1w"], X["X1"])
    c2, cells2 = RR.wr_class(d2, phi, sigma)
    t1 = prod["X1t"][0]["rdx"]["transfer_records"][-1]["cell_bias"]
    t0 = prod["X0t"][0]["rdx"]["transfer_records"][-1]["cell_bias"]
    for t in (t1, t0):
        if len(t) != 16 or not all(v is None or finite(v) for v in t):
            fail("a transfer cell_bias is not 16 finite values or None")
    td = [None if a is None or b is None else a - b for a, b in zip(t1, t0)]
    r3 = {name: dict(zip(("class", "cells_beyond_half_sigma"), RR.transfer_class(t, phi, sigma)), cell_bias=t)
          for name, t in (("X1t", t1), ("X0t", t0), ("difference", td))}
    r3["loop_untouched"] = {"X1t_equals_X1_bitwise": same_bits(prod["X1t"][1], prod["X1"][1]),
                            "X0t_equals_X0_bitwise": same_bits(prod["X0t"][1], prod["X0"][1])}
    b = {t: bias(t) for fam in FAMILIES.values() for t in fam}
    D1, Dp = b["X1c"] - b["X0c"], b["X1pc"] - b["X0c"]
    a_prior = np.maximum(np.abs(D1) - np.abs(Dp), 0.0)
    r4 = {"prior": {"change": D1.tolist(), "null": Dp.tolist(), "attributable": a_prior.tolist()},
          "gibuu": {"change": (b["X1g"] - b["X0g"]).tolist()},
          "q3": {"change": (b["X1q"] - b["X0q"]).tolist()},
          "weight_at_prior": {"change": (b["X1wc"] - b["X1c"]).tolist()}}
    r4["prior"]["class"], r4["prior"]["cells"] = excess_class(a_prior, phi, sigma)
    for t in ("gibuu", "q3", "weight_at_prior"):
        r4[t]["class"], r4[t]["cells"] = RR.wr_class(r4[t]["change"], phi, sigma)
    r4["bias"] = {t: v.tolist() for t, v in b.items()}
    attributable = {t: r4[t]["class"] for t in ("prior", "gibuu", "q3")}
    if c1p == "W2":
        outcome = {"outcome": "REFIT NULL W2", "statement": REFIT_W2, "cells": cells1p}
    elif not e_cells and all(v in ("W0", "W1") for v in attributable.values()):
        outcome = {"outcome": "LICENSED", "statement": SENTENCE, "silent": SILENT}
    else:
        named = {"R1_excess": e_cells, **{f"R4_{t}": r4[t]["cells"] for t, v in attributable.items() if v == "W2"}}
        outcome = {"outcome": "STATED SENSITIVITY", "statement": SENSITIVITY, "cells": named}
    out = {
        "schema": "rdx-readout/2",
        "label": "in MP-1's chain, and only for E_ν, the true vertex and the leading-proton KE (RDX-DECLARATION.md §4); "
                 "their reading is a difference within MP-1's chain, not against the paper's chain",
        "nc_x": "PASS: X0's xsec_flat and shape are bitwise X0_lat's",
        "R1p": {"delta": dp.tolist(), "class": c1p, "cells": cells1p},
        "R1": {"delta": d1.tolist(), "class": c1, "cells": cells1, "excess": e.tolist(),
               "excess_over_sigma_max": float(np.max(e / sigma)), "cells_excess_beyond_half_sigma": e_cells},
        "R2": {"delta": d2.tolist(), "class": c2, "cells": cells2, "role": "qualifies R1"},
        "R3": dict(r3, role="qualifies R1"),
        "R4": r4,
        "outcome": outcome,
        "phi": phi.tolist(), "sigma": sigma.tolist(),
        "interpretations": INTERPRETATIONS,
    }
    if not all_finite(out):
        fail("a computed value is not finite")
    return out


def checked_products(products: Path, logs: dict, spec: dict, pins: dict, n_fine: int, fine_shape: tuple) -> tuple:
    found = sorted(p.stem for p in Path(products).glob("*.npz"))
    if found != sorted(spec):
        fail(f"{products} holds {found}, not exactly the fifteen products")
    shas = log_shas(logs, spec)
    prod, got = {}, {}
    for task in spec:
        p = Path(products) / f"{task}.npz"
        got[task] = sha256(p)
        if got[task] != shas[task]:
            fail(f"{task}: sha256 {got[task]} is not the {shas[task]} its job printed")
        prod[task] = load(p)
        bad = array_problems(prod[task][1], prod[task][2], prod[task][3], spec[task]["closure"], n_fine, fine_shape)
        if bad:
            fail(f"{task}: {'; '.join(bad)}")
    ref = prod["X0"][0]
    for task, s in spec.items():
        bad = identity_problems(prod[task][0], s, pins, None if task == "X0" else ref)
        if bad:
            fail(f"{task}: {'; '.join(bad)}")
    return prod, got


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--products", type=Path, required=True)
    ap.add_argument("--log-s3a", type=Path, required=True)
    ap.add_argument("--log-s3b", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--definition", type=Path, default=DEFINITION)
    ap.add_argument("--stage1", type=Path, default=STAGE1)
    a = ap.parse_args(argv)
    if a.out.exists():
        fail(f"refusing to overwrite {a.out}")
    import build_cmodel5d as B5  # numpy only; imported here so the tests need no definition files
    import pvl_lib as L
    spec = tasks()
    pins = {k.lstrip("./"): v for k, v in sums(SUMS).items()}
    pins["ratio"] = sums(PVL_SUMS)[RATIO_KEY]
    fine_shape = tuple(len(L.FINE[ax]) - 1 for ax in L.AXES5)
    rmap, n = B5.load_definition(a.definition, a.stage1, B5.EXPECT)[:2]
    if n != 16 or rmap.size != int(np.prod(fine_shape)):
        fail(f"the definition gives {n} cells over {rmap.size} fine cells, not 16 over {int(np.prod(fine_shape))}")
    prod, got = checked_products(a.products, {"S3a": a.log_s3a, "S3b": a.log_s3b}, spec, pins, rmap.size, fine_shape)
    load_json = lambda p: json.loads(Path(p).read_text())  # noqa: E731
    phi = RR.rounding_floor(load_json(RR.I0), load_json(RR.CMODEL_JSON))
    sigma = np.asarray(load_json(RR.F1_READOUT)[RR.SIGMA_KEY]["C_total"], float)
    out = read(prod, lambda x: B5.integrals(x, rmap, n), phi, sigma)
    out["inputs"] = {"products_sha256": got, "i0": sha256(RR.I0), "cmodel_5d": sha256(RR.CMODEL_JSON),
                     "f1_readout": sha256(RR.F1_READOUT), "definition": sha256(a.definition),
                     "rdx_tasks": sha256(TASKS), "rdx_inputs_sums": sha256(SUMS),
                     "logs": {"S3a": sha256(a.log_s3a), "S3b": sha256(a.log_s3b)}}
    out["code_sha256"] = {"rdx_read.py": sha256(Path(__file__)), "rsn_read.py": sha256(Path(RR.__file__)),
                          "build_cmodel5d.py": sha256(Path(B5.__file__))}
    a.out.write_text(json.dumps(out, indent=1, ensure_ascii=False, allow_nan=False) + "\n")
    o = out["outcome"]
    print(f"[rdx] NC-X PASS; R1p {out['R1p']['class']}; R1 {out['R1']['class']} (excess cells "
          f"{out['R1']['cells_excess_beyond_half_sigma']}); R2 {out['R2']['class']}; R3 X1t {out['R3']['X1t']['class']}, "
          f"X0t {out['R3']['X0t']['class']}; R4 prior {out['R4']['prior']['class']}, gibuu {out['R4']['gibuu']['class']}, "
          f"q3 {out['R4']['q3']['class']}; OUTCOME {o['outcome']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
