#!/usr/bin/env python3
"""LL5D amendment A1b (LL5D-DECLARATION.md at 1acdee66, sections 3-7, 10, 11): the unfolds, the walls, clipcheck, the
null and the readout of the like-for-like 5D coverage test, read without (``minus2``, primary) and with (``all``)
GEANT_Neutron and GEANT_Proton. Binding 3 (LL5D-BINDING-1.md ruling 4); it implements the declaration as bound at M,
and reads from A1a's jobs only the gate's PASS or STOP, the sealed clip-prep products for section 5.3, and each
evaluation's clipped variance ratio r_c for the weakened label (the director's rulings of 2026-11-08).

A new module beside A1a's ll5d.py, which it imports unchanged (bound code is not edited in place): a named departure
from section 12's single-module wording (the director, 2026-11-08).

Subcommands:
* ``unfold``: products for one truth and role, the items comma-separated. Roles: ``central`` (d_T at its means, S1's
  path, seed 42), ``seed`` (the same at seed 45), ``block`` (d_T with one universe's MC, S1's path: the 175 blocks),
  ``stat`` (set A's replica b of the realization d~_T), ``toy`` (``<reading>_<seed>``: the nature, its per-row first
  order composite clipped row by row, Poisson pseudo-data at lambda+, the nominal MC with set A's streams),
  ``clipmean`` (``<reading>``: d_T plus the mean clipped mass |lambda-| over the declared draws, from the sealed
  clip-prep file, S1's path) and ``control`` (the four procedure controls, on the data).
* ``walls``: the pilot's 13 products, each unfold within the unit and the RSS limit, or REPRICE.
* ``clipcheck``: section 5.3, per truth and reading, o_c = U (x_clipmean - x_T)_c / sigma_c - tau_c against delta* =
  0.667 with S1's reported sigma as the proxy: TO_JOSEPH or PROCEED.
* ``null``: per truth, both readings: the blocks remade at T from the products (``minus2`` without the two bands'
  blocks, with the removal control), and the draw-matched nulls at the reading's seeds, for C_T and C_T^- (MEC).
* ``readout``: per truth, both readings: section 6's grade, the Cholesky reading rule, the weakened label, and section
  7's readouts, including the readings' differences, which describe; neither reading tests the other.

MEASURES, when run: products, a null, a grade per (truth, reading). CANNOT AUTHORIZE: a coverage statement beyond
section 13's licences, any change to the reported covariance, or a repair after a STOP (#939).
"""
from __future__ import annotations

import argparse
import hashlib
import io
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
import fd_1b_mc as mc  # noqa: E402
import fd_1b_null as fn  # noqa: E402
import fd_1b_score as fs  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import ll5d  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_universe  # noqa: E402

SCHEMA = "ll5d-b/1"
TAG = "ll5d"
ROLES = ("central", "seed", "block", "stat", "toy", "clipmean", "control")
TRUTHS, READINGS, REMOVED = ll5d.TRUTHS, ll5d.READINGS, ll5d.REMOVED
EVALUATIONS = ll5d.EVALUATIONS
SEED_CHECK = mc.SEED_CHECK                    # 45
STAT_REPLICAS = mc.STAT_REPLICAS              # set A's 1..50
CONTROLS = mc.CONTROLS                        # setA_b1, MaRES_0, Flux_0, GEANT_Pion_0 (section 10)
UNIT_SECONDS = mc.UNIT_SECONDS                # 1,062 s (section 9)
RSS_LIMIT_KIB = mc.RSS_LIMIT_KIB
CLIP_DELTA_STAR = 0.667                       # section 5.3
WEAK_RATIO = 0.9                              # the 11-03 clip rule item 4: "below 0.9", strict
GATE_KEYS = ("schema", "step", "truth", "verdict", "record")   # the only gate-record keys A1b reads
GATE_RECORD_PATH = ("record", "b", "<evaluation>", "variance_ratio", "option_1_clipped")
REMOVAL_TOL = 1e-12                           # C_T^(-2) against C_T - C_GN - C_GP, of max |C_T| (section 4)
N_DECLARED = len(ll5d.TOY_SEEDS["g18"])       # 300
PILOT = ([("data", "control", c) for c in CONTROLS] + [(t, "central", "T") for t in TRUTHS]
         + [(t, "clipmean", rd) for t in TRUTHS for rd in READINGS]
         + [("g18", "toy", f"{rd}_{ll5d.TOY_SEEDS['g18'][0]}") for rd in READINGS] + [("ar23", "stat", "1")])


class Refusal(RuntimeError):
    """An input or invariant is not what the step is defined on: INVALID, reported unrepaired."""


# ----------------------------------------------------------------------------------------------- the items


def product_name(truth: str, role: str, item: str) -> str:
    return f"{TAG}_{truth}_{role}_{item}.npz"


def items(truth: str) -> list[tuple[str, str]]:
    """Every product of a truth (section 9): central, seed, the 175 blocks, 50 stat replicas, 600 toys and 2 clipmeans:
    829. The four controls are the data's."""
    _, _, tags = ll5d.layout("all")
    out = [("central", "T"), ("seed", "T")] + [("block", u) for u in tags]
    out += [("stat", str(b)) for b in STAT_REPLICAS]
    out += [("toy", f"{rd}_{s}") for rd in READINGS for s in ll5d.TOY_SEEDS[truth]]
    return out + [("clipmean", rd) for rd in READINGS]


def parse_toy(item: str, truth: str) -> tuple[str, int]:
    reading, _, seed = item.partition("_")
    if reading not in READINGS or not seed.isdigit() or int(seed) not in ll5d.TOY_SEEDS[truth]:
        raise Refusal(f"toy item {item!r} is not <reading>_<one of {truth}'s declared seeds>")
    return reading, int(seed)


# ------------------------------------------------------------------------------------------------- the nature


def nature_inputs(world: dict, load, tags: list[str], r: np.ndarray) -> tuple[dict, dict, dict, dict]:
    """Sections 3.3-3.4 for one nature: each universe of ``tags`` (the draw's order) streamed once, its arrays as
    fd_1b_mc._single (universe_inputs) gives them, its tdw rows the bank's or, for a detector universe, tdw_ref; each
    per-row array composed in compose's order a_D = a_u1 + sum_{j>=2} (a_uj - a_ref) (a_ref the CV's, tdw_ref for tdw);
    then each tree clipped on its own composite, row by row: w_truth+ = max(wt_D, 0), tdw+ = max(tdw_D, 0) histogrammed
    by s5p_universe.denominator, w_reco+ = max(wr_D, 0) and bkg_w+ = max(bkgw_D, 0), which with r_T > 0 are lambda+.
    The truth's flux is the one Flux universe's Phi_u (a toy's draw holds exactly one; the k = 1 control's single
    non-flux universe keeps Phi_CV, as universe_inputs does). Returns (ui, ub) for fd_1b_mc.toy_experiment, the composites,
    and the descriptive record (section 3.4's counts and masses, section 7's clipping record, N1's maxima)."""
    inputs, bkg, bank_cv = world["inputs"], world["bkg"], world["bank_cv"]
    tdw_ref = world["tdw_ref"]
    refs = {"wt": np.asarray(inputs["w_truth"], float), "wr": np.asarray(inputs["w_reco"], float),
            "bkgw": np.asarray(bkg["bkg_w"], float), "tdw": np.asarray(tdw_ref, float)}
    acc, peak, phis = {}, {}, []
    for j, tag in enumerate(tags):
        _, zero = load(tag)
        single, phi = mc._single(inputs, bkg, bank_cv, tag, zero, world["flux"])
        arr = {"wt": single["wt"], "wr": single["wr"], "bkgw": single["bkgw"],
               "tdw": np.asarray(zero["tdw"], float) if "tdw" in zero else refs["tdw"]}
        if phi is not None:
            phis.append(np.asarray(phi, float))
        for q, a in arr.items():
            a = np.asarray(a, float)
            if j == 0:
                acc[q], peak[q] = a.copy(), np.abs(a)
            else:
                acc[q] += a - refs[q]
                np.maximum(peak[q], np.abs(a), out=peak[q])
        del single, zero, arr
    if len(phis) > 1:
        raise Refusal(f"a nature holds {len(phis)} Flux universes")
    edges = inputs["edges"]
    wtp, tdp = np.maximum(acc["wt"], 0.0), np.maximum(acc["tdw"], 0.0)
    dn = np.asarray(s5p_universe.denominator(bank_cv, tdp, edges), float)
    ui = dict(inputs, w_truth=wtp, w_reco=np.maximum(acc["wr"], 0.0), denom_nd=dn,
              flux=phis[0] if phis else np.asarray(inputs["flux"], float))   # k = 1 without Flux keeps Phi_CV
    ub = dict(bkg, bkg_w=np.maximum(acc["bkgw"], 0.0))
    return ui, ub, acc, nature_record(world, acc, peak, dn, r)


def nature_record(world: dict, acc: dict, peak: dict, dn: np.ndarray, r: np.ndarray) -> dict:
    """Descriptive, per nature: N1's maxima per array; the clipped fractions |sum lambda-| / sum lambda (signal on the
    reco-passing rows, background); the fine cells with dn+ = 0 < d_ref and with ofin+ = 0 < ofin_CV; and the clipped
    masses per fine cell (signal |lambda-| at the reco cells plus background at theirs; w_truth at the gen cells; tdw at
    the denominator rows' cells), as arrays for the product."""
    inputs, bkg, bank_cv = world["inputs"], world["bkg"], world["bank_cv"]
    edges = inputs["edges"]
    nf = int(np.prod([np.asarray(e).size - 1 for e in edges]))
    reco, ptru = np.asarray(inputs["pass_reco"], bool), np.asarray(inputs["pass_truth"], bool)
    gen = np.where(ptru, ll5d.flat_cells(np.asarray(inputs["MCgen"], float), edges), -1)
    rc = np.where(reco, ll5d.flat_cells(np.asarray(inputs["MCreco"], float), edges), -1)
    bc = ll5d.flat_cells(np.asarray(bkg["bkg_reco"], float), edges)
    td = ll5d.td_cells(bank_cv, edges)
    lam = acc["wr"] * r
    d_ref = np.asarray(s5p_universe.denominator(bank_cv, world["tdw_ref"], edges), float).ravel()
    ofin = ll5d._bins(gen, np.maximum(acc["wt"], 0.0), nf)
    ofin_cv = ll5d._bins(gen, np.asarray(inputs["w_truth"], float), nf)
    n1 = {q: float(np.max(ll5d.n1_ratio(acc[q], peak[q]))) for q in acc}
    rec = {"n1_max": n1,
           "clipped_fraction_signal": float(ll5d.clipped_fraction(np.minimum(lam[reco], 0.0).sum(), lam[reco].sum())),
           "clipped_fraction_background": float(ll5d.clipped_fraction(np.minimum(acc["bkgw"], 0.0).sum(),
                                                                      acc["bkgw"].sum())),
           "fine_cells_dn0_where_ref_positive": int(np.sum((dn.ravel() == 0) & (d_ref > 0))),
           "fine_cells_ofin0_where_cv_positive": int(np.sum((ofin == 0) & (ofin_cv > 0)))}
    arrays = {"clip_reco_fine": ll5d._bins(rc, np.maximum(-lam, 0.0), nf) + ll5d._bins(bc, np.maximum(-acc["bkgw"], 0.0), nf),
              "clip_truth_wt_fine": ll5d._bins(gen, np.maximum(-acc["wt"], 0.0), nf),
              "clip_tdw_fine": ll5d._bins(td, np.maximum(-acc["tdw"], 0.0), nf)}
    return {"record": rec, "arrays": arrays}


# ----------------------------------------------------------------------------------------- the clip-prep file


def read_clip_prep(path: Path, want_sha256: str) -> dict:
    """The gate's sealed clip-prep products (A1a section 5j), read once through O_NOATIME by the digest the gate record
    gives; a mismatch refuses. Only section 5.3's consumers (clipmean, clipcheck) call this."""
    with inv.open_noatime(path) as fh:
        raw = fh.read()
    if hashlib.sha256(raw).hexdigest() != want_sha256:
        raise Refusal(f"{path}: the clip-prep products are not the sealed file the gate recorded")
    z = np.load(io.BytesIO(raw), allow_pickle=False)
    out = {k: np.asarray(z[k]) for k in z.files}
    for rd in READINGS:
        if int(out[f"draws_{rd}"]) != N_DECLARED:
            raise Refusal(f"the clip-prep products hold {int(out[f'draws_{rd}'])} {rd} draws, not {N_DECLARED}")
    return out


def clipmean_experiment(inputs: dict, bkg: dict, r: np.ndarray, cp: dict, reading: str) -> tuple[dict, np.ndarray]:
    """Section 5.3's clipmean: d_T at its means (fd_1b_mc.mean_experiment) plus, as observed events at their counts,
    each row's mean |lambda-| over the declared draws (signal rows at their reco coordinates, background rows at
    theirs), inside the analysis window as build_full keeps its events (1B's clipmean_experiment's construction)."""
    exp, x_true = mc.mean_experiment(inputs, bkg, r)
    sig = np.asarray(cp[f"signal_negative_lambda_sum_{reading}"], float) / N_DECLARED
    bm = np.asarray(cp[f"background_negative_lambda_sum_{reading}"], float) / N_DECLARED
    reco = np.asarray(inputs["pass_reco"], bool)
    s_rows, b_rows = reco & (sig > 0), bm > 0
    coords = np.concatenate([np.asarray(inputs["MCreco"])[s_rows], np.asarray(bkg["bkg_reco"])[b_rows]])
    counts = np.concatenate([sig[s_rows], bm[b_rows]])
    keep = s5n_pseudo.fid_mask(coords, inputs["edges"])
    exp = dict(exp, obs=np.concatenate([exp["obs"], coords[keep]]),
               obs_counts=np.concatenate([exp["obs_counts"], counts[keep]]))
    return exp, x_true


# ------------------------------------------------------------------------------------------------ the unfolds


def run_item(a, world: dict, role: str, item: str, unfold_fn=None) -> tuple[dict, dict]:
    """One product's arrays and meta (sections 3.5, 4, 5.3, 10)."""
    inputs, bkg = world["inputs"], world["bkg"]
    load = lambda tag: ll5d.verified_weights(world, a, tag)  # noqa: E731
    zero = lambda tag: load(tag)[1]  # noqa: E731
    arrays, meta = {}, {}
    if role == "control":
        if item not in CONTROLS:
            raise Refusal(f"{item} is not a declared procedure control")
        if item == "setA_b1":
            xs, ev = (unfold_fn or mc._unfold_one64)(mc.stat_experiment(inputs, bkg, None, None, 1), a.threads)
        else:
            ui, ub, info = mc.compose(inputs, bkg, world["bank_cv"], [item], zero, world["flux"])
            xs, ev = (unfold_fn or mc._unfold_one32)(s5n_pseudo.build_data(ui, ub), a.threads)
        arrays = {"xsec_flat": np.asarray(xs, float).ravel(order="C")}
        meta.update(ev)
        return check_finite(arrays), meta
    t = a.truth
    r, ctl = ll5d.truths_r(world, a.prep, [t])
    if not ctl[t]["passes"]:
        raise Refusal(f"r_T > 0 fails at {t}: {ctl[t]}")
    r = r[t]
    if role in ("central", "seed", "block"):
        exp, x_true = mc.mean_experiment(inputs, bkg, r)
        if role == "block":
            if item not in ll5d.layout("all")[2]:
                raise Refusal(f"{item} is not one of S1's 175 universes")
            ui, ub, info = mc.compose(inputs, bkg, world["bank_cv"], [item], zero, world["flux"])
            exp = mc.with_mc(exp, ui, ub)
            meta["universe_info"] = info
        elif item != "T":
            raise Refusal(f"{role} takes the item T")
        seed = SEED_CHECK if role == "seed" else toys.ESTIMATOR_SEED
        xs, ev = (unfold_fn or mc._unfold_s1)(exp, a.threads, seed)
        arrays = {"xsec_flat": xs.ravel(order="C"), "xtrue_flat": np.asarray(x_true, float).ravel(order="C")}
        meta.update(ev)
    elif role == "stat":
        b = int(item)
        if b not in STAT_REPLICAS:
            raise Refusal(f"stat replica {b} is not one of set A's")
        exp = mc.stat_experiment(inputs, bkg, r, ll5d.STAT_SEED[t], b)
        xs, ev = (unfold_fn or mc._unfold_one64)(exp, a.threads)
        arrays = {"xsec_flat": np.asarray(xs, float).ravel(order="C")}
        meta.update(ev, stat_seed=ll5d.STAT_SEED[t], bootstrap_seed=b, jitter_seed=mc.JITTER_OFFSET + b)
    elif role == "toy":
        reading, seed = parse_toy(item, t)
        d = toys.draw_for_seed(seed, mc.via_noatime(toys.flux_probabilities, a.flux_constraint), world["groups"])
        tags = ll5d.reading_draws([mc.draw_universes(d)], reading)[0]
        if sum(x.rpartition("_")[0] == sa.FLUX for x in tags) != 1:
            raise Refusal(f"toy {item}: its draw does not hold exactly one Flux universe")
        ui, ub, _, nrec = nature_inputs(world, load, tags, r)
        exp, x_true = mc.toy_experiment(inputs, bkg, ui, ub, r, seed)
        x_true = np.asarray(x_true, float)
        if not np.all(np.isfinite(x_true)):
            raise Refusal("a non-finite truth")
        xs, ev = (unfold_fn or mc._unfold)(exp, a.threads)
        arrays = {"xsec_flat": xs.ravel(order="C"), "xtrue_flat": x_true.ravel(order="C"), **nrec["arrays"]}
        meta.update(ev, draw=d, reading=reading, universes=tags, nature=nrec["record"])
    elif role == "clipmean":
        if item not in READINGS:
            raise Refusal(f"clipmean takes a reading, not {item!r}")
        cp = read_clip_prep(a.clip_prep, a.expect_clip_prep_sha256)
        exp, x_true = clipmean_experiment(inputs, bkg, r, cp, item)
        xs, ev = (unfold_fn or mc._unfold_s1)(exp, a.threads, toys.ESTIMATOR_SEED)
        arrays = {"xsec_flat": xs.ravel(order="C"), "xtrue_flat": np.asarray(x_true, float).ravel(order="C")}
        meta.update(ev, clip_prep_sha256=a.expect_clip_prep_sha256, reading=item)
    else:
        raise Refusal(f"role {role!r}")
    return check_finite(arrays), meta


def check_finite(arrays: dict) -> dict:
    if not np.all(np.isfinite(arrays["xsec_flat"])):
        raise Refusal("a non-finite unfolded value")
    return arrays


def run_unfold(a, unfold_fn=None) -> int:
    """The unfold job: one truth and role, the items in order; an existing product is kept (resumable)."""
    import s5e_candidate
    inv.OPENED.clear()
    s5e_candidate.install(toys.CONFIG)
    if a.role not in ROLES:
        raise Refusal(f"role {a.role!r}")
    if (a.role == "control") != (a.truth == "data"):
        raise Refusal("the control role runs on the data (--truth data), and only it")
    if a.role == "clipmean" and (a.clip_prep is None or a.expect_clip_prep_sha256 is None):
        raise Refusal("clipmean needs --clip-prep and its sealed sha256")
    world, _ = ll5d.load_world(a)
    a.out.mkdir(parents=True, exist_ok=True)
    status = 0
    for item in a.items.split(","):
        target = a.out / product_name(a.truth, a.role, item)
        if target.exists():
            continue
        toys.check_pins(world["pins"], a.bank, a.detector_dir)
        t1 = time.time()
        arrays, extra = run_item(a, world, a.role, item, unfold_fn)
        meta = {"schema": SCHEMA, "truth": a.truth, "role": a.role, "item": item, "config": toys.CONFIG,
                "iters": toys.ITERS, "estimator_seed": SEED_CHECK if a.role == "seed" else toys.ESTIMATOR_SEED,
                "threads": a.threads, **extra, "input_npz_sha256": world["npz_sha"], "bkg_dump_sha256": world["bkg_sha"],
                "pins_sha256": a.expect_pins_sha256, "flux_table_sha256": a.expect_flux_table_sha256,
                "tdw_ref_sha256": ll5d.TDW_REF_SHA256, "code_sha256": code_digests(),
                "slurm_job": os.environ.get("SLURM_JOB_ID"), "seconds_unfold": round(time.time() - t1, 3),
                "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "numpy_version": np.__version__}
        status |= s5n_pseudo.write_product(target, arrays, meta)
        print(json.dumps({"out": target.name, "seconds_unfold": meta["seconds_unfold"]}), flush=True)
    chk = inv.atime_check()
    (a.out / f"atime-{a.truth}-{a.role}-{os.environ.get('SLURM_JOB_ID', 'local')}-{os.getpid()}.json").write_text(
        json.dumps(chk, indent=1) + "\n")
    if chk["moved"]:
        print(f"[ll5d-b] DEVIATION: atime moved on {chk['moved']}", file=sys.stderr)
        return status | ll5d.ATIME_RC
    return status


def code_digests() -> dict:
    mods = {"ll5d_b.py": Path(__file__), **{k: Path(v) for k, v in (
        ("fd_1b_mc.py", mc.__file__), ("fd_1b_null.py", fn.__file__), ("fd_1b_score.py", fs.__file__),
        ("fd_1b_toys.py", toys.__file__), ("s5n_pseudo.py", s5n_pseudo.__file__), ("s5p_universe.py", s5p_universe.__file__),
        ("s1_assemble.py", sa.__file__))}}
    out = {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in mods.items()}
    out.update({f"ll5d:{k}": v for k, v in ll5d.code_digests().items()})
    return out


# -------------------------------------------------------------------------------------------------- the walls


def walls(unfolds: Path) -> dict:
    """Section 9's re-price trigger over the pilot's 13 products: every one present, each unfold within the unit
    (1,062 s) and its peak RSS within S1's per-lane limit; else REPRICE (an amendment)."""
    rows = []
    for truth, role, item in PILOT:
        name = product_name(truth, role, item)
        p = unfolds / name
        if not p.exists():
            return {"verdict": "REPRICE", "why": f"missing {name}", "rows": rows}
        m = json.loads(str(np.load(p, allow_pickle=False)["meta"]))
        rows.append({"product": name, "seconds_unfold": m["seconds_unfold"], "peak_rss_kib": m["peak_rss_kib"]})
    s_max, r_max = max(r["seconds_unfold"] for r in rows), max(r["peak_rss_kib"] for r in rows)
    ok = s_max <= UNIT_SECONDS and r_max <= RSS_LIMIT_KIB
    return {"verdict": "PASS" if ok else "REPRICE", "max_seconds_unfold": s_max, "max_peak_rss_kib": r_max,
            "unit_seconds": UNIT_SECONDS, "rss_limit_kib": RSS_LIMIT_KIB, "rows": rows}


# ------------------------------------------------------------------------------------------------ clipcheck


def _x(unfolds: Path, truth: str, role: str, item: str, key: str = "xsec_flat") -> np.ndarray:
    with inv.open_noatime(unfolds / product_name(truth, role, item)) as fh:
        return np.asarray(np.load(fh, allow_pickle=False)[key], float)


def clip_offset(U: np.ndarray, x_clipmean: np.ndarray, x_T: np.ndarray, sigma: np.ndarray, cp: dict,
                reading: str) -> dict:
    """Section 5.3 for one (truth, reading): tau_c = mean over the declared draws of U (T_D clipped - T_D unclipped) /
    sigma_c, and o_c = U (x_clipmean - x_T)_c / sigma_c - tau_c (its sign the error's, e = x_hat - T)."""
    tc = np.asarray(cp[f"U_T_clipped_{reading}"], float)
    tu = np.asarray(cp[f"U_T_unclipped_{reading}"], float)
    if tc.shape != (N_DECLARED, sa.N_CELLS) or tu.shape != tc.shape:
        raise Refusal(f"{reading}: the clip-prep truths are not {N_DECLARED} x {sa.N_CELLS}")
    truth_shift = (tc - tu).mean(axis=0)
    unfold_shift = U @ x_clipmean - U @ x_T
    tau = truth_shift / sigma
    o = unfold_shift / sigma - tau
    return {"tau_c": tau.tolist(), "o_c": o.tolist(), "unfold_shift": unfold_shift.tolist(),
            "truth_shift": truth_shift.tolist(),
            "cells_at_or_above_delta_star": [f"R{c:02d}" for c in range(o.size) if abs(o[c]) >= CLIP_DELTA_STAR]}


def clipcheck(a) -> dict:
    """Section 5.3's rule, fixed before any number: any cell at any (truth, reading) with |o_c| >= delta* = 0.667 is
    TO_JOSEPH, before any bulk; otherwise PROCEED. sigma_c's proxy is S1's reported sigma at the data
    (fd_1b_score.reported_matrix); the readout recomputes o_c with C_T."""
    s1 = mc.via_noatime(fs.load_s1, a.staged / "s1" / "s1_assembly.npz")
    U = sa.functional_matrix(sa.fine_map(a.definition))
    if not ll5d.same_functional(U, s1["U"]):
        raise Refusal("the definition's functional is not S1's")
    sigma = np.sqrt(np.diag(fs.reported_matrix(s1)))
    out, hit = {}, []
    for t, path, sha in zip(a.truths, a.clip_prep, a.expect_clip_prep_sha256):
        cp = read_clip_prep(path, sha)
        x_T = _x(a.unfolds, t, "central", "T")
        for rd in READINGS:
            m = json.loads(str(np.load(a.unfolds / product_name(t, "clipmean", rd), allow_pickle=False)["meta"]))
            if m.get("clip_prep_sha256") != sha:
                raise Refusal(f"{t}/{rd}: the clipmean was made from another clip-prep file")
            res = clip_offset(U, _x(a.unfolds, t, "clipmean", rd), x_T, sigma, cp, rd)
            out[f"{t}/{rd}"] = res
            hit += [f"{t}/{rd}:{c}" for c in res["cells_at_or_above_delta_star"]]
    return {"schema": SCHEMA, "step": "clipcheck", "delta_star": CLIP_DELTA_STAR, "evaluations": out,
            "sigma": "S1's reported (fd_data_product C_total_plus_C_resp), a proxy for C_T",
            "clip_prep_sha256": dict(zip(a.truths, a.expect_clip_prep_sha256)),
            "verdict": "TO_JOSEPH" if hit else "PROCEED", "cells": hit}


# --------------------------------------------------------------------------------------------- the blocks at T


def _cells(unfolds: Path, truth: str, role: str, its, U: np.ndarray) -> np.ndarray:
    return np.array([U @ _x(unfolds, truth, role, i) for i in its])


def bands_of(reading: str) -> list[str]:
    _, bands, _ = ll5d.layout(reading)
    return [b for b in sa.EXPECT if b in bands]


def remade(unfolds: Path, truth: str, s1: dict, U: np.ndarray, w_flux: np.ndarray, cmodel_frac: np.ndarray,
           reading: str) -> dict:
    """Section 4 at T for one reading: fd_1b_mc.remade's construction (S1's procedure on the products) over the
    reading's bands only. ``minus2`` leaves band:GEANT_Neutron and band:GEANT_Proton out of the sum and the null's laws;
    every other block, the laterals carried at T and the normalization, is the same."""
    X_T = _cells(unfolds, truth, "central", ["T"], U)[0]
    if not np.array_equal(X_T, _cells(unfolds, truth, "seed", ["T"], U)[0]):
        raise Refusal("the seed check failed: estimator seed 45 differs from 42 at T")
    blocks, laws = {}, []
    for band in bands_of(reading):
        n = sa.EXPECT[band]
        X = _cells(unfolds, truth, "block", [f"{band}_{i}" for i in range(n)], U)
        p = w_flux / w_flux.sum() if band == sa.FLUX else np.full(n, 1.0 / n)
        blocks[f"band:{band}"] = sa.mat_cov(X, w_flux if band == sa.FLUX else None)
        laws.append((f"band:{band}", fn.Discrete.centred(X, p), X))
    R = _cells(unfolds, truth, "stat", [str(b) for b in STAT_REPLICAS], U)
    blocks["stat"] = np.cov(R, rowvar=False, ddof=1)
    g = X_T / s1["f"]
    deltas = {}
    for b in sa.LATERAL_BANDS:
        B = s1["blocks"][f"lat:{b}"]
        k = int(np.argmax(np.diag(B)))
        v = B[:, k] / math.sqrt(B[k, k]) if B[k, k] > 0 else np.zeros_like(X_T)   # B = v v^T, v = Delta_b / 2
        deltas[b] = 2 * v
        blocks[f"lat:{b}"] = np.outer(v * g, v * g)
        laws.append((f"lat:{b}", fn.Discrete.two_point(2 * v * g), None))
    blocks["normalization"] = np.outer(sa.NORM_FRACTION * X_T, sa.NORM_FRACTION * X_T)
    C_e = sum(blocks.values())
    C_mabs = sa.model_abs(X_T, cmodel_frac)
    return {"X_T": X_T, "blocks": blocks, "C_e": C_e, "C_model_abs": C_mabs, "C_T": C_e + C_mabs, "laws": laws,
            "gauss": blocks["stat"] + blocks["normalization"] + C_mabs, "deltas": deltas, "stat_R": R}


def removal_control(rm_all: dict, rm_m2: dict) -> dict:
    """Section 4's control: C_T^(-2) equals C_T - C_GEANT_Neutron - C_GEANT_Proton to 1e-12 of max |C_T|, elementwise
    (not bitwise: the sums' order differs)."""
    want = rm_all["C_T"] - rm_all["blocks"]["band:GEANT_Neutron"] - rm_all["blocks"]["band:GEANT_Proton"]
    dev = float(np.max(np.abs(rm_m2["C_T"] - want)))
    lim = REMOVAL_TOL * float(np.max(np.abs(rm_all["C_T"])))
    return {"max_abs_dev": dev, "limit": lim, "passes": bool(dev <= lim)}


def products_digest(unfolds: Path, truth: str, roles: tuple[str, ...]) -> str:
    """One digest over the named roles' products at T, so the null pins exactly the products it was made from."""
    left = sorted(p.name for p in unfolds.glob(f"{TAG}_{truth}_*.partial-*"))
    if left:
        raise Refusal(f"partial products are present: {left[:3]}")
    h = hashlib.sha256()
    for p in sorted(unfolds.glob(f"{TAG}_{truth}_*.npz")):
        if p.name.split("_")[2] in roles:
            h.update(p.name.encode())
            h.update(s5n_pseudo.sha256_path(p).encode())
    return h.hexdigest()


BLOCK_ROLES = ("central", "seed", "block", "stat")


def setup(a) -> tuple[dict, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    s1 = mc.via_noatime(fs.load_s1, a.staged / "s1" / "s1_assembly.npz")
    U = sa.functional_matrix(sa.fine_map(a.definition))
    if not ll5d.same_functional(U, s1["U"]):
        raise Refusal("the definition's functional is not S1's")
    frac, minus = mc.cmodel_parts(a.staged / "s1" / "s1_assembly.npz", a.cmodel_json)
    w = mc.via_noatime(sa.flux_weights, a.flux_constraint)
    return s1, U, frac, minus, w


def null_step(a) -> dict:
    """Section 6's null at T, both readings, from the remade products only, before any toy error is read: the
    removal control, then per reading the draw-matched null for C_T and for C_T^- (leave-out-MEC) at the reading's
    seed (section 3.6), 2,000,000 error vectors, check_matched at 1e-12."""
    s1, U, frac, minus, w = setup(a)
    rms = {rd: remade(a.unfolds, a.truth, s1, U, w, frac, rd) for rd in READINGS}
    ctl = removal_control(rms["all"], rms["minus2"])
    out = {"schema": SCHEMA, "step": "null", "truth": a.truth, "removal_control": ctl,
           "products_sha256": products_digest(a.unfolds, a.truth, BLOCK_ROLES), "made_from": mc.made_from(a, U)}
    if not ctl["passes"]:
        out["verdict"] = "INVALID"
        return out
    for rd, rm in rms.items():
        e = f"{a.truth}/{rd}"
        laws = [law for _, law, _ in rm["laws"]]
        out[e] = {}
        for name, C_mabs in (("C_T", rm["C_model_abs"]), ("C_T_minus_mec", sa.model_abs(rm["X_T"], minus))):
            C = rm["C_e"] + C_mabs
            null = fn.null_contents(laws, rm["blocks"]["stat"] + rm["blocks"]["normalization"] + C_mabs, C,
                                    seed=ll5d.NULL_SEED[e])
            thr = fn.thresholds(null)
            out[e][name] = {"p_cell": null["p_cell"].tolist(), "se_cell": null["se_cell"].tolist(),
                            "q_joint": null["q_joint"], "se_joint": null["se_joint"], "ndf": null["ndf"],
                            "chi2_cut": null["chi2_cut"], "n_mc": null["n_mc"], "seed": null["seed"],
                            "match_rel": null["match_rel"], "thresholds": thr, "size": fn.size(null, thr)}
    out["verdict"] = "PASS"
    return out


# ---------------------------------------------------------------------------------------------- the readout


def cholesky_tol(C: np.ndarray) -> dict:
    """COV2D-BINDING-2 addendum A5's tolerance, from C alone: max(1e-9, 10 kappa_2(C) eps), kappa_2 = lambda_max /
    lambda_min (cov2d_readout.cholesky_tol's rule; a test holds them equal)."""
    lam = np.linalg.eigvalsh(np.asarray(C, np.float64))
    eps = float(np.finfo(np.float64).eps)
    kappa = float(lam[-1] / lam[0]) if lam[0] > 0 else float("inf")
    return {"rule": "max(1e-9, 10 kappa_2(C) eps)", "kappa2": kappa, "eps": eps, "tol": max(1e-9, 10 * kappa * eps)}


def reading_rule(chk: dict) -> dict:
    """The Cholesky reading rule (COV2D-BINDING-2's A5 M line, ruling 3, carried to 16 cells): a grade at ndf = 16 must
    show a finite kappa_2, a finite tol and a finite max_rel_diff <= tol, the grade having used that tol; otherwise its
    (truth, reading) is INVALID. A grade with no compared values fails."""
    fin = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)  # noqa: E731
    cmp = chk.get("compared") or {}
    if not cmp:
        return {"passes": False, "why": "no compared values"}
    if cmp.get("ndf") != sa.N_CELLS:
        return {"passes": True, "why": f"ndf {cmp.get('ndf')}: the rule applies at ndf {sa.N_CELLS} only"}
    k, tol, mrd = chk.get("kappa2"), chk.get("tol"), cmp.get("max_rel_diff")
    ok = fin(k) and fin(tol) and fin(mrd) and mrd <= tol and cmp.get("tol") == tol
    return {"passes": bool(ok), "why": "finite, max_rel_diff <= tol, the grade used the recorded tol" if ok else
            "not finite, or max_rel_diff > tol, or the grade's tol is not the recorded tol"}


def graded(E: np.ndarray, C: np.ndarray, null: dict) -> tuple[dict | None, dict, dict]:
    """fd_1b_mc.grade under A5's tolerance, with the compared values captured; a refusal is returned, not raised."""
    chk = cholesky_tol(C)
    compared: dict = {}
    try:
        g = mc.grade(E, C, null, chol_tol=chk["tol"], chol_out=compared)
    except mc.Refusal as exc:
        chk["compared"] = getattr(exc, "compared", compared)
        return None, chk, {"passes": False, "why": f"grade refused: {exc}"}
    chk["compared"] = compared
    return g, chk, reading_rule(chk)


def gate_ratios(path: Path, want_sha256: str, truth: str) -> dict:
    """The weakened label's input (the director's ruling on A1b): from the gate record, digest-pinned, ONLY each
    evaluation's per-cell clipped variance ratio r_c (record.b[e].variance_ratio.option_1_clipped). The record's keys
    are checked against GATE_KEYS read; nothing else is read."""
    with inv.open_noatime(path) as fh:
        raw = fh.read()
    if hashlib.sha256(raw).hexdigest() != want_sha256:
        raise Refusal("the gate record's digest is not the one given")
    g = json.loads(raw)
    seen = {k: g[k] for k in GATE_KEYS if k in g}
    if seen.get("truth") != truth or seen.get("verdict") != "PASS":
        raise Refusal(f"the gate record is {seen.get('truth')}/{seen.get('verdict')}, not {truth}/PASS")
    out = {}
    for rd in READINGS:
        e = f"{truth}/{rd}"
        r = np.asarray(seen["record"]["b"][e]["variance_ratio"]["option_1_clipped"], float)
        if r.shape != (sa.N_CELLS,):
            raise Refusal(f"{e}: the gate's clipped variance ratio is not {sa.N_CELLS} cells")
        out[e] = r
    return out


def weakened(cell_flag: list[bool], ratio: np.ndarray) -> dict:
    """The 11-03 clip rule item 4: a pass in a cell whose clipped variance ratio is below 0.9 (strictly) counts as
    weakened. Descriptive: it moves no verdict and changes no count."""
    w = [c for c in range(len(cell_flag)) if not cell_flag[c] and float(ratio[c]) < WEAK_RATIO]
    return {"weakened_cells": [f"R{c:02d}" for c in w], "share": len(w) / len(cell_flag), "threshold": WEAK_RATIO,
            "rule": "a pass with the gate's clipped variance ratio strictly below 0.9 (11-03 clip rule, item 4)"}


def toy_errors(unfolds: Path, truth: str, reading: str, U: np.ndarray, rm: dict, f: np.ndarray) -> tuple:
    """The reading's toys in seed order (exactly the declared seeds, no partials): e = x_hat - U T_D, x_hat the
    surrogate of the laterals and the normalization on the cell integrals (fd_1b_score.surrogate)."""
    left = sorted(p.name for p in unfolds.glob(f"{TAG}_{truth}_toy_*.partial-*"))
    if left:
        raise Refusal(f"partial products are present: {left[:3]}")
    have = sorted(p.name for p in unfolds.glob(f"{TAG}_{truth}_toy_{reading}_*.npz"))
    want = sorted(product_name(truth, "toy", f"{reading}_{s}") for s in ll5d.TOY_SEEDS[truth])
    if have != want:
        raise Refusal(f"{truth}/{reading}: the toy products are not exactly the declared seeds ({len(have)} of 300)")
    X_raw, X_true, draws, nat = [], [], [], []
    for s in ll5d.TOY_SEEDS[truth]:
        with inv.open_noatime(unfolds / product_name(truth, "toy", f"{reading}_{s}")) as fh:
            z = np.load(fh, allow_pickle=False)
            X_raw.append(U @ np.asarray(z["xsec_flat"], float))
            X_true.append(U @ np.asarray(z["xtrue_flat"], float))
            m = json.loads(str(z["meta"]))
        draws.append(m["draw"])
        nat.append(m["nature"])
    X_hat = fs.surrogate(np.array(X_raw), draws, rm["deltas"], f, rm["X_T"])
    return X_hat - np.array(X_true), draws, np.array(X_true), nat


def readout_reading(E: np.ndarray, rm: dict, null: dict, null_minus: dict, minus: np.ndarray, ratio: np.ndarray,
                    clip: dict, X_true: np.ndarray, nat: list, x_T_hat: np.ndarray, x_T_true: np.ndarray,
                    w_flux: np.ndarray) -> dict:
    """Section 6 and section 7 for one (truth, reading)."""
    g, chk, rule = graded(E, rm["C_T"], null)
    C_minus = rm["C_e"] + sa.model_abs(rm["X_T"], minus)
    gm, chk_m, rule_m = graded(E, C_minus, null_minus)
    rec = {"cholesky_check": chk, "cholesky_check_minus": chk_m, "reading_rule": {"C_T": rule, "C_T_minus": rule_m}}
    if not (rule["passes"] and rule_m["passes"]):
        rec["verdict"] = "INVALID"
        return rec
    sigma = np.sqrt(np.diag(rm["C_T"]))
    flagged = [c for c, fl in enumerate(g["cell_flag"]) if fl]
    o_CT = (np.asarray(clip["unfold_shift"]) - np.asarray(clip["truth_shift"])) / sigma    # section 5.3 under C_T
    sig_e = np.sqrt(np.diag(rm["C_e"]))
    offset = -sum(law.probs @ X - rm["X_T"] for _, law, X in rm["laws"] if X is not None)
    rec.update({
        "grade": g, "verdict": g["verdict"], "leave_out_mec": {"grade": gm, "changes_no_verdict": True},
        "weakened": weakened(g["cell_flag"], ratio),
        "clipping_artefact_reading": {f"R{c:02d}": bool(abs(o_CT[c]) >= CLIP_DELTA_STAR) for c in flagged},
        "readouts": {
            "spread_alone_vs_C_e": {"counts": np.sum(np.abs(E) <= sig_e, axis=0).tolist(),
                                    "pull_mean": (E / sig_e).mean(axis=0).tolist(),
                                    "pull_sd": (E / sig_e).std(axis=0, ddof=1).tolist()},
            "bias_over_sigma": (E.mean(axis=0) / sigma).tolist(),
            "predicted_offset_uncentred_draws": np.asarray(offset, float).tolist(),
            "clipping": {"o_c_under_C_T": o_CT.tolist(),
                         "clipped_fraction_signal": [n["clipped_fraction_signal"] for n in nat],
                         "clipped_fraction_background": [n["clipped_fraction_background"] for n in nat],
                         "fine_cells_dn0_where_ref_positive": [n["fine_cells_dn0_where_ref_positive"] for n in nat],
                         "fine_cells_ofin0_where_cv_positive": [n["fine_cells_ofin0_where_cv_positive"] for n in nat]},
            "realization_check": {"per_cell_sigma": ((x_T_hat - x_T_true) / sigma).tolist(),
                                  "what": "x_hat_T (the central unfold of d_T) against U T, per cell in sigma_c"}}})
    return rec


def readout(a) -> dict:
    """Sections 6-7 at one truth, both readings. The null is the committed one, by digest, made from these very
    products; the clip offsets are clipcheck's, by digest; the gate record is read only for r_c (gate_ratios)."""
    if inv.sha256_noatime(a.null) != a.expect_null_sha256:
        raise Refusal("the null's digest differs from the declared one")
    with inv.open_noatime(a.null) as fh:
        nl = json.loads(fh.read().decode())
    if nl.get("verdict") != "PASS" or nl["products_sha256"] != products_digest(a.unfolds, a.truth, BLOCK_ROLES):
        raise Refusal("the null was not made from these products, or did not pass")
    if inv.sha256_noatime(a.clipcheck) != a.expect_clipcheck_sha256:
        raise Refusal("clipcheck's digest differs from the declared one")
    with inv.open_noatime(a.clipcheck) as fh:
        cc = json.loads(fh.read().decode())
    s1, U, frac, minus, w = setup(a)
    if nl.get("made_from") != mc.made_from(a, U):
        raise Refusal("the definition, the cmodel json or U is not the one the null was made from")
    ratios = gate_ratios(a.gate, a.expect_gate_sha256, a.truth)
    x_T_hat = U @ _x(a.unfolds, a.truth, "central", "T")
    x_T_true = U @ _x(a.unfolds, a.truth, "central", "T", "xtrue_flat")
    out = {"schema": SCHEMA, "step": "readout", "truth": a.truth, "null_sha256": a.expect_null_sha256,
           "clipcheck_sha256": a.expect_clipcheck_sha256, "gate_sha256": a.expect_gate_sha256, "evaluations": {}}
    p_hat = {}
    for rd in READINGS:
        e = f"{a.truth}/{rd}"
        rm = remade(a.unfolds, a.truth, s1, U, w, frac, rd)
        E, draws, X_true, nat = toy_errors(a.unfolds, a.truth, rd, U, rm, s1["f"])
        clip = cc["evaluations"][e]
        out["evaluations"][e] = readout_reading(E, rm, mc._null_dict(nl[e]["C_T"]), mc._null_dict(nl[e]["C_T_minus_mec"]),
                                                minus, ratios[e], clip, X_true, nat, x_T_hat, x_T_true, w)
        g = out["evaluations"][e].get("grade")
        if g:
            p_hat[rd] = (np.asarray(g["counts"]) / E.shape[0], np.asarray(g["pull_mean"]))
    if set(p_hat) == set(READINGS):
        out["between_readings"] = {"p_hat_all_minus_minus2": (p_hat["all"][0] - p_hat["minus2"][0]).tolist(),
                                   "pull_mean_all": p_hat["all"][1].tolist(),
                                   "pull_mean_minus2": p_hat["minus2"][1].tolist(),
                                   "note": "descriptive; neither reading tests the other"}
    out["verdicts"] = {e: v.get("verdict") for e, v in out["evaluations"].items()}
    return out


# ----------------------------------------------------------------------------------------------------- main


def _world_args(p) -> None:
    for k in ("npz", "bkg", "bank", "detector-dir", "pins", "flux-constraint", "flux-table", "prep", "manifest"):
        p.add_argument(f"--{k}", type=Path, required=True)
    for k in ("pins", "flux-table", "manifest"):
        p.add_argument(f"--expect-{k}-sha256", required=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("unfold")
    _world_args(p)
    p.add_argument("--truth", choices=TRUTHS + ("data",), required=True)
    p.add_argument("--role", choices=ROLES, required=True)
    p.add_argument("--items", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--threads", type=int, default=1)
    p.add_argument("--clip-prep", type=Path, default=None)
    p.add_argument("--expect-clip-prep-sha256", default=None)
    p = sub.add_parser("walls")
    p.add_argument("--unfolds", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("clipcheck")
    for k in ("staged", "definition", "unfolds", "out"):
        p.add_argument(f"--{k}", type=Path, required=True)
    p.add_argument("--truths", nargs=2, choices=TRUTHS, required=True)
    p.add_argument("--clip-prep", type=Path, nargs=2, required=True)
    p.add_argument("--expect-clip-prep-sha256", nargs=2, required=True)
    for name in ("null", "readout"):
        p = sub.add_parser(name)
        for k in ("staged", "definition", "unfolds", "cmodel-json", "flux-constraint", "out"):
            p.add_argument(f"--{k}", type=Path, required=True)
        p.add_argument("--truth", choices=TRUTHS, required=True)
        if name == "readout":
            for k in ("null", "clipcheck", "gate"):
                p.add_argument(f"--{k}", type=Path, required=True)
                p.add_argument(f"--expect-{k}-sha256", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "unfold":
        return run_unfold(a)
    if a.out.exists():
        raise Refusal(f"refusing to overwrite {a.out}")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    inv.OPENED.clear()
    try:
        rec = {"walls": lambda: walls(a.unfolds), "clipcheck": lambda: clipcheck(a), "null": lambda: null_step(a),
               "readout": lambda: readout(a)}[a.cmd]()
    except (Refusal, ll5d.Refusal, mc.Refusal, inv.Refusal, toys.Refusal) as exc:     # section 10: INVALID, unrepaired
        bad = {"schema": SCHEMA, "step": a.cmd, "verdict": "INVALID", "why": str(exc), "atime": inv.atime_check()}
        a.out.with_suffix(".invalid.json").write_text(json.dumps(bad, indent=1, sort_keys=True))
        print(f"LL5D-{a.cmd.upper()} INVALID ({exc})")
        return 5 | (ll5d.ATIME_RC if bad["atime"]["moved"] else 0)
    rec["atime"] = inv.atime_check()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(rec, indent=1, sort_keys=True))
    print(f"LL5D-{a.cmd.upper()} verdict={rec.get('verdict', rec.get('verdicts'))}")
    rc = {"PASS": 0, "PROCEED": 0, "REPRICE": 4, "TO_JOSEPH": 3, "INVALID": 5}.get(rec.get("verdict"), 0)
    return rc | (ll5d.ATIME_RC if rec["atime"]["moved"] else 0)


if __name__ == "__main__":
    sys.exit(main())
