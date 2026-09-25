#!/usr/bin/env python3
"""s5n successor unfolds with ``--bkg-mode negweight-refined``: repeated experiments, bootstraps and
the real data, from the ROOT-free npz inputs and the s5c background dump.

Authority: ``docs/orchestration/AUTHORIZATION-20260925-negweight-refined-successor.md``; contract
``docs/orchestration/state/s5n/contract.json`` (``family``, ``sampling_model``). The estimator is the
s5c F2 configuration (``s5c_unfold.unfold(..., "deterministic", ...)``). The background treatment is
the driver's: ``unfold_nd_omnifold_unbinned.py`` builds the signed sample {observed events at +w} U
{background template at -w}, restricted to the analysis window on every axis, refines it with
``unfold_2d_omnifold_unbinned.refine_stay_positive`` (called here, not re-implemented) using an
LGBMClassifier with ``random_state = estimator_seed + 3``, and feeds the refined non-negative sample
to step 1. The only difference from the driver is that the refinement classifier also carries the
F2 configuration's parameters, which the driver does not pass (they are recorded as evidence).

Sampling model (contract ``sampling_model``), stated so nothing is implicit:

* Signal MC rows split by a keyed hash into A (unfolding MC, weights x2) and B (pseudo-data source);
  background MC rows split by an independent keyed hash into C (pseudo-data source) and D (template,
  weights x2). Pseudo-data signal counts ``n_i ~ Poisson(2 w_reco_i r_i)`` per reco-passing B row;
  pseudo-data background counts ``m_j ~ Poisson(2 w_bkg_j)`` per C row. Truth: B's reweighted truth
  through the analysis's extraction (``s5c_pseudo.build_experiment``'s definition).
* Bootstrap replica: every observed event is resampled individually (a count-k row gets
  ``Poisson(k)``; a real-data event ``Poisson(1)``), every unfolding-MC row gets ``Poisson(1)`` on
  ``w_truth`` and ``w_reco``, every template row ``Poisson(1)`` on its weight, and the refinement is
  REFIT on the replica's signed sample.
* ``--data``: the real data (the npz's measured events, count 1) against the full background dump
  and the full MC (weights x1).

``--bkg-mode purity`` is the baseline: pseudo-experiments are exactly ``s5c_pseudo.build_experiment``
(control C0); ``--data`` uses the npz's stored purity weights.

MEASURES: one unfold of the named construction, with its refinement evidence. CANNOT AUTHORIZE: a
coverage, stability or bias claim by itself; for ``--data``, a measured bias (a purity versus
negweight-refined difference on data is method sensitivity).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
_2D = _ND.parent / "2d-unfolding"
for _p in (str(_ND),):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import s5c_pseudo  # noqa: E402
import s5c_unfold  # noqa: E402

TRUTHS = ("nominal", "eavail_shape", "q3_given_eavail_w")
AXIS = s5c_pseudo.AXIS
BKG_SPLIT_SALT = 0xB6D5E1A7C3F29041  # background split key = split_key ^ salt: independent of the signal split
DRIVER_CLASSIFIER_DEFAULTS = {"n_estimators": 100, "num_leaves": 8, "learning_rate": 0.1, "verbose": -1}
REFINE_SEED_OFFSET = 3  # the driver: random_state = seed + 3


# ----------------------------------------------------------------------------------------- truth


def eavail_ratio_weight(gen: np.ndarray, edges: list, w_truth: np.ndarray, ratio: dict,
                        amplitude: float) -> np.ndarray:
    """r = 1 + a (rho_k - 1) on truth rows inside the 5D grid, rho_k the declared per-E_avail-bin shape
    ratio between two fixed generator predictions; then one constant rescales the in-grid rows so the
    w_truth-weighted in-grid total is unchanged (a pure shape departure). Rows outside the grid,
    including -9999 sentinels, keep r = 1."""
    e = np.asarray(edges[AXIS["eavail"]], float)
    if not np.allclose(np.asarray(ratio["eavail_edges"], float), e):
        raise ValueError("the ratio's E_avail edges differ from the grid's")
    rho = np.asarray(ratio["shape_ratio"], float)
    if rho.size != e.size - 1 or np.any(rho <= 0):
        raise ValueError("shape_ratio needs one positive value per E_avail bin")
    ok = np.ones(gen.shape[0], bool)
    for k in range(gen.shape[1]):
        ek = np.asarray(edges[k], float)
        ok &= (gen[:, k] >= ek[0]) & (gen[:, k] <= ek[-1])
    ie = np.clip(np.searchsorted(e, gen[ok, AXIS["eavail"]], side="right") - 1, 0, e.size - 2)
    raw = 1.0 + amplitude * (rho[ie] - 1.0)
    if np.any(raw <= 0):
        raise ValueError("amplitude makes the reweight non-positive")
    w = np.asarray(w_truth, float)[ok]
    raw *= w.sum() / (w * raw).sum()
    r = np.ones(gen.shape[0])
    r[ok] = raw
    return r


def truth_weight(name: str, inputs: dict, amplitude: float, ratio: dict | None) -> np.ndarray:
    if name == "eavail_shape":
        if ratio is None:
            raise ValueError("eavail_shape needs --eavail-ratio")
        return eavail_ratio_weight(inputs["MCgen"], inputs["edges"], inputs["w_truth"], ratio, amplitude)
    return s5c_pseudo.truth_weight(name, inputs["MCgen"], inputs["edges"], amplitude, w_truth=inputs["w_truth"])


# ------------------------------------------------------------------------------------ experiments


def fid_mask(coords: np.ndarray, edges: list) -> np.ndarray:
    """The driver's _fid_mask: inside [first, last) edge on every axis."""
    m = np.ones(coords.shape[0], bool)
    for k, e in enumerate(edges):
        m &= (coords[:, k] >= e[0]) & (coords[:, k] < e[-1])
    return m


def bkg_split_key(split_key: int) -> int:
    return int(split_key) ^ BKG_SPLIT_SALT


def build_pseudo(inputs: dict, bkg: dict, truth: str, amplitude: float, split_key: int, pseudo_seed: int,
                 ratio: dict | None = None, no_background: bool = False,
                 prior_matches_truth: bool = False) -> tuple[dict, np.ndarray, dict]:
    """One negweight-refined repeated experiment before refinement: the observed rows with their counts,
    the template rows with their weights, the unfolding MC (half A), and the true cross section.

    ``prior_matches_truth`` (DEVELOPMENT DIAGNOSTIC): half A's w_truth and w_reco also carry r, so the
    unfolding prior IS the truth model. A correct pipeline then closes up to statistical noise; a
    departure residual that survives it is a construction defect, one that vanishes is prior dependence."""
    edges = inputs["edges"]
    n = inputs["MCgen"].shape[0]
    is_b = s5c_pseudo.half_mask(n, split_key)
    nb = bkg["bkg_w"].shape[0]
    is_c = s5c_pseudo.half_mask(nb, bkg_split_key(split_key))
    rng = np.random.default_rng(pseudo_seed)
    r = truth_weight(truth, inputs, amplitude, ratio)
    b_reco = is_b & inputs["pass_reco"]
    n_sig = rng.poisson(2.0 * inputs["w_reco"][b_reco] * r[b_reco]).astype(float)
    m_bkg = rng.poisson(2.0 * bkg["bkg_w"][is_c]).astype(float)
    if no_background:
        m_bkg[:] = 0.0
    obs = np.concatenate([inputs["MCreco"][b_reco][n_sig > 0], bkg["bkg_reco"][is_c][m_bkg > 0]])
    counts = np.concatenate([n_sig[n_sig > 0], m_bkg[m_bkg > 0]])
    keep = fid_mask(obs, edges)
    tmpl = bkg["bkg_reco"][~is_c]
    tmpl_w = 2.0 * bkg["bkg_w"][~is_c]
    tkeep = fid_mask(tmpl, edges)
    if no_background:
        tkeep[:] = False
    a = ~is_b
    ra = r[a] if prior_matches_truth else 1.0
    exp = {
        "MCgen": inputs["MCgen"][a], "MCreco": inputs["MCreco"][a],
        "pass_reco": inputs["pass_reco"][a], "pass_truth": inputs["pass_truth"][a],
        "w_truth": 2.0 * inputs["w_truth"][a] * ra, "w_reco": 2.0 * inputs["w_reco"][a] * ra,
        "obs": obs[keep], "obs_counts": counts[keep], "tmpl": tmpl[tkeep], "tmpl_w": tmpl_w[tkeep],
        "denom_nd": inputs["denom_nd"], "flux": inputs["flux"], "data_pot": inputs["data_pot"],
        "n_nucleons": inputs["n_nucleons"], "edges": edges,
    }
    x_true = true_xsec(inputs, is_b, r)
    info = {
        "n_half_a": int(a.sum()), "n_half_b": int(is_b.sum()), "n_bkg_source_c": int(is_c.sum()),
        "n_bkg_template_d": int((~is_c).sum()), "bkg_split_key": bkg_split_key(split_key),
        "pseudo_signal_events": float(n_sig.sum()), "pseudo_background_events": float(m_bkg.sum()),
        "expected_signal": float((2.0 * inputs["w_reco"][b_reco] * r[b_reco]).sum()),
        "expected_background_source": float(2.0 * bkg["bkg_w"][is_c].sum()),
        "template_weight_in_window": float(exp["tmpl_w"].sum()),
        "observed_events_outside_window": float(counts[~keep].sum()),
        "truth_reweight_mean_in_b": float(r[is_b & inputs["pass_truth"]].mean()),
    }
    return exp, x_true, info


def true_xsec(inputs: dict, is_b: np.ndarray, r: np.ndarray) -> np.ndarray:
    """B's reweighted truth through the analysis's extraction, exactly as s5c_pseudo.build_experiment."""
    from xsec_nd import extract_cross_section_nd

    edges = inputs["edges"]
    sel = is_b & inputs["pass_truth"]
    gen_b = inputs["MCgen"][sel]
    wt_b = 2.0 * inputs["w_truth"][sel]
    unf_b, _ = np.histogramdd(gen_b, bins=edges, weights=wt_b * r[sel])
    ofin_b, _ = np.histogramdd(gen_b, bins=edges, weights=wt_b)
    dn = inputs["denom_nd"]
    comp_b = np.zeros_like(ofin_b)
    nz = dn > 0
    comp_b[nz] = ofin_b[nz] / dn[nz]
    x_true, _ = extract_cross_section_nd(unf_b, comp_b, inputs["flux"], float(inputs["data_pot"]),
                                         float(inputs["n_nucleons"]), edges)
    return x_true


def build_data(inputs: dict, bkg: dict) -> dict:
    """The real data: every measured event in the window at count 1, the full background dump in the
    window as the template at its POT-scaled weight, the full MC at weight x1."""
    edges = inputs["edges"]
    obs = inputs["measured"]
    keep = fid_mask(obs, edges)
    tmpl = bkg["bkg_reco"]
    tkeep = fid_mask(tmpl, edges)
    return {
        "MCgen": inputs["MCgen"], "MCreco": inputs["MCreco"], "pass_reco": inputs["pass_reco"],
        "pass_truth": inputs["pass_truth"], "w_truth": inputs["w_truth"], "w_reco": inputs["w_reco"],
        "obs": obs[keep], "obs_counts": np.ones(int(keep.sum())), "tmpl": tmpl[tkeep],
        "tmpl_w": np.asarray(bkg["bkg_w"], float)[tkeep],
        "denom_nd": inputs["denom_nd"], "flux": inputs["flux"], "data_pot": inputs["data_pot"],
        "n_nucleons": inputs["n_nucleons"], "edges": edges,
    }


def bootstrap_replica(exp: dict, b: int) -> dict:
    """Contract sampling_model.statistical_sigma.per_replica: per-event Poisson(k) on observed rows,
    Poisson(1) on unfolding-MC rows and on template rows; the caller refits the refinement."""
    rng_d = np.random.default_rng(b)
    rng_m = np.random.default_rng(b + 10_000_000)  # bootstrap_nd.py's data/MC stream separation
    rng_t = np.random.default_rng(b + 20_000_000)
    rep = dict(exp)
    rep["obs_counts"] = rng_d.poisson(exp["obs_counts"]).astype(float)
    pm = rng_m.poisson(1.0, exp["w_truth"].shape[0]).astype(float)
    rep["w_truth"] = exp["w_truth"] * pm
    rep["w_reco"] = exp["w_reco"] * pm
    rep["tmpl_w"] = exp["tmpl_w"] * rng_t.poisson(1.0, exp["tmpl_w"].shape[0])
    return rep


def signed_sample(exp: dict) -> tuple[np.ndarray, np.ndarray, int, int]:
    """{observed at +count} U {template at -weight}, rows with zero weight dropped."""
    ok_o = exp["obs_counts"] > 0
    ok_t = exp["tmpl_w"] > 0
    feat = np.concatenate([exp["obs"][ok_o], exp["tmpl"][ok_t]]).astype(float)
    w = np.concatenate([exp["obs_counts"][ok_o], -exp["tmpl_w"][ok_t]])
    return feat, w, int(ok_o.sum()), int(ok_t.sum())


# ------------------------------------------------------------------------------------- refinement


def refine_params(estimator_seed: int, threads: int) -> dict:
    return {"random_state": int(estimator_seed) + REFINE_SEED_OFFSET,
            **s5c_unfold.config_params("deterministic", threads)}


@contextmanager
def recorded_classifier(u2d, record: list):
    """Record the parameters of every classifier refine_stay_positive builds."""
    original = u2d._make_bkg_classifier

    def factory(estimator, params, device):
        clf = original(estimator, params, device)
        record.append(clf.get_params())
        return clf

    u2d._make_bkg_classifier = factory
    try:
        yield
    finally:
        u2d._make_bkg_classifier = original


def load_u2d():
    if str(_2D) not in sys.path:
        sys.path.insert(0, str(_2D))
    import unfold_2d_omnifold_unbinned as u2d  # imports ROOT, as the driver does

    return u2d


def refine(feat: np.ndarray, signed_w: np.ndarray, estimator_seed: int, threads: int, refine_fn=None) -> tuple[np.ndarray, dict]:
    """The driver's refinement with the F2 parameters; returns refined weights and their evidence."""
    params = refine_params(estimator_seed, threads)
    record: list = []
    t0 = time.time()
    if refine_fn is None:
        u2d = load_u2d()
        with recorded_classifier(u2d, record):
            w_ref, g, frac = u2d.refine_stay_positive(feat, signed_w, estimator="lgbm", device="cpu",
                                                      params=params, verbose=False)
    else:  # unit tests: an injected refinement with the same signature
        w_ref, g, frac = refine_fn(feat, signed_w, params)
        record.append(dict(DRIVER_CLASSIFIER_DEFAULTS, **params))
    if len(record) != 1:
        raise RuntimeError(f"expected one refinement classifier, saw {len(record)}")
    for key, value in {**DRIVER_CLASSIFIER_DEFAULTS, **params}.items():
        if record[0].get(key) != value:
            raise RuntimeError(f"refinement classifier {key}={record[0].get(key)!r}, wanted {value!r}")
    return w_ref, refinement_evidence(signed_w, w_ref, g, frac, record[0], time.time() - t0)


def refinement_evidence(signed_w, w_ref, g, frac, params, seconds) -> dict:
    """Contract control C1: what the refinement did to this product's measured side."""
    pos, neg = signed_w > 0, signed_w < 0
    factor = 2.0 * g - 1.0
    clipped = factor < 0
    s = float(w_ref.sum())
    return {
        "ran": True,
        "n_positive": int(pos.sum()), "n_negative": int(neg.sum()),
        "sum_positive": float(signed_w[pos].sum()), "sum_negative": float(signed_w[neg].sum()),
        "signed_sum": float(signed_w.sum()), "refined_sum": s,
        "refined_over_signed": s / float(signed_w.sum()),
        "clipped_fraction": float(frac), "n_clipped": int(clipped.sum()),
        "clipped_signed_mass": float((np.abs(signed_w) * factor)[clipped].sum()),
        "refined_on_negative_rows": float(w_ref[neg].sum()),
        "g_min": float(g.min()), "g_max": float(g.max()),
        "n_eff_signed_abs": float(np.abs(signed_w).sum() ** 2 / np.square(signed_w).sum()),
        "n_eff_refined": float(s ** 2 / np.square(w_ref).sum()) if s > 0 else 0.0,
        "classifier_params": {k: params.get(k) for k in sorted(params) if k not in ("objective", "class_weight", "importance_type")},
        "seconds": round(seconds, 3),
    }


# ----------------------------------------------------------------------------------------- unfold


def unfold_negweight(exp: dict, estimator_seed: int, threads: int, iters: int, permute_seed: int | None = None,
                     refine_fn=None, unfold_fn=None) -> tuple[np.ndarray, dict]:
    feat, signed, n_obs, n_tmpl = signed_sample(exp)
    ev_extra = {"n_observed_rows": n_obs, "n_template_rows": n_tmpl}
    if n_tmpl == 0:  # signal-only reference (C8): nothing to subtract, nothing to refine
        w_ref, ev = signed.copy(), {"ran": False, "reason": "no negative weights (signal-only reference)"}
    else:
        order = None
        if permute_seed is not None:
            order = np.random.default_rng(permute_seed).permutation(feat.shape[0])
            feat, signed = feat[order], signed[order]
        w_ref, ev = refine(feat, signed, estimator_seed, threads, refine_fn)
    ev.update(ev_extra)
    unf_in = {k: exp[k] for k in ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco",
                                  "denom_nd", "flux", "data_pot", "n_nucleons", "edges")}
    unf_in["measured"] = feat.astype(np.float32)
    unf_in["measured_weights"] = w_ref
    if permute_seed is not None:
        unf_in = s5c_unfold.permute(unf_in, permute_seed + 1)
    xs, params = (unfold_fn or s5c_unfold.unfold)(unf_in, "deterministic", estimator_seed, threads, iters)
    return xs, {"refinement": ev, "estimator_params": params}


# --------------------------------------------------------------------------------------------- io


def sha256_path(path: Path) -> str:
    return s5c_unfold.sha256_path(path)


def code_digests() -> dict:
    files = [Path(__file__).resolve(), _ND / "s5c_pseudo.py", _ND / "s5c_unfold.py", _ND / "omnifold_nn_core.py",
             _ND / "xsec_nd.py", _2D / "unfold_2d_omnifold_unbinned.py"]
    return {f.name: sha256_path(f) for f in files}


def write_product(out: Path, arrays: dict, meta: dict) -> int:
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.name + f".partial-{os.getpid()}.npz")
    np.savez_compressed(tmp, **arrays, meta=json.dumps(meta, default=str))
    if out.exists():  # another process finished first: keep the first product
        tmp.unlink()
        return 3
    os.replace(tmp, out)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--bkg", type=Path, required=True)
    ap.add_argument("--expect-npz-sha256", required=True)
    ap.add_argument("--expect-bkg-sha256", required=True)
    ap.add_argument("--bkg-mode", choices=("negweight-refined", "purity"), required=True)
    ap.add_argument("--estimator-seed", type=int, default=42)
    ap.add_argument("--truth", choices=TRUTHS, default="nominal")
    ap.add_argument("--amplitude", type=float, default=0.0)
    ap.add_argument("--eavail-ratio", type=Path, default=None, help="committed per-E_avail-bin shape ratio (eavail_shape)")
    ap.add_argument("--data", action="store_true", help="the real data instead of a repeated experiment")
    ap.add_argument("--pseudo-seed", type=int, default=None)
    ap.add_argument("--pseudo-seeds", default=None, help="first:last; one product per seed, split key from the seed")
    ap.add_argument("--split-key", type=int, default=None, help="purity baseline only (reproduces an s5c product)")
    ap.add_argument("--bootstrap-seeds", default=None, help="first:last replicas of ONE experiment or of --data")
    ap.add_argument("--no-background", action="store_true", help="DEVELOPMENT REFERENCE (C8) only")
    ap.add_argument("--permute-seed", type=int, default=None, help="row-order probe (C2c)")
    ap.add_argument("--prior-matches-truth", action="store_true",
                    help="DEVELOPMENT DIAGNOSTIC: the unfolding MC carries the truth reweight (defect vs prior dependence)")
    ap.add_argument("--threads", type=int, default=int(os.environ.get("SLURM_CPUS_PER_TASK", "32")))
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    many = a.pseudo_seeds is not None or a.bootstrap_seeds is not None
    if sum(x is not None for x in (a.pseudo_seed, a.pseudo_seeds)) + int(a.data) != 1:
        print("give exactly one of --data, --pseudo-seed, --pseudo-seeds", file=sys.stderr)
        return 2
    if a.pseudo_seeds and a.bootstrap_seeds:
        print("a bootstrap takes one experiment", file=sys.stderr)
        return 2
    if a.bkg_mode == "purity" and (a.bootstrap_seeds or a.no_background or a.permute_seed is not None
                                   or (a.pseudo_seed is not None and a.split_key is None)):
        print("purity is the baseline: --data, or --pseudo-seed with --split-key (an s5c product)", file=sys.stderr)
        return 2
    if a.no_background and (a.data or many):
        print("--no-background is a single-experiment development reference", file=sys.stderr)
        return 2
    if not many and a.out.exists():
        print(f"refusing to overwrite {a.out}", file=sys.stderr)
        return 3
    t0 = time.time()
    npz_sha, bkg_sha = sha256_path(a.npz), sha256_path(a.bkg)
    if npz_sha != a.expect_npz_sha256 or bkg_sha != a.expect_bkg_sha256:
        print(f"input digests {npz_sha} / {bkg_sha} differ from the expected ones", file=sys.stderr)
        return 4
    inputs = s5c_unfold.load_inputs(a.npz)
    bz = np.load(a.bkg, allow_pickle=True)
    bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
    if json.loads(str(bz["meta"]))["npz_sha256"] != npz_sha:
        print("refusing: background dump was made against a different npz", file=sys.stderr)
        return 4
    ratio, ratio_sha = None, None
    if a.eavail_ratio is not None:
        ratio, ratio_sha = json.loads(a.eavail_ratio.read_text()), sha256_path(a.eavail_ratio)
    base_meta = {"schema": "s5n-unfold/1", "bkg_mode": a.bkg_mode, "config": "deterministic",
                 "estimator_seed": a.estimator_seed, "threads": a.threads, "iters": a.iters,
                 "input_npz_sha256": npz_sha, "bkg_dump_sha256": bkg_sha, "eavail_ratio_sha256": ratio_sha,
                 "code_sha256": code_digests(), "slurm_job": os.environ.get("SLURM_JOB_ID"),
                 "slurm_step": os.environ.get("SLURM_STEP_ID"), "seconds_load": round(time.time() - t0, 3)}

    def one(exp, x_true, info, out, extra) -> int:
        t1 = time.time()
        if a.bkg_mode == "purity":
            xs, params = s5c_unfold.unfold(exp, "deterministic", a.estimator_seed, a.threads, a.iters)
            ev = {"estimator_params": params, "refinement": {"ran": False, "reason": "purity baseline"}}
        else:
            xs, ev = unfold_negweight(exp, a.estimator_seed, a.threads, a.iters, a.permute_seed)
        meta = dict(base_meta, **extra, experiment=info, **ev, seconds_unfold=round(time.time() - t1, 3))
        arrays = {"xsec_flat": xs.ravel(order="C"), "shape": np.array(xs.shape)}
        if x_true is not None:
            arrays["xtrue_flat"] = x_true.ravel(order="C")
        rc = write_product(out, arrays, meta)
        print(json.dumps({"out": out.name, "rc": rc, "seconds_unfold": meta["seconds_unfold"],
                          "refined_over_signed": ev["refinement"].get("refined_over_signed"),
                          "clipped_fraction": ev["refinement"].get("clipped_fraction")}))
        return rc

    def experiment(seed, split_key):
        if a.bkg_mode == "purity":
            return s5c_pseudo.build_experiment(inputs, bkg, a.truth, a.amplitude, split_key, seed)
        return build_pseudo(inputs, bkg, a.truth, a.amplitude, split_key, seed, ratio, a.no_background,
                            a.prior_matches_truth)

    truth_meta = {"truth": a.truth, "amplitude": a.amplitude, "no_background": a.no_background,
                  "prior_matches_truth": a.prior_matches_truth,
                  "permute_seed": a.permute_seed}
    if a.data:
        if a.bkg_mode == "purity":
            exp, info = dict(inputs), {"measured_weight_sum": float(inputs["measured_weights"].sum())}
        else:
            exp = build_data(inputs, bkg)
            info = {"n_observed": int(exp["obs"].shape[0]), "n_template": int(exp["tmpl"].shape[0]),
                    "template_weight": float(exp["tmpl_w"].sum())}
        if a.bootstrap_seeds is None:
            return one(exp, None, info, a.out, {"data": True})
        return bootstraps(a, exp, None, info, one, {"data": True})
    if a.pseudo_seed is not None:
        split_key = a.split_key if a.split_key is not None else s5c_pseudo.split_key_for(a.pseudo_seed)
        exp, x_true, info = experiment(a.pseudo_seed, split_key)
        extra = dict(truth_meta, pseudo_seed=a.pseudo_seed, split_key=split_key)
        if a.bootstrap_seeds is None:
            return one(exp, x_true, info, a.out, extra)
        return bootstraps(a, exp, x_true, info, one, extra)
    first, last = (int(v) for v in a.pseudo_seeds.split(":"))
    a.out.mkdir(parents=True, exist_ok=True)
    status = 0
    for seed in range(first, last + 1):
        target = a.out / f"{a.truth}_a{a.amplitude:g}_s{seed}.npz"
        if target.exists():
            continue
        split_key = s5c_pseudo.split_key_for(seed)
        exp, x_true, info = experiment(seed, split_key)
        status |= one(exp, x_true, info, target, dict(truth_meta, pseudo_seed=seed, split_key=split_key))
    return status


def bootstraps(a, exp, x_true, info, one, extra) -> int:
    first, last = (int(v) for v in a.bootstrap_seeds.split(":"))
    a.out.mkdir(parents=True, exist_ok=True)
    status = 0
    for b in range(first, last + 1):
        target = a.out / f"boot_b{b}.npz"
        if target.exists():
            continue
        status |= one(bootstrap_replica(exp, b), x_true, info, target, dict(extra, bootstrap_seed=b))
    return status


if __name__ == "__main__":
    sys.exit(main())
