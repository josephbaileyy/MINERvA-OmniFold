#!/usr/bin/env python3
"""EVW5D: configuration (e)'s central per-event unfolded weights, the sixteen-cell result's unbinned central value.

EVW5D-DECLARATION.md (docs/orchestration/state/measurement-paper/5d-community-20261024/fd/evw5d-20261125/). The
central data product of configuration (e), ``data_b-_j-.npz`` (sha256 fb5cc679...), stores only the binned cross
section: ``s5c_unfold.unfold`` computes the push weights in memory and discards them (s5c_unfold.py:124-146 @
abdc88c5). The ESS run (fd/receipts-ess, job 61082774) reran that one unfold through the pinned driver and reproduced
its ``xsec_flat`` byte for byte. This tool runs the same unfold the same way and writes the weights:

* the driver: the deploy's ``s5p_numerics.main`` at CODE_PIN, unchanged, with the production argv; two pass-through
  wrappers (``omnifold_nn_core.omnifold_loop``, ``s5c_unfold.unfold``) keep the push weights and the unfold's inputs;
* the shared machinery of ``nd-unfolding/ess_e/ess_capture.py`` (the ESS run's tool, its bytes pinned by ESS_SHA and
  executed from the bytes hashed): the pins, the O_NOATIME staging, the read guard and the helpers;
* GATE 1 (C-BIND): the re-made ``xsec_flat`` equals fb5cc679's byte for byte, and its meta equals the reference's but
  for the per-run fields. Otherwise STOP.json, no weights, exit 8;
* GATE 2 (C-F): the sixteen cell integrals, from the result and from the per-event contributions, equal the data
  product's f to F_RTOL;
* the products ``weights.npz`` (one row per truth-selected MC row), ``constants.npz`` and ``constants.json``, read back
  from the bytes hashed and checked against independently loaded inputs (C-FILE), re-histogrammed into the result bit
  for bit (C-SELF) and over every row, flow rows included (C-FLOW);
* C-COMPLETE: the per-fine-cell completeness ofin/denom_nd is MEASURED; a departure from 1 beyond COMPLETE_ATOL is a
  FINDING (reported, not a failure), since a binning that splits fine cells needs it at event level;
* ``SHA256SUMS`` and, last, ``evw5d.done`` (write-then-rename) with the verdict and the acceptance checks.

The key of a row is (input npz sha256 07fccc1a..., ``entry``), ``entry`` the row's index in the npz's ``MCgen``; rows
are the npz's truth-selected rows (``pass_truth``), in order. It is not a physical event id.

MEASURES: the central per-event weights of the reported sixteen-cell result, and their completeness.
CANNOT AUTHORIZE: any change to the result or its covariance, an uncertainty, or a statement about the five-axis
purity product, which is a different unfold.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import os
import platform
import resource
import socket
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

SCHEMA = "evw5d/1"
HERE = Path(__file__).resolve().parent
ESS_PATH = HERE.parent / "ess_e" / "ess_capture.py"
ESS_SHA = "4755681f6ba8bd5060fe6ed4902e940b71e3b641d87c978a1f8016faaec468da"   # the ESS run's tool (README.md:6)

N_CELLS = 16
TRUTH_COLS = ("truth_pt", "truth_pz", "truth_eavail", "truth_q3", "truth_W")     # s5p_stage1_inspect.AXES order
COLUMNS = ("entry",) + TRUTH_COLS + ("w_prior", "wpush", "w_unfolded", "fine_index", "reco_partner")
F_RTOL = 1e-14          # gate 2, the director's ruling of 2026-11-25
INDEP_RTOL = 1e-13      # the result from an independently written formula (a different multiplication order)
FLOW_RTOL = 1e-12       # the per-fine-cell sums by bincount against the driver's histogramdd
COMPLETE_ATOL = 1e-12   # |c - 1| beyond this, where the denominator is positive, is a finding (2D's C-CMAP bound)
VOLUME_RTOL = 1e-13     # the saved cell volumes against the products of the saved edges' widths
C_ONE_LEVEL = 1e-5      # the director's ruling: "completeness is 1 to 1e-5" is stated only if every fine cell is
PRODUCTS = ("constants.json", "constants.npz", "product/data_b-_j-.npz", "run.json", "weights.npz")
NPZ_MEMBERS = ("meta", "shape", "xsec_flat")    # s5n_pseudo.write_product's members (@ abdc88c5)
GATED = ("C-BIND", "C-KEY", "C-ENTRY", "C-GRID", "C-F", "C-FILE", "C-SELF", "C-FLOW", "C-PINS")
SUMS, DONE = "SHA256SUMS", "evw5d.done"
RC_FAIL, RC_STOP, RC_FAILED = 6, 8, 9


def _load_ess():
    """ess_capture.py, executed from the very bytes whose sha256 is checked."""
    raw = ESS_PATH.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != ESS_SHA:
        raise SystemExit(f"evw5d: {ESS_PATH} has sha256 {got}, pinned {ESS_SHA}: refusing")
    spec = importlib.util.spec_from_loader("ess_capture", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__file__ = str(ESS_PATH)
    sys.modules["ess_capture"] = mod
    exec(compile(raw, str(ESS_PATH), "exec"), mod.__dict__)
    return mod


ess = _load_ess()
Failed = ess.Failed


# --------------------------------------------------------------------------------------------------- helpers


def same_bits(a, b) -> bool:
    """Equal dtype, shape and bytes."""
    a, b = np.asarray(a), np.asarray(b)
    return a.dtype == b.dtype and a.shape == b.shape and np.ascontiguousarray(a).tobytes() == \
        np.ascontiguousarray(b).tobytes()


def max_rel(x, ref) -> float:
    """max |x/ref - 1| where ref != 0; inf if x is nonzero where ref is zero, or the shapes differ."""
    x, ref = np.asarray(x, np.float64), np.asarray(ref, np.float64)
    if x.shape != ref.shape:
        return float("inf")
    nz = ref != 0
    if np.any(x[~nz] != 0):
        return float("inf")
    return float(np.max(np.abs(x[nz] / ref[nz] - 1))) if nz.any() else 0.0


def read_npz(path: Path) -> tuple[str, dict]:
    """The sha256 of the file's bytes and the arrays parsed from those same bytes."""
    raw = Path(path).read_bytes()
    with np.load(io.BytesIO(raw), allow_pickle=False) as z:
        arrays = {k: np.array(z[k]) for k in z.files}
    return hashlib.sha256(raw).hexdigest(), arrays


def write_npz(path: Path, arrays: dict) -> None:
    with open(path, "xb") as fh:      # refuses an existing file
        np.savez(fh, **arrays)


def cell_integrals(xsec_flat, vol, fm) -> np.ndarray:
    """f_R = sum_{f in R} xsec_f vol_f, s1_assemble's integral."""
    xv = np.asarray(xsec_flat, np.float64) * vol
    return np.array([float(xv[fm == c].sum()) for c in range(N_CELLS)])


def contributions(w_unfolded, fine_index, comp, flux, n_nucleons, data_pot, good, fm, nd) -> tuple[np.ndarray, dict]:
    """Each row's contribution to its reported cell's integral, 1e4 w / (c_f flux_f N POT), summed per cell (ESS (B))."""
    flux_b = np.asarray(flux, np.float64).reshape((-1,) + (1,) * (nd - 1))
    den = (comp * flux_b * float(n_nucleons) * float(data_pot)).ravel(order="C")
    goodf = np.asarray(good).ravel(order="C")
    inside = fine_index >= 0
    fic = np.where(inside, fine_index, 0)
    used = inside & goodf[fic]
    wb = np.zeros(w_unfolded.shape[0], np.float64)
    wb[used] = 1.0e4 * w_unfolded[used] / den[fic[used]]
    cell = np.where(used, fm[fic], -1)
    sums = np.array([wb[cell == c].sum() for c in range(N_CELLS)])
    zero_den = int((inside & ~goodf[fic] & (fm[fic] >= 0)).sum())
    return sums, {"rows_in_reported_cells_with_zero_denominator": zero_den}


# ------------------------------------------------------------------------------------------ the table and constants


def build_table(d: dict, wpush, flat_index) -> dict:
    """The per-row columns, from the unfold's own inputs and push weights (s5c_unfold.py:135-138 @ abdc88c5)."""
    m = d["pass_truth"]
    if np.asarray(m).dtype != np.bool_:
        raise Failed(f"pass_truth has dtype {np.asarray(m).dtype}, not bool: the driver's mask would not be a mask")
    entry = np.flatnonzero(m)
    if entry.size and int(entry[-1]) >= 2 ** 32:
        raise Failed("an entry number does not fit uint32")
    mc = d["MCgen"]
    cols = {"entry": entry.astype(np.uint32)}
    for k, name in enumerate(TRUTH_COLS):
        cols[name] = np.ascontiguousarray(mc[m, k])
    cols["w_prior"] = np.ascontiguousarray(np.asarray(d["w_truth"])[m]).astype(np.float64)   # exact widening
    cols["wpush"] = np.asarray(wpush).astype(np.float64)      # exact: float64 already, or a widening
    cols["w_unfolded"] = wpush * d["w_truth"][m]               # the driver's histogram weight, the same expression
    samp = np.column_stack([mc[m, i] for i in range(mc.shape[1])])
    cols["fine_index"] = np.asarray(flat_index(samp, d["edges"])).astype(np.int32)
    cols["reco_partner"] = np.asarray(d["pass_reco"], bool)[m]
    return cols


def driver_maps(d: dict, w_unfolded, w_prior, samp, extract) -> dict:
    """The driver's own histograms and completeness, recomputed as s5c_unfold.unfold makes them (:137-145)."""
    edges = d["edges"]
    unf, _ = np.histogramdd(samp, bins=edges, weights=w_unfolded)
    ofin, _ = np.histogramdd(samp, bins=edges, weights=w_prior)
    dn = d["denom_nd"]
    comp = np.zeros_like(ofin)
    nz = dn > 0
    comp[nz] = ofin[nz] / dn[nz]
    xs, good = extract(unf, comp, d["flux"], float(d["data_pot"]), float(d["n_nucleons"]), edges)
    return {"unf": unf, "ofin": ofin, "comp": comp, "xs": xs, "good": good}


def build_constants(d: dict, maps: dict, vol, fm) -> dict:
    c = {f"edges_{i}": np.asarray(e, np.float64) for i, e in enumerate(d["edges"])}
    c.update(flux=np.asarray(d["flux"]), data_pot=np.float64(float(d["data_pot"])),
             n_nucleons=np.float64(float(d["n_nucleons"])), cm2_per_m2=np.float64(1.0e4),
             denom_nd=np.asarray(d["denom_nd"]), ofin=maps["ofin"], completeness=maps["comp"], good=maps["good"],
             volume=np.asarray(vol, np.float64), fine_to_cell=np.asarray(fm, "<i4"),
             xsec_flat=maps["xs"].ravel(order="C"))
    return c


# ---------------------------------------------------------------------------------------------------- controls


def check_bind(remade: dict, ref: dict, captured) -> dict:
    """C-BIND, gate 1: the re-made product (parsed from the bytes hashed) against fb5cc679's: exactly the producer's
    members, xsec_flat and shape bit for bit (dtype included), the in-memory result equal to the file, and the meta
    equal but for the per-run fields."""
    members = sorted(remade) == sorted(ref) == sorted(NPZ_MEMBERS)
    out = {"members_exact": bool(members)}
    if not members:
        out["pass"] = False
        return out
    rx, fx = remade["xsec_flat"], ref["xsec_flat"]
    out["xsec_flat_bytes_equal"] = same_bits(rx, fx)
    out["shape_bits_equal"] = same_bits(remade["shape"], ref["shape"])
    out["captured_equals_remade"] = same_bits(np.asarray(captured).ravel(order="C"), rx)
    out["n_entries"] = int(np.asarray(fx).size)
    try:
        sm_r = ess.strip_per_run(json.loads(str(remade["meta"])))
        sm_f = ess.strip_per_run(json.loads(str(ref["meta"])))
    except ValueError:
        sm_r, sm_f = {"unparsable": 1}, {"unparsable": 2}
    out["meta_equal_except_per_run"] = sm_r == sm_f
    out["meta_differing_keys"] = sorted(k for k in set(sm_r) | set(sm_f) if sm_r.get(k) != sm_f.get(k))
    out["pass"] = bool(out["xsec_flat_bytes_equal"] and out["shape_bits_equal"] and out["captured_equals_remade"]
                       and out["meta_equal_except_per_run"])
    if not out["xsec_flat_bytes_equal"] and np.shape(rx) == np.shape(fx):
        diff = np.asarray(rx) != np.asarray(fx)
        out.update(n_differ=int(diff.sum()), max_abs=float(np.max(np.abs(np.asarray(rx, float) - np.asarray(fx, float))))
                   if diff.any() else 0.0)
    return out


def check_key(d: dict, indep: dict, wpush) -> dict:
    """C-KEY: the arrays the unfold received are the npz's own, row for row; the key is unique and fits."""
    fields = ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco", "denom_nd", "flux")
    equal = {k: same_bits(d[k], indep[k]) for k in fields}
    equal["data_pot"] = same_bits(np.float64(float(d["data_pot"])), np.float64(float(indep["data_pot"])))
    equal["n_nucleons"] = same_bits(np.float64(float(d["n_nucleons"])), np.float64(float(indep["n_nucleons"])))
    ne = int(indep["nedges"])
    equal["edges"] = len(d["edges"]) == ne and all(
        same_bits(np.asarray(d["edges"][i], float), np.asarray(indep[f"edges_{i}"], float)) for i in range(ne))
    m = np.asarray(indep["pass_truth"])
    entry = np.flatnonzero(m) if m.dtype == np.bool_ else np.array([], np.int64)
    aligned = m.dtype == np.bool_ and np.asarray(wpush).shape == (int(m.sum()),)
    return {"equal": equal, "pass_truth_bool": bool(m.dtype == np.bool_), "push_aligned": bool(aligned),
            "n_rows": int(entry.size), "pass": bool(all(equal.values()) and aligned)}


def check_entries(entry) -> dict:
    """The key's uniqueness: strictly increasing uint32 entry numbers (so no row appears twice)."""
    e = np.asarray(entry)
    increasing = bool(e.size < 2 or np.all(np.diff(e.astype(np.int64)) > 0))
    unique = bool(np.unique(e).size == e.size)
    return {"dtype_uint32": e.dtype == np.uint32, "strictly_increasing": increasing, "unique": unique,
            "pass": bool(e.dtype == np.uint32 and increasing and unique)}


def check_file(t: dict, c: dict, indep: dict, wpush, expected_c: dict, flat_index, meta: dict, cj_raw: bytes,
               cjson: dict, pins: dict | None = None) -> dict:
    """C-FILE: the read-back columns against their sources, independently of the table that was written; the saved
    meta and constants.json against what was meant to be written."""
    out = {"columns_exact": sorted(t) == sorted(COLUMNS + ("meta",))}
    out["meta_equal"] = ("meta" in t and "meta" in c and json.loads(str(t["meta"])) == meta
                         and json.loads(str(c["meta"])) == meta)
    out["constants_json_equal"] = json.loads(cj_raw) == cjson
    out["constants_json_vs_arrays"] = check_constants_json(json.loads(cj_raw), c, t) if "meta" in t else False
    out["constants_exact"] = sorted(k for k in c if k != "meta") == sorted(expected_c)
    if not (out["columns_exact"] and out["constants_exact"]):
        out["pass"] = False
        return out
    m = np.asarray(indep["pass_truth"], bool)
    entry = np.flatnonzero(m)
    out["entry"] = same_bits(t["entry"], entry.astype(np.uint32))
    mc = indep["MCgen"]
    e = entry
    for k, name in enumerate(TRUTH_COLS):
        out[name] = same_bits(t[name], np.ascontiguousarray(mc[e, k]))
    out["w_prior"] = same_bits(t["w_prior"], np.ascontiguousarray(np.asarray(indep["w_truth"])[e]).astype(np.float64))
    out["wpush"] = same_bits(t["wpush"], np.asarray(wpush).astype(np.float64))
    out["w_unfolded"] = same_bits(t["w_unfolded"], np.asarray(wpush) * np.asarray(indep["w_truth"])[e])
    out["weights_float64"] = all(t[k].dtype == np.float64 for k in ("w_prior", "wpush", "w_unfolded"))
    out["reco_partner"] = same_bits(t["reco_partner"], np.asarray(indep["pass_reco"], bool)[e])
    edges = [np.asarray(c[f"edges_{i}"], float) for i in range(int(indep["nedges"]))]
    samp = np.column_stack([t[n] for n in TRUTH_COLS])
    out["fine_index"] = same_bits(t["fine_index"], np.asarray(flat_index(samp, edges)).astype(np.int32))
    out["constants"] = {k: same_bits(c[k], v) for k, v in expected_c.items() if k in c}
    # the input constants against the independent read itself, not only against what the builder made
    vs_in = {f"edges_{i}": same_bits(c[f"edges_{i}"], np.asarray(indep[f"edges_{i}"], np.float64))
             for i in range(int(indep["nedges"]))}
    vs_in.update(flux=same_bits(c["flux"], np.asarray(indep["flux"])),
                 data_pot=same_bits(c["data_pot"], np.float64(float(indep["data_pot"]))),
                 n_nucleons=same_bits(c["n_nucleons"], np.float64(float(indep["n_nucleons"]))),
                 denom_nd=same_bits(c["denom_nd"], np.asarray(indep["denom_nd"])))
    # pinned digests, checked on the saved bytes themselves (not on what the builder was given)
    pins = pins or {}
    fm = np.asarray(c["fine_to_cell"])
    vs_in["fine_to_cell_digest"] = (fm.dtype == np.dtype("<i4") and "fine_map" in pins
                                    and hashlib.sha256(fm.tobytes()).hexdigest() == pins["fine_map"])
    saved_meta = json.loads(str(t["meta"]))
    for k, pin in (("input_npz_sha256", "npz"), ("bkg_dump_sha256", "bkg"), ("result_sha256", "ref"),
                   ("code_pin", "code_pin")):
        vs_in[f"meta_{k}"] = pin in pins and saved_meta.get(k) == pins[pin]
    vs_in["meta_n_rows"] = saved_meta.get("n_rows") == int(entry.size)
    vs_in["meta_columns"] = saved_meta.get("columns") == list(COLUMNS)
    out["constants_vs_input"] = vs_in
    out["pass"] = bool(all(v for k, v in out.items() if k not in ("constants", "constants_vs_input"))
                       and all(out["constants"].values()) and len(out["constants"]) == len(expected_c)
                       and all(vs_in.values()))
    return out


def check_constants_json(cj: dict, c: dict, t: dict) -> bool:
    """constants.json's operands equal the saved arrays (exact float round trip), and its meta equals the npz meta."""
    try:
        axes = cj["truth_axes"]
        ok = (cj["data_pot"] == float(c["data_pot"]) and cj["n_nucleons"] == float(c["n_nucleons"])
              and cj["cm2_per_m2"] == float(c["cm2_per_m2"])
              and cj["flux_per_m2_per_POT_by_pt_bin"] == [float(x) for x in np.asarray(c["flux"])]
              and list(cj["edges"]) == list(axes)
              and all(cj["edges"][ax] == [float(x) for x in c[f"edges_{i}"]] for i, ax in enumerate(axes))
              and cj["fine_map_sha256_int32le"] == hashlib.sha256(np.asarray(c["fine_to_cell"]).tobytes()).hexdigest())
        meta = json.loads(str(t["meta"]))
        ok = ok and all(cj.get(k) == v for k, v in meta.items())
        f_saved = cell_integrals(c["xsec_flat"], c["volume"], c["fine_to_cell"])
        return bool(ok and len(cj["f_cm2_per_nucleon"]) == N_CELLS
                    and max_rel(cj["f_cm2_per_nucleon"], f_saved) == 0.0)
    except (KeyError, TypeError, ValueError):
        return False


def check_self(t: dict, c: dict, ref_xsec_flat, f_dp, extract, nd: int) -> dict:
    """C-SELF and gate 2 from the read-back files alone: the result bit for bit, an independent formula, and f."""
    edges = [np.asarray(c[f"edges_{i}"], float) for i in range(nd)]
    d = {"edges": edges, "denom_nd": c["denom_nd"], "flux": c["flux"], "data_pot": c["data_pot"],
         "n_nucleons": c["n_nucleons"]}
    samp = np.column_stack([t[n] for n in TRUTH_COLS])
    mp = driver_maps(d, t["w_unfolded"], t["w_prior"], samp, extract)
    xs = mp["xs"].ravel(order="C")
    out = {"xsec_bit_for_bit": same_bits(xs, ref_xsec_flat),
           "ofin_bit_for_bit": same_bits(mp["ofin"], c["ofin"]),
           "completeness_bit_for_bit": same_bits(mp["comp"], c["completeness"]),
           "good_bit_for_bit": same_bits(mp["good"], c["good"]),
           "saved_xsec_equals_reference": same_bits(c["xsec_flat"], ref_xsec_flat),
           "cm2_per_m2_exact": same_bits(c["cm2_per_m2"], np.float64(1.0e4))}
    widths = [np.diff(e) for e in edges]
    vol_edges = np.ones(tuple(w.size for w in widths))
    for k, w in enumerate(widths):
        vol_edges = vol_edges * w.reshape((1,) * k + (-1,) + (1,) * (nd - 1 - k))
    out["volume_vs_edges_max_rel"] = max_rel(c["volume"], vol_edges.ravel(order="C"))
    # the formula written out independently: d^5 sigma = 1e4 U / (vol c Phi(pT) N POT), zero where that is not > 0
    shape = mp["unf"].shape
    vol = np.asarray(c["volume"], np.float64).reshape(shape)
    phi = np.asarray(c["flux"], np.float64).reshape((-1,) + (1,) * (nd - 1))
    den = vol * mp["comp"] * phi * float(c["n_nucleons"]) * float(c["data_pot"])
    ok = den > 0
    x2 = np.zeros(shape)
    x2[ok] = mp["unf"][ok] / den[ok] * float(c["cm2_per_m2"])
    out["independent_formula_max_rel"] = max_rel(x2.ravel(order="C"), ref_xsec_flat)
    f_file = cell_integrals(xs, c["volume"], c["fine_to_cell"])
    out["f_from_file_max_rel"] = max_rel(f_file, f_dp)
    sums, extra = contributions(t["w_unfolded"], t["fine_index"], mp["comp"], c["flux"], c["n_nucleons"],
                                c["data_pot"], mp["good"], c["fine_to_cell"], nd)
    out["f_from_rows_max_rel"] = max_rel(sums, f_dp)
    out.update(extra)
    out["pass"] = bool(out["xsec_bit_for_bit"] and out["ofin_bit_for_bit"] and out["completeness_bit_for_bit"]
                       and out["good_bit_for_bit"] and out["saved_xsec_equals_reference"]
                       and out["cm2_per_m2_exact"] and out["volume_vs_edges_max_rel"] <= VOLUME_RTOL
                       and out["independent_formula_max_rel"] <= INDEP_RTOL
                       and out["f_from_file_max_rel"] <= F_RTOL and out["f_from_rows_max_rel"] <= F_RTOL)
    return out


def check_flow(t: dict, c: dict, unf_driver, n_pass_truth: int) -> dict:
    """C-FLOW: every truth-selected row is in the file; the rows inside the grid bin, by bincount over fine_index, to
    the driver's own per-cell sums of w_unfolded and w_prior; the rows outside it (truth on no fine cell) are
    counted, with their weight."""
    nfine = int(np.prod(np.asarray(c["ofin"]).shape))
    fi = t["fine_index"]
    in_range = bool(np.all((fi >= -1) & (fi < nfine)))
    ins = fi >= 0
    out = {"n_rows": int(fi.size), "n_rows_equal_pass_truth": int(fi.size) == int(n_pass_truth),
           "n_outside_grid": int((~ins).sum()), "w_unfolded_outside": float(t["w_unfolded"][~ins].sum()),
           "w_prior_outside": float(t["w_prior"][~ins].sum()), "fine_index_in_range": in_range}
    if in_range:
        unf_b = np.bincount(fi[ins], weights=t["w_unfolded"][ins], minlength=nfine)
        pri_b = np.bincount(fi[ins], weights=t["w_prior"][ins], minlength=nfine)
        out["unfolded_max_rel"] = max_rel(unf_b, np.asarray(unf_driver).ravel(order="C"))
        out["prior_max_rel"] = max_rel(pri_b, np.asarray(c["ofin"]).ravel(order="C"))
    else:
        out["unfolded_max_rel"] = out["prior_max_rel"] = float("inf")
    out["pass"] = bool(in_range and out["n_rows_equal_pass_truth"] and out["unfolded_max_rel"] <= FLOW_RTOL
                       and out["prior_max_rel"] <= FLOW_RTOL)
    return out


def measure_completeness(ofin, denom) -> dict:
    """C-COMPLETE, a measurement: c = ofin/denom per fine cell. A finding when |c - 1| > COMPLETE_ATOL in a cell with
    a positive denominator, or when a cell has signal weight but no denominator."""
    ofin, denom = np.asarray(ofin, np.float64).ravel(), np.asarray(denom, np.float64).ravel()
    pos = denom > 0
    c = np.zeros_like(ofin)
    c[pos] = ofin[pos] / denom[pos]
    dev = np.abs(c[pos] - 1)
    out = {"n_fine_cells": int(ofin.size), "n_denominator_positive": int(pos.sum()),
           "n_signal_without_denominator": int(((ofin != 0) & ~pos).sum()),
           "n_denominator_without_signal": int((pos & (ofin == 0)).sum()),
           "max_abs_c_minus_1": float(dev.max()) if dev.size else None,
           "n_cells_beyond_atol": int((dev > COMPLETE_ATOL).sum()),
           "c_min": float(c[pos].min()) if pos.any() else None, "c_max": float(c[pos].max()) if pos.any() else None,
           "sum_ofin_over_sum_denominator": float(ofin[pos].sum() / denom[pos].sum()) if pos.any() else None,
           "atol": COMPLETE_ATOL}
    out["c_one_to_1e-5_in_every_fine_cell"] = bool(
        pos.any() and out["n_signal_without_denominator"] == 0 and float(dev.max()) <= C_ONE_LEVEL)
    if dev.size:
        out["abs_c_minus_1_quantiles"] = {q: float(np.quantile(dev, float(q))) for q in ("0.5", "0.9", "0.99")}
    out["finding"] = bool(out["n_cells_beyond_atol"] > 0 or out["n_signal_without_denominator"] > 0
                          or not pos.any())
    return out


# --------------------------------------------------------------------------------------------- products and done


def sums_text(digests: dict) -> str:
    return "".join(f"{digests[p]}  {p}\n" for p in sorted(digests))


def parse_sums(text: str) -> dict | None:
    """Exactly the form sums_text writes: LF-terminated lines, no CR, no duplicate path."""
    if not text.endswith("\n") or "\r" in text:
        return None
    out = {}
    for line in text[:-1].split("\n"):
        h, sep, p = line.partition("  ")
        if not sep or len(h) != 64 or any(ch not in "0123456789abcdef" for ch in h) or p in out:
            return None
        out[p] = h
    return out


def listing(out: Path) -> list[str]:
    return sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file() or p.is_symlink())


def acceptance(out: Path, digests: dict) -> dict:
    """The products are exactly the expected set, SHA256SUMS parses to exactly their digest map, every product
    re-hashes equal, and nothing is a link."""
    files = [f for f in listing(out) if f != DONE]
    acc = {"product_set_exact": files == sorted(PRODUCTS + (SUMS,)),
           "digest_map_complete": sorted(digests) == sorted(PRODUCTS)}
    sums_path = out / SUMS
    try:
        parsed = parse_sums(sums_path.read_bytes().decode("ascii")) if sums_path.is_file() else None
    except UnicodeDecodeError:
        parsed = None
    acc["sums_parse_exact"] = parsed == digests
    acc["no_links"] = not any((out / f).is_symlink() for f in files)
    acc["rehash_equal"] = all((out / p).is_file() and ess.sha256_file(out / p) == h for p, h in digests.items())
    acc["pass"] = all(acc.values())
    return acc


DONE_KEYS = ("acceptance", "controls_verdict", "failed_controls", "finding_sizes", "findings", "products", "schema",
             "sha256sums_sha256", "verdict")


def accepted(out: Path, expect_sums_sha256: str, production: bool = True) -> bool:
    """For a consumer: SHA256SUMS's digest equal to the one the release binding records (which is what detects a
    replaced bundle), the acceptance re-run, and a PASS done marker of exactly the written schema and consistent with
    the hashed run.json (parsed from the bytes verified against SHA256SUMS). With ``production`` (the default),
    run.json must also record the production pins and no --fixture; tests pass production=False."""
    out = Path(out)
    try:
        if out.is_symlink() or not out.is_dir() or (out / DONE).is_symlink() or (out / SUMS).is_symlink():
            return False
        done = json.loads((out / DONE).read_bytes())
        raw = (out / SUMS).read_bytes()
        digests = parse_sums(raw.decode("ascii"))
    except (OSError, ValueError, UnicodeDecodeError):
        return False
    h = hashlib.sha256(raw).hexdigest()
    if digests is None or not isinstance(done, dict) or sorted(done) != sorted(DONE_KEYS) \
            or done.get("schema") != SCHEMA:
        return False
    if not isinstance(expect_sums_sha256, str) or h != expect_sums_sha256:
        return False
    fresh = acceptance(out, digests)
    if not (done["verdict"] == "PASS" and done["controls_verdict"] == "PASS"
            and done["failed_controls"] == [] and done["sha256sums_sha256"] == h
            and done["products"] == digests and done["acceptance"] == fresh and fresh["pass"]):
        return False
    try:
        rj = (out / "run.json").read_bytes()
        if hashlib.sha256(rj).hexdigest() != digests.get("run.json"):
            return False
        run = json.loads(rj)
    except (OSError, ValueError):
        return False
    if not isinstance(run, dict) or not isinstance(run.get("controls"), dict):
        return False
    ctl = run["controls"]
    if production and not (run.get("code_pin") == ess.CODE_PIN and run.get("main_pin") == ess.MAIN_PIN
                           and isinstance(run.get("argv"), list) and "--fixture" not in run["argv"]
                           and run.get("ess_digest") == ESS_SHA
                           and all((run.get("reads") or {}).get(k, {}).get("copy_digest") == ess.SHARED[k][1]
                                   for k in ess.SHARED)):
        return False
    return bool(run.get("schema") == SCHEMA and run.get("controls_verdict") == "PASS"
                and tuple(run.get("gated", ())) == GATED
                and all(isinstance(ctl.get(k), dict) and ctl[k].get("pass") is True for k in GATED)
                and run.get("findings") == done["findings"] and run.get("finding_sizes") == done["finding_sizes"])


def publish_done(out: Path, record: dict) -> None:
    ess.write_json(out / DONE, record)      # write-then-rename (ess_capture.write_json)


# --------------------------------------------------------------------------------------------------------- run


def capture_unfold(s5p_numerics, onc, s5c_unfold, argv: list) -> tuple[dict, np.ndarray, np.ndarray]:
    """The driver's main, unchanged, with two pass-through wrappers; returns the unfold's inputs, result and pushes."""
    loops, unfolds = [], []
    real_loop, real_unfold = onc.omnifold_loop, s5c_unfold.unfold

    def loop(*args, **kw):
        res = real_loop(*args, **kw)
        loops.append(res)
        return res

    def unfold(inputs, config, seed, threads, iters):
        xs, rec = real_unfold(inputs, config, seed, threads, iters)
        unfolds.append((inputs, xs))
        return xs, rec

    onc.omnifold_loop, s5c_unfold.unfold = loop, unfold
    try:
        rc = s5p_numerics.main(argv)
    finally:
        onc.omnifold_loop, s5c_unfold.unfold = real_loop, real_unfold
    if rc != 0:
        raise Failed(f"s5p_numerics.main returned {rc}")
    if len(loops) != 1 or len(unfolds) != 1:
        raise Failed(f"{len(loops)} OmniFold loops and {len(unfolds)} unfolds ran, expected one each")
    inputs, xs = unfolds[0]
    return inputs, xs, np.asarray(loops[0][1])


def load_indep(path: Path) -> dict:
    """An independent read of the staged npz (allow_pickle off), for C-KEY and C-FILE."""
    with np.load(path, allow_pickle=False) as z:
        keys = ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco", "denom_nd", "flux", "data_pot",
                "n_nucleons", "nedges")
        out = {k: np.array(z[k]) for k in keys}
        out.update({f"edges_{i}": np.array(z[f"edges_{i}"]) for i in range(int(out["nedges"]))})
    return out


def run(a, cfg: dict) -> int:
    t_start = time.time()
    deploy, out = a.deploy.resolve(), a.out
    record = {"schema": SCHEMA, "tool_digest": ess.sha256_file(Path(__file__).resolve()), "ess_digest": ESS_SHA,
              "argv": sys.argv, "host": socket.gethostname(), "slurm_job": os.environ.get("SLURM_JOB_ID"),
              "slurm_step": os.environ.get("SLURM_STEP_ID"), "python": platform.python_version(),
              "code_pin": cfg["code_pin"], "main_pin": cfg["main_pin"], "findings": [], "finding_sizes": {}}
    head = subprocess.run(["git", "-C", str(deploy), "rev-parse", "HEAD"], capture_output=True, text=True)
    if head.stdout.strip() != cfg["code_pin"]:
        raise Failed(f"deploy HEAD {head.stdout.strip()} is not {cfg['code_pin']}")
    for rel, pin in cfg["code_sha"].items():
        if ess.sha256_file(deploy / rel) != pin:
            raise Failed(f"{rel} in the deploy is not the pinned file")
    for p in (deploy / "nd-unfolding", deploy / "2d-unfolding"):
        sys.path.insert(0, str(p))
    import lightgbm
    import omnifold_nn_core as onc
    import s5c_unfold
    import s5e_trace
    import s5p_numerics
    import s5p_stage1_inspect as s1
    import xsec_nd
    record["versions"] = {"numpy": np.__version__, "lightgbm": lightgbm.__version__}
    if s5c_unfold.onc is not onc:
        raise Failed("s5c_unfold's omnifold_nn_core is another module object")
    h2 = json.loads(ess.git_show(deploy, cfg["main_pin"], *cfg["repo"]["h2"]))
    dp = json.loads(ess.git_show(deploy, cfg["main_pin"], *cfg["repo"]["dp"]))
    f_dp = np.asarray(dp["f"], np.float64)

    stage_dir = Path(a.stage_dir)
    stage_dir.mkdir(mode=0o700)          # refuses an existing directory
    try:
        copies, stats = ess.stage(cfg["shared"], stage_dir, cfg["noatime"], cfg["check_atime"])
        record["reads"] = stats
        argv = ["--npz", str(copies["npz"]), "--bkg", str(copies["bkg"]),
                "--expect-npz-sha256", cfg["shared"]["npz"][1], "--expect-bkg-sha256", cfg["shared"]["bkg"][1],
                "--config", "R", "--iters", "5", "--construction", "data", "--pairs=-:-", "--tag", "data",
                "--threads", str(cfg["threads"]), "--out", str(out / "product")]
        record["producer_argv"] = argv
        t0 = time.time()
        d, xs, wpush = capture_unfold(s5p_numerics, onc, s5c_unfold, argv)
        record["seconds_producer"] = round(time.time() - t0, 3)
        product = out / "product" / "data_b-_j-.npz"
        digests = {"product/data_b-_j-.npz": ess.sha256_file(product)}     # hashed the moment the driver returns
        for name in cfg["modules"]:
            mod = sys.modules.get(name)
            if mod is None or not Path(mod.__file__).resolve().is_relative_to(deploy):
                raise Failed(f"module {name} is not loaded from the deploy ({getattr(mod, '__file__', None)})")

        # ---- GATE 1, C-BIND: the re-made product against fb5cc679's, each parsed from the very bytes hashed
        remade_digest, remade = read_npz(product)
        ref_digest, ref = read_npz(copies["ref"])
        if remade_digest != digests["product/data_b-_j-.npz"] or ref_digest != cfg["shared"]["ref"][1]:
            raise Failed("a product's bytes changed between their hash and their parse")
        bind = check_bind(remade, ref, xs)
        bind.update(reference_digest=ref_digest, remade_digest=remade_digest)
        record["C-BIND"] = bind
        if not bind["pass"]:
            record["verdict"] = "STOP: the re-made result is not fb5cc679's; no weights are written"
            ess.write_json(out / "STOP.json", record)
            return RC_STOP
        rx = remade["xsec_flat"]
        captured = xs.ravel(order="C")

        controls = {"C-BIND": bind}
        indep = load_indep(copies["npz"])
        controls["C-KEY"] = check_key(d, indep, wpush)
        if not controls["C-KEY"]["pass"]:
            record.update(controls=controls, verdict="FAIL: C-KEY; no weights are written")
            ess.write_json(out / "FAILED.json", record)
            return RC_FAIL

        # ---- the table, the driver's maps and the fine grid's mapping (ESS's checks)
        table = build_table(d, wpush, s5e_trace.flat_index)
        controls["C-ENTRY"] = check_entries(table["entry"])
        m = d["pass_truth"]
        samp = np.column_stack([d["MCgen"][m, i] for i in range(d["MCgen"].shape[1])])
        maps = driver_maps(d, table["w_unfolded"], table["w_prior"], samp, xsec_nd.extract_cross_section_nd)
        cmap, n_boxes = s1.coarse_map(s1.H2_EDGES)
        hm = np.asarray(h2["h2_to_reporting_cell"], int)
        if hm.size != n_boxes or int(h2["n_reporting_cells"]) != N_CELLS:
            raise Failed("the H2 definition does not map its boxes onto 16 cells")
        fm = np.where(cmap >= 0, hm[cmap], -1).astype("<i4")
        vol = s1.fine_volume()
        edges = d["edges"]
        grid = {"recomputed_xs_bit_for_bit": same_bits(maps["xs"], xs),
                "edges_equal_fine_grid": len(edges) == len(s1.AXES) and all(
                    np.array_equal(np.asarray(e, float), np.asarray(s1.FINE[ax], float))
                    for e, ax in zip(edges, s1.AXES)),
                "fine_map_digest_equal": hashlib.sha256(fm.tobytes()).hexdigest() == cfg["fine_map_sha"]
                == h2["fine_map_sha256_int32le"],
                "volume_equal": bool(np.allclose(vol, xsec_nd._bin_volume(xs.shape, edges).ravel(order="C"),
                                                 rtol=1e-13, atol=0.0))}
        grid["pass"] = all(grid.values())
        controls["C-GRID"] = grid

        # ---- GATE 2, C-F: the sixteen cell integrals, from the result and from the rows, against the data product
        f_res = cell_integrals(captured, vol, fm)
        sums, extra = contributions(table["w_unfolded"], table["fine_index"], maps["comp"], d["flux"],
                                    d["n_nucleons"], d["data_pot"], maps["good"], fm, xs.ndim)
        cf = {"f_from_result_max_rel": max_rel(f_res, f_dp), "f_from_rows_max_rel": max_rel(sums, f_dp),
              "f": [float(x) for x in f_res], **extra}
        cf["pass"] = bool(cf["f_from_result_max_rel"] <= F_RTOL and cf["f_from_rows_max_rel"] <= F_RTOL)
        controls["C-F"] = cf

        # ---- the products, written once, then read back from the bytes hashed
        constants = build_constants(d, maps, vol, fm)
        meta = {"schema": SCHEMA, "key": "(input npz sha256, entry): entry is the row's index in the npz's MCgen; "
                "rows are its pass_truth rows in order; not a physical event id",
                "input_npz_sha256": cfg["shared"]["npz"][1], "bkg_dump_sha256": cfg["shared"]["bkg"][1],
                "result_sha256": cfg["shared"]["ref"][1], "code_pin": cfg["code_pin"],
                "columns": list(COLUMNS), "truth_axes": list(s1.AXES), "n_rows": int(table["entry"].size)}
        write_npz(out / "weights.npz", {**table, "meta": np.array(json.dumps(meta))})
        write_npz(out / "constants.npz", {**constants, "meta": np.array(json.dumps(meta))})
        cjson = {**meta, "data_pot": float(constants["data_pot"]), "n_nucleons": float(constants["n_nucleons"]),
                 "cm2_per_m2": 1.0e4, "flux_per_m2_per_POT_by_pt_bin": [float(x) for x in constants["flux"]],
                 "edges": {ax: [float(x) for x in constants[f"edges_{i}"]] for i, ax in enumerate(s1.AXES)},
                 "f_cm2_per_nucleon": cf["f"], "fine_map_sha256_int32le": cfg["fine_map_sha"],
                 "formula": "d5sigma_f = 1e4 * sum_{rows in fine cell f} w_unfolded / (completeness_f * flux[pT bin "
                            "of f] * n_nucleons * data_pot * volume_f), zero unless that denominator is finite and "
                            "> 0 (the saved good mask); flux in m^-2/POT, data_pot in POT; "
                            "f_R = sum_{f in R} d5sigma_f * volume_f"}
        cbytes = (json.dumps(cjson, indent=1) + "\n").encode()
        with open(out / "constants.json", "xb") as fh:
            fh.write(cbytes)
        digests["weights.npz"], t_read = read_npz(out / "weights.npz")
        digests["constants.npz"], c_read = read_npz(out / "constants.npz")
        cj_raw = (out / "constants.json").read_bytes()
        digests["constants.json"] = hashlib.sha256(cj_raw).hexdigest()
        controls["C-FILE"] = check_file(t_read, c_read, indep, wpush, constants, s5e_trace.flat_index,
                                        meta, cj_raw, cjson,
                                        {"fine_map": cfg["fine_map_sha"], "npz": cfg["shared"]["npz"][1],
                                         "bkg": cfg["shared"]["bkg"][1], "ref": cfg["shared"]["ref"][1],
                                         "code_pin": cfg["code_pin"]})
        controls["C-SELF"] = check_self(t_read, c_read, rx, f_dp, xsec_nd.extract_cross_section_nd, xs.ndim)
        controls["C-FLOW"] = check_flow(t_read, c_read, maps["unf"], int(np.count_nonzero(indep["pass_truth"])))
        comp = measure_completeness(maps["ofin"], d["denom_nd"])
        controls["C-COMPLETE"] = comp
        if comp["finding"]:
            record["findings"].append("C-COMPLETE")
            record["finding_sizes"]["C-COMPLETE"] = {k: comp[k] for k in (
                "max_abs_c_minus_1", "n_cells_beyond_atol", "n_signal_without_denominator")}
            print(f"FINDING: C-COMPLETE {record['finding_sizes']['C-COMPLETE']}", flush=True)

        # ---- after the run: the pinned code and the staged copies are unchanged
        pins_after = {rel: ess.sha256_file(deploy / rel) == pin for rel, pin in cfg["code_sha"].items()}
        stage_after = {k: ess.sha256_file(p) == cfg["shared"][k][1] for k, p in copies.items()}
        controls["C-PINS"] = {"code": pins_after, "staged_copies": stage_after,
                              "pass": all(pins_after.values()) and all(stage_after.values())}
    finally:
        ess.shutil.rmtree(stage_dir, ignore_errors=True)

    gated = GATED
    controls_pass = all(controls[k]["pass"] for k in gated)
    record.update(controls=controls, gated=list(gated), controls_verdict="PASS" if controls_pass else "FAIL",
                  seconds_total=round(time.time() - t_start, 3),
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    rj = (json.dumps(record, indent=1, default=str) + "\n").encode()
    with open(out / "run.json", "xb") as fh:
        fh.write(rj)
    digests["run.json"] = hashlib.sha256(rj).hexdigest()
    sums = sums_text(digests)
    with open(out / SUMS, "xb") as fh:
        fh.write(sums.encode("ascii"))
    acc = acceptance(out, digests)
    verdict = "PASS" if controls_pass and acc["pass"] else "FAIL"
    publish_done(out, {"schema": SCHEMA, "verdict": verdict, "controls_verdict": record["controls_verdict"],
                       "failed_controls": [k for k in gated if not controls[k]["pass"]],
                       "findings": record["findings"], "finding_sizes": record["finding_sizes"],
                       "acceptance": acc, "sha256sums_sha256": hashlib.sha256(sums.encode()).hexdigest(),
                       "products": digests})
    print(f"evw5d: {verdict}; findings {record['findings']}", flush=True)
    return 0 if verdict == "PASS" else RC_FAIL


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--deploy", type=Path, required=True, help="a clean clone at CODE_PIN")
    ap.add_argument("--out", type=Path, required=True, help="a new directory under --out-root")
    ap.add_argument("--out-root", type=Path, required=True, help="the job's $OUT: the only allowed protected root")
    ap.add_argument("--stage-dir", required=True, help="a new node-local directory, e.g. /dev/shm/evw5d-<job>")
    ap.add_argument("--fixture", type=Path, default=None, help="TESTS ONLY: pins and paths from a JSON; refused in Slurm")
    a = ap.parse_args(argv)
    cfg = {"code_pin": ess.CODE_PIN, "main_pin": ess.MAIN_PIN, "shared": ess.SHARED, "repo": ess.REPO,
           "code_sha": ess.CODE_SHA, "fine_map_sha": ess.FINE_MAP_SHA256, "modules": ess.MODULES,
           "threads": ess.THREADS, "protected": ess.PROTECTED, "noatime": getattr(os, "O_NOATIME", None),
           "check_atime": True}
    if a.fixture is not None:
        if os.environ.get("SLURM_JOB_ID"):
            print("evw5d: --fixture is refused inside a Slurm job", file=sys.stderr)
            return 2
        fx = json.loads(a.fixture.read_text())
        cfg.update({k: v for k, v in fx.items() if k not in ("shared", "repo")})
        cfg["shared"] = {k: tuple(v) for k, v in fx.get("shared", {}).items()} or ess.SHARED
        cfg["repo"] = {k: tuple(v) for k, v in fx.get("repo", {}).items()} or ess.REPO
    if cfg["noatime"] is None:
        print("evw5d: O_NOATIME is not available: refusing a plain read", file=sys.stderr)
        return 2
    if a.out.exists():
        print(f"evw5d: --out {a.out} exists: an attempt needs a new --out", file=sys.stderr)
        return 2
    out_root = os.path.realpath(a.out_root)
    if not os.path.realpath(a.out).startswith(out_root.rstrip("/") + "/"):
        print("evw5d: --out is not under --out-root", file=sys.stderr)
        return 2
    a.out.mkdir(parents=True)            # refuses an existing --out
    if not os.path.realpath(a.out).startswith(out_root.rstrip("/") + "/"):
        print("evw5d: --out is not under --out-root", file=sys.stderr)
        return 2
    ess.install_guard(cfg["protected"], [out_root], cfg["noatime"])
    try:
        return run(a, cfg)
    except Failed as e:
        ess.write_json(a.out / "FAILED.json", {"schema": SCHEMA, "verdict": f"FAILED: {e}", "argv": sys.argv})
        print(f"evw5d: FAILED: {e}", file=sys.stderr)
        return RC_FAILED


if __name__ == "__main__":
    sys.exit(main())
