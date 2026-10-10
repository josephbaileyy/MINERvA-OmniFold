"""Synthetic controls for the D-ID driver (no MINERvA data).

Each mechanism the diagnostic relies on is shown to fire on the defect it targets and to stay silent on
the clean case, first on small dense fixtures against ``../gbdt/comparator.py``, then end to end on a
synthetic event file with the real 5D grid, real functional rows and real truth-reweight code. Run from
the repository root with at most two threads:

    OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2 \
        python3 -m pytest -q -p no:cacheprovider docs/orchestration/state/next-preparation-20261009/d-id/test_did.py
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pytest
from scipy import sparse

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("did_driver", HERE / "did.py")
did = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = did
spec.loader.exec_module(did)
CFG = json.loads((HERE / "config.json").read_text())
cmp = did.load_comparator(CFG["code"]["comparator.py"])
com = did.load_committed(CFG["code"]["nd-unfolding"])
AXES = ("pt", "pz", "eavail", "q3", "W")


def _smearing(n_truth, n_reco, width, efficiency=0.8):
    ct = (np.arange(n_truth) + 0.5) / n_truth
    cr = (np.arange(n_reco) + 0.5) / n_reco
    k = np.exp(-0.5 * ((cr[:, None] - ct[None, :]) / width) ** 2)
    return efficiency * k / k.sum(axis=0, keepdims=True)


def _fixture():
    r = _smearing(12, 18, 0.06)
    prior = 1e4 * (1.0 + 0.5 * np.sin(np.linspace(0, 3, 12)))
    truth = prior * (1.0 + 0.3 * np.cos(np.linspace(0, 6, 12)))
    return r, prior, truth


# ---------------------------------------------------------------------------- response algebra


def test_sparse_response_and_same_sample_identity():
    """Pairs + response equal a brute-force dense response; same-sample data = R t + b exactly."""
    rng = np.random.default_rng(1)
    n, n_fine, n_reco = 5000, 20, 15
    tf = rng.integers(-1, n_fine, n)  # -1: truth outside the grid (a known reco term)
    rf = rng.integers(-1, n_reco, n)
    passed = rng.uniform(size=n) < 0.7
    wt, wr = rng.uniform(0.5, 1.5, n), rng.uniform(0.5, 1.5, n)
    coarse = np.arange(n_fine) // 4
    sig = passed & (rf >= 0)
    pair, bkg = sig & (tf >= 0), sig & (tf < 0)
    u = np.bincount(tf[tf >= 0], weights=wt[tf >= 0], minlength=n_fine)
    grid = did.make_grid("G", coarse, 5, u)
    pairs = did.Pairs.build(rf[pair], tf[pair], n_fine)
    r = did.response(grid, pairs, pairs.sums(wr[pair]), u, n_reco).toarray()
    dense = np.zeros((n_reco, 5))
    for i in np.flatnonzero(pair):
        dense[rf[i], coarse[tf[i]]] += wr[i]
    dense /= np.bincount(coarse[tf[tf >= 0]], weights=wt[tf >= 0], minlength=5)[None, :]
    np.testing.assert_allclose(r, dense, rtol=1e-13)
    y = np.bincount(rf[sig], weights=wr[sig], minlength=n_reco)
    b = np.bincount(rf[bkg], weights=wr[bkg], minlength=n_reco)
    np.testing.assert_allclose(r @ did.coarse_sum(grid, u) + b, y, rtol=1e-12)
    # an empty coarse cell is dropped and listed
    u2 = u.copy()
    u2[coarse == 3] = 0
    assert did.make_grid("G", coarse, 5, u2).dropped == [3]


def test_split_edges_rule_on_the_real_grid():
    fine = [CFG["fine_edges"][a] for a in AXES]
    j = [CFG["J_edges"][a] for a in AXES]
    got = [did.split_edges(f, c) for f, c in zip(fine, j)]
    assert got == [[0.0, 0.25, 0.55, 0.7, 0.85, 2.5, 4.5], [1.5, 2.5, 3.5, 4.5, 6.0, 40.0, 60.0],
                   [0.0, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0], [0.0, 0.6, 1.2, 2.0, 100.0],
                   [0.0, 1.1, 1.4, 1.8, 2.2, 3.0, 100.0]]  # pz [3.5, 6]: 4.5 and 5.0 tie, lower kept


def test_coarse_map_reproduces_the_committed_j_rows():
    """T1 cell of every fine cell equals the support of s5c_coverage's J rows (the traces' functionals)."""
    fine = [np.asarray(CFG["fine_edges"][a]) for a in AXES]
    j = [CFG["J_edges"][a] for a in AXES]
    c1 = did.coarse_of_fine(fine, j)
    contract = json.loads((did.REPO / CFG["s5c_contract"]).read_text())
    u, names = com.s5c_coverage.reported_functionals(contract)
    for row, name in zip(u, names):
        if name.startswith("J"):
            assert set(np.unique(c1[row > 0])) == {int(name[1:])}


# ---------------------------------------------------------------------------------- IBU


def test_ibu_equals_the_reference_update():
    r, prior, truth = _fixture()
    y = r @ truth
    ref = cmp.ibu(r, y, prior, 60)
    maps = np.eye(12)
    got = did.ibu(sparse.csr_matrix(r), y, np.zeros(18), prior, 60, maps=maps, record=tuple(range(1, 61)))
    np.testing.assert_allclose(got.trajectory, ref, rtol=1e-12)


def test_known_term_and_zero_efficiency_cells():
    """With a known reco term the same-sample nominal closes exactly; a zero-efficiency cell keeps its
    prior (the reference refuses it)."""
    r, prior, truth = _fixture()
    r = r.copy()
    r[:, 4] = 0.0
    b = np.linspace(5, 50, 18)
    res = did.ibu(sparse.csr_matrix(r), r @ prior + b, b, prior, 200)
    np.testing.assert_allclose(res.final, prior, rtol=1e-12)
    res = did.ibu(sparse.csr_matrix(r), r @ truth + b, b, prior, 400)
    assert res.final[4] == prior[4]
    with pytest.raises(ValueError):
        cmp.ibu(r, r @ truth, prior, 3)


def test_convergence_flag_both_directions():
    r, prior, truth = _fixture()
    y = r @ truth
    ok = did.ibu(sparse.csr_matrix(r), y, np.zeros(18), prior, 100000, tol=1e-10)
    assert ok.converged and ok.last_rel_change < 1e-10
    capped = did.ibu(sparse.csr_matrix(r), y, np.zeros(18), prior, 20, tol=1e-10)
    assert capped.converged is False and capped.iterations == 20


# ------------------------------------------------------------------------- Fisher / null space


def test_fisher_widths_and_invisible_share_equal_the_reference():
    r, _, truth = _fixture()
    rng = np.random.default_rng(3)
    maps = rng.normal(size=(7, 12))
    f = did.fisher(sparse.csr_matrix(r), truth, np.zeros(18))
    np.testing.assert_allclose(f, cmp.fisher(r, truth), rtol=1e-12)
    values, vectors = np.linalg.eigh(f)
    sigma, null = did.widths_from_eig(values, vectors, maps)
    ref = cmp.cr_width(r, truth, maps)
    np.testing.assert_allclose(sigma, ref.sigma, rtol=1e-12)
    np.testing.assert_allclose(null, ref.null_fraction, rtol=1e-12, atol=1e-15)
    resid = 300.0 * vectors[:, 0] + 3.0 * vectors[:, -1]
    np.testing.assert_allclose(did.invisible_from_eig(values, vectors, resid, maps),
                               cmp.invisible_share(r, truth, resid, maps), rtol=1e-10, atol=1e-12)


def test_singular_fisher_flags_the_null_functional_only():
    r, _, truth = _fixture()
    r = r.copy()
    r[:, 7] = r[:, 6]
    maps = np.zeros((3, 12))
    maps[0, 6], maps[0, 7] = 1.0, -1.0
    maps[1, 6] = maps[1, 7] = 1.0
    maps[2, 0] = 1.0
    values, vectors = np.linalg.eigh(did.fisher(sparse.csr_matrix(r), truth, np.zeros(18)))
    sigma, null = did.widths_from_eig(values, vectors, maps)
    assert np.isinf(sigma[0]) and null[0] > 0.99 and np.isfinite(sigma[1:]).all()
    # a known reco term only adds variance: widths grow, never shrink
    sig_b, _ = did.widths_from_eig(*np.linalg.eigh(did.fisher(sparse.csr_matrix(r), truth, np.full(18, 500.0))),
                                   maps)
    assert np.all(sig_b[1:] > sigma[1:])


# ---------------------------------------------------------------------- functional projection


def test_projection_is_exact_with_own_shares_and_biased_with_nominal_ones():
    rng = np.random.default_rng(4)
    n_fine = 12
    coarse = np.arange(n_fine) // 3
    u_nom = rng.uniform(1, 2, n_fine)
    u_dep = u_nom * np.where(np.arange(n_fine) % 3 == 0, 1.5, 1.0)  # a within-cell departure
    grid = did.make_grid("G", coarse, 4, u_nom)
    rows = sparse.csr_matrix(rng.uniform(0, 1, (5, n_fine)))
    t_dep = did.coarse_sum(grid, u_dep)
    exact = did.functional_matrix(rows, grid, u_dep) @ t_dep
    np.testing.assert_allclose(exact, rows @ u_dep, rtol=1e-13)
    biased = did.functional_matrix(rows, grid, u_nom) @ t_dep
    assert np.max(np.abs(biased / (rows @ u_dep) - 1)) > 1e-3
    fine_grid = did.make_grid("F", np.arange(n_fine), n_fine, u_nom)  # T3: no within-cell freedom
    np.testing.assert_allclose(did.functional_matrix(rows, fine_grid, u_nom) @ u_dep, rows @ u_dep, rtol=1e-13)


# ------------------------------------------------------------------------- decision layer


def _labels(spec):
    return [{"iteration": i, "identifiability": d} for i, d in spec]


W, I, AP, F = "weakly-identified", "identified-at-target", "approximation-dominated", "iteration-faithful"


def test_declare_stage4_rule_and_nonconvergence():
    r = np.full(4, 0.10)
    none = np.zeros(4, bool)
    b_like = _labels([(F, I)] * 4)
    assert did.declare(cmp, b_like, r, np.full(4, 0.01), none, np.ones(4, bool))["branch"] == "B"
    pending = did.declare(cmp, b_like, r, None, none, None)
    assert pending["branch"] == "B-undeclarable" and pending["b_candidates"] == [0, 1, 2, 3]
    assert did.declare(cmp, _labels([(F, W)] * 3 + [(F, I)]), r, None, none, None)["branch"] == "C"
    stalled = did.declare(cmp, b_like, r, np.full(4, 0.01), none, np.zeros(4, bool))
    assert stalled["branch"] == "mixed" and stalled["nonconverged_b_candidates"] == 4
    tie = did.declare(cmp, _labels([(F, W)] * 2 + [(AP, I)] * 2), r, np.full(4, 0.09), none, np.ones(4, bool))
    assert tie["branch"] == "C" and tie["tie"] == ["C", "A"]


def test_b_counted_agrees_with_the_reference_aggregation():
    """The trace reading's B set must be exactly what branch_outcome counts toward B."""
    rng = np.random.default_rng(11)
    kinds = [(F, I), (AP, I), ("mixed", I), (F, W), (F, "intermediate")]
    for _ in range(200):
        n = 12
        lab = _labels([kinds[i] for i in rng.integers(0, len(kinds), n)])
        r = rng.choice([0.01, 0.05, -0.08], n)
        r_inf = r * rng.choice([0.1, 0.9, np.inf], n)
        sens = rng.uniform(size=n) < 0.2
        got = did.b_counted(cmp, lab, r, r_inf, sens)
        ref = cmp.branch_outcome(lab, r, r_inf, sens)
        assert got.size == round(ref["shares"]["B"] * ref["n_eligible"])


def test_sensitive_flags_and_trace_reading():
    a = _labels([(F, I), (AP, I), (F, W)])
    b = _labels([(F, I), (F, I), (F, W)])
    assert did.sensitive_flags(a, b, None).tolist() == [False, True, False]
    assert did.sensitive_flags(a, None, None).tolist() == [False, False, False]
    assert did.trace_reading(cmp, 0.10, 0.11, 40) == "tracks"
    assert did.trace_reading(cmp, 0.012, -0.015, 40) == "tracks"
    assert did.trace_reading(cmp, 0.10, 0.01, 40) == "departs"
    assert did.trace_reading(cmp, 0.10, 0.10, None) == "untraced"


def test_budget_cap_stops_before_and_inside_long_work():
    budget = did.Budget(cap_core_hours=1e-9)
    with pytest.raises(did.CapReached):
        budget.check(1.0)
    r, prior, truth = _fixture()
    with pytest.raises(did.CapReached):
        did.ibu(sparse.csr_matrix(r), r @ truth, np.zeros(18), prior, 5000, tol=0.0, budget=budget, check_every=10)


# ------------------------------------------------------------------------- end-to-end world


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _world(root: Path, scale: float = 1e3, n: int = 40000) -> dict:
    """A synthetic event file on the real grid. Truth occupies the first two J bins of every axis
    (32 J cells), so T2 stays small; reco is a smeared truth, ~30% of truth rows are missed."""
    rng = np.random.default_rng(20261010)
    fine = [np.asarray(CFG["fine_edges"][a], float) for a in AXES]
    hi = [0.85, 6.0, 1.5, 2.0, 2.2]
    gen = np.column_stack([rng.uniform(e[0], h, n) for e, h in zip(fine, hi)]).astype(np.float32)
    gen[:40] = -9999.0  # truth sentinels inside pass_truth: the known reco term
    reco = (gen * rng.normal(1.0, 0.45, gen.shape) + rng.normal(0.0, 0.15, gen.shape)).astype(np.float32)
    reco[:40] = gen[40:80] * 1.01
    pass_truth = rng.uniform(size=n) < 0.95
    pass_truth[:40] = True
    pass_reco = rng.uniform(size=n) < 0.55 + 0.35 * (gen[:, 2] / 1.5).clip(0, 1)
    w_truth = scale * rng.uniform(0.8, 1.2, n)
    w_reco = w_truth * rng.uniform(0.95, 1.05, n)
    m = pass_truth & np.all(gen > -9000, axis=1)
    ofin, _ = np.histogramdd(gen[m].astype(float), bins=fine, weights=w_truth[m])
    path = root / CFG["events"]["file"]
    path.parent.mkdir(parents=True, exist_ok=True)
    arrays = {"MCgen": gen, "MCreco": reco, "pass_reco": pass_reco, "pass_truth": pass_truth,
              "w_truth": w_truth, "w_reco": w_reco, "denom_nd": ofin / 0.95,
              "flux": np.linspace(5e-4, 7e-4, len(fine[0]) - 1), "data_pot": np.array(1.1e21),
              "n_nucleons": np.array(3.2e30), "nedges": np.array(5)}
    arrays.update({f"edges_{i}": e for i, e in enumerate(fine)})
    np.savez(path, **arrays)
    with zipfile.ZipFile(path, "a") as z:  # reading a real-data key would raise: AM-17's control
        z.writestr("measured.npy", b"not an array")
        z.writestr("measured_weights.npy", b"not an array")
    return {"path": path}


def _probe(root: Path, cfg: dict):
    """Stage 1 of the driver on the world, to read its truths, folds and exact IBU for the fixtures."""
    d = did.Diagnostic(cfg, root, root / "probe", did.Budget(10.0), cmp, com)
    d.load_events()
    d.build_rows()
    d.histograms()
    d.grids()
    return d


def _write_products(root: Path, d, cfg: dict, factor: float) -> dict:
    """GBDT stand-ins: functional residual = factor x the exact T2 nominal-weighted IBU residual at every K
    (factor 1: iteration-faithful by construction; factor 3: approximation-dominated)."""
    names = d.names
    receipt = {"study_K": {"b0": {"runs": {}}, "cap10": {"runs": {}}}}
    traces = {}
    for name, spec in cfg["comparators"]["traces"].items():
        ws = spec["weight_set"]
        k_max = 10 if spec["family"] == "cap10" else (200 if ws in ("nominal", "w3") else 40)
        f_true = d.f_true(d.h[ws]["u"])
        tr = d.run_trajectory("T2", ws, "same", "nom", keep_all=True)
        r = np.nan_to_num(tr["r"][:k_max])
        fn = f_true * (1.0 + factor * r)
        out = root / spec["file"]
        out.parent.mkdir(parents=True, exist_ok=True)
        arrays = {"fn_push": fn, "fn_true_A": f_true}
        if ws in ("nominal", "w3") and spec["family"] == "b0":
            arrays["fn_true"] = f_true
            arrays["xsec_flat"] = d.kappa * d.h[ws]["u"] * 1.01
            arrays["meta"] = np.array(json.dumps({"functional_names": names,
                                                  "input_npz_sha256": cfg["events"]["expect_sha256"]}))
        np.savez(out, **arrays)
        traces[name] = {**spec, "expect_sha256": _sha(out)}
        series = {}
        for k in (1, 5, 10) + ((20, 40) if k_max >= 40 else ()):
            rk = did.rel(fn[k - 1], f_true)
            series[str(k)] = {g: {"median_abs_pct": 100 * float(np.median(np.abs(
                rk[np.array(d.f183)[(d.groups == g) & d.reported]])))} for g in ("EW", "J", "H2")}
        receipt["study_K"][spec["family"]]["runs"][spec["receipt_run"]] = {"K": k_max, "series": series}
    rp = root / "stage2_receipt.json"
    rp.write_text(json.dumps(receipt))
    cfg["records"]["stage2_receipt"]["expect_sha256"] = _sha(rp)
    targets = {}
    for name, spec in cfg["comparators"]["s5e"].items():
        ws = spec["weight_set"]
        f_true = d.f_true(d.h[ws]["u"])[:153]
        y = np.zeros(d.n_fine)
        y[d.reco_cells] = d.h[ws]["y"]
        arrays = {"fn_push": np.tile(f_true * 1.02, (30, 1)), "fn_true": f_true, "reco5d_true": y,
                  "xsec_flat": d.kappa * d.h[ws]["u"] * 1.02,
                  "meta": np.array(json.dumps({"input_npz_sha256": cfg["events"]["expect_sha256"],
                                               "construction": "asimov_same", "iters": 30}))}
        lam = {}
        for k in (5, 15, 30):
            push = y * (1.0 + 0.01 / k)
            arrays[f"reco5d_push_it{k}"] = push.astype(np.float32)
            ok = y > 0
            lam[str(k)] = float(np.sum((push.astype(np.float32).astype(float)[ok] - y[ok]) ** 2 / y[ok]))
        out = root / spec["file"]
        out.parent.mkdir(parents=True, exist_ok=True)
        np.savez(out, **arrays)
        if name in ("asimov_b0_eavail", "asimov_b0_q3"):
            y0 = d.h["nominal"]["y"]
            yy = d.h[ws]["y"]
            targets[name] = {"S_dep": float(np.sum((y0 - yy) ** 2 / yy)), "lambda_5d": lam}
    for name, spec in cfg["comparators"]["d3_sig"].items():
        for i, f in enumerate(spec["files"]):
            out = root / f
            out.parent.mkdir(parents=True, exist_ok=True)
            ws = {"eavail": "gibuu", "q3": "q3", "nominal": "nominal"}[name]
            f_true = d.f_true(d.h[ws]["u"])[:153]
            key = com.s5n_pseudo.s5c_pseudo.split_key_for(cfg["split"]["seed"] + i) if name == "eavail" else 7
            np.savez(out, fn_push=np.tile(f_true, (20, 1)), fn_true=f_true,
                     meta=np.array(json.dumps({"input_npz_sha256": cfg["events"]["expect_sha256"], "no_background": True,
                                               "split_key": key, "pseudo_seed": cfg["split"]["seed"] + i})))
    return {"traces": traces, "receipt": rp, "targets": targets}


def _strong_ratios(root: Path, cfg: dict, coarse: bool = False) -> None:
    """Fixture departures strong enough to leave eligible (> 2%) residuals in the small world: smooth
    fine-cell shape ratios read by the committed ``ratio_nd`` path (s5e_deform.ratio_weight). With
    ``coarse`` the ratio is constant inside every J cell, so no weighting has within-cell freedom."""
    fine = [np.asarray(CFG["fine_edges"][a], float) for a in AXES]
    jcell = [did.coarse_of_fine([fine[a]], [CFG["J_edges"][AXES[a]]]) for a in range(5)]
    specs = {"gibuu": ((0, 1, 2), 1.0), "w1": ((0, 2), 2.0), "w3": ((0, 1, 2), 3.0), "q3": ((2, 3, 4), 1.5),
             "w2": ((2, 4), 2.5)}
    for ws in cfg["weight_sets"]:
        if ws["name"] not in specs:
            continue
        axes, phase = specs[ws["name"]]
        centres = np.meshgrid(*[(jcell[a] if coarse else np.arange(len(fine[a]) - 1)).astype(float) for a in axes],
                              indexing="ij")
        rho = np.exp(0.6 * np.sin(phase + sum(c * (k + 1) * 0.7 for k, c in enumerate(centres))))
        path = root / f"ratio_{ws['name']}.json"
        path.write_text(json.dumps({"schema": "s5e-shape-ratio/1", "axes": list(axes),
                                    "edges": [fine[a].tolist() for a in axes],
                                    "shape_ratio": rho.ravel(order="C").tolist()}))
        ws.update({"truth": "ratio_nd", "amplitude": 1.0, "ratio": str(path), "ratio_expect_sha256": _sha(path)})


def _config(root: Path, world: dict, coarse: bool = False) -> dict:
    cfg = copy.deepcopy(CFG)
    _strong_ratios(root, cfg, coarse)
    cfg["events"]["expect_sha256"] = _sha(world["path"])
    cfg["events"]["pair_rows_expected"] = None
    cfg["reco_cells_expected"] = None
    return cfg


def _ready_world(tmp_path: Path, factor: float, scale: float = 1e3, coarse: bool = False):
    world = _world(tmp_path, scale=scale)
    cfg = _config(tmp_path, world, coarse)
    # the driver must be told the file's counts, as for the real file: learn them from the rows
    d = did.Diagnostic(cfg, tmp_path, tmp_path / "probe", did.Budget(10.0), cmp, com)
    d.load_events()
    d.build_rows()
    sig = d.pr & (d.rf_fine >= 0)
    cfg["events"]["pair_rows_expected"] = int(np.sum(sig & (d.tf >= 0)))
    y = np.bincount(d.rf_fine[sig], weights=d.wr[sig], minlength=d.n_fine)
    cfg["reco_cells_expected"] = int(np.sum(y > 0))
    d = _probe(tmp_path, cfg)
    prod = _write_products(tmp_path, d, cfg, factor)
    cfg["comparators"]["traces"] = prod["traces"]
    cfg["records"]["stage2_receipt"]["path"] = str(prod["receipt"])
    cfg["records"]["diag_receipt"]["targets"] = prod["targets"]
    w2 = d.f_true(d.h["w2"]["u"])[d.f183]
    tr = d.run_trajectory("T2", "w2", "same", "nom", keep_all=True)
    op = dict(np.load(did.REPO / CFG["operands"]["path"]))
    op["assessment_W2"] = np.tile(w2 * (1 + factor * np.nan_to_num(tr["r"][4][d.f183])), (3, 1))
    op["assessment_W2_truth"] = np.tile(w2, (3, 1))
    np.savez(tmp_path / "operands.npz", **op)
    cfg["operands"]["path"] = str(tmp_path / "operands.npz")
    cfg["operands"]["expect_sha256"] = _sha(tmp_path / "operands.npz")
    cfg["iterations"]["convergence_max"] = 20000
    return cfg


def _run(cfg: dict, root: Path, out: str, **kw) -> tuple[int, dict]:
    path = root / f"{out}.json"
    path.write_text(json.dumps(cfg))
    rc = did.main(["--config", str(path), "--inputs", str(root), "--out", str(root / out), *kw.get("argv", [])])
    return rc, json.loads((root / out / "results.json").read_text())


@pytest.fixture(scope="module")
def faithful_world(tmp_path_factory):
    root = tmp_path_factory.mktemp("faithful")
    return root, _ready_world(root, factor=1.0)


@pytest.fixture(scope="module")
def approximate_world(tmp_path_factory):
    root = tmp_path_factory.mktemp("approx")
    return root, _ready_world(root, factor=5.0)


def _env(monkeypatch):
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        monkeypatch.setenv(var, "2")


def test_end_to_end_binning_bias_makes_functionals_resolution_sensitive(faithful_world, monkeypatch):
    """Positive control of the resolution-sensitivity rule. The stand-in equals the nominal-weighted T2
    IBU, whose residual is within-cell binning bias that the departure-weighted response removes: every
    functional is iteration-faithful at the primary setting, and the label change across weightings
    excludes it. Also: every stage completes and every gating control passes."""
    root, cfg = faithful_world
    _env(monkeypatch)
    rc, out = _run(cfg, root, "run_faithful")
    assert rc == 0, out["stages"]
    assert all(v["status"] == "complete" for v in out["stages"].values())
    assert all(c.get("pass", True) for c in out["controls"].values() if isinstance(c, dict))
    assert out["admission"]["A10_keys_read"]["detail"]["real_data_keys_never_read"] == ["measured", "measured_weights"]
    big = [x for ws in out["decision"]["labels"].values() for x in ws["J"] if abs(x["r_gbdt_K5"]) > 0.02]
    assert big and all(x["T2_nom"]["iteration"] == "iteration-faithful" for x in big)
    assert all(x["sensitive"] and x["T2_dep"]["iteration"] != "iteration-faithful" for x in big)
    for res in out["decision"]["maps"].values():
        assert res["branch"] == "no-eligible-functional" and res["n_eligible"] == 0
    tables = np.load(root / "run_faithful" / "tables.npz")
    assert tables["traj/T2/same/nom/gibuu/r"].shape[0] == 200


def test_end_to_end_no_within_cell_freedom_means_no_binning_bias(tmp_path, monkeypatch):
    """Negative control of the binning-bias term (AM-4/AM-5): with departures constant inside every J
    cell, the nominal- and departure-weighted responses and projections coincide, the binning bias is
    zero to rounding at every grid, the labels agree across weightings, and nothing counts toward A."""
    _env(monkeypatch)
    cfg = _ready_world(tmp_path, factor=1.0, coarse=True)
    rc, out = _run(cfg, tmp_path, "run_coarse")
    assert rc == 0
    for ws in ("gibuu", "w1", "w3", "q3", "w2"):  # the fixture-ratio departures (P1r-P3r keep real files)
        for grp in ("EW", "J", "H2"):
            row = out["summaries"][ws][grp]
            for k in ("binning_bias_T2_K5", "binning_bias_T2_K200"):
                assert row[k]["max"] < 1e-9, (ws, grp, k, row[k])
    labels = [x for ws in out["decision"]["labels"].values() for x in ws["J"]]
    assert labels and all(x["T2_dep"] == x["T2_nom"] for x in labels)
    assert all(res["shares"]["A"] == 0.0 for res in out["decision"]["maps"].values())


def test_end_to_end_approximate_estimator_reaches_branch_a(approximate_world, monkeypatch):
    root, cfg = approximate_world
    _env(monkeypatch)
    rc, out = _run(cfg, root, "run_approx")
    assert rc == 0, out["stages"]
    j = out["decision"]["maps"]["J"]
    # residual = 5 x exact IBU's: approximation-dominated wherever eligible; identified at this exposure
    assert j["n_eligible"] > 0 and j["shares"]["A"] > 0.5 and j["branch"] == "A", j


def test_end_to_end_weak_exposure_reaches_branch_c(tmp_path, monkeypatch):
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        monkeypatch.setenv(var, "2")
    cfg = _ready_world(tmp_path, factor=5.0, scale=1e-3)  # same shapes, 10^6 times less information
    rc, out = _run(cfg, tmp_path, "run_weak")
    assert rc == 0
    j = out["decision"]["maps"]["J"]
    assert j["branch"] == "C" and j["shares"]["C"] > 0.5, j


def test_cap_during_stage4_leaves_branch_b_undeclarable(faithful_world, monkeypatch):
    root, cfg = faithful_world
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        monkeypatch.setenv(var, "2")
    capped = copy.deepcopy(cfg)
    capped["price_s"]["convergence_T2"] = 1e9  # the next unit of stage 4 cannot fit: stop before it
    rc, out = _run(capped, root, "run_cap4")
    assert rc == 5
    assert out["stages"]["4"]["status"] == "cap" and out["stages"]["5"]["status"] == "not-started"
    for res in out["decision"]["maps"].values():
        assert res["branch"] in ("C", "A", "B-undeclarable", "no-eligible-functional"), res
        assert res.get("stage4") in ("missing", None)


def test_cap_during_stage1_declares_nothing(faithful_world, monkeypatch):
    root, cfg = faithful_world
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        monkeypatch.setenv(var, "2")
    capped = copy.deepcopy(cfg)
    capped["price_s"]["weights_and_histograms"] = 1e9
    rc, out = _run(capped, root, "run_cap1")
    assert rc == 5 and out["stages"]["1"]["status"] == "cap"
    assert "decision" not in out and all(out["stages"][k]["status"] == "not-started" for k in "2345")


def test_a_tampered_input_stops_everything(faithful_world, monkeypatch):
    root, cfg = faithful_world
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        monkeypatch.setenv(var, "2")
    bad = copy.deepcopy(cfg)
    bad["events"]["expect_sha256"] = "0" * 64
    rc, out = _run(bad, root, "run_bad_digest")
    assert rc == 4 and not out["admission"]["A1_event_digest"]["pass"]
    bad = copy.deepcopy(cfg)
    bad["comparators"]["traces"]["k_b0_w1"]["expect_sha256"] = "f" * 64
    rc, out = _run(bad, root, "run_bad_trace")
    assert rc == 4 and not out["admission"]["A4_trace_k_b0_w1"]["pass"]
    assert out["admission"]["A1_event_digest"]["pass"]  # earlier checks ran, later stages did not
    assert out["stages"]["1"]["status"] == "failed" and out["stages"]["2"]["status"] == "not-started"


def test_receipt_series_check_both_directions():
    """A6 on finite values (the small world's receipt medians are NaN, so this is its real control)."""
    rng = np.random.default_rng(5)
    true = rng.uniform(1, 2, 30)
    fn = true * (1 + rng.normal(0, 0.05, (10, 30)))
    groups = {"EW": np.arange(10), "J": np.arange(10, 25), "H2": np.arange(25, 30)}
    series = {str(k): {g: {"median_abs_pct": 100 * float(np.median(np.abs(fn[k - 1, pos] / true[pos] - 1)))}
                       for g, pos in groups.items()} for k in (1, 5, 10)}
    assert did.receipt_series_deviation(fn, true, series, groups) == (0.0, 0)
    series["5"]["J"]["median_abs_pct"] *= 1.001
    worst, _ = did.receipt_series_deviation(fn, true, series, groups)
    assert 9e-4 < worst < 1.1e-3
    series["5"]["J"]["median_abs_pct"] = float("nan")
    assert did.receipt_series_deviation(fn, true, series, groups)[0] == np.inf
    shifted = fn.copy()
    shifted[4] = fn[5]  # a trace whose prefix is not the receipt's
    series["5"]["J"]["median_abs_pct"] = 100 * float(np.median(np.abs(fn[4, groups["J"]] / true[groups["J"]] - 1)))
    assert did.receipt_series_deviation(shifted, true, series, groups)[0] > 1e-3


def test_thread_limit_is_enforced(faithful_world, monkeypatch):
    root, cfg = faithful_world
    monkeypatch.setenv("OMP_NUM_THREADS", "8")
    path = root / "threads.json"
    path.write_text(json.dumps(cfg))
    assert did.main(["--config", str(path), "--inputs", str(root), "--out", str(root / "run_threads")]) == 2
