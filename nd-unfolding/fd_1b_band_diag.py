#!/usr/bin/env python3
"""1B pre-check, band diagnosis (state/measurement-paper/5d-community-20261024/FD-1B-BAND-DIAGNOSIS-DECLARATION.md):
is the GEANT_Neutron and GEANT_Proton departure of Part 1's rule S a defect or a non-linearity?

F_src = sqrt(E / B) compares the toys' factors moved on the pseudo-data (E) with the same factors moved on the
unfolding simulation (B). This module varies only the estimator seed and the size of the factor (f -> f**eps), and
splits the factor into its signal and background channels. The truth is never varied.

Subcommands:

* ``same``: section 4.2 (rule K against rule S) from Part 1's products, and the control that Part 1's F_src and kappa
  are reproduced bit for bit;
* ``inputs``: section 4.3, the row-level check that both sides carry the same factor on the same reco rows; and
  section 4.6's out-of-window and non-positive-row shares (HW);
* ``unfold``: one item of section 7's table per product (mode E or B, seed, eps, channel);
* ``pilot``: section 5's E and B rebuild controls and the walls; rc 0 PASS, 1 REPRICE, 2 INVALID;
* ``readout``: sections 4.4 to 4.6.

Every pscratch read goes through ``fd_1b_inv``'s O_NOATIME readers. Gate D's own builder
(``fd_1b_score.derivation_blocks``) and ``fd_1b_score.load_s1`` read plainly, so they are not called: their arithmetic
is repeated here on O_NOATIME reads, and the reproduction of Part 1's readout bit for bit checks the repetition.
``fd_1b_precheck_fd``, ``fd_1b_inv``, ``fd_1b_toys``, ``fd_1b_score``, ``s1_assemble`` and ``s5n_pseudo`` are imported
and unchanged.

MEASURES: the declared readouts, labelled DERIVATION. CANNOT AUTHORIZE: a repair, a change to the toys, gate D, M_d,
the window, the covariance or kappa, any change to the coverage test, a study of the truth dependence, or any claim.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import resource
import sys
import time
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_1b_inv as inv  # noqa: E402
import fd_1b_precheck_fd as pfd  # noqa: E402
import fd_1b_score as fs  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5e_candidate  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_universe  # noqa: E402

SCHEMA = "fd-1b-band-diag/1"
TAG = "fd1b_bdg"
WINDOW = inv.WINDOW
RESOLVE_K = inv.RESOLVE_K
DETECTOR = tuple(sorted(sa.DETECTOR_BANDS))
SUBJECTS = ("GEANT_Neutron", "GEANT_Proton")
REFERENCES = ("GEANT_Pion", "MinosEfficiency")
# Part 1's rule S cells_outside (readout.json /bands/<b>/rule_S/cells_outside, 8e05ca9b)
DEPARTING = {"GEANT_Neutron": ("R00", "R02", "R08", "R09", "R10", "R11"), "GEANT_Proton": ("R01", "R05", "R07", "R08")}
BASE_SEED = toys.ESTIMATOR_SEED
SEEDS = tuple(sa.SEEDS)
EPS = (0.5, 1.0, 2.0)
EPS_LABEL = {0.5: "e050", 1.0: "e100", 2.0: "e200"}
CHANNELS = ("both", "signal", "background")
MODES = ("E", "B")
SAME_TOL_DNOM, SAME_TOL_A = 1e-12, 1e-5
P_SCALES, P_CONSTANT = 0.5, 0.25
UNIT_SECONDS, RSS_LIMIT_KIB = inv.UNIT_SECONDS, inv.RSS_LIMIT_KIB
# the seed varies by design (section 2), so it is not one of the keys every product must share
ONE_CODE_KEYS = tuple(k for k in inv.ONE_CODE_KEYS if k != "estimator_seed")
Refusal = inv.Refusal
Invalid = fs.Invalid
CELLS = [f"R{c:02d}" for c in range(sa.N_CELLS)]

if BASE_SEED != SEEDS[0]:
    raise RuntimeError("the toys' estimator seed is not the first of S1's seeds")


def band_universes(bands) -> list[str]:
    return [f"{b}_{i}" for b in bands for i in range(sa.EXPECT[b])]


def detector_universes() -> list[str]:
    return band_universes(DETECTOR)


def subject_universes() -> list[str]:
    return band_universes(SUBJECTS)


# ---------------------------------------------------------------------------------------------------------- the items


def pilot_items() -> list[tuple]:
    """Section 7's pilot: E at seed 42, eps 1, both, for CV and the 8 detector universes; B the same for CV and the 4
    subject universes."""
    return ([("E", u, BASE_SEED, 1.0, "both") for u in ["CV"] + detector_universes()]
            + [("B", u, BASE_SEED, 1.0, "both") for u in ["CV"] + subject_universes()])


def bulk_items() -> list[tuple]:
    """Section 7's bulk: the seeds, the scale and the channels."""
    seeds = [(m, u, s, 1.0, "both") for u in detector_universes() for m in MODES for s in SEEDS[1:]]
    scale = [(m, u, BASE_SEED, e, "both") for u in detector_universes() for m in MODES for e in (0.5, 2.0)]
    chans = [(m, u, BASE_SEED, 1.0, c) for u in subject_universes() for m in MODES for c in ("signal", "background")]
    return seeds + scale + chans


def items() -> list[tuple]:
    return pilot_items() + bulk_items()


def product_name(mode: str, u: str, seed: int, eps: float, channel: str, tag: str = TAG) -> str:
    return f"{tag}_{mode}_{u}_s{seed}_{EPS_LABEL[eps]}_{channel}.npz"


# -------------------------------------------------------------------------------------------------------- the factors


def scaled(f: np.ndarray, eps: float) -> np.ndarray:
    """f**eps; at eps = 1 the factor itself, with no arithmetic, so eps = 1 reproduces Part 1 bit for bit."""
    if eps == 1.0:
        return f
    return np.power(f, eps)


def channel_factors(fs_: np.ndarray, fb: np.ndarray, channel: str) -> tuple[np.ndarray, np.ndarray]:
    """'both' keeps both factors; 'signal' sets the background factor to exactly 1; 'background' the signal's."""
    if channel == "both":
        return fs_, fb
    if channel == "signal":
        return fs_, np.ones(fb.shape[0])
    if channel == "background":
        return np.ones(fs_.shape[0]), fb
    raise ValueError(f"channel {channel!r}")


def item_factors(u: str, eps: float, channel: str, inputs: dict, bkg: dict, bank: Path,
                 det_dir: Path) -> tuple[np.ndarray, np.ndarray, dict]:
    """The toys' factors for universe u alone (``fd_1b_precheck_fd.toy_factors``, O_NOATIME), scaled and split."""
    if u == "CV":
        return np.ones(inputs["w_reco"].shape[0]), np.ones(bkg["bkg_w"].shape[0]), {}
    fs_, fb, rec = pfd.toy_factors(u, inputs, bkg, bank, det_dir)
    fs_, fb = channel_factors(scaled(fs_, eps), scaled(fb, eps), channel)
    return fs_, fb, rec


def experiment(mode: str, fs_: np.ndarray, fb: np.ndarray, inputs: dict, bkg: dict, exp_cv: dict,
               x_true_cv: np.ndarray) -> tuple[dict, np.ndarray]:
    """E: the derivation's construction (``fd_1b_toys.experiment('derivation', ...)``, :338-343): the nominal truth,
    every draw at its mean, the factors on the pseudo-data, the CV simulation. B: the CV experiment's pseudo-data,
    unfolded with the CV simulation carrying the factors on reco and background (``fd_1b_precheck_fd`` mode B)."""
    if mode == "E":
        r = s5n_pseudo.truth_weight("nominal", inputs, 0.0, None)
        exp, x_true, _ = toys.build_full(inputs, bkg, r, fs_, fb, None, expectation=True)
        return exp, x_true
    if mode == "B":
        ui = dict(inputs, w_reco=np.asarray(inputs["w_reco"], float) * fs_)
        ub = dict(bkg, bkg_w=np.asarray(bkg["bkg_w"], float) * fb)
        return pfd.with_mc(exp_cv, ui, ub), x_true_cv
    raise ValueError(f"mode {mode!r}")


# ---------------------------------------------------------------------------------------------------------- the job


def _job_inputs(a) -> tuple[dict, dict, dict, str, str]:
    npz_sha, bkg_sha = inv.sha256_noatime(a.npz), inv.sha256_noatime(a.bkg)
    if (npz_sha, bkg_sha) != (sa.INPUT_NPZ_SHA256, sa.BKG_SHA256):
        raise Refusal(f"input digests {npz_sha} / {bkg_sha} are not the declared ones")
    if inv.sha256_noatime(a.pins) != a.expect_pins_sha256:
        raise Refusal("pins file digest differs")
    with inv.open_noatime(a.pins) as fh:
        pins = json.loads(fh.read().decode())
    toys.check_pins(pins, a.bank, a.detector_dir)
    inputs = inv.load_inputs(a.npz)
    bz = inv.load_npz(a.bkg, allow_pickle=True)
    bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
    return pins, inputs, bkg, npz_sha, bkg_sha


def _check_weights(pins: dict, u: str, det_dir: Path) -> None:
    for k in s5p_universe.weight_keys(det_dir, u):
        p = det_dir / f"{u}_{k}.npy"
        if inv.sha256_noatime(p) != pins["files"][str(p)]["sha256"]:
            raise Refusal(f"{p}: digest differs from the pins file")


def run_unfold(a, unfold_fn=None) -> int:
    inv.OPENED.clear()
    s5e_candidate.install(toys.CONFIG)
    legal = set(items())
    eps = float(a.eps)
    todo = a.universes.split(",")
    for u in todo:
        if (a.mode, u, a.seed, eps, a.channel) not in legal:
            raise Refusal(f"({a.mode}, {u}, seed {a.seed}, eps {eps}, {a.channel}) is not an item of section 7")
    pins, inputs, bkg, npz_sha, bkg_sha = _job_inputs(a)
    exp_cv, x_true_cv = inv.nominal_experiment(inputs, bkg)
    a.out.mkdir(parents=True, exist_ok=True)
    status = 0
    for u in todo:
        target = a.out / product_name(a.mode, u, a.seed, eps, a.channel, a.tag)
        if target.exists():
            continue
        toys.check_pins(pins, a.bank, a.detector_dir)
        if u != "CV":
            _check_weights(pins, u, a.detector_dir)
        t1 = time.time()
        fs_, fb, rec = item_factors(u, eps, a.channel, inputs, bkg, a.bank, a.detector_dir)
        for name, f in (("signal", fs_), ("background", fb)):
            if not np.all(np.isfinite(f)) or np.any(f < 0):
                raise Refusal(f"{target.name}: {name} factor non-finite or negative")
        exp, x_true = experiment(a.mode, fs_, fb, inputs, bkg, exp_cv, x_true_cv)
        if not np.array_equal(np.asarray(exp["flux"], float), np.asarray(inputs["flux"], float)):
            raise Refusal(f"{target.name}: the unfolding flux is not the CV's")
        xs, ev = (unfold_fn or s5n_pseudo.unfold_negweight)(exp, a.seed, a.threads, toys.ITERS)
        xs = np.asarray(xs, float)
        if not np.all(np.isfinite(xs)):
            raise Refusal(f"{target.name}: a non-finite unfolded value")
        meta = {"schema": SCHEMA, "mode": a.mode, "universe": u, "estimator_seed": a.seed, "eps": eps,
                "channel": a.channel, "truth": "nominal", "config": toys.CONFIG, "capacity": None, "iters": toys.ITERS,
                "threads": a.threads, "factor_record": rec, **ev, "input_npz_sha256": npz_sha,
                "bkg_dump_sha256": bkg_sha, "pins_sha256": a.expect_pins_sha256,
                "unfolding_flux_sha256": pfd.array_sha256(exp["flux"]),
                "code_sha256": {**toys.code_digests(),
                                "fd_1b_inv.py": s5n_pseudo.sha256_path(Path(inv.__file__).resolve()),
                                "fd_1b_precheck_fd.py": s5n_pseudo.sha256_path(Path(pfd.__file__).resolve()),
                                "fd_1b_band_diag.py": s5n_pseudo.sha256_path(Path(__file__).resolve())},
                "slurm_job": os.environ.get("SLURM_JOB_ID"), "seconds_unfold": round(time.time() - t1, 3),
                "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "numpy_version": np.__version__}
        status |= s5n_pseudo.write_product(target, {"xsec_flat": xs.ravel(order="C"),
                                                    "xtrue_flat": np.asarray(x_true, float).ravel(order="C")}, meta)
        print(json.dumps({"out": target.name, "seconds_unfold": meta["seconds_unfold"]}), flush=True)
    chk = inv.atime_check()
    (a.out / f"atime-{a.mode}-{os.environ.get('SLURM_JOB_ID', 'local')}-{os.getpid()}.json").write_text(
        json.dumps(chk, indent=1) + "\n")
    if chk["moved"]:
        print(f"[fd-1b-band-diag] DEVIATION: atime moved on {chk['moved']}", file=sys.stderr)
        return status | 8
    return status


# ---------------------------------------------------------------------------------------------- section 4.3, inputs


def compare_rows(got_x, got_w, want_x, want_w) -> dict:
    got_x, want_x = np.asarray(got_x), np.asarray(want_x)
    got_w, want_w = np.asarray(got_w, float), np.asarray(want_w, float)
    if got_x.shape != want_x.shape or got_w.shape != want_w.shape:
        return {"equal": False, "n_rows": [int(got_w.shape[0]), int(want_w.shape[0])], "n_differ": None,
                "max_rel_diff": None}
    bad = ~np.all(got_x == want_x, axis=tuple(range(1, got_x.ndim))) | (got_w != want_w)
    rel = np.abs(got_w - want_w) / np.where(want_w != 0, np.abs(want_w), 1.0)
    return {"equal": not bool(bad.any()), "n_rows": int(got_w.shape[0]), "n_differ": int(bad.sum()),
            "max_rel_diff": float(rel.max()) if rel.size else 0.0}


def input_check(u: str, inputs: dict, bkg: dict, bank: Path, det_dir: Path, exp_cv: dict, x_true_cv) -> dict:
    """Section 4.3 for universe u at eps 1, channel both: E's observed rows and counts against B's simulation reco
    weights (signal) and B's template (background), inside the window, rows of zero or negative weight absent on both
    sides; and HW's shares (section 4.6)."""
    fs_, fb, _ = item_factors(u, 1.0, "both", inputs, bkg, bank, det_dir)
    expE, _ = experiment("E", fs_, fb, inputs, bkg, exp_cv, x_true_cv)
    expB, _ = experiment("B", fs_, fb, inputs, bkg, exp_cv, x_true_cv)
    edges = inputs["edges"]
    reco = np.asarray(inputs["pass_reco"], bool)
    w_sig = np.asarray(expB["w_reco"], float)[reco]
    rows = np.asarray(inputs["MCreco"])[reco]
    pos = w_sig > 0
    k_sig = s5n_pseudo.fid_mask(rows[pos], edges)
    n_sig = int(k_sig.sum())
    tmpl_w = np.asarray(expB["tmpl_w"], float)
    tpos = tmpl_w > 0
    obs, cnt = np.asarray(expE["obs"]), np.asarray(expE["obs_counts"], float)
    sig = compare_rows(obs[:n_sig], cnt[:n_sig], rows[pos][k_sig], w_sig[pos][k_sig])
    bkg_ = compare_rows(obs[n_sig:], cnt[n_sig:], np.asarray(expB["tmpl"])[tpos], tmpl_w[tpos])
    w0 = np.asarray(inputs["w_reco"], float)[reco]
    d = w0 * (fs_[reco] - 1.0)
    inw = s5n_pseudo.fid_mask(rows, edges)
    tot = float(d[inw].sum())
    hw = {"in_window_sum": tot,
          "out_of_window_share": float(d[~inw].sum()) / tot if tot != 0 else None,
          "non_positive_in_window_share": float(d[inw & (w_sig <= 0)].sum()) / tot if tot != 0 else None}
    return {"signal": sig, "background": bkg_, "HW": hw}


def run_inputs(a) -> tuple[dict, int]:
    inv.OPENED.clear()
    pins, inputs, bkg, npz_sha, bkg_sha = _job_inputs(a)
    exp_cv, x_true_cv = inv.nominal_experiment(inputs, bkg)
    per = {}
    for u in detector_universes():
        _check_weights(pins, u, a.detector_dir)
        per[u] = input_check(u, inputs, bkg, a.bank, a.detector_dir, exp_cv, x_true_cv)
    ok = all(v["signal"]["equal"] and v["background"]["equal"] for v in per.values())
    chk = inv.atime_check()
    out = {"schema": SCHEMA, "step": "inputs", "label": "DERIVATION", "verdict": "EQUAL" if ok else "DIFFER",
           "universes": per, "input_npz_sha256": npz_sha, "bkg_dump_sha256": bkg_sha,
           "pins_sha256": a.expect_pins_sha256, "atime": chk}
    if chk["moved"]:
        return out, 8
    return out, 0 if ok else 1


# ------------------------------------------------------------------------------------- Part 1's objects, O_NOATIME


def staged_digests(staged: Path) -> dict:
    with inv.open_noatime(staged / "staged.json") as fh:
        rec = json.loads(fh.read().decode())
    return {r["dest"]: r["sha256"] for r in rec["staged"] if "dest" in r}


def load_checked(path: Path, want: str | None, seen: dict) -> dict:
    """An npz through O_NOATIME, its digest checked against ``want`` (when given) and against any earlier read."""
    got = inv.sha256_noatime(path)
    if want is not None and got != want:
        raise Invalid(f"{path.name}: sha256 {got} is not the staged {want}")
    if seen.get(str(path), got) != got:
        raise Invalid(f"{path.name}: its digest changed since it was first read")
    seen[str(path)] = got
    return inv.load_npz(path)


def load_s1(staged: Path, digests: dict, seen: dict) -> dict:
    """``fd_1b_score.load_s1``'s f and U, on an O_NOATIME read of the staged assembly."""
    p = staged / "s1" / "s1_assembly.npz"
    if inv.sha256_noatime(p) != fs.S1_NPZ_SHA256:
        raise Invalid("the staged S1 assembly is not S1's")
    z = load_checked(p, digests.get("s1/s1_assembly.npz"), seen)
    return {"f": np.asarray(z["f"], float), "U": np.asarray(z["U"], float)}


def check_estimator(m: dict, seed: int) -> list[str]:
    """``s1_assemble.check_meta``'s estimator clauses (:203-208) on a metadata dict, at ``seed``."""
    est = [(e.get("n_estimators"), e.get("num_leaves"), e.get("random_state")) for e in m.get("estimator_params", [])]
    cp = (m.get("refinement") or {}).get("classifier_params") or {}
    bad = []
    if (m.get("config"), m.get("capacity"), m.get("iters"), m.get("estimator_seed")) != ("R", None, 5, seed):
        bad.append("config/capacity/iters/seed")
    if est != [(100, 8, seed)] * 3:
        bad.append(f"estimators {est}")
    if (cp.get("n_estimators"), cp.get("num_leaves"), cp.get("random_state")) != (400, 31, seed + 3):
        bad.append("refinement")
    return bad


def derivation(staged: Path, digests: dict, seen: dict, s1: dict) -> dict:
    """Gate D's derivation arithmetic (``fd_1b_score.derivation_blocks``, fd_1b_score.py:432-466) for CV and the 8
    detector universes: x_u = U xsec, the truth the same in every product, g = f / (U truth), and each detector band's
    carried block. The meta checks are the builder's."""
    U = s1["U"]
    x, z_cv = {}, None
    truth = None
    for u in ["CV"] + detector_universes():
        dest = f"derivation/{inv.DER_TAG}_{u}.npz"
        z = load_checked(staged / dest, digests.get(dest), seen)
        m = json.loads(str(z["meta"]))
        if (m.get("schema"), m.get("arm"), m.get("mode"), m.get("universe")) != (toys.SCHEMA, "derivation",
                                                                                 "derivation", u):
            raise Invalid(f"{dest}: not the derivation product for {u}")
        if json.loads(json.dumps(toys.single_universe(u))) != m.get("draw") or check_estimator(m, BASE_SEED):
            raise Invalid(f"{dest}: not universe {u} alone at the 1B estimator")
        x[u] = U @ np.asarray(z["xsec_flat"], float)
        xt = np.asarray(z["xtrue_flat"], float)
        if truth is None:
            truth = xt
        elif not np.array_equal(xt, truth):
            raise Invalid(f"{dest}: its truth differs from CV's")
        if u == "CV":
            z_cv = np.asarray(z["xsec_flat"], float)
    g = s1["f"] / (U @ truth)
    carried = {b: sa.mat_cov(np.array([x[u] for u in band_universes((b,))])) * np.outer(g, g) for b in DETECTOR}
    return {"x": x, "g": g, "carried": carried, "cv_xsec_flat": z_cv}


def part1_products(unf: Path, seen: dict, U: np.ndarray) -> dict:
    """Part 1's P3 products for CV and the 8 detector universes in modes A, B and Dnom: U xsec (Dnom: U xsec - U
    xtrue), U xtrue, and the raw xsec_flat."""
    out = {}
    for mode in pfd.MODES:
        for u in ["CV"] + detector_universes():
            p = unf / f"{pfd.TAG}_{mode}_{u}.npz"
            z = load_checked(p, None, seen)
            m = json.loads(str(z["meta"]))
            if (m.get("schema"), m.get("mode"), m.get("universe")) != (pfd.SCHEMA, mode, u):
                raise Invalid(f"{p.name}: not Part 1's mode {mode}, universe {u}")
            xs, xt = np.asarray(z["xsec_flat"], float), np.asarray(z["xtrue_flat"], float)
            x = U @ xs
            out[(mode, u)] = {"x": x - U @ xt if mode == "Dnom" else x, "Ux": x, "Ut": U @ xt, "xsec_flat": xs}
    return out


def part1_blocks(p1: dict, g: np.ndarray) -> dict:
    """Part 1's per-band blocks (``fd_1b_precheck_fd.mode_blocks``, :309-344): A and B carried by g, Dnom uncarried."""
    out = {}
    for mode in pfd.MODES:
        for b in DETECTOR:
            C = sa.mat_cov(np.array([p1[(mode, u)]["x"] for u in band_universes((b,))]))
            out[(mode, b)] = C if mode == "Dnom" else C * np.outer(g, g)
    return out


def bits_equal(x, ref) -> bool:
    return np.array_equal(np.asarray(x, float), np.asarray(ref, float), equal_nan=True)


# ------------------------------------------------------------------------------------------------ section 4.2, same


def hk_reading(E: np.ndarray, B: np.ndarray, A: np.ndarray, D: np.ndarray, g: np.ndarray, resolved: list[int]) -> dict:
    """SAME COMPARISON iff |ln(g^2 Dnom / E)| <= 1e-12 and |ln(B / A)| <= 1e-5 in every kappa-resolved cell."""
    with np.errstate(divide="ignore", invalid="ignore"):
        dd = np.abs(np.log(g ** 2 * D / E))
        da = np.abs(np.log(B / A))
    bad = [CELLS[c] for c in resolved if not (dd[c] <= SAME_TOL_DNOM and da[c] <= SAME_TOL_A)]
    return {"verdict": "DIFFERENT" if bad else "SAME COMPARISON", "cells_outside": bad,
            "max_abs_ln_g2Dnom_over_E": float(max((dd[c] for c in resolved), default=0.0)),
            "max_abs_ln_B_over_A": float(max((da[c] for c in resolved), default=0.0)), "n_resolved": len(resolved)}


def same(staged: Path, unf: Path, readout_json: Path) -> dict:
    seen: dict = {}
    digests = staged_digests(staged)
    s1 = load_s1(staged, digests, seen)
    d = derivation(staged, digests, seen, s1)
    p1 = part1_products(unf, seen, s1["U"])
    for mode in pfd.MODES:
        if not bits_equal(p1[(mode, "CV")]["xsec_flat"], d["cv_xsec_flat"]):
            raise Invalid(f"Part 1's mode {mode} at CV is not the derivation CV product bitwise")
    blk = part1_blocks(p1, d["g"])
    ro = json.loads(readout_json.read_text())
    g = d["g"]
    bands = {}
    for b in DETECTOR:
        E = np.diag(d["carried"][b])
        A, B, D = (np.diag(blk[(m, b)]) for m in pfd.MODES)
        with np.errstate(divide="ignore", invalid="ignore"):
            F_src = np.sqrt(E / B)
            kappa = np.sqrt(D / (A / g ** 2))
        ref = ro["bands"][b]["factors"]
        if not bits_equal(F_src, ref["F_src"]) or not bits_equal(kappa, ref["kappa"]):
            raise Invalid(f"band {b}: Part 1's F_src or kappa is not reproduced bit for bit")
        resolved = [CELLS.index(c) for c in ro["bands"][b]["resolved"]["kappa"]]
        desc = {}
        for u in band_universes((b,)):
            xb = np.mean([d["x"][v] for v in band_universes((b,))], axis=0)
            sE = d["x"][u] - xb
            tcv = p1[("Dnom", "CV")]["Ut"]
            with np.errstate(divide="ignore", invalid="ignore"):
                r1 = np.abs(d["x"][u] - p1[("Dnom", u)]["Ux"]) / np.abs(sE)
                r2 = np.abs(p1[("Dnom", u)]["Ut"] - tcv) / np.abs(tcv)
            desc[u] = {"max_rel_UxE_minus_UxDnom": float(np.nanmax(np.where(np.isfinite(r1), r1, np.nan))),
                       "max_rel_UTu_minus_UTcv": float(np.nanmax(np.where(np.isfinite(r2), r2, np.nan)))}
        bands[b] = {"HK": hk_reading(E, B, A, D, g, resolved), "per_universe": desc}
    return {"schema": SCHEMA, "step": "same", "label": "DERIVATION", "cells": CELLS, "bands": bands,
            "reproduced": {"part1_readout_sha256": inv.sha256_noatime(readout_json), "F_src_kappa_bitwise": True},
            "digests": seen}


# ----------------------------------------------------------------------------------------------- section 7, pilot


def pilot(unfolds: Path, staged: Path, part1_unf: Path, tag: str = TAG) -> dict:
    """Section 5's rebuild controls and section 7's walls on the 14 pilot products."""
    seen: dict = {}
    digests = staged_digests(staged)
    rows, bad = [], []
    for mode, u, seed, eps, ch in pilot_items():
        p = unfolds / product_name(mode, u, seed, eps, ch, tag)
        if not p.exists():
            raise Refusal(f"pilot product {p.name} is missing")
        z = load_checked(p, None, seen)
        m = json.loads(str(z["meta"]))
        if (m.get("schema"), m.get("mode"), m.get("universe"), m.get("estimator_seed"), m.get("eps"),
                m.get("channel")) != (SCHEMA, mode, u, seed, eps, ch) or check_estimator(m, seed):
            raise Invalid(f"{p.name}: not pilot item {mode} {u}")
        if mode == "E":
            dest = f"derivation/{inv.DER_TAG}_{u}.npz"
            ref = load_checked(staged / dest, digests.get(dest), seen)["xsec_flat"]
        else:
            ref = load_checked(part1_unf / f"{pfd.TAG}_B_{u}.npz", None, seen)["xsec_flat"]
        if not bits_equal(z["xsec_flat"], ref):
            bad.append(f"{mode}_{u}")
        rows.append({"item": f"{mode}_{u}", "seconds_unfold": float(m["seconds_unfold"]),
                     "peak_rss_kib": int(m["peak_rss_kib"])})
    s_max = max(r["seconds_unfold"] for r in rows)
    r_max = max(r["peak_rss_kib"] for r in rows)
    walls = "PASS" if s_max <= UNIT_SECONDS and r_max <= RSS_LIMIT_KIB else "REPRICE"
    verdict = "INVALID" if bad else walls
    return {"schema": SCHEMA, "step": "P2", "items": rows, "rebuild_not_bitwise": bad, "walls": walls,
            "max_seconds_unfold": s_max, "unit_seconds": UNIT_SECONDS, "max_peak_rss_kib": r_max,
            "rss_limit_kib": RSS_LIMIT_KIB, "verdict": verdict, "digests": seen}


# ------------------------------------------------------------------------------------------- sections 4.4 to 4.6


def in_window(x) -> np.ndarray:
    return inv.in_window(x)


def seed_reading(F: dict, res: dict, c: int) -> str:
    """SEED-STABLE iff F_src is resolved and outside the window, on seed 42's side of 1, at all five seeds."""
    side = math.copysign(1.0, math.log(F[BASE_SEED][c]))
    for s in SEEDS:
        v = F[s][c]
        if not res[s][c] or bool(in_window(v)) or not (v > 0) or math.copysign(1.0, math.log(v)) != side:
            return "SEED-SENSITIVE"
    return "SEED-STABLE"


def slopes(F: dict, res: dict, c: int) -> dict:
    """Section 4.5's p_up and p_down for cell c from F_src at eps 1/2, 1 and 2 (seed 42)."""
    sigma = math.copysign(1.0, math.log(F[1.0][c]))
    ell = {e: sigma * math.log(F[e][c]) for e in EPS if res[e][c] and F[e][c] > 0}
    out: dict = {"ell": {str(e): v for e, v in ell.items()}}
    if 2.0 not in ell:
        out["p_up"] = None
    else:
        out["p_up"] = -math.inf if ell[2.0] <= 0 else math.log2(ell[2.0] / ell[1.0])
    if 0.5 not in ell:
        out["p_down"] = None
    else:
        out["p_down"] = math.inf if ell[0.5] <= 0 else math.log2(ell[1.0] / ell[0.5])
    return out


def scale_reading(sl: dict) -> str:
    up, down = sl["p_up"], sl["p_down"]
    if up is None:
        return "NOT READ"
    if up >= P_SCALES and (down is None or down >= P_SCALES):
        return "SCALES"
    if abs(up) <= P_CONSTANT and (down is None or abs(down) <= P_CONSTANT):
        return "CONSTANT"
    return "MIXED"


def band_scale(cells: dict) -> str:
    read = [v for v in cells.values() if v not in ("NOT READ",)]
    if not read:
        return "NOT READ"
    for k in ("SCALES", "CONSTANT"):
        if all(v == k for v in read):
            return k
    return "MIXED"


def _jsonable(x):
    if isinstance(x, float) and math.isinf(x):
        return "+inf" if x > 0 else "-inf"
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_jsonable(v) for v in x]
    return x


def readout(staged: Path, part1_unf: Path, unfolds: Path, i0_json: Path, readout_json: Path,
            tag: str = TAG) -> dict:
    seen: dict = {}
    digests = staged_digests(staged)
    s1 = load_s1(staged, digests, seen)
    U = s1["U"]
    d = derivation(staged, digests, seen, s1)
    g = d["g"]
    p1 = part1_products(part1_unf, seen, U)
    ro = json.loads(readout_json.read_text())
    r0 = json.loads(i0_json.read_text())
    if r0.get("floor", {}).get("kind") != "measured":
        raise Invalid("I0's floor is not the measured one")
    sn2 = r0["floor"]["upper_factor"]["nom"] * np.asarray(r0["sigma_J_nom_carried"]) ** 2
    # every new product: its item, its estimator at its seed, one code and one input set
    x_new, metas = {}, {}
    for it in items():
        mode, u, seed, eps, ch = it
        p = unfolds / product_name(mode, u, seed, eps, ch, tag)
        if not p.exists():
            raise Invalid(f"{p.name} is missing")
        z = load_checked(p, None, seen)
        m = json.loads(str(z["meta"]))
        if (m.get("schema"), m.get("mode"), m.get("universe"), m.get("estimator_seed"), m.get("eps"),
                m.get("channel")) != (SCHEMA, mode, u, seed, eps, ch) or check_estimator(m, seed):
            raise Invalid(f"{p.name}: not item {it}")
        metas[it] = m
        x_new[it] = U @ np.asarray(z["xsec_flat"], float)
    for key in ONE_CODE_KEYS:
        vals = {json.dumps(v.get(key), sort_keys=True) for v in metas.values()}
        if len(vals) != 1 or next(iter(metas.values())).get(key) is None:
            raise Invalid(f"the new products are not one code and one input set: {key} takes {len(vals)} values")

    def x_of(mode, u, seed, eps, ch):
        if (seed, eps, ch) == (BASE_SEED, 1.0, "both"):
            return d["x"][u] if mode == "E" else p1[("B", u)]["x"]
        return x_new[(mode, u, seed, eps, ch)]

    def blocks(b, seed, eps, ch):
        us = band_universes((b,))
        E = np.diag(sa.mat_cov(np.array([x_of("E", u, seed, eps, ch) for u in us])) * np.outer(g, g))
        B = np.diag(sa.mat_cov(np.array([x_of("B", u, seed, eps, ch) for u in us])) * np.outer(g, g))
        f_n = inv.noise_factor(b, None) * sn2
        with np.errstate(divide="ignore", invalid="ignore"):
            F = np.sqrt(E / B)
        return F, ~pfd.noise(E, B, f_n, f_n), {u: {"E": x_of("E", u, seed, eps, ch).tolist(),
                                                     "B": x_of("B", u, seed, eps, ch).tolist()} for u in us}

    out_bands = {}
    for b in DETECTOR:
        F42, res42, _ = blocks(b, BASE_SEED, 1.0, "both")
        ref = ro["bands"][b]
        if not bits_equal(F42, ref["factors"]["F_src"]) or \
                [CELLS[c] for c in range(sa.N_CELLS) if res42[c]] != ref["resolved"]["F_src"]:
            raise Invalid(f"band {b}: seed 42's F_src or its resolution is not Part 1's")
        Fs, Rs, Vs = {}, {}, {}
        for s in SEEDS:
            Fs[s], Rs[s], Vs[f"s{s}"] = blocks(b, s, 1.0, "both")
        Fe, Re = {1.0: Fs[BASE_SEED], 0.5: None, 2.0: None}, {1.0: Rs[BASE_SEED]}
        Ve = {}
        for e in (0.5, 2.0):
            Fe[e], Re[e], Ve[EPS_LABEL[e]] = blocks(b, BASE_SEED, e, "both")
        rec: dict = {"seed_values": {f"s{s}": Fs[s].tolist() for s in SEEDS},
                     "seed_resolved": {f"s{s}": [CELLS[c] for c in range(sa.N_CELLS) if Rs[s][c]] for s in SEEDS},
                     "eps_values": {EPS_LABEL[e]: Fe[e].tolist() for e in EPS},
                     "eps_resolved": {EPS_LABEL[e]: [CELLS[c] for c in range(sa.N_CELLS) if Re[e][c]] for e in EPS},
                     "cell_values": {**Vs, **Ve}}
        with np.errstate(divide="ignore", invalid="ignore"):
            lnF = np.log(np.array([Fs[s] for s in SEEDS]))
        rec["seed_sd_ln_F_src"] = np.std(lnF, axis=0).tolist()
        rec["outside_per_seed"] = {f"s{s}": [CELLS[c] for c in range(sa.N_CELLS) if Rs[s][c] and not in_window(Fs[s][c])]
                                   for s in SEEDS}
        if b in SUBJECTS:
            cells = {}
            for name in DEPARTING[b]:
                c = CELLS.index(name)
                sr = seed_reading(Fs, Rs, c)
                if sr == "SEED-STABLE":
                    sl = slopes(Fe, Re, c)
                    cells[name] = {"seed": sr, **sl, "scale": scale_reading(sl)}
                else:
                    cells[name] = {"seed": sr, "scale": "NOT READ"}
            rec["departing"] = cells
            rec["scale_band"] = band_scale({k: v["scale"] for k, v in cells.items()})
            ch = {}
            for c_ in ("signal", "background"):
                Fc, Rc, Vc = blocks(b, BASE_SEED, 1.0, c_)
                ch[c_] = {"F_src": Fc.tolist(), "resolved": [CELLS[c] for c in range(sa.N_CELLS) if Rc[c]],
                          "cell_values": Vc}
            rec["channels"] = ch
        out_bands[b] = rec
    return _jsonable({"schema": SCHEMA, "step": "readout", "label": "DERIVATION", "cells": CELLS, "window": list(WINDOW),
                      "resolve_k": RESOLVE_K, "departing_cells": {k: list(v) for k, v in DEPARTING.items()},
                      "bands": out_bands, "part1_readout_sha256": inv.sha256_noatime(readout_json),
                      "i0_sha256": inv.sha256_noatime(i0_json), "digests": seen})


# ------------------------------------------------------------------------------------------------------------ main


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("same")
    for k in ("staged", "unfolds", "readout", "out"):
        p.add_argument(f"--{k}", type=Path, required=True)
    for name in ("inputs", "unfold"):
        p = sub.add_parser(name)
        for k in ("npz", "bkg", "bank", "detector-dir", "pins", "out"):
            p.add_argument(f"--{k}", type=Path, required=True)
        p.add_argument("--expect-pins-sha256", required=True)
    p.add_argument("--mode", choices=MODES, required=True)
    p.add_argument("--seed", type=int, choices=SEEDS, required=True)
    p.add_argument("--eps", choices=("0.5", "1", "2"), required=True)
    p.add_argument("--channel", choices=CHANNELS, required=True)
    p.add_argument("--universes", required=True)
    p.add_argument("--threads", type=int, default=int(os.environ.get("SLURM_CPUS_PER_TASK", "32")))
    p.add_argument("--tag", default=TAG)
    p = sub.add_parser("pilot")
    for k in ("unfolds", "staged", "part1-unfolds", "out"):
        p.add_argument(f"--{k}", type=Path, required=True)
    p.add_argument("--tag", default=TAG)
    p = sub.add_parser("readout")
    for k in ("staged", "part1-unfolds", "unfolds", "i0", "readout", "out"):
        p.add_argument(f"--{k}", type=Path, required=True)
    p.add_argument("--tag", default=TAG)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "unfold":
            return run_unfold(a)
        if a.out.exists():
            raise Refusal(f"refusing to overwrite {a.out}")
        rc = 0
        if a.cmd == "same":
            res = same(a.staged, a.unfolds, a.readout)
        elif a.cmd == "inputs":
            res, rc = run_inputs(a)
        elif a.cmd == "pilot":
            res = pilot(a.unfolds, a.staged, a.part1_unfolds, a.tag)
            rc = {"PASS": 0, "REPRICE": 1, "INVALID": 2}[res["verdict"]]
        else:
            res = readout(a.staged, a.part1_unfolds, a.unfolds, a.i0, a.readout, a.tag)
        res["code_sha256"] = {"fd_1b_band_diag.py": s5n_pseudo.sha256_path(Path(__file__).resolve())}
        a.out.write_text(json.dumps(res, indent=1) + "\n")
        print(json.dumps({"out": str(a.out), "step": res.get("step"), "verdict": res.get("verdict"), "rc": rc}))
        return rc
    except (Refusal, Invalid, SystemExit, ValueError, OSError) as e:
        if isinstance(e, SystemExit) and not isinstance(e.code, str):
            raise
        print(f"[fd-1b-band-diag] refusing: {type(e).__name__}: {e}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())
