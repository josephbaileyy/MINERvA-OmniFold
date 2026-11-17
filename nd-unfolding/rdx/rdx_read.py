#!/usr/bin/env python3
"""RDX readings (RDX-DECLARATION.md §4): NC-X, then R1p, R1, R2, R3, R4 and the outcome, on the fifteen S3a/S3b
products. Numpy only; it runs on the laptop, in a clean clone at the bound sha, on products fetched by O_NOATIME copy.

    rdx_read.py --products <dir of the 15 .npz> --log <rdx_s3_a job log> --log <rdx_s3_b job log> --out <readout.json>

Refusals, each before anything is written:
  - a product whose sha256 is not the one its job printed (sbatch_rdx_arms.sh prints `sha256sum` of every product it
    wrote; the --log files are those job logs). Every one of the fifteen tasks must be printed exactly once;
  - a product whose meta is not its declared task's (rdx_tasks.tsv): rung, arm, features, closure, the tune_v1 ratio,
    seed 42, 5 iterations, 32 threads, its input and background pins (rdx-inputs-SHA256SUMS), the estimator and
    refinement parameters of X0, and the RDX options with their fit, predict and transfer counts;
  - NC-X: X0's xsec_flat must equal X0_lat's bitwise. "If NC-X fails, nothing is read."
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
SUMS = _HERE / "rdx-inputs-SHA256SUMS"
PVL_SUMS = _PVL / "prep-SHA256SUMS"
DEFINITION = _PVL / "readouts" / "h2_definition.json"
STAGE1 = _ROOT / "docs/orchestration/state/s5p/stage1/stage1_inspect.json"
RATIO_KEY = "./ratios/L-5D-PV/tune_v1.json"
AXES5 = ["pt", "pz", "eavail", "q3", "W"]
SEED, ITERS, THREADS = 42, 5, 32
SHA_LINE = re.compile(r"^([0-9a-f]{64})  \S*/products/([A-Za-z0-9_]+)\.npz$")
CELLS = [f"R{c:02d}" for c in range(16)]
SENTENCE = ("in MP-1's chain, adding E_nu, the true vertex and the leading-proton KE to the misses regressor moves the "
            "unfolded result by no more than half the reported sigma in any cell, beyond the refit null")
SILENT = "It is silent on any quantity not added."
# Where §4 leaves the reader a choice, the choice made here; each is put to the audit and to J7.
INTERPRETATIONS = [
    "R1's attributable excess e_c = |delta1_c| - |deltap_c| is compared with 0.5 sigma_c per cell; a cell is named when "
    "e_c > 0.5 sigma_c (equality is not named, as RSN's W classes)",
    "R4 reads each closure against its own truth: b = X / X_true - 1 on the 16 cells (rsn_cmodel's closure bias), and a "
    "change is the difference of two such biases",
    "R4 at the prior: the attributable change is |b(X1c) - b(X0c)| - |b(X1pc) - b(X0c)| per cell, clipped at 0, W-classed",
    "R4 at the A7 GiBUU hybrid and the q3 tilt: no refit null was declared there, so the change b(X1) - b(X0) is read in "
    "full as the attributable change (conservative)",
    "R4's X1wc - X1c (the weight at the prior) is reported and W-classed beside R2, as a qualifier; it is not one of the "
    "outcome's 'attributable changes at all three truths'",
    "R3's difference is t_c(X1t) - t_c(X0t) at the last iteration, T-classed as each transfer is; a cell with no masked "
    "rows in either is None and fails T0 and T1, as in RSN",
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
    return dict(ln.split()[::-1] for ln in Path(path).read_text().splitlines() if ln.strip())


def tasks(path: Path = TASKS) -> dict:
    out = {}
    for ln in Path(path).read_text().splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        task, job, features, permute, weight, truth, transfer, closure, inputs, _ = ln.split("\t")
        out[task] = {"job": job, "features": features, "permute": None if permute == "-" else int(permute),
                     "weight": weight, "truth": truth, "transfer": transfer == "yes", "closure": closure == "yes",
                     "inputs": inputs}
    return out


def log_shas(logs: list, names) -> dict:
    """{task: sha256} from the jobs' `sha256sum` lines. Each declared task exactly once; no other product named."""
    seen: dict = {}
    for p in logs:
        for ln in Path(p).read_text(errors="replace").splitlines():
            m = SHA_LINE.match(ln.strip())
            if not m:
                continue
            sha, task = m.groups()
            if task not in names:
                fail(f"{p}: the log names a product {task} that is not a declared task")
            if task in seen:
                fail(f"the logs print {task}'s sha256 more than once")
            seen[task] = sha
    missing = sorted(set(names) - set(seen))
    if missing:
        fail(f"the logs print no sha256 for {missing}")
    return seen


def load(path: Path) -> tuple[dict, np.ndarray, np.ndarray | None]:
    z = np.load(path, allow_pickle=False)
    meta = json.loads(str(z["meta"]))
    x = np.asarray(z["xsec_flat"], float)
    xt = np.asarray(z["xtrue_flat"], float) if "xtrue_flat" in z.files else None
    return meta, x, xt


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
    refine = meta.get("refinement") or {}
    if spec["closure"]:
        if refine.get("ran") is not False:
            bad.append("a closure must record that the refinement did not run")
    elif refine.get("ran") is not True:
        bad.append("the refinement must have run")
    if ref is not None:
        if meta.get("estimator_params") != ref.get("estimator_params"):
            bad.append("estimator_params differ from X0's")
        if not spec["closure"] and refine.get("classifier_params") != (ref.get("refinement") or {}).get("classifier_params"):
            bad.append("refinement parameters differ from X0's")
    r = meta.get("rdx") or {}
    wide = spec["features"] == "wide"
    want = {"regressor_features": spec["features"], "regressor_weight": spec["weight"], "truth": spec["truth"],
            "transfer": spec["transfer"], "truthx_permute": spec["permute"],
            "truthx_sidecar_sha256": pins["truthx_RDX_ALL.npz"] if wide else None}
    for k, v in want.items():
        if r.get(k) != v:
            bad.append(f"rdx.{k} {r.get(k)!r} != {v!r}")
    instrumented = wide or spec["weight"] != "none" or spec["transfer"]
    if r.get("fit_calls") != (ITERS if instrumented else None):
        bad.append(f"rdx.fit_calls {r.get('fit_calls')!r}")
    if wide and r.get("predict_calls") != ITERS:
        bad.append(f"rdx.predict_calls {r.get('predict_calls')!r}")
    if spec["transfer"] and len(r.get("transfer_records") or []) != ITERS:
        bad.append("a transfer step must carry one transfer record per iteration")
    return bad


def rel(a, b) -> np.ndarray:
    a, b = np.asarray(a, float), np.asarray(b, float)
    if np.any(b <= 0) or not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        fail("a relative difference needs finite values and a positive reference in every cell")
    return a / b - 1.0


def excess_class(e, phi, sigma) -> tuple[str, list]:
    """An attributable excess, clipped at 0 (a smaller change than the null is no attributable change), W-classed."""
    return RR.wr_class(np.maximum(np.asarray(e, float), 0.0), phi, sigma)


def read(prod: dict, integ, phi, sigma) -> dict:
    """prod: {task: (meta, x, xt)}, already sha- and identity-checked; integ: x -> the 16 cell integrals."""
    phi, sigma = np.asarray(phi, float), np.asarray(sigma, float)
    if phi.shape != (16,) or sigma.shape != (16,) or np.any(phi <= 0) or np.any(sigma <= 0):
        fail("phi_c and sigma_c must be 16 positive values")
    if not np.array_equal(prod["X0"][1], prod["X0_lat"][1]):
        fail("NC-X: X0's product does not equal X0_lat's bitwise; nothing is read")
    X = {t: integ(v[1]) for t, v in prod.items()}

    def bias(t):
        xt = prod[t][2]
        if xt is None:
            fail(f"{t} carries no truth reference")
        return rel(X[t], integ(xt))

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
    td = [None if a is None or b is None else a - b for a, b in zip(t1, t0)]
    r3 = {name: dict(zip(("class", "cells_beyond_half_sigma"), RR.transfer_class(t, phi, sigma)), cell_bias=t)
          for name, t in (("X1t", t1), ("X0t", t0), ("difference", td))}
    r3["loop_untouched"] = {"X1t_equals_X1": bool(np.array_equal(prod["X1t"][1], prod["X1"][1])),
                            "X0t_equals_X0": bool(np.array_equal(prod["X0t"][1], prod["X0"][1]))}
    b = {t: bias(t) for t in ("X0c", "X1c", "X1pc", "X1wc", "X0g", "X1g", "X0q", "X1q")}
    D1, Dp = b["X1c"] - b["X0c"], b["X1pc"] - b["X0c"]
    a_prior = np.abs(D1) - np.abs(Dp)
    r4 = {"prior": {"change": D1.tolist(), "null": Dp.tolist(), "attributable": a_prior.tolist()},
          "gibuu": {"change": (b["X1g"] - b["X0g"]).tolist()},
          "q3": {"change": (b["X1q"] - b["X0q"]).tolist()},
          "weight_at_prior": {"change": (b["X1wc"] - b["X1c"]).tolist()}}
    r4["prior"]["class"], r4["prior"]["cells"] = excess_class(a_prior, phi, sigma)
    for t in ("gibuu", "q3", "weight_at_prior"):
        r4[t]["class"], r4[t]["cells"] = RR.wr_class(r4[t]["change"], phi, sigma)
    for t in ("X0c", "X1c", "X1pc", "X1wc", "X0g", "X1g", "X0q", "X1q"):
        r4.setdefault("bias", {})[t] = b[t].tolist()
    attributable = {t: r4[t]["class"] for t in ("prior", "gibuu", "q3")}
    if c1p == "W2":
        outcome = {"outcome": "REFIT NULL W2",
                   "statement": "the refit alone moves the result in the named cells; R1 is not attributable, and no "
                                "claim is made about the three quantities", "cells": cells1p}
    elif not e_cells and all(v in ("W0", "W1") for v in attributable.values()):
        outcome = {"outcome": "LICENSED", "statement": SENTENCE, "silent": SILENT}
    else:
        named = {"R1_excess": e_cells, **{f"R4_{t}": r4[t]["cells"] for t, v in attributable.items() if v == "W2"}}
        outcome = {"outcome": "STATED SENSITIVITY",
                   "statement": "a stated sensitivity in the named cells; whether the unfolding changes is a separate "
                                "decision for Joseph", "cells": named}
    return {
        "schema": "rdx-readout/1",
        "label": "in MP-1's chain, and only for E_nu, the true vertex and the leading-proton KE (RDX-DECLARATION.md §4); "
                 "their reading is a difference within MP-1's chain, not against the paper's chain",
        "nc_x": "PASS: X0 equals X0_lat bitwise",
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


def checked_products(products: Path, logs: list, spec: dict, pins: dict) -> tuple[dict, dict]:
    shas = log_shas(logs, list(spec))
    prod, got = {}, {}
    for task in spec:
        p = Path(products) / f"{task}.npz"
        if not p.is_file():
            fail(f"no product {p}")
        got[task] = sha256(p)
        if got[task] != shas[task]:
            fail(f"{task}: sha256 {got[task]} is not the {shas[task]} its job printed")
        prod[task] = load(p)
    ref = prod["X0"][0]
    for task, s in spec.items():
        bad = identity_problems(prod[task][0], s, pins, None if task == "X0" else ref)
        if bad:
            fail(f"{task}: {'; '.join(bad)}")
        if (prod[task][2] is not None) != s["closure"]:
            fail(f"{task}: a truth reference is carried exactly by the closures")
    return prod, got


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--products", type=Path, required=True)
    ap.add_argument("--log", type=Path, action="append", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--definition", type=Path, default=DEFINITION)
    ap.add_argument("--stage1", type=Path, default=STAGE1)
    a = ap.parse_args(argv)
    if a.out.exists():
        fail(f"refusing to overwrite {a.out}")
    import build_cmodel5d as B5  # numpy only; imported here so the tests need no definition files
    spec = tasks()
    s = sums(SUMS)
    pins = {k.lstrip("./"): v for k, v in s.items()}
    pins["ratio"] = sums(PVL_SUMS)[RATIO_KEY]
    prod, got = checked_products(a.products, a.log, spec, pins)
    rmap, n = B5.load_definition(a.definition, a.stage1, B5.EXPECT)[:2]
    load_json = lambda p: json.loads(Path(p).read_text())  # noqa: E731
    phi = RR.rounding_floor(load_json(RR.I0), load_json(RR.CMODEL_JSON))
    sigma = np.asarray(load_json(RR.F1_READOUT)[RR.SIGMA_KEY]["C_total"], float)
    out = read(prod, lambda x: B5.integrals(x, rmap, n), phi, sigma)
    out["inputs"] = {"products_sha256": got, "i0": sha256(RR.I0), "cmodel_5d": sha256(RR.CMODEL_JSON),
                     "f1_readout": sha256(RR.F1_READOUT), "definition": sha256(a.definition),
                     "rdx_tasks": sha256(TASKS), "rdx_inputs_sums": sha256(SUMS)}
    out["code_sha256"] = {"rdx_read.py": sha256(Path(__file__)), "rsn_read.py": sha256(Path(RR.__file__)),
                          "build_cmodel5d.py": sha256(Path(B5.__file__))}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    o = out["outcome"]
    print(f"[rdx] NC-X PASS; R1p {out['R1p']['class']}; R1 {out['R1']['class']} (excess cells "
          f"{out['R1']['cells_excess_beyond_half_sigma']}); R2 {out['R2']['class']}; R3 X1t {out['R3']['X1t']['class']}, "
          f"X0t {out['R3']['X0t']['class']}; R4 prior {out['R4']['prior']['class']}, gibuu {out['R4']['gibuu']['class']}, "
          f"q3 {out['R4']['q3']['class']}; OUTCOME {o['outcome']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
