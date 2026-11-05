#!/usr/bin/env python3
"""REF-G1: binned IBU on the H2 truth grid, integrated to R00-R15, beside configuration (e) (frozen driver).

Declaration: ``docs/orchestration/state/measurement-paper/5d-community-20261024/REF-G1-DECLARATION.md``, bound at
step one by ``REF-G1-BINDING-1.md``. Every number this file uses comes from ``config.json`` beside it.

Reused, never re-implemented (each digest-pinned in ``config.json`` and checked before import):

* IBU-1's ``Producers``, ``World``, ``Half``, ``unfold_ibu``, ``n_variants`` and ``write``
  (``nd-unfolding/ibu1/ibu1.py``), with IBU-1's own pinned producers behind them;
* S1's ``fine_map`` and ``functional_matrix`` (``s1_assemble.py``), the 16 rows Sum_f x_f vol_f of R00-R15;
* the H2 coarse cells ``s5p_stage1_inspect.coarse_map(H2_EDGES)``;
* ``s5p_numerics.jittered`` and ``cell_membership``; ``s5n_pseudo.build_data`` and ``bootstrap_replica``;
* ``s5p_universe.weights``, ``universe_inputs`` and ``check_alignment``;
* ``pvl_lib.row_weight``, ``prior_inputs`` and ``closure_inputs``.

The truth grid is the only change from IBU-1 (control G-IBU1): IBU-1's J world with its coarse map replaced by the
H2 cells, and its 153 functional rows by S1's 16 reporting-cell rows.

Units (each writes one npz holding every K of the declared set, both background variants):

  central            the data
  replica:B          (e)'s replica construction, step for step (s5p_numerics.py:183-200): jittered(inputs, bkg,
                     100+B), then build_data, then bootstrap_replica(exp, B). It refuses (rc 5) if the jitter moves
                     any fine-grid membership, as (e)'s loop does. That refusal is a defensive guard real data
                     cannot reach: edge-safe jitter leaves float32(edge) in place, and every other float32 value
                     lies at least 1/2 ulp from the edge, so a +-1/2-ulp step cannot cross it; the test reaches it
                     only by substituting the jitter. G-draw rebuilds the replica independently and compares the
                     per-row arrays the declaration lists bitwise (rc 6 on a difference)
  universe:BAND:IDX  every CV weight replaced by the universe's, as s5p_universe does for (e)
  universe:CV        the universe code with the CV weights, for G-CV
  vertex:NAME        the data with the MC prior reweighted by the ladder's truth ratio, as build_cmodel5d's X_k
  closure:NAME       noise-free: F0b's pv-ladder closure at the ratio (pvl_lib.closure_inputs), nominal prior
  gibu1              IBU-1's data unit, by this driver on IBU-1's J world, for G-IBU1

MEASURES: binned IBU estimates of R00-R15 on the declared inputs. CANNOT AUTHORIZE: a reading (``ref_g1_read.py``
applies the declared ones), a reported estimator, or any claim.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ND = REPO / "nd-unfolding"
CONFIG = HERE / "config.json"
for _p in (ND / "ibu1", ND / "pv-ladder", ND):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import ibu1  # noqa: E402

GateFailure = ibu1.GateFailure
sha256 = ibu1.sha256
RC_GATE, RC_MOVED, RC_DRAW = 4, 5, 6


class MembershipMoved(RuntimeError):
    """The jitter changed a fine-grid membership: (e)'s loop refuses here (s5p_numerics.py:188-191), and so does g1."""


class Lib:
    """The committed modules, imported from this checkout only after their digests match config.json."""

    def __init__(self, cfg: dict):
        for rel, digest in cfg["code_sha256"].items():
            if sha256(REPO / rel) != digest:
                raise GateFailure(f"{rel} digest differs from config.json")
        self.ibu1_cfg = json.loads((REPO / cfg["ibu1_config"]).read_text())
        self.prod = ibu1.Producers(self.ibu1_cfg)
        import pvl_lib  # noqa: E402
        import s1_assemble  # noqa: E402
        import s5p_numerics  # noqa: E402
        import s5p_stage1_inspect  # noqa: E402
        import s5p_universe  # noqa: E402

        for m in (s1_assemble, s5p_numerics, s5p_stage1_inspect, s5p_universe):
            if Path(m.__file__).resolve().parent != ND.resolve():
                raise GateFailure(f"{m.__name__} resolved outside this checkout: {m.__file__}")
        if Path(pvl_lib.__file__).resolve().parent != (ND / "pv-ladder").resolve():
            raise GateFailure(f"pvl_lib resolved outside this checkout: {pvl_lib.__file__}")
        self.s1a, self.num, self.s1, self.uni, self.pvl = s1_assemble, s5p_numerics, s5p_stage1_inspect, s5p_universe, pvl_lib
        self.s5n = self.prod.s5n_pseudo


# ------------------------------------------------------------------------------------------- worlds


def worlds(lib: Lib, cfg: dict, inputs: dict, contract: dict, chunk: int = 2_000_000) -> tuple:
    """IBU-1's J world, and the g1 world: the same rows, the H2 coarse cells and S1's 16 rows."""
    jw = ibu1.World(lib.prod, inputs, contract, chunk=chunk)
    gw = copy.copy(jw)
    gw.coarse_of, gw.n_coarse = lib.s1.coarse_map(lib.s1.H2_EDGES)
    gw.U = lib.s1a.functional_matrix(lib.s1a.fine_map(REPO / cfg["definition"]["path"]))
    gw.names = [f"R{c:02d}" for c in range(gw.U.shape[0])]
    return jw, gw


def with_inputs(world, inputs: dict):
    """The same world, extracting with a unit's own denominator and flux (a universe or a reweighted prior)."""
    w = copy.copy(world)
    w.inputs = inputs
    return w


def full_half(n: int, w_truth, w_reco) -> ibu1.Half:
    return ibu1.Half(np.arange(n), w_truth, w_reco)


def unfold_experiment(world, half: ibu1.Half, exp: dict, ks: list[int]) -> tuple[dict, dict]:
    """IBU-1's arm-N data path (ibu1.run_data): both background variants of ``n_variants``, each through
    ``unfold_ibu``. Returns the arrays {ks, F_fold, F_sub} and the per-variant diagnostics."""
    arrays, diag = {"ks": np.array(ks)}, {}
    for name, (y, b_extra) in ibu1.n_variants(world, exp).items():
        r = ibu1.unfold_ibu(world, half, y, b_extra, ks)
        arrays[f"F_{name}"] = r.pop("F")
        diag[name] = r
    return arrays, diag


# ------------------------------------------------------------------------------------------- replicas


def replica_experiment(lib: Lib, inputs: dict, bkg: dict, base_cells: dict, b: int, offset: int) -> dict:
    """(e)'s replica b, step for step: jitter (seed offset + b), the membership refusal, build_data, bootstrap. The
    refusal cannot fire on real data (edge-safe jitter cannot cross an edge; see the module docstring)."""
    ji, jb = lib.num.jittered(inputs, bkg, offset + b)
    moved = {k: int((v != base_cells[k]).sum()) for k, v in lib.num.cell_membership(ji, jb["bkg_reco"]).items()}
    if any(moved.values()):
        raise MembershipMoved(f"jitter {offset + b} changed grid membership {moved}")
    return lib.s5n.bootstrap_replica(lib.s5n.build_data(ji, jb), b)


def g_draw(lib: Lib, inputs: dict, bkg: dict, b: int, offset: int, rep: dict) -> dict:
    """G-draw: (e)'s construction called directly, its per-row arrays compared bitwise with the replica g1 unfolds:
    the keep masks (observed and template rows in the window), obs_counts, the MC Poisson factors and tmpl_w."""
    ji, jb = lib.num.jittered(inputs, bkg, offset + b)
    exp = lib.s5n.build_data(ji, jb)
    ref = lib.s5n.bootstrap_replica(exp, b)
    edges = inputs["edges"]
    checks = {
        "keep_observed": np.array_equal(lib.s5n.fid_mask(ji["measured"], edges),
                                        lib.s5n.fid_mask(np.asarray(inputs["measured"], np.float64), edges)),
        "keep_template": np.array_equal(lib.s5n.fid_mask(jb["bkg_reco"], edges),
                                        lib.s5n.fid_mask(np.asarray(bkg["bkg_reco"], np.float64), edges)),
        "obs_counts": np.array_equal(rep["obs_counts"], ref["obs_counts"]),
        "mc_poisson": np.array_equal(rep["w_truth"], ref["w_truth"]) and np.array_equal(rep["w_reco"], ref["w_reco"]),
        "tmpl_w": np.array_equal(rep["tmpl_w"], ref["tmpl_w"]),
    }
    return {"checks": {k: bool(v) for k, v in checks.items()}, "pass": bool(all(checks.values()))}


# ------------------------------------------------------------------------------------------- the ratios


def load_ratio(lib: Lib, cfg: dict, name: str) -> dict:
    p = Path(cfg["ratios"]["dir"]) / f"{name}.json"
    if sha256(p) != cfg["ratios"]["sha256"][name]:
        raise GateFailure(f"ratio {name} digest differs from config.json")
    ratio = json.loads(p.read_text())
    if tuple(ratio["axes"]) != lib.pvl.RUNGS["L-5D-PV"][1]:
        raise GateFailure(f"ratio {name}'s axes are not L-5D-PV's")
    return ratio


def row_weight(lib: Lib, inputs: dict, ratio: dict) -> np.ndarray:
    return lib.pvl.row_weight(inputs["MCgen"], lib.pvl.RUNGS["L-5D-PV"][0], ratio, inputs["pass_truth"])


# ------------------------------------------------------------------------------------------- units


def universes(cfg: dict) -> list[str]:
    """BAND:IDX of every (e) universe in the preconditions listing (S1's products, s1_assemble.EXPECT's bands)."""
    listing = json.loads((REPO / cfg["listing"]["path"]).read_text())
    out = []
    for f in listing["files"]["e_universes"]:
        tag = Path(f["path"]).name[len("S1_"):-len(".npz")]
        band, idx = tag.rsplit("_", 1)
        out.append(f"{band}:{idx}")
    return sorted(out)


class Run:
    """The loaded inputs and worlds, shared by every unit of one invocation."""

    def __init__(self, lib: Lib, cfg: dict, inputs: dict, bkg: dict, contract: dict, chunk: int = 2_000_000):
        self.lib, self.cfg, self.inputs, self.bkg = lib, cfg, inputs, bkg
        self.jw, self.gw = worlds(lib, cfg, inputs, contract, chunk)
        self.ks = list(cfg["iterations"]["reported"])
        self.n = inputs["MCgen"].shape[0]
        self.base_cells = lib.num.cell_membership(inputs, bkg["bkg_reco"])
        self._bank_cv = None

    def bank_cv(self):
        if self._bank_cv is None:
            self._bank_cv = np.load(Path(self.cfg["inputs"]["bank"]) / "cv.npz", allow_pickle=True)
            self.lib.uni.check_alignment(self._bank_cv, self.inputs, self.bkg)
        return self._bank_cv

    def central(self) -> tuple[dict, dict]:
        exp = self.lib.s5n.build_data(self.inputs, self.bkg)
        half = full_half(self.n, self.inputs["w_truth"], self.inputs["w_reco"])
        arrays, diag = unfold_experiment(self.gw, half, exp, self.ks)
        return arrays, {"variants": diag}

    def gibu1(self) -> tuple[dict, dict]:
        exp = self.lib.s5n.build_data(self.inputs, self.bkg)
        half = full_half(self.n, self.inputs["w_truth"], self.inputs["w_reco"])
        arrays, diag = unfold_experiment(self.jw, half, exp, self.ks)
        return arrays, {"variants": diag, "world": "IBU-1's J grid and 153 functionals"}

    def replica(self, b: int) -> tuple[dict, dict]:
        off = int(self.cfg["replicas"]["jitter_offset"])
        rep = replica_experiment(self.lib, self.inputs, self.bkg, self.base_cells, b, off)
        draw = g_draw(self.lib, self.inputs, self.bkg, b, off, rep)
        half = full_half(self.n, rep["w_truth"], rep["w_reco"])
        arrays, diag = unfold_experiment(self.gw, half, rep, self.ks)
        return arrays, {"variants": diag, "bootstrap_seed": b, "jitter_seed": off + b, "g_draw": draw}

    def universe(self, band: str, idx: str) -> tuple[dict, dict]:
        cfg = self.cfg["inputs"]
        if band == "CV":
            w = {"wt": self.inputs["w_truth"], "wr": self.inputs["w_reco"], "denom_nd": self.inputs["denom_nd"],
                 "bkgw": self.bkg["bkg_w"]}
            digests = {}
        else:
            wdir = Path(cfg["detector_dir"] if band in self.lib.s1a.DETECTOR_BANDS else cfg["bank"])
            tag = f"{band}_{idx}"
            w = self.lib.uni.weights(wdir, tag)
            digests = {k: sha256(wdir / f"{tag}_{k}.npy") for k in self.lib.uni.weight_keys(wdir, tag)}
        flux_file = None
        if band == "Flux":
            flux_file = Path(cfg["flux_universe_file"])
            if sha256(flux_file) != cfg["flux_universe_file_sha256"]:
                raise GateFailure("the flux universe file digest differs from config.json")
        ui, ub, info = self.lib.uni.universe_inputs(self.inputs, self.bkg, None if band == "CV" else self.bank_cv(),
                                                    w, band, idx, flux_file)
        exp = self.lib.s5n.build_data(ui, ub)
        half = full_half(self.n, ui["w_truth"], ui["w_reco"])
        arrays, diag = unfold_experiment(with_inputs(self.gw, ui), half, exp, self.ks)
        return arrays, {"variants": diag, "universe": f"{band}:{idx}", "universe_info": info, "weight_sha256": digests}

    def vertex(self, name: str) -> tuple[dict, dict]:
        ratio = load_ratio(self.lib, self.cfg, name)
        r = row_weight(self.lib, self.inputs, ratio)
        ui, guard = self.lib.pvl.prior_inputs(self.inputs, r)
        exp = self.lib.s5n.build_data(ui, self.bkg)
        half = full_half(self.n, ui["w_truth"], ui["w_reco"])
        arrays, diag = unfold_experiment(with_inputs(self.gw, ui), half, exp, self.ks)
        return arrays, {"variants": diag, "vertex": name, "ratio_sha256": self.cfg["ratios"]["sha256"][name],
                        "prior_guard": guard}

    def closure(self, name: str) -> tuple[dict, dict]:
        ratio = load_ratio(self.lib, self.cfg, name)
        r = row_weight(self.lib, self.inputs, ratio)
        exp, x_true = self.lib.pvl.closure_inputs(self.inputs, r)
        half = full_half(self.n, self.inputs["w_truth"], self.inputs["w_reco"])
        arrays, diag = unfold_experiment(self.gw, half, exp, self.ks)
        arrays["X_true"] = self.gw.functionals(x_true)
        return arrays, {"variants": diag, "closure": name, "ratio_sha256": self.cfg["ratios"]["sha256"][name]}


def environment() -> dict:
    import scipy
    return {"interpreter": sys.executable, "python_version": sys.version, "numpy": np.__version__,
            "scipy": scipy.__version__}


def gibu1_environment(cfg: dict) -> tuple[bool, dict]:
    """G-IBU1 is bitwise, so the gibu1 unit runs only in IBU-1's recorded environment: the interpreter and Python
    version of IBU-1's D_N unit (config.json gibu1_environment, cited to IBU-1's guard inventory). IBU-1 recorded no
    numpy or scipy version; this unit records its own."""
    env = environment()
    want = cfg["gibu1_environment"]
    return (env["interpreter"], env["python_version"]) == (want["interpreter"], want["python_version"]), env


def parse_units(cfg: dict, specs: list[str]) -> list[tuple]:
    """central | gibu1 | replica:B | replicas:A-B | universe:BAND:IDX | universe:CV | universes:all | vertex:NAME |
    closure:NAME; refuses anything the configuration does not declare."""
    first, last = cfg["replicas"]["first"], cfg["replicas"]["last"]
    known_u = set(universes(cfg))
    out = []
    for s in specs:
        kind, _, rest = s.partition(":")
        if kind in ("central", "gibu1") and not rest:
            out.append((kind,))
        elif kind == "replica" and rest.isdigit() and first <= int(rest) <= last:
            out.append(("replica", int(rest)))
        elif kind == "replicas" and "-" in rest:
            a, b = (int(v) for v in rest.split("-"))
            if not first <= a <= b <= last:
                raise ValueError(f"replicas {rest} outside {first}-{last}")
            out += [("replica", i) for i in range(a, b + 1)]
        elif kind == "universe" and rest == "CV":
            out.append(("universe", "CV", "-"))
        elif kind == "universe" and rest in known_u:
            out.append(("universe", *rest.split(":")))
        elif kind == "universes" and rest == "all":
            out += [("universe", *u.split(":")) for u in sorted(known_u)]
        elif kind == "vertex" and rest in cfg["vertices"]:
            out.append(("vertex", rest))
        elif kind == "closure" and rest in cfg["closures"]:
            out.append(("closure", rest))
        else:
            raise ValueError(f"unknown unit {s!r}")
    return out


def unit_name(u: tuple) -> str:
    if u[0] == "replica":
        return f"replica_b{u[1]}"
    if u[0] == "universe":
        return "universe_CV" if u[1] == "CV" else f"universe_{u[1]}_{u[2]}"
    return "_".join(str(x) for x in u)


def run_unit(run: Run, u: tuple, out: Path) -> int:
    """One unit. Its done-marker carries its control verdict; a unit is skipped only when that verdict is PASS, so a
    product that failed G-draw is never taken as done on a rerun (it is refused, rc 6)."""
    target = out / f"{unit_name(u)}.npz"
    marker = out / f"{unit_name(u)}.done"
    if target.exists():
        verdict = json.loads(marker.read_text()).get("verdict") if marker.exists() else None
        if verdict == "PASS":
            return 0
        print(f"refusing: {target.name} exists without a PASS done-marker (verdict {verdict})", file=sys.stderr)
        return RC_DRAW
    env = None
    if u[0] == "gibu1":
        ok, env = gibu1_environment(run.cfg)
        if not ok:
            print(f"refusing: gibu1 runs only in IBU-1's environment, not {env}", file=sys.stderr)
            return RC_GATE
    t0 = time.time()
    try:
        arrays, meta = getattr(run, u[0])(*u[1:])
    except MembershipMoved as e:
        print(f"refusing: {e}", file=sys.stderr)
        return RC_MOVED
    meta.update(schema="ref-g1-unit/1", unit=unit_name(u), ks=run.ks, seconds=round(time.time() - t0, 3),
                code_sha256=run.cfg["code_sha256"], driver_sha256=sha256(Path(__file__).resolve()),
                config_sha256=sha256(CONFIG), slurm_job=os.environ.get("SLURM_JOB_ID"),
                environment=env or environment())
    passed = "g_draw" not in meta or meta["g_draw"]["pass"]
    ibu1.write(target, arrays, meta)
    marker.write_text(json.dumps({"unit": meta["unit"], "verdict": "PASS" if passed else "FAIL",
                                  "sha256": sha256(target)}) + "\n")
    print(json.dumps({"unit": meta["unit"], "seconds": meta["seconds"],
                      **({"g_draw": meta["g_draw"]["pass"]} if "g_draw" in meta else {})}), flush=True)
    return 0 if passed else RC_DRAW


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--unit", action="append", required=True, help="a unit (repeatable); see the module docstring")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--threads", type=int, default=1)
    a = ap.parse_args(argv)
    cfg = json.loads(CONFIG.read_text())
    if a.threads > cfg["resources"]["max_threads_per_task"]:
        print("refusing: thread count above the declared cap", file=sys.stderr)
        return 2
    try:
        units = parse_units(cfg, a.unit)
    except ValueError as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 2
    try:
        if sha256(REPO / cfg["listing"]["path"]) != cfg["listing"]["sha256"]:
            raise GateFailure("the preconditions listing digest differs from config.json")
        lib = Lib(cfg)
        icfg = lib.ibu1_cfg
        contract = json.loads((REPO / icfg["contract"]["path"]).read_text())
        if sha256(REPO / icfg["contract"]["path"]) != icfg["contract"]["expect_sha256"]:
            raise GateFailure("contract digest differs from IBU-1's config")
        inputs, bkg = ibu1.load_inputs(lib.prod, icfg, Path(cfg["inputs"]["of_inputs_5d"]), Path(cfg["inputs"]["bkg_dump"]))
        run = Run(lib, cfg, inputs, bkg, contract)
    except GateFailure as e:
        print(f"refusing: {e}", file=sys.stderr)
        return RC_GATE
    a.out.mkdir(parents=True, exist_ok=True)
    rc = 0
    for u in units:
        r = run_unit(run, u, a.out)
        if r == RC_MOVED:
            return r
        rc = rc or r
    return rc


if __name__ == "__main__":
    sys.exit(main())
