#!/usr/bin/env python3
"""FD-PRR route 2: binned IBU on the same noise-free pseudo-data and the same unfolding MC as B0 (declaration §3.4).

    prr_ibu.py run --queue-dir DIR --stage JSON --out DIR

The experiment is not rebuilt here. Each B0 queue line (FD-PRR's own, from ``prr_probe.py tasks``) is run through the
bound runner ``s5p_nullexp.main``, unchanged, under B0's namespace check, and stopped where ``s5p_nullexp.build``
returns: before the refinement, before any unfold, before anything is written. The captured experiment is the one B0
unfolds, at the same split. Then, through REF-G1's code unchanged:

* the response is binned from MC half A, the rows and weights (e) was handed (``ibu1.half_from_experiment``; it
  refuses unless the experiment's unfolding MC is exactly half A x2);
* ``ref_g1.unfold_experiment``: IBU-1's D'Agostini update with the background as a known additive term (``fold``,
  primary) and subtracted (``sub``), on the H2 truth grid, integrated to R00-R15 (S1's functional rows), at every K;
* the truth on R00-R15 is the experiment's own x_true through the same rows.

R-ID (descriptive): at the nominal truth, the binned Cramer-Rao width of each reporting cell's truth count, by D-ID's
definition (``did.fisher``, ``did.widths_from_eig``), on the response, the prior and the known term the ``fold``
unfold used, captured as it calls ``did.ibu``. A cell's count is IBU's own representation of it: each H2 cell's
estimate spread over its fine cells by the prior shape (``did.share_matrix``), summed over the fine cells the cell's
S1 row covers.

R-SUP (descriptive): per truth and cell, MC half A's weights after the truth reweight (w_truth x r): their sum, sum
of squares, Kish effective count and largest single-row share (the 11-04 diagnosis's A-S at the reported cells).

C-IBU: the adapter, on REF-G1's NuWro closure experiment (``pvl_lib.closure_inputs`` on the full MC), reproduces
REF-G1's committed ``R2.nuwro.median_abs_residual_ibu`` to 1e-12 relative.

Every read outside the repository and the output is of a staged copy (``prr_probe.py stage``), under REF-G1's read
guard.

MEASURES: binned IBU estimates on the study's pseudo-data. CANNOT AUTHORIZE: a reading (``prr_read.py``) or a claim.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ND = HERE.parent
REPO = ND.parent
for _p in (HERE, ND / "ref_g1", ND / "ibu1", ND / "pv-ladder", ND):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import prr_probe as P  # noqa: E402

SCHEMA = "prr-route2/1"
KS = (1, 2, 3, 4, 5, 10, 20, 50, 200)
K_PRIMARY = 5
VARIANT = "fold"
CIBU = {"readout": "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ref-g1/a1-read/readout.json",
        "readout_sha256": "4db170d36cffa0be2aeb53926e94158ef4e5e2e1d88fa50dd29baeace8ed6fd7",
        "key": ("R2", "nuwro", "median_abs_residual_ibu"), "tol": 1e-12, "ratio": "nuwro"}
CODE_PINS = {
    "nd-unfolding/ref_g1/ref_g1.py": "8e34c48552857f5eec55e1067f70f4d26b2a6de0eaae46c57983fd91fbc6e7b1",
    "nd-unfolding/ref_g1/ref_g1_read.py": "46deacb6dd6034cd9a0ff8c3385c0a6b1a7754e99674889bd93111bea3a40e8b",
    "nd-unfolding/ref_g1/config.json": "2ac94c1d0bfc47958276be024cfe038177d777c3eeb7dc8b4e7aaaeb699b1436",
    "nd-unfolding/ibu1/ibu1.py": "f862a953425c006f6c73f2190bd65172eb9295f0f6c181d3d2247d4de881cf12",
    "nd-unfolding/ibu1/config.json": "82a24f419d4e738dec025840c92b66a163c34737528ed554fd5017424842e67f",
}


def experiments() -> list[tuple[str, int]]:
    """(truth, seed) of every IBU unfold: the 12 truths at the primary split, and the floor truth and the prior at each
    floor split (s_IBU, §3.5)."""
    return [(t, P.PRIMARY_SEED) for t in P.TRUTHS] + [(t, s) for s in P.FLOOR_SEEDS for t in (P.FLOOR_TRUTH, P.PRIOR)]


def b0_lines(queue_dir: Path) -> dict[tuple[str, int], list[str]]:
    """The runner argv of each B0 task, read from FD-PRR's own queues."""
    out = {}
    for j in P.JOBS:
        for line in (queue_dir / f"{j}.tsv").read_text().splitlines():
            if not line or line.startswith("#"):
                continue
            cols = line.split("\t")
            if cols[1] != "B0":
                continue
            argv = cols[4:]
            i = argv.index("--")
            truth = argv[argv.index("--truth") + 1]
            seed = int(argv[i + 1:][argv[i + 1:].index("--pseudo-seeds") + 1].split(":")[0])
            out[(truth, seed)] = argv[i + 1:]
    missing = [e for e in experiments() if e not in out]
    if missing:
        raise P.Refused(f"the queues carry no B0 line for {missing}")
    return out


# ------------------------------------------------------------------------------------------- the capture
class _Built(Exception):
    pass


@contextmanager
def _restored(module, names):
    saved = {n: getattr(module, n) for n in names}
    try:
        yield
    finally:
        for n, v in saved.items():
            setattr(module, n, v)


def capture(truth: str, argv: list[str], cache: dict, scratch: Path) -> dict:
    """Run B0's line through ``s5p_nullexp.main`` and stop where ``build`` returns. Returns the experiment, x_true,
    the split key and the per-row truth weight r the experiment handed ``s5n_pseudo.true_xsec``. ``cache`` holds the
    loaded inputs across truths (``s5c_unfold.load_inputs``, the runner's own loader, memoized for this call). The
    runner makes its --out directory before it builds, so --out is moved to ``scratch``, which must be empty or
    absent and is left empty: B0's own output directory is never touched."""
    import estimator_stability_probe as esp
    import s5c_unfold
    import s5n_pseudo
    import s5p_nullexp
    argv = list(argv)
    if scratch.exists() and any(scratch.iterdir()):
        raise P.Refused(f"the scratch directory {scratch} is not empty")
    argv[argv.index("--out") + 1] = str(scratch)
    if "--alternative-truth" in argv:
        i = argv.index("--alternative-truth") + 1
        argv[i] = esp.closure_truth_kind(Path(argv[argv.index("--alternative") + 1]), argv[i])
    seen: dict = {}
    real_build, real_true, real_load = s5p_nullexp.build, s5n_pseudo.true_xsec, s5c_unfold.load_inputs

    def build(ui, ub, split, seed, expectation, mc_fraction):
        exp, x_true, info = real_build(ui, ub, split, seed, expectation, mc_fraction)
        seen.update(exp=exp, x_true=np.asarray(x_true), info=info, split=int(split), seed=int(seed),
                    expectation=bool(expectation), mc_fraction=mc_fraction)
        raise _Built()

    def true_xsec(inputs, is_b, r):
        seen["r"] = np.array(r, float, copy=True)
        return real_true(inputs, is_b, r)

    def load_inputs(path):
        key = str(Path(path).resolve())
        if key not in cache:
            cache[key] = real_load(path)
        return cache[key]

    state = {"checked": False, "columns": None}
    with _restored(s5n_pseudo, ("refine_params", "code_digests", "truth_weight", "TRUTHS", "true_xsec")), \
            _restored(s5p_nullexp, ("build",)), _restored(s5c_unfold, ("load_inputs",)):
        s5p_nullexp.build, s5n_pseudo.true_xsec, s5c_unfold.load_inputs = build, true_xsec, load_inputs
        try:
            with P.namespace_guard("B0", truth, state), esp.pvl_truth():
                rc = s5p_nullexp.main(argv)
        except _Built:
            rc = None
    if scratch.exists() and any(scratch.iterdir()):
        raise P.Refused(f"{truth}: the runner wrote into {scratch}")
    if "exp" not in seen or "r" not in seen:
        raise P.Refused(f"{truth}: the runner never reached its experiment (rc {rc})")
    if not (state["checked"] and seen["expectation"] and seen["mc_fraction"] == "half"):
        raise P.Refused(f"{truth}: not B0's checked noise-free half-MC experiment")
    return seen


# ------------------------------------------------------------------------------------------- the unfold
def route2(gw, half, exp: dict, x_true: np.ndarray, ks=KS) -> dict:
    """The adapter: REF-G1's unfold_experiment on one experiment and half, and the truth through the same S1 rows."""
    import ref_g1
    arrays, diag = ref_g1.unfold_experiment(gw, half, exp, list(ks))
    arrays["X_true"] = gw.functionals(x_true)
    return {"arrays": arrays, "diag": diag}


@contextmanager
def capture_ibu(did, sink: list):
    """Record the response, data, known term and prior each ``did.ibu`` call receives, and the grid and prior truth
    ``did.make_grid`` builds, then run the committed functions unchanged."""
    real_ibu, real_grid = did.ibu, did.make_grid

    def ibu(r, y, b, prior, n_iter, **kw):
        sink.append({"R": r, "b": np.asarray(b, float), "prior": np.asarray(prior, float)})
        return real_ibu(r, y, b, prior, n_iter, **kw)

    def make_grid(name, coarse_of, n_coarse, u_nominal):
        g = real_grid(name, coarse_of, n_coarse, u_nominal)
        sink.append({"grid": g, "u_fine": np.asarray(u_nominal, float)})
        return g

    did.ibu, did.make_grid = ibu, make_grid
    try:
        yield
    finally:
        did.ibu, did.make_grid = real_ibu, real_grid


def fine_to_cell(U: np.ndarray) -> np.ndarray:
    """Each fine cell's reporting cell (-1 for none) from S1's rows; refuses a fine cell under two rows."""
    nz = np.asarray(U) != 0
    if np.any(nz.sum(axis=0) > 1):
        raise P.Refused("a fine cell lies under two reporting cells")
    return np.where(nz.any(axis=0), nz.argmax(axis=0), -1)


def r_id(did, U: np.ndarray, rec: list) -> dict:
    """R-ID on the ``fold`` unfold's captured problem (its make_grid, then its ibu call)."""
    g = next(x for x in rec if "grid" in x)
    pb = next(x for x in rec if "R" in x)
    grid, u_fine = g["grid"], g["u_fine"]
    share = did.share_matrix(grid, u_fine)
    member = (np.asarray(U) != 0).astype(float)
    maps = np.asarray(share.T.dot(member.T)).T  # (16, n_cells): each reporting cell's truth count from the grid
    f = did.fisher(pb["R"], pb["prior"], pb["b"])
    values, vectors = np.linalg.eigh(f)
    sigma, null = np.full(maps.shape[0], np.nan), np.full(maps.shape[0], np.nan)
    ok = np.linalg.norm(maps, axis=1) > 0
    sigma[ok], null[ok] = did.widths_from_eig(values, vectors, maps[ok])
    value = maps @ pb["prior"]
    rel = np.divide(sigma, np.abs(value), out=np.full_like(sigma, np.nan), where=np.abs(value) > 0)
    return {"label": "descriptive, read by nothing: the binned Cramer-Rao width of each cell's truth count at the "
                     "analysis exposure (D-ID's definition), on the fold unfold's own response, prior and known term",
            "sigma_rel": rel.tolist(), "null_fraction": null.tolist(), "n_cells_grid": int(grid.n_cells),
            "n_null_modes": int(np.sum(values <= 1e-12 * values.max()))}


def r_sup(world, half, r: np.ndarray, cell_of_fine: np.ndarray) -> dict:
    """R-SUP for one truth: half A's weights x the truth's row weight, per reporting cell."""
    t = world.tflat[half.rows]
    ok = t >= 0
    c = np.full(t.size, -1, np.int64)
    c[ok] = cell_of_fine[t[ok]]
    w = half.w_truth * r[half.rows]
    out = {"sum_w": [], "sum_w2": [], "kish": [], "max_share": [], "rows": []}
    for k in range(P.N_CELLS):
        wk = w[c == k]
        s, s2 = float(wk.sum()), float((wk ** 2).sum())
        out["sum_w"].append(s)
        out["sum_w2"].append(s2)
        out["kish"].append(s * s / s2 if s2 > 0 else 0.0)
        out["max_share"].append(float(wk.max() / s) if s > 0 else None)
        out["rows"].append(int(wk.size))
    return out


# ------------------------------------------------------------------------------------------- C-IBU
def c_ibu(lib, gw, inputs: dict, ratio_path: Path, ratio_sha: str, repo: Path = REPO, cibu: dict = CIBU) -> dict:
    """The adapter on REF-G1's NuWro closure experiment reproduces REF-G1's committed reading to 1e-12 relative."""
    import ref_g1
    if P.sha256_path(repo / cibu["readout"]) != cibu["readout_sha256"]:
        raise P.Refused("C-IBU: the REF-G1 readout is not its pin")
    if P.sha256_path(ratio_path) != ratio_sha:
        raise P.Refused("C-IBU: the closure ratio is not its pin")
    ratio = json.loads(ratio_path.read_text())
    r = ref_g1.row_weight(lib, inputs, ratio)
    exp, x_true = lib.pvl.closure_inputs(inputs, r)
    half = ref_g1.full_half(inputs["MCgen"].shape[0], inputs["w_truth"], inputs["w_reco"])
    res = route2(gw, half, exp, x_true, ks=(K_PRIMARY,))
    x = np.asarray(res["arrays"][f"F_{VARIANT}"][0], float)
    got = float(np.median(np.abs(x / res["arrays"]["X_true"] - 1)))
    want = json.loads((repo / cibu["readout"]).read_text())
    for k in cibu["key"]:
        want = want[k]
    rel = abs(got / want - 1)
    return {"got": got, "committed": want, "rel": rel, "tol": cibu["tol"], "pass": bool(rel <= cibu["tol"])}


# ------------------------------------------------------------------------------------------- the run
def run(queue_dir: Path, stage_json: Path, out: Path) -> int:
    import ibu1
    import ref_g1
    P.check_pins()
    P.check_pins(CODE_PINS)
    stage_rec = json.loads(stage_json.read_text())
    P.verify_stage(stage_rec)
    copies = {e["role"]: Path(e["copy"]) for e in stage_rec["files"]}
    sha = {e["role"]: e["sha256"] for e in stage_rec["files"]}
    lines = b0_lines(queue_dir)
    cfg = json.loads(ref_g1.CONFIG.read_text())
    lib = ref_g1.Lib(cfg)
    icfg = lib.ibu1_cfg
    contract = json.loads((REPO / icfg["contract"]["path"]).read_text())
    inputs, bkg = ibu1.load_inputs(lib.prod, icfg, copies["of_inputs_5d"], copies["bkg_dump"])
    if cfg["ratios"]["sha256"][CIBU["ratio"]] != sha["closure_ratio_nuwro"]:
        raise P.Refused("C-IBU: the staged closure ratio is not REF-G1's")
    _, gw = ref_g1.worlds(lib, cfg, inputs, contract)
    cell_of_fine = fine_to_cell(gw.U)
    t0 = time.time()
    rec = {"schema": SCHEMA, "ks": list(KS), "k_primary": K_PRIMARY, "variant_primary": VARIANT,
           "experiments": {}, "R-SUP": {}, "code_sha256": {"prr_ibu.py": P.sha256_path(Path(__file__).resolve()),
                                                             "prr_probe.py": P.sha256_path(Path(P.__file__).resolve()),
                                                             **CODE_PINS, **P.CODE_PINS}}
    rec["C-IBU"] = c_ibu(lib, gw, inputs, copies["closure_ratio_nuwro"], sha["closure_ratio_nuwro"])
    arrays_out = {}
    cache = {str(Path(copies["of_inputs_5d"]).resolve()): inputs}
    import s5c_pseudo
    for truth, seed in experiments():
        seen = capture(truth, lines[(truth, seed)], cache, out / "scratch")
        is_b = s5c_pseudo.half_mask(inputs["MCgen"].shape[0], seen["split"])
        half = ibu1.half_from_experiment(gw, seen["exp"], is_b)
        sink: list = []
        with capture_ibu(lib.prod.did, sink):
            res = route2(gw, half, seen["exp"], seen["x_true"])
        key = f"{truth}_s{seed}"
        for k, v in res["arrays"].items():
            arrays_out[f"{key}__{k}"] = np.asarray(v)
        rec["experiments"][key] = {"truth": truth, "seed": seed, "split_key": seen["split"],
                                   "diag": res["diag"], "n_half_rows": int(half.rows.size)}
        if seed == P.PRIMARY_SEED:
            rec["R-SUP"][truth] = r_sup(gw, half, seen["r"], cell_of_fine)
            if truth == P.PRIOR:
                rec["R-ID"] = r_id(lib.prod.did, gw.U, sink)
    rec["seconds"] = round(time.time() - t0, 3)
    rec["environment"] = ref_g1.environment()
    rec["slurm_job"] = os.environ.get("SLURM_JOB_ID")
    if (out / "scratch").exists():
        (out / "scratch").rmdir()
    ibu1.write(out / "route2.npz", arrays_out, {"schema": SCHEMA})
    (out / "route2.json").write_text(json.dumps(rec, indent=1, default=str) + "\n")
    print(json.dumps({"experiments": len(rec["experiments"]), "C-IBU": rec["C-IBU"]["pass"]}))
    return 0 if rec["C-IBU"]["pass"] else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0], allow_abbrev=False)
    ap.add_argument("cmd", choices=("run",))
    ap.add_argument("--queue-dir", type=Path, required=True)
    ap.add_argument("--stage", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    try:
        a.out.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print(f"refusing: {a.out} exists", file=sys.stderr)
        return 2
    import ref_g1
    stage_dir = Path(json.loads(a.stage.read_text())["dest"])
    try:
        with ref_g1.read_guards(ref_g1.PROTECTED, (REPO, a.out, stage_dir, a.queue_dir), root=False):
            return run(a.queue_dir, a.stage, a.out)
    except (P.Refused, ref_g1.GateFailure) as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
