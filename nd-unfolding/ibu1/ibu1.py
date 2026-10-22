#!/usr/bin/env python3
"""IBU-1: binned iterative Bayesian unfolding on the OmniFold studies' own pseudo-experiments (frozen driver).

Specification: ``docs/orchestration/state/2d-closeout/stageF/methods/IBU1-SPEC.md``. Its amendments, the
pins and the reading rule are in ``.../methods/ibu1/DECLARATION.md``; each amendment is coded here where
its tag ``IA-n`` appears. Every number this file uses comes from ``config.json`` beside it.

Reused, never re-implemented (each digest-pinned in ``config.json`` and checked before import):

* the pseudo-experiments: ``s5c_pseudo.build_experiment`` (arm P, the s5c Tier-S construction) and
  ``s5n_pseudo.build_pseudo`` with ``s5e_deform.install_ratio_truth`` (arm N, the s5n/s5e negative-weight
  construction); the N bootstrap ``s5n_pseudo.bootstrap_replica``; the real data ``s5n_pseudo.build_data``;
* the D'Agostini update with a known additive term and the J-grid algebra: D-ID's ``did.ibu``,
  ``coarse_of_fine``, ``make_grid``, ``Pairs``, ``response``, ``share_matrix``, ``coarse_sum``;
* the 5D binning ``s5e_trace.flat_index``; the extraction ``xsec_nd.extract_cross_section_nd``;
* the 153 reported functionals ``s5c_coverage.reported_functionals``.

The P bootstrap replica is the six lines of ``s5c_pseudo.run_bootstrap`` that build it (that function also
unfolds and writes, so it cannot be called); ``p_bootstrap_replica`` is tested equal to it by capture, and
the run repeats that capture on the real input (control ``replica_capture``).

MEASURES: per pseudo-experiment, the binned IBU estimate of the 153 functionals at K in the declared set,
next to the paired OmniFold product's estimate and the experiment's own truth. CANNOT AUTHORIZE: a
measured cross section, a coverage claim for OmniFold, or any change to a claim.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from scipy import sparse

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ND = REPO / "nd-unfolding"
CONFIG = HERE / "config.json"


class GateFailure(RuntimeError):
    """A pinned digest, a producer path or a pairing check disagreed: the unit is not a result."""


def sha256(path: Path, chunk: int = 1 << 24) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while block := fh.read(chunk):
            h.update(block)
    return h.hexdigest()


# ----------------------------------------------------------------------------------- producers


class Producers:
    """The committed modules, imported from this checkout only after their digests match the pins."""

    def __init__(self, cfg: dict):
        for rel, digest in cfg["code_sha256"].items():
            if sha256(REPO / rel) != digest:
                raise GateFailure(f"{rel} digest differs from config.json")
        if str(ND) not in sys.path:
            sys.path.insert(0, str(ND))
        import s5c_coverage  # noqa: E402
        import s5c_pseudo  # noqa: E402
        import s5e_deform  # noqa: E402
        import s5e_trace  # noqa: E402
        import s5n_pseudo  # noqa: E402
        import xsec_nd  # noqa: E402

        did_path = REPO / cfg["did_py"]
        spec = importlib.util.spec_from_file_location("ibu1_did", did_path)
        did = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = did  # dataclasses resolve the module by name
        spec.loader.exec_module(did)
        for module in (s5c_coverage, s5c_pseudo, s5e_deform, s5e_trace, s5n_pseudo, xsec_nd):
            if Path(module.__file__).resolve().parent != ND.resolve():
                raise GateFailure(f"{module.__name__} resolved outside this checkout: {module.__file__}")
        s5e_deform.install_ratio_truth(s5n_pseudo)  # truth ratio_nd (W2, W3), exactly as s5e_candidate.install
        self.s5c_pseudo, self.s5n_pseudo, self.s5e_trace = s5c_pseudo, s5n_pseudo, s5e_trace
        self.s5c_coverage, self.xsec_nd, self.did = s5c_coverage, xsec_nd, did


# --------------------------------------------------------------------------------- the J world


def in_window(coords: np.ndarray, edges: list) -> np.ndarray:
    """IA-7: the reco rule both constructions apply to the measured side, [first, last) on every axis
    (``s5n_pseudo.fid_mask``; purity gives a row on an upper edge weight 0)."""
    ok = np.ones(coords.shape[0], bool)
    for k, e in enumerate(edges):
        ok &= (coords[:, k] >= e[0]) & (coords[:, k] < e[-1])
    return ok


class World:
    """Per-row reco cell, fine truth cell and (reco, fine) pair of the whole MC sample, computed once."""

    def __init__(self, prod: Producers, inputs: dict, contract: dict, chunk: int = 2_000_000):
        if not np.all(inputs["pass_truth"]):
            raise GateFailure("a reco-passing row without pass_truth would sit in no response or known term")
        self.prod = prod
        self.edges = inputs["edges"]
        self.shape = tuple(len(e) - 1 for e in self.edges)
        self.n_fine = int(np.prod(self.shape))
        n = inputs["MCgen"].shape[0]
        fi = prod.s5e_trace.flat_index
        tflat = np.empty(n, np.int64)
        rflat = np.empty(n, np.int64)
        for s in range(0, n, chunk):
            gen, reco = inputs["MCgen"][s:s + chunk], inputs["MCreco"][s:s + chunk]
            tflat[s:s + chunk] = fi(gen, self.edges)
            r = fi(reco, self.edges)
            r[~in_window(reco, self.edges)] = -1
            rflat[s:s + chunk] = r
        tflat[~inputs["pass_truth"]] = -1
        rflat[~inputs["pass_reco"]] = -1
        self.tflat, self.rflat = tflat, rflat
        pair_rows = (rflat >= 0) & (tflat >= 0)
        self.pair_index = np.flatnonzero(pair_rows)
        self.pairs = prod.did.Pairs.build(rflat[pair_rows], tflat[pair_rows], self.n_fine)
        self.known_rows = np.flatnonzero((rflat >= 0) & (tflat < 0) & inputs["pass_truth"])  # IA-8 (D-ID AM-2)
        J = contract["measurement"]["partition_J"]
        coarse_edges = [J["edges"][ax] for ax in ("pt", "pz", "eavail", "q3", "W")]
        self.coarse_of = prod.did.coarse_of_fine(self.edges, coarse_edges)
        self.n_coarse = int(np.prod([len(c) - 1 for c in coarse_edges]))
        self.U, self.names = prod.s5c_coverage.reported_functionals(contract)
        self.inputs = inputs
        self.reweights: dict = {}

    def reco_hist(self, coords: np.ndarray, w: np.ndarray) -> np.ndarray:
        flat = self.prod.s5e_trace.flat_index(np.asarray(coords, float), self.edges)
        flat[~in_window(np.asarray(coords, float), self.edges)] = -1
        return self.prod.s5e_trace.binned(flat, w, self.n_fine)

    def functionals(self, xs: np.ndarray) -> np.ndarray:
        return self.U @ np.asarray(xs, float).ravel(order="C")


class Half:
    """The unfolding MC an OmniFold unfold of this experiment trained on: row indices into the full
    sample and the weights it was handed (half A x2, a bootstrap replica's, or the full MC x1)."""

    def __init__(self, rows: np.ndarray, w_truth: np.ndarray, w_reco: np.ndarray):
        self.rows, self.w_truth, self.w_reco = rows, np.asarray(w_truth, float), np.asarray(w_reco, float)


def half_from_experiment(world: World, exp: dict, is_b: np.ndarray | None) -> Half:
    """IA-9 (response provenance): the response is built from exactly the rows and weights the comparator's
    unfold received, mapped back to the full sample. Same-sample (no split) when is_b is None."""
    rows = np.arange(world.tflat.size) if is_b is None else np.flatnonzero(~is_b)
    if exp["MCgen"].shape[0] != rows.size:
        raise GateFailure("the experiment's unfolding MC is not the declared half")
    scale = 1.0 if is_b is None else 2.0
    probe = rows[:: max(1, rows.size // 1000)]
    step = max(1, rows.size // 1000)
    if not (np.array_equal(exp["MCgen"][::step], world.inputs["MCgen"][probe])
            and np.array_equal(exp["w_truth"], scale * world.inputs["w_truth"][rows])
            and np.array_equal(exp["w_reco"], scale * world.inputs["w_reco"][rows])):
        raise GateFailure("the experiment's unfolding MC rows or weights differ from the mapped half")
    return Half(rows, exp["w_truth"], exp["w_reco"])


def unfold_ibu(world: World, half: Half, y: np.ndarray, b_extra: np.ndarray, ks: list[int]) -> dict:
    """IBU on the J grid (IA-4): prior = the half's own truth, K iterations, then each J estimate spread
    over its fine cells by the half's truth shape (D-ID AM-4) and passed through the committed extraction
    exactly as ``s5c_unfold.unfold`` does. Returns the 153 functionals at every K in ``ks``."""
    did = world.prod.did
    ok = world.tflat[half.rows] >= 0
    u_fine = np.bincount(world.tflat[half.rows][ok], weights=half.w_truth[ok], minlength=world.n_fine)
    grid = did.make_grid("J", world.coarse_of, world.n_coarse, u_fine)
    pos = np.full(world.tflat.size, -1, np.int64)
    pos[half.rows] = np.arange(half.rows.size)
    p_local = pos[world.pair_index]
    keep = p_local >= 0
    pw = np.bincount(world.pairs.of_row[keep], weights=half.w_reco[p_local[keep]], minlength=world.pairs.reco.size)
    used = pw != 0
    pairs = did.Pairs(world.pairs.reco[used], world.pairs.fine[used], np.empty(0, np.int64))
    R = did.response(grid, pairs, pw[used], u_fine, world.n_fine)
    k_local = pos[world.known_rows]
    k_ok = k_local >= 0
    b_known = np.bincount(world.rflat[world.known_rows][k_ok], weights=half.w_reco[k_local[k_ok]], minlength=world.n_fine)
    prior = did.coarse_sum(grid, u_fine)
    res = did.ibu(R, np.asarray(y, float), b_known + np.asarray(b_extra, float), prior, max(ks),
                  maps=np.eye(grid.n_cells), record=tuple(ks))
    share = did.share_matrix(grid, u_fine)
    out = np.array([extract(world, share @ t, u_fine) for t in res.trajectory])
    eff = np.asarray(R.sum(axis=0)).ravel()
    return {"F": out, "n_cells": grid.n_cells, "acceptance_holes": int(np.sum(eff <= 0)),
            "negative_y_cells": int(np.sum(y < 0)), "b_known_sum": float(b_known.sum())}


def extract(world: World, unf_fine: np.ndarray, u_fine: np.ndarray) -> np.ndarray:
    """``s5c_unfold.unfold``'s extraction: completeness from the half's unreweighted truth."""
    dn = world.inputs["denom_nd"]
    comp = np.zeros(world.shape)
    nz = dn > 0
    comp[nz] = u_fine.reshape(world.shape)[nz] / dn[nz]
    xs, _ = world.prod.xsec_nd.extract_cross_section_nd(
        np.asarray(unf_fine).reshape(world.shape), comp, world.inputs["flux"], float(world.inputs["data_pot"]),
        float(world.inputs["n_nucleons"]), world.edges)
    return world.functionals(xs)


def oracle_floor(world: World, half: Half, r: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """IA-14: the floor the J-cell estimator cannot remove at any K or n. The EXACT departed J totals of the
    unfolding half go through the same spreading (by the half's unreweighted truth shape) and extraction as an
    IBU estimate; the reference is the half's departed truth through ``build_experiment``'s x_true spelling
    (reweighted counts over unreweighted completeness). Returns (oracle, reference) functionals."""
    did = world.prod.did
    ok = world.tflat[half.rows] >= 0
    t_rows = world.tflat[half.rows][ok]
    u_fine = np.bincount(t_rows, weights=half.w_truth[ok], minlength=world.n_fine)
    u_dep = np.bincount(t_rows, weights=half.w_truth[ok] * r[half.rows][ok], minlength=world.n_fine)
    grid = did.make_grid("J", world.coarse_of, world.n_coarse, u_fine)
    t_exact = did.coarse_sum(grid, u_dep)
    oracle = extract(world, did.share_matrix(grid, u_fine) @ t_exact, u_fine)
    return oracle, extract(world, u_dep, u_fine)


def truth_reweight(world: World, unit: dict, ratios: dict) -> np.ndarray:
    """The unit's declared truth reweight r on every MC row, by the producer that built its pseudo-data."""
    inp = world.inputs
    if unit["arm"] == "P":
        return world.prod.s5c_pseudo.truth_weight(unit["truth"], inp["MCgen"], world.edges, unit["amplitude"],
                                                  w_truth=inp["w_truth"])
    return world.prod.s5n_pseudo.truth_weight(unit["truth"], inp, unit["amplitude"], ratios.get(unit.get("ratio")))


# -------------------------------------------------------------------------- the two constructions


@contextmanager
def capture_purity(s5c_pseudo, sink: list):
    """Record the raw (coords, counts) that ``build_experiment`` hands ``purity_weights`` (it resolves the
    name at call time), then run the committed function unchanged."""
    original = s5c_pseudo.purity_weights

    def wrapper(coords, counts, bkg_nd, edges):
        sink.append((coords, counts))
        return original(coords, counts, bkg_nd, edges)

    s5c_pseudo.purity_weights = wrapper
    try:
        yield
    finally:
        s5c_pseudo.purity_weights = original


def build_p(world: World, bkg: dict, truth: str, amplitude: float, split_key: int, seed: int):
    """Arm P: the s5c Tier-S pseudo-experiment. Variants (IA-5): ``pur`` = the binned purity-weighted
    measured sample OmniFold received (primary); ``fold`` = the raw counts with the nominal background
    prediction ``bkg_nd`` as a known term in the fold (secondary)."""
    sp = world.prod.s5c_pseudo
    sink: list = []
    with capture_purity(sp, sink):
        exp, x_true, info = sp.build_experiment(world.inputs, bkg, truth, amplitude, split_key, seed)
    if len(sink) != 1:
        raise GateFailure(f"purity_weights called {len(sink)} times")
    coords, counts = sink[0]
    if not (np.array_equal(np.asarray(exp["measured"], float), coords) and counts.shape[0] == coords.shape[0]):
        raise GateFailure("the measured rows are not the raw rows purity_weights received")
    is_b = sp.half_mask(world.tflat.size, split_key)
    exp = dict(exp, raw_counts=counts)
    return exp, x_true, info, is_b, p_variants(world, bkg, exp, exp["measured_weights"], counts)


def p_variants(world: World, bkg: dict, exp: dict, measured_weights: np.ndarray, counts: np.ndarray) -> dict:
    return {"pur": (world.reco_hist(exp["measured"], measured_weights), np.zeros(world.n_fine)),
            "fold": (world.reco_hist(exp["measured"], counts), np.asarray(bkg["bkg_nd"], float).ravel(order="C"))}


def p_bootstrap_replica(exp: dict, b: int) -> tuple[dict, np.ndarray]:
    """``s5c_pseudo.run_bootstrap``'s replica (its lines 241-247), returned instead of unfolded, with the
    per-measured-row Poisson(1) draws, which variant ``fold`` applies to the raw counts of the same rows."""
    rng_d = np.random.default_rng(b)
    rng_m = np.random.default_rng(b + 10_000_000)
    rep = dict(exp)
    draws = rng_d.poisson(1.0, exp["measured_weights"].shape[0])
    rep["measured_weights"] = exp["measured_weights"] * draws
    pm = rng_m.poisson(1.0, exp["w_truth"].shape[0]).astype(float)
    rep["w_truth"] = exp["w_truth"] * pm
    rep["w_reco"] = exp["w_reco"] * pm
    return rep, draws


def build_n(world: World, bkg: dict, truth: str, amplitude: float, split_key: int, seed: int, ratio: dict | None):
    """Arm N: the s5n/s5e negative-weight pseudo-experiment before refinement. Variants (IA-5): ``fold`` =
    the observed counts with the template (half D x2) as a known term in the fold (primary); ``sub`` =
    max(0, observed - template) per reco cell (secondary)."""
    sn = world.prod.s5n_pseudo
    exp, x_true, info = sn.build_pseudo(world.inputs, bkg, truth, amplitude, split_key, seed, ratio)
    is_b = world.prod.s5c_pseudo.half_mask(world.tflat.size, split_key)
    return exp, x_true, info, is_b, n_variants(world, exp)


def n_variants(world: World, exp: dict) -> dict:
    y = world.reco_hist(exp["obs"], exp["obs_counts"])
    tmpl = world.reco_hist(exp["tmpl"], exp["tmpl_w"])
    return {"fold": (y, tmpl), "sub": (np.maximum(0.0, y - tmpl), np.zeros(world.n_fine))}


# ------------------------------------------------------------------------------------- pairing


def expected_construction(cfg: dict, unit: dict, truth: str, amplitude: float) -> dict:
    """IA-3: the construction flags a paired product must carry. ``required`` keys must be present and equal;
    ``if_present`` keys are compared when the product's schema records them (older s5c products do not)."""
    pins = cfg["inputs"]
    required = {"truth": truth, "amplitude": amplitude, "input_npz_sha256": pins["of_inputs_5d_sha256"],
                "bkg_dump_sha256": pins["bkg_dump_sha256"]}
    if_present = {"no_background": False, "prior_matches_truth": False, "iters": 5, "estimator_seed": 42,
                  "permute_seed": None, "config": "deterministic"}
    if unit["arm"] == "N":
        required["bkg_mode"] = "negweight-refined"
        ratio = unit.get("ratio")
        required["eavail_ratio_sha256"] = None if ratio is None else cfg["ratios"][ratio]["expect_sha256"]
    return {"required": required, "if_present": if_present}


def comparator_gate(path: Path, x_true: np.ndarray | None, info: dict, seed: int | None, split_key: int | None,
                    expect: dict) -> dict:
    """IA-3: the paired OmniFold product must carry this experiment's truth bitwise, its seed and split key,
    the same experiment record (counts, sums; it identifies the Poisson draws and the halves) and the declared
    construction flags."""
    z = np.load(path, allow_pickle=True)
    meta = json.loads(str(z["meta"]))
    checks = {
        "experiment_record": json.loads(json.dumps(info, default=str)) == meta.get("experiment"),
        "pseudo_seed": seed is None or meta.get("pseudo_seed") == seed,
        "split_key": split_key is None or meta.get("split_key") == split_key,
    }
    for k, v in expect["required"].items():
        checks[f"meta.{k}"] = k in meta and meta[k] == v
    for k, v in expect["if_present"].items():
        if k in meta:
            checks[f"meta.{k}"] = meta[k] == v
    if x_true is not None:
        checks["xtrue_bitwise"] = "xtrue_flat" in z.files and np.array_equal(z["xtrue_flat"], x_true.ravel(order="C"))
    return {"path": str(path), "sha256": sha256(path), "checks": checks, "pass": all(checks.values()),
            "xsec_flat": np.asarray(z["xsec_flat"], float)}


# -------------------------------------------------------------------------------------- units


def run_experiments(world: World, cfg: dict, bkg: dict, unit: dict, out: Path, ratios: dict,
                    only: tuple[int, int] | None = None) -> int:
    ks = cfg["iterations"]["reported"]
    seeds = [(s, k) for s, k in unit_seeds(unit) if only is None or only[0] <= s <= only[1]]
    rc = 0
    for seed, split_key in seeds:
        target = out / f"{unit['name']}_s{seed}.npz"
        if target.exists():
            continue
        t0 = time.time()
        if unit["arm"] == "P":
            exp, x_true, info, is_b, variants = build_p(world, bkg, unit["truth"], unit["amplitude"], split_key, seed)
        else:
            exp, x_true, info, is_b, variants = build_n(world, bkg, unit["truth"], unit["amplitude"], split_key, seed,
                                                       ratios.get(unit.get("ratio")))
        half = half_from_experiment(world, exp, is_b)
        t1 = time.time()
        if unit["name"] not in world.reweights:
            world.reweights = {unit["name"]: truth_reweight(world, unit, ratios)}
        f_oracle, f_true_a = oracle_floor(world, half, world.reweights[unit["name"]])
        arrays = {"f_true": world.functionals(x_true), "ks": np.array(ks), "f_oracle": f_oracle, "f_true_A": f_true_a}
        diag = {}
        for name, (y, b_extra) in variants.items():
            r = unfold_ibu(world, half, y, b_extra, ks)
            arrays[f"F_{name}"] = r.pop("F")
            diag[name] = r
        gate = None
        cpath = comparator_path(unit, seed)
        if cpath is not None:
            if not cpath.exists():
                gate = {"path": str(cpath), "pass": False, "checks": {"exists": False}}
            else:
                g = comparator_gate(cpath, x_true, info, seed, split_key,
                                    expected_construction(cfg, unit, unit["truth"], unit["amplitude"]))
                arrays["f_of"] = world.functionals(g.pop("xsec_flat"))
                gate = g
            rc |= 0 if gate["pass"] else 8
        meta = {"schema": "ibu1-experiment/1", "unit": unit["name"], "arm": unit["arm"], "truth": unit["truth"],
                "amplitude": unit["amplitude"], "ratio": unit.get("ratio"), "pseudo_seed": seed, "split_key": split_key,
                "experiment": info, "n_half_a": int(half.rows.size), "variants": diag, "comparator": gate,
                "seconds_build": round(t1 - t0, 3), "seconds_ibu": round(time.time() - t1, 3)}
        write(target, arrays, meta)
        print(json.dumps({"unit": unit["name"], "seed": seed, "gate": None if gate is None else gate["pass"],
                          "s_build": meta["seconds_build"], "s_ibu": meta["seconds_ibu"]}), flush=True)
    return rc


def run_bootstrap(world: World, cfg: dict, bkg: dict, unit: dict, out: Path) -> int:
    """IA-6: sigma for IBU from the comparator's own declared bootstrap experiment and replica seeds."""
    ks = cfg["iterations"]["reported"]
    seed, split_key = unit["experiment"]["pseudo_seed"], unit["experiment"]["split_key"]
    target = out / f"{unit['name']}.npz"
    if target.exists():
        return 0
    if unit["arm"] == "P":
        exp, x_true, info, is_b, _ = build_p(world, bkg, "nominal", 0.0, split_key, seed)
    else:
        exp, x_true, info, is_b, _ = build_n(world, bkg, "nominal", 0.0, split_key, seed, None)
    gate = comparator_gate(REPO_PATH(unit["comparator_base"]), None, info, seed, split_key,
                           expected_construction(cfg, unit, "nominal", 0.0))
    gate.pop("xsec_flat")
    controls = {}
    if unit["arm"] == "P":
        controls["replica_capture"] = replica_capture(world.prod, exp, unit["replicas"][0])
    first, last = unit["replicas"]
    F = {"pur": [], "fold": []} if unit["arm"] == "P" else {"fold": [], "sub": []}
    t0 = time.time()
    for b in range(first, last + 1):
        if unit["arm"] == "P":
            rep, draws = p_bootstrap_replica(exp, b)
            variants = p_variants(world, bkg, exp, rep["measured_weights"], exp["raw_counts"] * draws)
        else:
            rep = world.prod.s5n_pseudo.bootstrap_replica(exp, b)
            variants = n_variants(world, rep)
        half = Half(np.flatnonzero(~is_b), rep["w_truth"], rep["w_reco"])
        for name, (y, b_extra) in variants.items():
            F[name].append(unfold_ibu(world, half, y, b_extra, ks)["F"])
    meta = {"schema": "ibu1-bootstrap/1", "unit": unit["name"], "arm": unit["arm"], "pseudo_seed": seed,
            "split_key": split_key, "replicas": [first, last], "experiment": info, "comparator": gate,
            "controls": controls, "seconds": round(time.time() - t0, 3)}
    arrays = {f"F_{k}": np.array(v) for k, v in F.items()}
    arrays["ks"] = np.array(ks)
    write(target, arrays, meta)
    ok = gate["pass"] and all(c.get("pass", True) for c in controls.values())
    print(json.dumps({"unit": unit["name"], "gate": gate["pass"], "controls": {k: v["pass"] for k, v in controls.items()}}), flush=True)
    return 0 if ok else 8


def replica_capture(prod: Producers, exp: dict, b: int) -> dict:
    """Control: ``s5c_pseudo.run_bootstrap`` builds the same replica as ``p_bootstrap_replica``. Its unfold
    is replaced by a capture that raises before anything is written."""
    sp = prod.s5c_pseudo
    seen: list = []

    class Captured(Exception):
        pass

    def capture(rep, *args, **kwargs):
        seen.append(rep)
        raise Captured

    original_build, original_unfold = sp.build_experiment, sp.s5c_unfold.unfold
    sp.build_experiment = lambda *a, **k: (exp, None, {})
    sp.s5c_unfold.unfold = capture
    try:
        scratch = Path(tempfile.mkdtemp(prefix="ibu1-capture-"))
        ns = argparse.Namespace(truth="nominal", amplitude=0.0, split_key=None, pseudo_seed=None,
                                bootstrap_seeds=f"{b}:{b}", out=scratch, config="deterministic",
                                estimator_seed=42, threads=1, iters=5)
        try:
            sp.run_bootstrap(ns, None, None, "", "")
        except Captured:
            pass
        written = sorted(p.name for p in scratch.iterdir())
        shutil.rmtree(scratch)
    finally:
        sp.build_experiment, sp.s5c_unfold.unfold = original_build, original_unfold
    mine, _ = p_bootstrap_replica(exp, b)
    same = len(seen) == 1 and all(np.array_equal(seen[0][k], mine[k]) for k in ("measured_weights", "w_truth", "w_reco"))
    return {"replica": b, "pass": bool(same and not written), "files_written": written}


def run_data(world: World, cfg: dict, bkg: dict, unit: dict, out: Path) -> int:
    """IA-11: the real data at K in the declared set, full MC x1, both arms' background treatments."""
    ks = cfg["iterations"]["reported"]
    target = out / f"{unit['name']}.npz"
    if target.exists():
        return 0
    inp = world.inputs
    half = Half(np.arange(world.tflat.size), inp["w_truth"], inp["w_reco"])
    if unit["arm"] == "P":
        variants = {"pur": (world.reco_hist(inp["measured"], inp["measured_weights"]), np.zeros(world.n_fine)),
                    "fold": (world.reco_hist(inp["measured"], np.ones(inp["measured"].shape[0])),
                             np.asarray(bkg["bkg_nd"], float).ravel(order="C"))}
    else:
        variants = n_variants(world, world.prod.s5n_pseudo.build_data(inp, bkg))
    arrays = {"ks": np.array(ks)}
    diag = {}
    for name, (y, b_extra) in variants.items():
        r = unfold_ibu(world, half, y, b_extra, ks)
        arrays[f"F_{name}"] = r.pop("F")
        diag[name] = r
    write(target, arrays, {"schema": "ibu1-data/1", "unit": unit["name"], "arm": unit["arm"], "variants": diag})
    return 0


# ------------------------------------------------------------------------------------- helpers


def REPO_PATH(p: str) -> Path:
    return Path(p) if os.path.isabs(p) else REPO / p


def unit_seeds(unit: dict) -> list[tuple[int, int]]:
    """(seed, split key) pairs: explicit pairs, or a seed range with the split key the comparator's batch
    mode derived (``s5c_pseudo.split_key_for``; IA-2)."""
    if "pairs" in unit:
        return [(int(s), int(k)) for s, k in unit["pairs"]]
    first, last = unit["seeds"]
    return [(s, split_key_for(s)) for s in range(first, last + 1)]


def split_key_for(seed: int) -> int:
    return (seed * 0x9E3779B1 + 0x5C5C) % (2**61 - 1)  # tested equal to s5c_pseudo.split_key_for


def comparator_path(unit: dict, seed: int) -> Path | None:
    c = unit.get("comparator")
    if not c:
        return None
    if "paths" in c:
        p = c["paths"].get(str(seed))
        return None if p is None else REPO_PATH(p)
    first, last = c["seeds"]
    return REPO_PATH(c["template"].format(seed=seed)) if first <= seed <= last else None


def write(target: Path, arrays: dict, meta: dict) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + f".partial-{os.getpid()}.tmp")  # never matches a reader's *.npz glob
    with open(tmp, "wb") as fh:
        np.savez_compressed(fh, **arrays, meta=json.dumps(meta, default=str))
    if target.exists():
        tmp.unlink()
        return
    os.replace(tmp, target)


def load_inputs(prod: Producers, cfg: dict, npz: Path, bkg_path: Path) -> tuple[dict, dict]:
    pins = cfg["inputs"]
    if sha256(npz) != pins["of_inputs_5d_sha256"]:
        raise GateFailure("of_inputs_5d.npz digest differs from config.json")
    if sha256(bkg_path) != pins["bkg_dump_sha256"]:
        raise GateFailure("bkg_dump.npz digest differs from config.json")
    inputs = prod.s5c_pseudo.s5c_unfold.load_inputs(npz)
    bz = np.load(bkg_path, allow_pickle=True)
    if json.loads(str(bz["meta"]))["npz_sha256"] != pins["of_inputs_5d_sha256"]:
        raise GateFailure("background dump was made against a different npz")
    return inputs, {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}


def load_ratios(cfg: dict) -> dict:
    out = {}
    for name, r in cfg["ratios"].items():
        p = REPO / r["path"]
        if sha256(p) != r["expect_sha256"]:
            raise GateFailure(f"ratio {name} digest differs from config.json")
        out[name] = json.loads(p.read_text())
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--bkg", type=Path, required=True)
    ap.add_argument("--unit", action="append", required=True, help="a unit name from config.json (repeatable)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seeds", default=None, help="first:last, a sub-range of ONE experiments unit's declared seeds")
    ap.add_argument("--threads", type=int, default=1)
    a = ap.parse_args(argv)
    cfg = json.loads(CONFIG.read_text())
    if a.threads > cfg["resources"]["max_threads_per_task"]:
        print("refusing: thread count above the declared cap", file=sys.stderr)
        return 2
    units = {u["name"]: u for u in cfg["units"]}
    missing = [u for u in a.unit if u not in units]
    if missing:
        print(f"refusing: unknown units {missing}", file=sys.stderr)
        return 2
    only = None
    if a.seeds is not None:
        only = tuple(int(v) for v in a.seeds.split(":"))
        declared = {s for s, _ in unit_seeds(units[a.unit[0]])} if units[a.unit[0]]["kind"] == "experiments" else set()
        if len(a.unit) != 1 or not declared or not set(range(only[0], only[1] + 1)) <= declared:
            print("refusing: --seeds must be a sub-range of one experiments unit's declared seeds", file=sys.stderr)
            return 2
    try:
        prod = Producers(cfg)
        contract = json.loads((REPO / cfg["contract"]["path"]).read_text())
        if sha256(REPO / cfg["contract"]["path"]) != cfg["contract"]["expect_sha256"]:
            raise GateFailure("contract digest differs from config.json")
        inputs, bkg = load_inputs(prod, cfg, a.npz, a.bkg)
        ratios = load_ratios(cfg)
        world = World(prod, inputs, contract)
        if len(world.names) != cfg["functionals"]["count"]:
            raise GateFailure("functional count differs from config.json")
    except GateFailure as e:
        print(f"refusing: {e}", file=sys.stderr)
        return 4
    rc = 0
    for name in a.unit:
        u = units[name]
        if u["kind"] == "experiments":
            rc |= run_experiments(world, cfg, bkg, u, a.out, ratios, only)
        elif u["kind"] == "bootstrap":
            rc |= run_bootstrap(world, cfg, bkg, u, a.out)
        elif u["kind"] == "data":
            rc |= run_data(world, cfg, bkg, u, a.out)
    return rc


if __name__ == "__main__":
    sys.exit(main())
