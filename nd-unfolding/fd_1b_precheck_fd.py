#!/usr/bin/env python3
"""1B gate-D pre-check, Part 1 (state/measurement-paper/5d-community-20261024/FD-1B-PRECHECK-FD-DECLARATION.md): the
Flux band and the four detector bands, each drawn alone at the 1B configuration, split as I2 and kappa split the
interaction group.

Subcommands:

* ``stage``: ``fd_1b_inv.stage`` unchanged (each input read once with O_NOATIME into a verified copy);
* ``unfold``: one Flux or detector universe per product, on the derivation CV experiment's pseudo-data, in mode
  A (S1's universe in the unfolding MC, ``s5p_universe.universe_inputs``, with Phi_u for Flux), B (the toys' own source
  factors on the MC side; truth, denominator and flux the CV's) or Dnom (nature is the universe at r = 1, unfolded with
  the nominal simulation and Phi_CV);
* ``walls``: the pilot's re-price trigger, rc 0 PASS, 1 REPRICE;
* ``readout``: per band and per group, F_src = sqrt(E/B), F_side = sqrt(B/A), F_truth = sqrt(A/M), kappa =
  sqrt(Dnom/A_unc); rules S, F and K; the Flux normalization-only block A_Phi (descriptive).

The unfolding flux is set in every mode (declaration section 2.1): ``fd_1b_inv.with_mc`` replaces only
``fd_1b_inv.MC_KEYS``, which leaves the flux the pseudo-data's. That is right for the interaction universes I2 ran and
wrong here, so ``with_mc`` below also replaces ``flux``, and each product records the sha256 of the flux it unfolded
with. Every pscratch input is opened with O_NOATIME through ``fd_1b_inv``'s readers. ``fd_1b_inv``, ``fd_1b_moded``,
``fd_1b_toys``, ``fd_1b_score``, ``fd_1b_diag``, ``s1_assemble``, ``s5p_universe`` and ``s5n_pseudo`` are imported
and unchanged.

    fd_1b_precheck_fd.py stage --spec SPEC.json --out DIR
    fd_1b_precheck_fd.py unfold --mode A --universes Flux_0,Flux_1 --npz N --bkg B --bank K --detector-dir D \\
        --flux-file F --pins P --expect-pins-sha256 H --out U
    fd_1b_precheck_fd.py walls --unfolds U --out W
    fd_1b_precheck_fd.py readout --staged DIR --unfolds U --gate-d G --diag DG --i0 I0 --out O

MEASURES: the declared readouts, labelled DERIVATION. CANNOT AUTHORIZE: a coverage verdict, a change to the toys,
M_d, the covariance or gate D's window, a 1B rerun, or any claim.
"""
from __future__ import annotations

import argparse
import hashlib
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
import fd_1b_diag as fdg  # noqa: E402
import fd_1b_inv as inv  # noqa: E402
import fd_1b_score as fs  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5e_candidate  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_nullexp as ne  # noqa: E402
import s5p_universe  # noqa: E402

SCHEMA = "fd-1b-precheck-fd/1"
WINDOW = inv.WINDOW
BANDS = (sa.FLUX,) + tuple(sorted(sa.DETECTOR_BANDS))
GROUPS = {"flux": (sa.FLUX,), "detector": tuple(sorted(sa.DETECTOR_BANDS))}
MODES = ("A", "B", "Dnom")
DER_TAG, S1_TAG, TAG = inv.DER_TAG, inv.S1_TAG, "fd1b_pfd"
RESOLVE_K = inv.RESOLVE_K
# the unfolding-MC keys every mode sets: fd_1b_inv's, and the flux (section 2.1)
UNFOLD_MC_KEYS = inv.MC_KEYS + ("flux",)
PILOT = (("A", "CV"), ("B", "CV"), ("Dnom", "CV"), ("A", "Flux_0"), ("B", "Flux_0"), ("Dnom", "Flux_0"),
         ("A", "MinosEfficiency_0"), ("B", "MinosEfficiency_0"))
UNIT_SECONDS = inv.UNIT_SECONDS
RSS_LIMIT_KIB = inv.RSS_LIMIT_KIB
ONE_CODE_KEYS = inv.ONE_CODE_KEYS + ("flux_file_sha256",)
FACTORS = ("F_src", "F_side", "F_truth")
Refusal = inv.Refusal


def universes() -> list[str]:
    """The 108 universes this part unfolds: Flux_0..99 and the 8 detector universes, in band order."""
    return [f"{b}_{i}" for b in BANDS for i in range(sa.EXPECT[b])]


def band_of(tag: str) -> str:
    return tag.rpartition("_")[0]


def array_sha256(x) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(x, np.float64)).tobytes()).hexdigest()


# --------------------------------------------------------------------------------------------- the unfolding inputs


def weights_dir(tag: str, bank: Path, det_dir: Path) -> Path:
    return det_dir if band_of(tag) in sa.DETECTOR_BANDS else bank


def toy_factors(tag: str, inputs: dict, bkg: dict, bank: Path, det_dir: Path) -> tuple[np.ndarray, np.ndarray, dict]:
    """The toys' source factors for one Flux or detector universe alone (``fd_1b_toys.source_factors`` on
    ``single_universe(tag)``, :243-260): signal reco weights x wr_u / w_reco and background x bkgw_u / bkg_w, no truth
    preservation, read here with O_NOATIME. A test holds them equal to the toys' own bitwise."""
    w = inv.universe_weights(weights_dir(tag, bank, det_dir), tag, "keep")
    wr, bw = np.asarray(inputs["w_reco"], float), np.asarray(bkg["bkg_w"], float)
    used_r, used_b = np.asarray(inputs["pass_reco"], bool), np.ones(bw.size, bool)
    rec: dict = {}
    fs_ = np.ones(wr.shape[0]) * ne.checked_ratio(w["wr"], wr, used_r, f"{tag}:wr", rec)
    fb = np.ones(bw.shape[0]) * ne.checked_ratio(w["bkgw"], bw, used_b, f"{tag}:bkgw", rec)
    for name, f in (("signal", fs_), ("background", fb)):
        if not np.all(np.isfinite(f)) or np.any(f < 0):
            raise Refusal(f"{tag} {name} source factor: non-finite or negative")
    return fs_, fb, rec


def mode_inputs(mode: str, tag: str, inputs: dict, bkg: dict, bank: Path, det_dir: Path, bank_cv: dict,
                flux_file: Path) -> tuple[dict, dict, dict]:
    """The universe's arrays for one mode: A and Dnom take S1's universe (``universe_inputs``, Phi_u for Flux); B
    takes the CV MC with the toys' factors on reco and background. ``tag == "CV"`` gives the CV's arrays."""
    if tag == "CV":
        return dict(inputs), dict(bkg), {}
    if mode in ("A", "Dnom"):
        w = inv.universe_weights(weights_dir(tag, bank, det_dir), tag, "zero")
        band, _, idx = tag.rpartition("_")
        ui, ub, info = s5p_universe.universe_inputs(inputs, bkg, bank_cv, w, band, idx,
                                                    flux_file if band == sa.FLUX else None)
        if band in sa.DETECTOR_BANDS:
            # HD1's premise, recorded and not gated: are the dump's truth weights and denominator the CV's?
            info["wt_equals_cv"] = bool(np.array_equal(ui["w_truth"], np.asarray(inputs["w_truth"], float)))
            info["denom_equals_cv"] = bool(np.array_equal(ui["denom_nd"], np.asarray(inputs["denom_nd"], float)))
        return ui, ub, info
    if mode == "B":
        fs_, fb, rec = toy_factors(tag, inputs, bkg, bank, det_dir)
        return (dict(inputs, w_reco=np.asarray(inputs["w_reco"], float) * fs_),
                dict(bkg, bkg_w=np.asarray(bkg["bkg_w"], float) * fb), rec)
    raise ValueError(f"mode {mode!r}")


def with_mc(exp: dict, ui: dict, ub: dict) -> dict:
    """The experiment's pseudo-data with (ui, ub) as the unfolding MC, the flux included (section 2.1)."""
    mc = s5n_pseudo.build_data(ui, ub)
    return dict(exp, **{k: mc[k] for k in UNFOLD_MC_KEYS})


def experiment(mode: str, inputs: dict, bkg: dict, ui: dict, ub: dict, exp_cv: dict,
               x_true_cv: np.ndarray) -> tuple[dict, np.ndarray]:
    """A and B: the derivation CV experiment's pseudo-data, unfolded with (ui, ub) and ui's flux. Dnom: pseudo-data
    from (ui, ub) at r = 1 with the universe's own truth, unfolded with the nominal simulation and Phi_CV."""
    if mode in ("A", "B"):
        return with_mc(exp_cv, ui, ub), x_true_cv
    if mode == "Dnom":
        ones_s, ones_b = np.ones(ui["w_reco"].shape[0]), np.ones(ub["bkg_w"].shape[0])
        exp, x_true, _ = toys.build_full(ui, ub, np.ones(ui["MCgen"].shape[0]), ones_s, ones_b, None, expectation=True)
        return with_mc(exp, inputs, bkg), x_true
    raise ValueError(f"mode {mode!r}")


def expected_flux(mode: str, tag: str, inputs: dict, ui: dict) -> np.ndarray:
    """The flux each mode must unfold with: Phi_u for A on a Flux universe, Phi_CV otherwise."""
    return np.asarray(ui["flux"] if (mode == "A" and band_of(tag) == sa.FLUX) else inputs["flux"], float)


def run_unfold(a, unfold_fn=None) -> int:
    inv.OPENED.clear()
    s5e_candidate.install(toys.CONFIG)
    npz_sha, bkg_sha = inv.sha256_noatime(a.npz), inv.sha256_noatime(a.bkg)
    if (npz_sha, bkg_sha) != (sa.INPUT_NPZ_SHA256, sa.BKG_SHA256):
        raise Refusal(f"input digests {npz_sha} / {bkg_sha} are not the declared ones")
    if inv.sha256_noatime(a.pins) != a.expect_pins_sha256:
        raise Refusal("pins file digest differs")
    with inv.open_noatime(a.pins) as fh:
        pins = json.loads(fh.read().decode())
    toys.check_pins(pins, a.bank, a.detector_dir)
    # the flux file is the staged copy (declaration section 6), which flux_universe (ROOT in production) then reads
    # plainly: its digest is read plainly too, so the job's atime check tracks sources only and not this copy
    flux_sha = sa.sha256(a.flux_file)
    inputs = inv.load_inputs(a.npz)
    bz = inv.load_npz(a.bkg, allow_pickle=True)
    bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
    bank_cv = inv.load_npz(a.bank / "cv.npz", allow_pickle=True)
    alignment = s5p_universe.check_alignment(bank_cv, inputs, bkg)
    exp_cv, x_true_cv = inv.nominal_experiment(inputs, bkg)
    legal = set(universes()) | {"CV"}
    a.out.mkdir(parents=True, exist_ok=True)
    status = 0
    for tag in a.universes.split(","):
        if tag not in legal:
            raise Refusal(f"{tag} is not CV, a Flux universe or a detector universe")
        target = a.out / f"{a.tag}_{a.mode}_{tag}.npz"
        if target.exists():
            continue
        toys.check_pins(pins, a.bank, a.detector_dir)
        if tag != "CV":
            d = weights_dir(tag, a.bank, a.detector_dir)
            for k in s5p_universe.weight_keys(d, tag):
                p = d / f"{tag}_{k}.npy"
                if inv.sha256_noatime(p) != pins["files"][str(p)]["sha256"]:
                    raise Refusal(f"{p}: digest differs from the pins file")
        t1 = time.time()
        ui, ub, info = mode_inputs(a.mode, tag, inputs, bkg, a.bank, a.detector_dir, bank_cv, a.flux_file)
        exp, x_true = experiment(a.mode, inputs, bkg, ui, ub, exp_cv, x_true_cv)
        want = expected_flux(a.mode, tag, inputs, ui)
        if not np.array_equal(np.asarray(exp["flux"], float), want):
            raise Refusal(f"{target.name}: the unfolding flux is not mode {a.mode}'s")
        xs, ev = (unfold_fn or s5n_pseudo.unfold_negweight)(exp, toys.ESTIMATOR_SEED, a.threads, toys.ITERS)
        xs = np.asarray(xs, float)
        if not np.all(np.isfinite(xs)):
            raise Refusal(f"{target.name}: a non-finite unfolded value")
        meta = {"schema": SCHEMA, "mode": a.mode, "universe": tag, "truth": "nominal" if a.mode != "Dnom" else "universe",
                "config": toys.CONFIG, "capacity": None, "iters": toys.ITERS, "estimator_seed": toys.ESTIMATOR_SEED,
                "threads": a.threads, "mode_info": info, **ev, "input_npz_sha256": npz_sha, "bkg_dump_sha256": bkg_sha,
                "pins_sha256": a.expect_pins_sha256, "flux_file_sha256": flux_sha, "alignment": alignment,
                "unfolding_flux_sha256": array_sha256(exp["flux"]), "cv_flux_sha256": array_sha256(inputs["flux"]),
                "code_sha256": {**toys.code_digests(), "fd_1b_inv.py": s5n_pseudo.sha256_path(Path(inv.__file__).resolve()),
                                "fd_1b_precheck_fd.py": s5n_pseudo.sha256_path(Path(__file__).resolve())},
                "slurm_job": os.environ.get("SLURM_JOB_ID"), "seconds_unfold": round(time.time() - t1, 3),
                "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "numpy_version": np.__version__,
                "edges": [np.asarray(e, float).tolist() for e in inputs["edges"]]}
        status |= s5n_pseudo.write_product(target, {"xsec_flat": xs.ravel(order="C"),
                                                    "xtrue_flat": np.asarray(x_true, float).ravel(order="C"),
                                                    "unfolding_flux": np.asarray(exp["flux"], float),
                                                    "cv_flux": np.asarray(inputs["flux"], float)}, meta)
        print(json.dumps({"out": target.name, "seconds_unfold": meta["seconds_unfold"]}), flush=True)
    chk = inv.atime_check()
    (a.out / f"atime-{a.mode}-{os.environ.get('SLURM_JOB_ID', 'local')}-{os.getpid()}.json").write_text(
        json.dumps(chk, indent=1) + "\n")
    if chk["moved"]:
        print(f"[fd-1b-precheck-fd] DEVIATION: atime moved on {chk['moved']}", file=sys.stderr)
        return status | 8
    return status


def pilot_walls(unfolds: Path, tag: str = TAG) -> dict:
    """The re-price trigger (declaration section 7): PASS iff all eight pilot products exist, the largest
    seconds_unfold is at most UNIT_SECONDS and the largest peak RSS at most RSS_LIMIT_KIB; else REPRICE."""
    rows = []
    for mode, u in PILOT:
        p = unfolds / f"{tag}_{mode}_{u}.npz"
        if not p.exists():
            raise Refusal(f"pilot product {p.name} is missing")
        m = json.loads(str(inv.load_npz(p)["meta"]))
        if (m.get("mode"), m.get("universe")) != (mode, u) or m.get("peak_rss_kib") is None:
            raise Refusal(f"{p.name}: not pilot item {mode} {u}, or no peak_rss_kib")
        rows.append({"item": f"{mode}_{u}", "seconds_unfold": float(m["seconds_unfold"]),
                     "peak_rss_kib": int(m["peak_rss_kib"])})
    s_max = max(r["seconds_unfold"] for r in rows)
    r_max = max(r["peak_rss_kib"] for r in rows)
    ok = s_max <= UNIT_SECONDS and r_max <= RSS_LIMIT_KIB
    return {"schema": SCHEMA, "step": "P2", "items": rows, "max_seconds_unfold": s_max, "unit_seconds": UNIT_SECONDS,
            "max_peak_rss_kib": r_max, "rss_limit_kib": RSS_LIMIT_KIB, "verdict": "PASS" if ok else "REPRICE"}


# --------------------------------------------------------------------------------------------------------- the rules


def in_window(x) -> np.ndarray:
    return inv.in_window(x)


def rule_s(F_src: np.ndarray, resolved: np.ndarray) -> dict:
    """REPRODUCED iff F_src is inside the window in every resolved cell; DEPARTS lists the cells outside."""
    out = [c for c in range(F_src.size) if resolved[c] and not in_window(F_src[c])]
    return {"verdict": "DEPARTS" if out else "REPRODUCED", "cells_outside": [f"R{c:02d}" for c in out],
            "values_outside": [float(F_src[c]) for c in out], "n_resolved": int(np.sum(resolved))}


def rule_k(kappa: np.ndarray, resolved: np.ndarray) -> dict:
    out = [c for c in range(kappa.size) if resolved[c] and not in_window(kappa[c])]
    return {"verdict": "FAIL" if out else "PASS", "cells_outside": [f"R{c:02d}" for c in out],
            "values_outside": [float(kappa[c]) for c in out], "n_resolved": int(np.sum(resolved))}


def attribute(F: dict, c: int) -> dict:
    """I2's rule for cell c (``fd_1b_inv.attribute`` without its S1-resolved F_truth clause, which the noise class
    replaces here): the factor with the largest |ln F| on the departure's side of 1, if it lies outside the window
    and carries at least half of |ln rho|; otherwise unresolved."""
    tot = math.log(F["total"][c])
    side = [(abs(math.log(F[k][c])), k) for k in FACTORS if math.log(F[k][c]) * tot > 0]
    if not side:
        return {"factor": None, "why": "no factor on the departure's side"}
    mag, k = max(side)
    if bool(in_window(F[k][c])) or mag < 0.5 * abs(tot):
        return {"factor": None, "why": f"{k} inside the window or under half"}
    return {"factor": k}


def level(attr: dict) -> dict:
    """Each factor's count over the n attributed cells, read separately: the account if more than n/2, refuted as
    the account if at most n/4, otherwise partial; n = 0 reads nothing to attribute."""
    n = len(attr)
    counts = {k: sum(1 for v in attr.values() if v["factor"] == k) for k in FACTORS}
    counts["unresolved"] = sum(1 for v in attr.values() if v["factor"] is None)
    if n == 0:
        return {"n_cells": 0, "counts": counts, "level": {k: "nothing to attribute" for k in FACTORS}}
    lv = {k: "account" if counts[k] > n / 2 else ("refuted" if counts[k] <= n / 4 else "partial") for k in FACTORS}
    return {"n_cells": n, "counts": counts, "level": lv}


def factors(E: np.ndarray, B: np.ndarray, A: np.ndarray, M: np.ndarray) -> dict:
    return {"total": np.sqrt(E / M), "F_src": np.sqrt(E / B), "F_side": np.sqrt(B / A), "F_truth": np.sqrt(A / M)}


def noise(P: np.ndarray, Q: np.ndarray, floor_p: np.ndarray, floor_q: np.ndarray) -> np.ndarray:
    """A cell where both compared blocks lie below RESOLVE_K x their own pure-noise expectation (I0's rule)."""
    return inv.noise_consistent(P, Q, floor_p, floor_q, RESOLVE_K)


# ---------------------------------------------------------------------------------------------------------- readout


def mode_blocks(unfolds: Path, tag: str, U: np.ndarray, g: np.ndarray, w_flux: np.ndarray, cv_flat: np.ndarray,
                metas: dict) -> dict:
    """Per band and mode: A and B carried by g (as I2's), Dnom's error block U x_hat - U T_u uncarried (as stage 0's),
    by S1's estimator, weighted for Flux. Each mode's CV product must equal the derivation CV product bitwise."""
    out, phis = {m: {} for m in MODES}, []
    for mode in MODES:
        cv = inv.load_npz(unfolds / f"{tag}_{mode}_CV.npz")
        metas[f"{mode}_CV"] = json.loads(str(cv["meta"]))
        if not np.array_equal(np.asarray(cv["xsec_flat"], float), cv_flat):
            raise fs.Invalid(f"mode {mode} at CV does not reproduce the derivation CV product bitwise")
        for b in BANDS:
            X = []
            for i in range(sa.EXPECT[b]):
                u = f"{b}_{i}"
                z = inv.load_npz(unfolds / f"{tag}_{mode}_{u}.npz")
                meta = json.loads(str(z["meta"]))
                if (meta.get("mode"), meta.get("universe"), meta.get("schema")) != (mode, u, SCHEMA):
                    raise fs.Invalid(f"{tag}_{mode}_{u}.npz: not mode {mode}, universe {u}")
                want_cv = not (mode == "A" and b == sa.FLUX)
                if (meta["unfolding_flux_sha256"] == meta["cv_flux_sha256"]) != want_cv:
                    raise fs.Invalid(f"{tag}_{mode}_{u}.npz: its unfolding flux is not mode {mode}'s")
                if array_sha256(z["unfolding_flux"]) != meta["unfolding_flux_sha256"]:
                    raise fs.Invalid(f"{tag}_{mode}_{u}.npz: its flux array is not the one its metadata names")
                metas[f"{mode}_{u}"] = meta
                if mode == "A" and b == sa.FLUX:
                    phis.append(np.asarray(z["unfolding_flux"], float))
                x = U @ np.asarray(z["xsec_flat"], float)
                X.append(x - U @ np.asarray(z["xtrue_flat"], float) if mode == "Dnom" else x)
            C = sa.mat_cov(np.array(X), w_flux if b == sa.FLUX else None)
            out[mode][b] = C if mode == "Dnom" else C * np.outer(g, g)
    for key in ONE_CODE_KEYS:
        vals = {json.dumps(v.get(key), sort_keys=True) for v in metas.values()}
        if len(vals) != 1 or metas[next(iter(metas))].get(key) is None:
            raise fs.Invalid(f"the products are not one code and one input set: {key} takes {len(vals)} values")
    out["phi_flux"] = phis
    return out


def flux_norm_block(cv_flat: np.ndarray, edges: list, phis: list, cv_flux: np.ndarray, U: np.ndarray,
                    g: np.ndarray, w_flux: np.ndarray) -> np.ndarray:
    """A_Phi (descriptive, HF2): the weighted block of the shift S1's Phi_u alone makes with the MC unchanged, the
    flux being a per-pT divisor on axis 0 (xsec_nd.py:54-80): U [x_hat_CV (Phi_CV / Phi_u - 1)], carried by g as A
    is. Phi_u is each Flux universe's mode-A unfolding flux, in universe order."""
    shape = tuple(len(e) - 1 for e in edges)
    x = np.asarray(cv_flat, float).reshape(shape)
    cv = np.asarray(cv_flux, float)
    expand = (slice(None),) + (None,) * (len(shape) - 1)
    S = [U @ (x * (cv / np.asarray(p, float) - 1.0)[expand]).ravel() for p in phis]
    return sa.mat_cov(np.array(S), w_flux) * np.outer(g, g)


def readout(staged: Path, unfolds: Path, gate_d: Path, diag_json: Path, i0_json: Path, tag: str = TAG) -> dict:
    if sa.sha256(gate_d) != fdg.GATE_D_SHA256:
        raise fs.Invalid(f"{gate_d} is not gate D's committed readout")
    r0 = json.loads(i0_json.read_text())
    dg = json.loads(diag_json.read_text())
    s1 = fs.load_s1(staged / "s1" / "s1_assembly.npz")
    constraint = staged / "flux_constraint.txt"
    d = fs.derivation_blocks(staged / "derivation", DER_TAG, s1, constraint)
    w = sa.flux_weights(constraint)
    U, g = s1["U"], d["g"]
    cells = [f"R{c:02d}" for c in range(sa.N_CELLS)]
    E = {b: np.diag(d["carried"][f"band:{b}"]) for b in BANDS}
    M = {b: np.diag(s1["blocks"][f"band:{b}"]) for b in BANDS}
    # control E: gate D's per-group ratios and the diagnosis's per-band ratios, bit for bit
    gd = json.loads(gate_d.read_text())
    for grp, bs in GROUPS.items():
        e = sum(d["carried"][f"band:{b}"] for b in bs)
        m = sum(s1["blocks"][f"band:{b}"] for b in bs)
        if np.sqrt(np.diag(e) / np.diag(m)).tolist() != gd["per_group_sigma_ratio"][grp]:
            raise fs.Invalid(f"the {grp} ratio does not reproduce gate D's committed readout bit for bit")
    for b in BANDS:
        if fdg.ratio(E[b], M[b]) != dg["per_band"][b]["sigma_ratio"]:
            raise fs.Invalid(f"{b}: the per-band ratio does not reproduce the diagnosis's bit for bit")
    # control M: S1's staged universe unfolds rebuild the assembly's blocks exactly
    uni = sa.universe_bands([staged / "uni"], S1_TAG)
    for b in BANDS:
        X = np.array([U @ sa.xs(p) for p in uni[b]])
        if not np.array_equal(sa.mat_cov(X, w if b == sa.FLUX else None), s1["blocks"][f"band:{b}"]):
            raise fs.Invalid(f"band {b}: the staged S1 unfolds do not reproduce the assembly's block exactly")
    cv_z = np.load(staged / "derivation" / f"{DER_TAG}_CV.npz", allow_pickle=False)
    cv_flat = np.asarray(cv_z["xsec_flat"], float)
    metas: dict = {}
    blk = mode_blocks(unfolds, tag, U, g, w, cv_flat, metas)
    flux_staged = {r["sha256"] for r in json.loads((staged / "staged.json").read_text())["staged"] if r["role"] == "flux-file"}
    if len(flux_staged) != 1 or metas["A_CV"]["flux_file_sha256"] not in flux_staged:
        raise fs.Invalid("the products' flux file is not the staged one")
    A = {b: np.diag(blk["A"][b]) for b in BANDS}
    B = {b: np.diag(blk["B"][b]) for b in BANDS}
    D = {b: np.diag(blk["Dnom"][b]) for b in BANDS}
    # the floors: I0's measured ones, committed (i0.json), at the upper level; per band x the estimator's factor
    if r0.get("floor", {}).get("kind") != "measured":
        raise fs.Invalid("I0's floor is not the measured one")
    k = r0["floor"]["upper_factor"]
    sd2, sn2 = k["data"] * np.asarray(r0["sigma_J_data"]) ** 2, k["nom"] * np.asarray(r0["sigma_J_nom_carried"]) ** 2
    nf = {b: inv.noise_factor(b, w) for b in BANDS}

    def sets(bs):
        e, m, a, bb, dn = (sum(X[b] for b in bs) for X in (E, M, A, B, D))
        f_d, f_n, f_u = (sum(nf[b] for b in bs) * x for x in (sd2, sn2, sn2 / g ** 2))
        F = factors(e, bb, a, m)
        F["kappa"] = np.sqrt(dn / (a / g ** 2))
        res = {"F_src": ~noise(e, bb, f_n, f_n), "F_side": ~noise(bb, a, f_n, f_n), "F_truth": ~noise(a, m, f_n, f_d),
               "kappa": ~noise(dn, a / g ** 2, f_u, f_u)}
        res["total"] = ~noise(e, m, f_n, f_d)
        return F, res

    out_bands, out_groups = {}, {}
    for name, bs, sink in ([(b, (b,), out_bands) for b in BANDS] + [(gname, gbs, out_groups) for gname, gbs in GROUPS.items()]):
        with np.errstate(divide="ignore", invalid="ignore"):
            F, res = sets(bs)
            prod = F["F_src"] * F["F_side"] * F["F_truth"]
        ok = np.isfinite(prod) & np.isfinite(F["total"])
        if not np.allclose(prod[ok], F["total"][ok], rtol=1e-12, atol=0):
            raise fs.Invalid(f"{name}: the identity rho = F_src F_side F_truth fails")
        allres = res["F_src"] & res["F_side"] & res["F_truth"] & res["total"]
        out_cells = [c for c in range(sa.N_CELLS) if allres[c] and not in_window(F["total"][c])]
        attr = {cells[c]: attribute(F, c) for c in out_cells}
        sink[name] = {"factors": {kk: v.tolist() for kk, v in F.items()},
                      "resolved": {kk: [cells[c] for c in range(sa.N_CELLS) if v[c]] for kk, v in res.items()},
                      "rule_S": rule_s(F["F_src"], res["F_src"]), "rule_F": {"attribution": attr, **level(attr)},
                      "rule_K": rule_k(F["kappa"], res["kappa"])}
    # descriptive: HF2, the Flux normalization-only block, and the detector dump's arrays against the CV's
    a_cv = inv.load_npz(unfolds / f"{tag}_A_CV.npz")
    edges = [np.asarray(e, float) for e in metas["A_CV"]["edges"]]
    a_phi = flux_norm_block(cv_flat, edges, blk["phi_flux"], a_cv["cv_flux"], U, g, w)
    desc = {"sqrt_A_phi_over_A_flux": np.sqrt(np.diag(a_phi) / A[sa.FLUX]).tolist(),
            "detector_dump_equals_cv": {u: {k: metas[f"A_{u}"]["mode_info"].get(k) for k in ("wt_equals_cv", "denom_equals_cv")}
                                        for u in universes() if band_of(u) in sa.DETECTOR_BANDS}}
    return {"schema": SCHEMA, "step": "readout", "label": "DERIVATION", "cells": cells, "window": list(WINDOW),
            "resolve_k": RESOLVE_K, "bands": out_bands, "groups": out_groups, "descriptive": desc,
            "gate_d_sha256": sa.sha256(gate_d), "diag_sha256": sa.sha256(diag_json), "i0_sha256": sa.sha256(i0_json)}


# ------------------------------------------------------------------------------------------------------------ main


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("stage")
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("unfold")
    p.add_argument("--mode", choices=MODES, required=True)
    p.add_argument("--universes", required=True)
    for k in ("npz", "bkg", "bank", "detector-dir", "flux-file", "pins", "out"):
        p.add_argument(f"--{k}", type=Path, required=True)
    p.add_argument("--expect-pins-sha256", required=True)
    p.add_argument("--threads", type=int, default=int(os.environ.get("SLURM_CPUS_PER_TASK", "32")))
    p.add_argument("--tag", default=TAG)
    p = sub.add_parser("walls")
    p.add_argument("--unfolds", type=Path, required=True)
    p.add_argument("--tag", default=TAG)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("readout")
    for k in ("staged", "unfolds", "gate-d", "diag", "i0", "out"):
        p.add_argument(f"--{k}", type=Path, required=True)
    p.add_argument("--tag", default=TAG)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "unfold":
            return run_unfold(a)
        if a.out.exists():
            raise Refusal(f"refusing to overwrite {a.out}")
        if a.cmd == "stage":
            rec = inv.stage(json.loads(a.spec.read_text()), a.out)
            (a.out / "staged.json").write_text(json.dumps(rec, indent=1) + "\n")
            print(json.dumps({"staged": len(rec["staged"]), "missing": rec["missing"]}))
            return 0 if not rec["missing"] else 3
        if a.cmd == "walls":
            res = pilot_walls(a.unfolds, a.tag)
            a.out.write_text(json.dumps(res, indent=1) + "\n")
            print(json.dumps({"out": str(a.out), "verdict": res["verdict"]}))
            return 0 if res["verdict"] == "PASS" else 1
        res = readout(a.staged, a.unfolds, a.gate_d, a.diag, a.i0, a.tag)
        res["code_sha256"] = {"fd_1b_precheck_fd.py": sa.sha256(Path(__file__).resolve())}
        a.out.write_text(json.dumps(res, indent=1) + "\n")
        print(json.dumps({"out": str(a.out), "S": {k: v["rule_S"]["verdict"] for k, v in res["groups"].items()},
                          "K": {k: v["rule_K"]["verdict"] for k, v in res["groups"].items()}}))
        return 0
    except (Refusal, fs.Invalid, SystemExit, ValueError, OSError) as e:
        if isinstance(e, SystemExit) and not isinstance(e.code, str):
            raise
        print(f"[fd-1b-precheck-fd] refusing: {type(e).__name__}: {e}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())
