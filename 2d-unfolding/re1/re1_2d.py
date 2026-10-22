#!/usr/bin/env python3
"""RE-1 2D path: the adopted 2D estimator with purity subtraction or with the Stay-Positive refinement
at 400 trees / 31 leaves, on the real data or on background-inclusive pseudo-experiments.

Authority: ``docs/orchestration/state/2d-closeout/stageF/methods/RE1-SPEC.md`` (C2) and its amendment
declaration ``docs/orchestration/state/2d-closeout/stageF/methods/re1/RE1-AMENDMENT-DECLARATION.md``.

    re1_2d.py dump   --omnifile F --mcfile M --expect-omnifile-sha256 S --expect-mcfile-sha256 S --out C.npz
    re1_2d.py data   --cache C.npz --expect-cache-sha256 S --arm purity|refined --out X.npz
    re1_2d.py pseudo --cache C.npz --expect-cache-sha256 S --pseudo-seeds FIRST:LAST --out DIR

Nothing in the frozen driver ``2d-unfolding/unfold_2d_omnifold_unbinned.py`` is edited or re-implemented.
Its loaders, purity weights, refinement, completeness and cross-section extraction are called as module
functions, and the unfold is the driver's own ``OmniFold_helper_functions.omnifold`` call with the
driver's arguments (``unfold_2d_omnifold_unbinned.py:2080-2097``):

* the estimator: LightGBM, 100 trees, 8 leaves, learning rate 0.1, ``random_state`` 42/43/44 for the
  step-1 classifier, step-2 classifier and step-1 regressor (``--seed 42``), five iterations, MC event
  weights; the adopted ``E_U`` launcher ``sbatch_unfold_2d_MEFHC_5iter_universes_full_CV.sh``.
* ``purity``: ``build_measured_training_2d``, the per-reco-bin ``max(0, (D - B) / D)`` down-weight.
* ``refined``: the signed sample {observed at +count} U {background template at -weight}, refined by
  ``refine_stay_positive`` with an LGBMClassifier at ``random_state`` 45 (the driver's seed + 3),
  ``n_estimators`` 400 and ``num_leaves`` 31; everything else at the driver's classifier defaults.
  This is the only setting the driver cannot reach: it passes ``random_state`` alone
  (``unfold_2d_omnifold_unbinned.py:2037-2042``).

``dump`` reads the omnifile once with the driver's loaders, exactly as ``main()`` does, and caches the
arrays, so the many unfolds of ``pseudo`` need no ROOT tree reads. ``data`` on the purity arm is the K1
control: it must regenerate ``E_U``'s ``hXSec2D``.

Pseudo-experiment sampling, the s5n model (``nd-unfolding/s5n_pseudo.py`` ``build_pseudo``), in 2D:

* signal MC rows split by the keyed hash ``s5c_pseudo.half_mask`` into A (unfolding MC, weights x2)
  and B (pseudo-data source); background MC rows split by an independent key into C (pseudo-data
  source) and D (background template, weights x2). The keys come from the seed
  (``s5c_pseudo.split_key_for``, ``s5n_pseudo.bkg_split_key``).
* pseudo-data: ``n_i ~ Poisson(2 w_reco_i)`` per reco-passing B row and ``m_j ~ Poisson(2 w_bkg_j)``
  per C row, at nominal truth (no reweight).
* BOTH ARMS UNFOLD THE SAME PSEUDO-DATA against the same template D: purity takes D's histogram as the
  background prediction, the refinement takes D's rows at negative weight. The arm difference is
  therefore paired, and it isolates the background treatment.
* truth: B's truth through the analysis's own extraction (``s5n_pseudo.true_xsec``'s definition).

MEASURES: one 2D unfold per arm with its refinement evidence. CANNOT AUTHORIZE: a coverage, bias or
validation claim by itself, or any change to the adopted 2D result (Joseph's decision).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
_2D = _REPO / "2d-unfolding"
_ND = _REPO / "nd-unfolding"
_OF_PY = _REPO / "unbinned_unfolding" / "python"

SCHEMA_CACHE = "re1-2d-cache/1"
SCHEMA_PRODUCT = "re1-2d-unfold/1"
ARMS = ("purity", "refined")
ESTIMATOR_SEED = 42                       # the adopted E_U launcher's --seed
ITERS = 5
OMNIFOLD_SEED_OFFSETS = (0, 1, 2)         # driver: step1 = seed, step2 = seed + 1, regressor = seed + 2
REFINE_SEED_OFFSET = 3                    # driver: refinement random_state = seed + 3
REFINE_OVERRIDE = {"n_estimators": 400, "num_leaves": 31}
LGBM_DEFAULTS = {"n_estimators": 100, "num_leaves": 8, "learning_rate": 0.1, "verbose": -1}
FLUX_HIST = "pTmu_reweightedflux_integrated"
SIG_KEYS = ("truth_pt", "truth_pz", "reco_pt", "reco_pz", "pass_reco", "pass_truth", "w_truth", "w_reco")


def sha256_path(path: Path, chunk: int = 1 << 24) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                return h.hexdigest()
            h.update(block)


def load_modules():
    """The frozen driver and the OmniFold helper, both from THIS checkout.

    The driver's main() inserts a hard-coded cluster path for the helper (OI-136); it is never called
    here, so this checkout's helper is the one imported, and its origin is recorded and checked."""
    for p in (str(_OF_PY), str(_2D), str(_ND)):
        if p not in sys.path:
            sys.path.insert(0, p)
    import unfold_2d_omnifold_unbinned as u2d  # imports ROOT, as the driver does
    from omnifold import OmniFold_helper_functions as ohf
    helper = Path(sys.modules["omnifold"].__file__).resolve()
    if helper != (_OF_PY / "omnifold.py").resolve() or Path(u2d.__file__).resolve() != (_2D / "unfold_2d_omnifold_unbinned.py").resolve():
        raise RuntimeError(f"imported {helper} / {u2d.__file__}, not this checkout's modules")
    return u2d, ohf


def code_digests() -> dict:
    files = [Path(__file__).resolve(), _2D / "unfold_2d_omnifold_unbinned.py", _OF_PY / "omnifold.py",
             _ND / "s5c_pseudo.py", _ND / "s5n_pseudo.py"]
    return {f.name: sha256_path(f) for f in files}


def nd_modules():
    """The s5c/s5n sampling modules, from this checkout (numpy-only at import)."""
    if str(_ND) not in sys.path:
        sys.path.insert(0, str(_ND))
    import s5c_pseudo
    import s5n_pseudo
    return s5c_pseudo, s5n_pseudo


def split_keys(seed: int) -> tuple[int, int]:
    """The s5n keys: the signal split from the seed, the background split from an independent salt."""
    s5c_pseudo, s5n_pseudo = nd_modules()
    key = s5c_pseudo.split_key_for(seed)
    return key, s5n_pseudo.bkg_split_key(key)


# ------------------------------------------------------------------------------------------- dump


def dump(omnifile: Path, mcfile: Path, branch_select: str = "derived") -> tuple[dict, dict]:
    """Every array main() builds before the unfold, read with the driver's own loaders and arguments
    (``unfold_2d_omnifold_unbinned.py:1630-1790``, ``--use-weights``, no universe, no closure)."""
    u2d, _ = load_modules()
    ROOT = u2d.ROOT
    pt_edges, pz_edges = u2d.PT_EDGES, u2d.PZ_EDGES
    pt_lo, pt_hi, pz_lo, pz_hi = pt_edges[0], pt_edges[-1], pz_edges[0], pz_edges[-1]
    f_in = ROOT.TFile.Open(str(omnifile), "READ")
    if not f_in or f_in.IsZombie():
        raise RuntimeError(f"could not open {omnifile}")
    t_sig, t_bkg, t_data, t_den = (f_in.Get(n) for n in ("mc_signal_reco", "mc_background", "data", "mc_truth_denom"))
    if not (t_sig and t_bkg and t_data and t_den):
        raise RuntimeError("missing a required TTree")
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f_in)
    p_misses = f_in.Get("hasTruthOnlyMisses")
    has_misses = bool(int(p_misses.GetVal())) if p_misses else False
    flux_bins, _ = u2d.load_flux_bins(str(mcfile), FLUX_HIST, pt_edges)
    h_data = u2d.make_th2d("hDataReco2D", "Data reco", pt_edges, pz_edges)
    h_bkg = u2d.make_th2d("hBkgReco2D", "Background reco (POT-scaled)", pt_edges, pz_edges)
    log: list = []
    sel = {"branch_select": branch_select, "selection_log": log}
    meas_pt, meas_pz = u2d.call_loader(u2d.fill_data_reco_2d, t_data, h_data, pt_lo, pt_hi, pz_lo, pz_hi, **sel)
    bkg_pt, bkg_pz, bkg_w = u2d.call_loader(u2d.fill_bkg_reco_2d, t_bkg, h_bkg, pot_scale, pt_lo=pt_lo,
                                            pt_hi=pt_hi, pz_lo=pz_lo, pz_hi=pz_hi, universe_branch=None, **sel)
    sig = u2d.call_loader(u2d.collect_signal_arrays_2d, t_sig, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale,
                          use_weights=True, universe_branch=None, alt_universe_branch=None, **sel)
    den = u2d.call_loader(u2d.collect_truth_denom_arrays, t_den, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale,
                          use_weights=True, universe_branch=None, **sel)
    n_fakes = int((sig["pass_reco"] & ~sig["pass_truth"]).sum())
    if n_fakes:  # post-Phase-18 omnifiles carry the fakes in mc_background (driver :1795-1806)
        raise RuntimeError(f"{n_fakes} signal fakes: this path supports post-Phase-18 inputs only")
    arrays = {f"sig_{k}": np.asarray(sig[k]) for k in SIG_KEYS}
    arrays.update(meas_pt=meas_pt, meas_pz=meas_pz, bkg_pt=bkg_pt, bkg_pz=bkg_pz, bkg_w=bkg_w,
                  den_pt=den["truth_pt"], den_pz=den["truth_pz"], den_w=den["w_truth"],
                  flux_bins=np.asarray(flux_bins, float), h_data_driver=th2_array(h_data),
                  h_bkg_driver=th2_array(h_bkg))
    meta = {"data_pot": data_pot, "mc_pot": mc_pot, "pot_scale": pot_scale, "has_truth_only_misses": has_misses,
            "n_nucleons": u2d.TRACKER_FIDUCIAL_N_NUCLEONS, "pt_edges": list(pt_edges), "pz_edges": list(pz_edges),
            "branch_select": branch_select, "selection_log": log, "n_fakes": n_fakes}
    return arrays, meta


def th2_array(h) -> np.ndarray:
    """All bin contents including under- and overflow, indexed [ix, iy]."""
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    return np.array([[h.GetBinContent(ix, iy) for iy in range(ny + 2)] for ix in range(nx + 2)])


def load_cache(path: Path) -> tuple[dict, dict]:
    d = np.load(path, allow_pickle=False)
    meta = json.loads(str(d["meta"]))
    if meta.get("schema") != SCHEMA_CACHE:
        raise RuntimeError(f"{path} is not an {SCHEMA_CACHE} cache")
    return {k: d[k] for k in d.files if k != "meta"}, meta


# ------------------------------------------------------------------------------------- experiments


def sig_dict(c: dict, rows: np.ndarray | slice, wscale: float = 1.0) -> dict:
    s = {k: c[f"sig_{k}"][rows] for k in SIG_KEYS}
    s["w_truth"] = wscale * s["w_truth"]
    s["w_reco"] = wscale * s["w_reco"]
    return s


def build_data(c: dict) -> dict:
    """The real data at count 1 against the full background MC and the full signal MC (weights x1)."""
    return {"sig": sig_dict(c, slice(None)), "obs_pt": c["meas_pt"], "obs_pz": c["meas_pz"],
            "obs_counts": np.ones(c["meas_pt"].shape[0]), "tmpl_pt": c["bkg_pt"], "tmpl_pz": c["bkg_pz"],
            "tmpl_w": c["bkg_w"], "truth_sig": None, "info": {"data": True}}


def build_pseudo(c: dict, seed: int) -> dict:
    """One s5n repeated experiment in 2D at nominal truth (``s5n_pseudo.build_pseudo``, r = 1)."""
    key, bkey = split_keys(seed)
    n, nb = c["sig_w_truth"].shape[0], c["bkg_w"].shape[0]
    half_mask = nd_modules()[0].half_mask
    is_b, is_c = half_mask(n, key), half_mask(nb, bkey)
    rng = np.random.default_rng(seed)
    b_reco = is_b & c["sig_pass_reco"]
    n_sig = rng.poisson(2.0 * c["sig_w_reco"][b_reco]).astype(float)
    m_bkg = rng.poisson(2.0 * c["bkg_w"][is_c]).astype(float)
    obs_pt = np.concatenate([c["sig_reco_pt"][b_reco][n_sig > 0], c["bkg_pt"][is_c][m_bkg > 0]])
    obs_pz = np.concatenate([c["sig_reco_pz"][b_reco][n_sig > 0], c["bkg_pz"][is_c][m_bkg > 0]])
    counts = np.concatenate([n_sig[n_sig > 0], m_bkg[m_bkg > 0]])
    d = ~is_c
    info = {"seed": seed, "split_key": key, "bkg_split_key": bkey, "n_half_a": int((~is_b).sum()),
            "n_half_b": int(is_b.sum()), "n_bkg_source_c": int(is_c.sum()), "n_bkg_template_d": int(d.sum()),
            "pseudo_signal_events": float(n_sig.sum()), "pseudo_background_events": float(m_bkg.sum()),
            "expected_signal": float(2.0 * c["sig_w_reco"][b_reco].sum()),
            "expected_background_source": float(2.0 * c["bkg_w"][is_c].sum()),
            "template_weight": float(2.0 * c["bkg_w"][d].sum())}
    return {"sig": sig_dict(c, ~is_b, 2.0), "obs_pt": obs_pt, "obs_pz": obs_pz, "obs_counts": counts,
            "tmpl_pt": c["bkg_pt"][d], "tmpl_pz": c["bkg_pz"][d], "tmpl_w": 2.0 * c["bkg_w"][d],
            "truth_sig": sig_dict(c, is_b, 2.0), "info": info}


def purity_measured(u2d, exp: dict, edges) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """Purity: the driver's per-bin down-weight on histograms of the observed counts and the template;
    each observed row carries count x (max(0, D - B) / D) for its bin (``s5c_pseudo.purity_weights``)."""
    h_d = u2d.make_th2d("hDataReco2D", "Data reco", *edges)
    h_b = u2d.make_th2d("hBkgReco2D", "Background reco", *edges)
    for pt, pz, k in zip(exp["obs_pt"], exp["obs_pz"], exp["obs_counts"]):
        h_d.Fill(float(pt), float(pz), float(k))
    for pt, pz, w in zip(exp["tmpl_pt"], exp["tmpl_pz"], exp["tmpl_w"]):
        h_b.Fill(float(pt), float(pz), float(w))
    ratio, _ = u2d.build_measured_training_2d(exp["obs_pt"], exp["obs_pz"], h_d, h_b)
    w = exp["obs_counts"] * ratio
    return exp["obs_pt"], exp["obs_pz"], w, {"ran": False, "reason": "purity", "h_data": th2_array(h_d),
                                              "h_bkg": th2_array(h_b), "measured_sum": float(w.sum())}


def signed_sample(exp: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """{observed at +count} U {template at -weight}, in that order and with every row, as the driver
    builds it (``unfold_2d_omnifold_unbinned.py:2030-2035``). Unlike ``s5n_pseudo.signed_sample``, a
    zero-weight template row is kept, so on the real data this is the driver's sample exactly."""
    pt = np.concatenate([exp["obs_pt"], exp["tmpl_pt"]]).astype(float)
    pz = np.concatenate([exp["obs_pz"], exp["tmpl_pz"]]).astype(float)
    w = np.concatenate([exp["obs_counts"], -exp["tmpl_w"]])
    return pt, pz, w


def refine_params(estimator_seed: int) -> dict:
    return {"random_state": int(estimator_seed) + REFINE_SEED_OFFSET, **REFINE_OVERRIDE}


@contextmanager
def recorded_classifier(u2d, record: list):
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


def refined_measured(u2d, exp: dict, estimator_seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    pt, pz, signed = signed_sample(exp)
    params = refine_params(estimator_seed)
    record: list = []
    t0 = time.time()
    with recorded_classifier(u2d, record):
        w_ref, g, frac = u2d.refine_stay_positive(np.column_stack([pt, pz]), signed, estimator="lgbm",
                                                  device="cpu", params=params, verbose=False)
    if len(record) != 1:
        raise RuntimeError(f"expected one refinement classifier, saw {len(record)}")
    for key, value in {**LGBM_DEFAULTS, **params}.items():
        if record[0].get(key) != value:
            raise RuntimeError(f"refinement classifier {key}={record[0].get(key)!r}, wanted {value!r}")
    return pt, pz, w_ref, refinement_evidence(signed, w_ref, g, frac, record[0], time.time() - t0)


def refinement_evidence(signed_w, w_ref, g, frac, params, seconds) -> dict:
    return nd_modules()[1].refinement_evidence(signed_w, w_ref, g, frac, params, seconds)


@contextmanager
def recorded_lgbm(record: list):
    """Record the parameters of every LightGBM estimator the OmniFold helper fits (it imports the
    classes at call time from the lightgbm module, so the fit methods are wrapped there)."""
    import lightgbm
    originals = {cls: cls.fit for cls in (lightgbm.LGBMClassifier, lightgbm.LGBMRegressor)}

    def wrap(cls, fit):
        def recorded_fit(self, *args, **kwargs):
            record.append({"class": cls.__name__, **self.get_params()})
            return fit(self, *args, **kwargs)
        return recorded_fit

    for cls, fit in originals.items():
        cls.fit = wrap(cls, fit)
    try:
        yield
    finally:
        for cls, fit in originals.items():
            cls.fit = fit


def check_omnifold_fits(record: list, estimator_seed: int, iters: int) -> dict:
    """Every fit carries the driver's parameters: 2 classifiers x iters and <= 1 regressor x iters."""
    seeds = {estimator_seed + o for o in OMNIFOLD_SEED_OFFSETS}
    for p in record:
        if p.get("random_state") not in seeds:
            raise RuntimeError(f"omnifold fit random_state {p.get('random_state')!r} not in {sorted(seeds)}")
        for key, value in LGBM_DEFAULTS.items():
            if p.get(key) != value:
                raise RuntimeError(f"omnifold fit {key}={p.get(key)!r}, wanted {value!r}")
    n_clf = sum(p["class"] == "LGBMClassifier" for p in record)
    n_reg = sum(p["class"] == "LGBMRegressor" for p in record)
    if n_clf != 2 * iters or n_reg not in (0, iters):
        raise RuntimeError(f"omnifold fits: {n_clf} classifier, {n_reg} regressor (iters {iters})")
    return {"n_classifier_fits": n_clf, "n_regressor_fits": n_reg,
            "random_states": sorted({p["random_state"] for p in record})}


def unfold(u2d, ohf, sig: dict, mpt, mpz, mw, estimator_seed: int, iters: int) -> tuple[np.ndarray, dict]:
    """The driver's omnifold call (``unfold_2d_omnifold_unbinned.py:2080-2097``, ``--use-weights``)."""
    s = estimator_seed
    record: list = []
    with recorded_lgbm(record):
        _, step2 = ohf.omnifold(
            np.column_stack([sig["truth_pt"], sig["truth_pz"]]), np.column_stack([sig["reco_pt"], sig["reco_pz"]]),
            np.column_stack([mpt, mpz]), sig["pass_reco"], sig["pass_truth"], np.ones(mpt.shape[0], dtype=bool),
            int(iters), MCgen_weights=sig["w_truth"], MCreco_weights=sig["w_reco"], measured_weights=mw,
            classifier1_params={"random_state": s}, classifier2_params={"random_state": s + 1},
            regressor_params={"random_state": s + 2}, parameter_format="dict", estimator="lgbm", device="cpu")
    return step2, check_omnifold_fits(record, s, iters)


def xsec(u2d, sig: dict, step2: np.ndarray | None, c: dict, meta: dict) -> np.ndarray:
    """hXSec2D [ix, iy] (14 x 16): hUnfold2D from the truth-passing rows (step2 x w_truth; step2 None =
    the truth itself), divided by the completeness of ``sig`` against the full truth denominator."""
    edges = (meta["pt_edges"], meta["pz_edges"])
    m = sig["pass_truth"]
    tpt, tpz, tw = sig["truth_pt"][m], sig["truth_pz"][m], sig["w_truth"][m]
    if step2 is not None and step2.shape[0] != tpt.shape[0]:
        raise RuntimeError(f"weight size mismatch: truth {tpt.shape[0]}, step2 {step2.shape[0]}")
    h_u = u2d.make_th2d("hUnfold2D", "Unfolded (2D OmniFold)", *edges)
    ratio = np.ones(tpt.shape[0]) if step2 is None else step2
    for pt, pz, r, w in zip(tpt, tpz, ratio, tw):
        h_u.Fill(float(pt), float(pz), float(r) * float(w))
    den = {"truth_pt": c["den_pt"], "truth_pz": c["den_pz"], "w_truth": c["den_w"]}
    h_c, _, _ = u2d.compute_omnifold_completeness_2d(sig, *edges, den)
    h_x = u2d.extract_cross_section_2d(h_u, h_c, c["flux_bins"], meta["data_pot"], meta["n_nucleons"], *edges)
    return th2_array(h_x)[1:-1, 1:-1]


def run_arm(u2d, ohf, exp: dict, arm: str, c: dict, meta: dict, iters: int) -> tuple[np.ndarray, dict]:
    edges = (meta["pt_edges"], meta["pz_edges"])
    t0 = time.time()
    if arm == "purity":
        mpt, mpz, mw, ev = purity_measured(u2d, exp, edges)
        ev = {k: v for k, v in ev.items() if k not in ("h_data", "h_bkg")}
    else:
        mpt, mpz, mw, ev = refined_measured(u2d, exp, ESTIMATOR_SEED)
    step2, fits = unfold(u2d, ohf, exp["sig"], mpt, mpz, mw, ESTIMATOR_SEED, iters)
    x = xsec(u2d, exp["sig"], step2, c, meta)
    return x, {"arm": arm, "refinement": ev, "omnifold_fits": fits, "n_measured_rows": int(mpt.shape[0]),
               "measured_weight_sum": float(np.sum(mw)), "seconds": round(time.time() - t0, 3)}


# --------------------------------------------------------------------------------------------- io


def write_product(out: Path, arrays: dict, meta: dict) -> int:
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.name + f".partial-{os.getpid()}.npz")
    np.savez_compressed(tmp, **arrays, meta=json.dumps(meta, default=str, sort_keys=True))
    if out.exists():  # another process finished first: keep the first product, never overwrite
        tmp.unlink()
        return 3
    os.replace(tmp, out)
    return 0


def environment() -> dict:
    import lightgbm
    return {"python": platform.python_version(), "numpy": np.__version__, "lightgbm": lightgbm.__version__,
            "host": platform.node(), "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
            "slurm_job": os.environ.get("SLURM_JOB_ID"), "slurm_step": os.environ.get("SLURM_STEP_ID")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dump")
    d.add_argument("--omnifile", type=Path, required=True)
    d.add_argument("--mcfile", type=Path, required=True)
    d.add_argument("--expect-omnifile-sha256", required=True)
    d.add_argument("--expect-mcfile-sha256", required=True)
    d.add_argument("--branch-select", choices=("all", "derived"), default="derived")
    d.add_argument("--out", type=Path, required=True)
    for name in ("data", "pseudo"):
        p = sub.add_parser(name)
        p.add_argument("--cache", type=Path, required=True)
        p.add_argument("--expect-cache-sha256", required=True)
        p.add_argument("--iters", type=int, default=ITERS)
        p.add_argument("--out", type=Path, required=True)
    sub.choices["data"].add_argument("--arm", choices=ARMS, required=True)
    sub.choices["pseudo"].add_argument("--pseudo-seeds", required=True, help="FIRST:LAST inclusive")
    a = ap.parse_args(argv)

    if a.cmd == "dump":
        if a.out.exists():
            print(f"refusing to overwrite {a.out}", file=sys.stderr)
            return 3
        got = (sha256_path(a.omnifile), sha256_path(a.mcfile))
        if got != (a.expect_omnifile_sha256, a.expect_mcfile_sha256):
            print(f"input digests {got} differ from the expected ones", file=sys.stderr)
            return 4
        t0 = time.time()
        arrays, meta = dump(a.omnifile, a.mcfile, a.branch_select)
        meta.update(schema=SCHEMA_CACHE, omnifile=str(a.omnifile), omnifile_sha256=got[0], mcfile=str(a.mcfile),
                    mcfile_sha256=got[1], code_sha256=code_digests(), environment=environment(),
                    seconds=round(time.time() - t0, 3))
        return write_product(a.out, arrays, meta)

    cache_sha = sha256_path(a.cache)
    if cache_sha != a.expect_cache_sha256:
        print(f"cache sha256 {cache_sha} != {a.expect_cache_sha256}", file=sys.stderr)
        return 4
    c, cmeta = load_cache(a.cache)
    u2d, ohf = load_modules()
    base = {"schema": SCHEMA_PRODUCT, "cache_sha256": cache_sha, "omnifile_sha256": cmeta["omnifile_sha256"],
            "estimator_seed": ESTIMATOR_SEED, "iters": a.iters, "refine_params": refine_params(ESTIMATOR_SEED),
            "code_sha256": code_digests(), "environment": environment()}
    if a.cmd == "data":
        if a.out.exists():
            print(f"refusing to overwrite {a.out}", file=sys.stderr)
            return 3
        exp = build_data(c)
        x, ev = run_arm(u2d, ohf, exp, a.arm, c, cmeta, a.iters)
        rc = write_product(a.out, {"xsec": x}, dict(base, data=True, **ev))
        print(json.dumps({"out": a.out.name, "rc": rc, "arm": a.arm, "seconds": ev["seconds"]}))
        return rc
    first, last = (int(v) for v in a.pseudo_seeds.split(":"))
    a.out.mkdir(parents=True, exist_ok=True)
    status = 0
    for seed in range(first, last + 1):
        target = a.out / f"nominal_s{seed}.npz"
        if target.exists():
            continue
        t0 = time.time()
        exp = build_pseudo(c, seed)
        x_true = xsec(u2d, exp["truth_sig"], None, c, cmeta)
        arrays, evs = {"xtrue": x_true}, {}
        for arm in ARMS:  # the same pseudo-data in both arms
            arrays[f"xsec_{arm}"], evs[arm] = run_arm(u2d, ohf, exp, arm, c, cmeta, a.iters)
        rc = write_product(target, arrays, dict(base, pseudo_seed=seed, experiment=exp["info"], arms=evs,
                                                seconds=round(time.time() - t0, 3)))
        status |= rc
        print(json.dumps({"out": target.name, "rc": rc, "seconds": round(time.time() - t0, 3),
                          "refined_over_signed": evs["refined"]["refinement"].get("refined_over_signed"),
                          "clipped_fraction": evs["refined"]["refinement"].get("clipped_fraction")}))
    return status


if __name__ == "__main__":
    sys.exit(main())
