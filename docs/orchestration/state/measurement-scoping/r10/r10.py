#!/usr/bin/env python3
"""R10: does reconstructed information beyond the five binned reco scalars narrow the J width floor and cut the
departure residual? (SCOPING.md section 4.2; DECLARATION.md in this directory.)

D-ID's binned setting, unchanged, through D-ID's own frozen driver (``did.py``, digest-checked, imported as MP-4A did):
its event admission, rows, truth reweights, truth grids T1/T2, functional rows, ``Pairs``/``response``/``ibu``/
``fisher``/``widths_from_eig``. Only the RECO binning changes, per configuration:

* (i) the five scalars refined f = 2 or 4 per axis (every bin split at its midpoint, once or twice: MP-4A extra (c));
* (ii) a sixth reco axis, a whole-event tuple variable C1-C4 in 3 weighted tertile bins plus a missing category, at
  f = 1 and f = 2, and the declared pair C2 x C3 at f = 1;
* each configuration's NULL TWIN: its own reco-cell labels permuted at random among the rows of each f = 1 cell, so
  the twin has exactly its occupancy and none of its information;
* the GLOBAL NULL ``null3@f1``: a 3-bin seeded uniform axis at f = 1, which must leave the decisive figures within the
  split-half noise band (the swap of the two halves).

For every configuration and weight set: exact binned IBU (K = 1..200) from the nominal prior, and Cramer-Rao widths
at the nominal truth, in D-ID's roles. ``split`` (DECIDES): response, prior and known term from half A, data and truth
from half B. ``same`` (descriptive, optimistic): everything from the full sample. ``swap`` (f = 1 and the global null
only): the two halves exchanged, for the noise band. The verdict is ``verdict()``.

MEASURES: binned, signal-only, noise-free widths and residuals under alternative reco binnings.
CANNOT AUTHORIZE: an estimator, an interval, a measurement, a coverage statement, or any run.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import sys
import time
import traceback
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
CONFIG = HERE / "config.json"
DEPARTURES = ("gibuu", "w1", "w2", "w3")  # the four the residual leg counts (q3 is descriptive)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def load_did(cfg: dict):
    pins = cfg["did"]
    for key in ("driver", "config", "tables", "results"):
        p = REPO / pins[key]["path"]
        if sha256(p) != pins[key]["sha256"]:
            raise SystemExit(f"refusing: {p} differs from the pinned D-ID {key}")
    path = REPO / pins["driver"]["path"]
    spec = importlib.util.spec_from_file_location("r10_did", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------------------------------------------- pure helpers (tested)
def halved(edges) -> np.ndarray:
    """Every bin split in two at its arithmetic midpoint (MP-4A ``build_problem.halved``)."""
    e = np.asarray(edges, float)
    out = np.empty(2 * e.size - 1)
    out[0::2] = e
    out[1::2] = 0.5 * (e[:-1] + e[1:])
    return out


def refined(edges: list, f: int) -> list:
    """f = 1, 2 or 4: the edges halved log2(f) times."""
    if f not in (1, 2, 4):
        raise ValueError(f"refinement {f} is not declared")
    out = [np.asarray(e, float) for e in edges]
    for _ in range({1: 0, 2: 1, 4: 2}[f]):
        out = [halved(e) for e in out]
    return out


def derived_variable(name: str, raw: dict) -> np.ndarray:
    """C1-C4 from the extracted branches (DECLARATION section 3). NaN = missing (no reco row, a sentinel, or an empty
    denominator)."""
    def clean(x):
        x = np.asarray(x, float)
        return np.where(np.isfinite(x) & (x >= 0), x, np.nan)
    if name == "C1":
        return clean(raw["part_response_recoil_allNonMuonClusters_tracker_nClus"]) \
            + clean(raw["part_response_recoil_allNonMuonClusters_ecal_nClus"]) \
            + clean(raw["part_response_recoil_allNonMuonClusters_hcal_nClus"])
    if name == "C2":
        tr = clean(raw["part_response_total_recoil_passive_allNonMuonClusters_tracker"])
        tot = tr + clean(raw["part_response_total_recoil_passive_allNonMuonClusters_ecal"]) \
            + clean(raw["part_response_total_recoil_passive_allNonMuonClusters_hcal"])
        return np.divide(tr, tot, out=np.full_like(tr, np.nan), where=tot > 0)
    if name == "C3":
        return clean(raw["part_response_container_total_recoil_passive_primaryHadrons_id_sz"])
    if name == "C4":
        return clean(raw["MasterAnaDev_BlobNClusters_sz"])
    raise ValueError(name)


def tertile_bins(v: np.ndarray, w: np.ndarray, use: np.ndarray) -> tuple[np.ndarray, dict]:
    """Bins 0/1/2 at the w-weighted tertiles of v over the rows ``use`` with a finite v; bin 3 = missing.
    v <= q1 -> 0, q1 < v <= q2 -> 1, v > q2 -> 2 (ties stay together, so a bin may be empty)."""
    ok = use & np.isfinite(v)
    order = np.argsort(v[ok], kind="stable")
    vs, cw = v[ok][order], np.cumsum(w[ok][order])
    q = [float(vs[min(np.searchsorted(cw, t * cw[-1]), vs.size - 1)]) for t in (1 / 3, 2 / 3)]
    b = np.full(v.size, 3, np.int8)
    fin = np.isfinite(v)
    b[fin] = np.where(v[fin] <= q[0], 0, np.where(v[fin] <= q[1], 1, 2))
    present = sorted(int(x) for x in np.unique(b[use]))
    return b, {"edges": q, "categories_present": present, "n_missing_used": int(np.sum(use & ~fin)),
               "weight_share": {str(k): float(w[use & (b == k)].sum() / w[use].sum()) for k in range(4)}}


def permuted_within(group: np.ndarray, label: np.ndarray, seed) -> np.ndarray:
    """The null twin: ``label`` permuted at random among the rows of each ``group`` (rows with group < 0 get -1).
    Every group keeps exactly its multiset of labels, so every label keeps its row count; which row gets which label
    is independent of everything else."""
    idx = np.flatnonzero(group >= 0)
    g = group[idx]
    a = idx[np.lexsort((np.random.default_rng(seed).random(idx.size), g))]  # rows by group, random order within
    b = idx[np.argsort(g, kind="stable")]                                    # rows by group, original order within
    out = np.full(label.size, -1, np.int64)
    out[a] = label[b]
    return out


def quantile_inf(v: np.ndarray, p: float) -> float:
    """MP-4A's quantile with +inf allowed (``run_mp4a.quantile_inf``): numpy's linear rule, +inf if a neighbour is."""
    v = np.sort(np.asarray(v, float))
    pos = p * (v.size - 1)
    i = int(np.floor(pos))
    g = pos - i
    if g == 0 or i + 1 >= v.size:
        return float(v[i])
    if np.isinf(v[i]) or np.isinf(v[i + 1]):
        return float(np.inf)
    return float(v[i] + g * (v[i + 1] - v[i]))


def width_stats(sigma_rel: np.ndarray) -> dict:
    """J widths with holes (+inf or NaN) as +inf, MP-4A's primary convention; finite-only beside it."""
    v = np.where(np.isfinite(sigma_rel), sigma_rel, np.inf)
    fin = v[np.isfinite(v)]
    return {"n": int(v.size), "n_inf": int(np.isinf(v).sum()), "median": quantile_inf(v, 0.5),
            "p90": quantile_inf(v, 0.9), "median_finite": float(np.median(fin)) if fin.size else None,
            "p90_finite": float(np.quantile(fin, 0.9)) if fin.size else None, "n_le_10pct": int(np.sum(v <= 0.10))}


def resid_stats(r: np.ndarray) -> dict:
    """D-ID's summary rule (``Diagnostic.summaries``): |r| over the finite values, numpy median and p90. An empty set
    gives NaN, which no leg of the rule can satisfy."""
    v = np.abs(np.asarray(r, float))
    v = v[np.isfinite(v)]
    if not v.size:
        return {"median": float("nan"), "p90": float("nan"), "max": float("nan"), "n": 0}
    return {"median": float(np.median(v)), "p90": float(np.quantile(v, 0.9)), "max": float(v.max()), "n": int(v.size)}


def ratio(a: float, b: float) -> float:
    """a / b for the margins; inf when b is 0 and a is not, NaN when both are."""
    if b == 0:
        return float("nan") if a == 0 else float("inf")
    return a / b


def leg_a(w: dict, base_median: float, rule: dict) -> bool:
    return (w["median"] <= rule["width_median_max"] and w["p90"] <= rule["width_p90_max"]) \
        or w["median"] <= rule["width_halving"] * base_median


def leg_b(res: dict, base: dict, rule: dict) -> int:
    """How many of the four departures have their J median |r_IBU(5)| cut to <= (1 - 1/3) x the f = 1 value."""
    return sum(res[d] <= rule["cut_keep_fraction"] * base[d] for d in DEPARTURES)


def global_null(f1_split: dict, f1_swap: dict, null_split: dict, rule: dict) -> dict:
    """The memo's null: the 3-bin uniform axis leaves the decisive figures (the J T2 width median, the four departures'
    J median |r(5)|) within max(k x |split - swap| at f = 1, rel x |f = 1|)."""
    q = {"width_median": (f1_split["width"]["median"], f1_swap["width"]["median"], null_split["width"]["median"])}
    q.update({f"resid_{d}": (f1_split["resid"][d], f1_swap["resid"][d], null_split["resid"][d]) for d in DEPARTURES})
    rows = {}
    for k, (a, s, n) in q.items():
        band = max(rule["null_band_k"] * abs(a - s), rule["null_band_rel"] * abs(a))
        rows[k] = {"f1_split": a, "f1_swap": s, "null": n, "band": band, "within": abs(n - a) <= band}
    return {"per_quantity": rows, "pass": all(v["within"] for v in rows.values())}


def verdict(cfgs: dict, rule: dict, null_check: dict) -> dict:
    """The declared rule (DECLARATION section 1 and 4.3) on split-half figures only, over ANY OF the 11 decisive
    configurations.

    ``cfgs[name] = {"width": width_stats at T2, "resid": {departure: J median |r(5)|}, "twin": name or None,
    "decisive": bool}``; the baseline is ``cfgs["f1"]``. Per decisive X with twin T:
    * UNDETERMINED if T satisfies leg A or leg B (the instrument reads noise as information at X's occupancy);
    * PASS if X satisfies leg A and leg B, X's width median is below T's, and X's residual is below T's at >= 3 of
      the four departures;
    * FAIL otherwise.
    R10: INCOMPLETE if the global null fails; else PASS if any X passes; else STOP if every X fails; else INCOMPLETE.
    The margins over the twin are reported for every X (the director's condition: multiplicity made visible)."""
    base = cfgs["f1"]
    need = rule["min_departures"]
    rows = {}
    for name, c in cfgs.items():
        if not c.get("decisive"):
            continue
        t = cfgs[c["twin"]]
        a, b = leg_a(c["width"], base["width"]["median"], rule), leg_b(c["resid"], base["resid"], rule)
        ta, tb = leg_a(t["width"], base["width"]["median"], rule), leg_b(t["resid"], base["resid"], rule)
        beat_w = c["width"]["median"] < t["width"]["median"]
        beat_r = sum(c["resid"][d] < t["resid"][d] for d in DEPARTURES)
        if ta or tb >= need:
            state = "UNDETERMINED"
        elif a and b >= need and beat_w and beat_r >= need:
            state = "PASS"
        else:
            state = "FAIL"
        rows[name] = {"state": state, "leg_a": a, "leg_b_departures": b, "twin": c["twin"], "twin_leg_a": ta,
                      "twin_leg_b_departures": tb, "beats_twin_width": beat_w, "beats_twin_residual_departures": beat_r,
                      "margin": {"width_median_x_over_twin": ratio(c["width"]["median"], t["width"]["median"]),
                                 "width_median_x_over_f1": ratio(c["width"]["median"], base["width"]["median"]),
                                 "resid_x_over_twin": {d: ratio(c["resid"][d], t["resid"][d]) for d in DEPARTURES},
                                 "resid_x_over_f1": {d: ratio(c["resid"][d], base["resid"][d]) for d in DEPARTURES}}}
    states = [v["state"] for v in rows.values()]
    passing = sorted(k for k, v in rows.items() if v["state"] == "PASS")
    if not null_check["pass"]:
        word = "INCOMPLETE"
    elif passing:
        word = "PASS"
    elif all(s == "FAIL" for s in states):
        word = "STOP"
    else:
        word = "INCOMPLETE"
    return {"verdict": word, "passing": passing, "n_decisive": len(rows),
            "undetermined": sorted(k for k, v in rows.items() if v["state"] == "UNDETERMINED"),
            "global_null": null_check, "per_config": rows}


# ------------------------------------------------------------------------------------------- the run
class R10:
    def __init__(self, cfg: dict, inputs: Path, extra: Path, out: Path, did_cfg: dict | None = None,
                 did_tables: Path | None = None, did_results: Path | None = None):
        """``did_cfg``, ``did_tables`` and ``did_results`` replace D-ID's committed files only in the synthetic tests
        (``test_r10.py``)."""
        self.cfg, self.inputs, self.extra_path, self.outdir, self.did_cfg = cfg, inputs, extra, out, did_cfg
        self.did_tables = did_tables or REPO / cfg["did"]["tables"]["path"]
        self.did_results = did_results or REPO / cfg["did"]["results"]["path"]
        self.did = load_did(cfg)
        self.out = {"schema": "r10-results/1", "status": "running",
                    "code_sha256": {"r10.py": sha256(Path(__file__).resolve()), "config.json": sha256(CONFIG)},
                    "controls": {}, "configs": {}, "variables": {}, "timing": {}}
        self.arrays: dict = {}
        self.t0 = time.time()

    def save(self) -> None:
        """Written after every configuration and on any failure, so a late cap or error keeps what was done."""
        self.out["timing"] = {"wall_s": time.time() - self.t0,
                              "cpu_s": self.budget.used_s() if hasattr(self, "budget") else None,
                              "peak_rss_bytes": self.budget.peak_rss_bytes() if hasattr(self, "budget") else None}
        self.outdir.mkdir(parents=True, exist_ok=True)
        tmp = self.outdir / "r10_results.json.tmp"
        tmp.write_text(json.dumps(self.out, indent=1, default=float) + "\n")
        tmp.replace(self.outdir / "r10_results.json")

    def _build_did(self):
        did, cfg = self.did, self.cfg
        dcfg = copy.deepcopy(self.did_cfg or json.loads((REPO / cfg["did"]["config"]["path"]).read_text()))
        dcfg["weight_sets"] = [w for w in dcfg["weight_sets"] if w["name"] in cfg["weight_sets"]]
        outer = self

        class Base(did.Diagnostic):
            def build_rows(self) -> None:
                d = self.d
                m = np.asarray(d["pass_truth"], bool)
                m_idx = np.flatnonzero(m)
                pr = np.asarray(d["pass_reco"], bool)[m]
                outer.rf = {}
                for f in (1, 2, 4):
                    e = refined(self.edges, f)
                    rf = -np.ones(m_idx.size, dtype=np.int64)
                    rf[pr] = did.by_chunks(self.com.s5e_trace.flat_index, d["MCreco"], e, m_idx[pr])
                    outer.rf[f] = rf
                    outer.out.setdefault("refinement", {})[str(f)] = {"n_cells_total": int(np.prod([len(x) - 1 for x in e]))}
                outer.n_rows_all = int(m.size)
                super().build_rows()
                # K0 (plumbing): the f = 1 rows built here are D-ID's; the refinements keep exactly the same rows on grid
                k0 = {"f1_equals_did": bool(np.array_equal(self.m_idx, m_idx)
                                            and np.array_equal(outer.rf[1], self.rf_fine.astype(np.int64))),
                      "same_rows_on_grid_f2": bool(np.array_equal(outer.rf[2] >= 0, outer.rf[1] >= 0)),
                      "same_rows_on_grid_f4": bool(np.array_equal(outer.rf[4] >= 0, outer.rf[1] >= 0))}
                k0["pass"] = all(k0.values())
                outer.out["controls"]["K0_rows"] = k0
                if not k0["pass"]:
                    raise did.AdmissionFailure(f"K0: {k0}")

            def histograms(self) -> None:
                outer.rows = {k: getattr(self, k) for k in ("tf", "rf_fine", "wt", "wr", "pr", "m_idx")}
                key = int(self.cfg["split"]["key"])
                outer.rows["is_b"] = self.com.s5n_pseudo.s5c_pseudo.half_mask(self.d["MCgen"].shape[0], key)[self.m_idx]
                outer.rw = {ws.name: self.weights(ws) for ws in self.sets}
                super().histograms()

        budget = did.Budget(cfg["limits"]["cpu_core_hours"], 0.0, cfg["limits"]["ram_bytes"])
        self.budget = budget
        cmp = did.load_comparator(dcfg["code"]["comparator.py"])
        com = did.load_committed(dcfg["code"]["nd-unfolding"])
        run = Base(dcfg, self.inputs, Path("/nonexistent-not-written"), budget, cmp, com)
        run.checkpoint = lambda: None
        run.check_records()
        run.load_events()
        run.build_rows()
        run.histograms()
        run.grids()
        self.run = run
        self.out["admission"] = {k: v["pass"] for k, v in run.out["admission"].items()}
        self.J = run.reported_positions("J")
        self.groups = {g: run.reported_positions(g) for g in ("J", "EW", "H2")}

    # ---- K1: D-ID's own machinery reproduces its committed tables, bitwise, on full per-functional arrays
    def control_did(self) -> None:
        run, cfg = self.run, self.cfg
        tables = np.load(self.did_tables)
        summ = json.loads(Path(self.did_results).read_text())["summaries"]
        f183 = np.asarray(run.f183)
        out = {}
        for grid in ("T1", "T2"):
            w = run.widths(grid, "nominal", "nom")
            out[f"widths_{grid}"] = bool(np.array_equal(w["sigma_rel"][f183], tables[f"{grid}/nominal/widths_nom/sigma_rel"],
                                                        equal_nan=True))
        for ws in cfg["weight_sets"]:
            tr = run.run_trajectory("T2", ws, "same", "nom", keep_all=True)
            i5 = tr["K"].index(5)
            want = tables[f"traj/T2/same/nom/{ws}/r"]
            out[f"r_K5_all_functionals_{ws}"] = bool(int(tables[f"traj/T2/same/nom/{ws}/K"][i5]) == 5
                                                     and np.array_equal(tr["r"][i5][f183], want[i5], equal_nan=True))
            got = resid_stats(tr["r"][i5][self.J])["median"]
            m = summ[ws]["J"]["r_ibu_T2_nom_K5"]["median"]
            out[f"J_median_K5_{ws}"] = {"got": got, "want": m, "equal": got == m}
        out["pass"] = all(v if isinstance(v, bool) else v["equal"] for v in out.values())
        self.out["controls"]["K1_did_reproduced"] = out
        if not out["pass"]:
            raise self.did.AdmissionFailure(f"K1: D-ID not reproduced: {out}")

    # ---- the generic configuration path
    def hist(self, cell: np.ndarray, pop: np.ndarray | None, sets: list[str], swap: bool) -> dict:
        did, run, rw = self.did, self.run, self.rw
        tf, rf, wt, wr, pr, is_b = (self.rows[k] for k in ("tf", "rf_fine", "wt", "wr", "pr", "is_b"))
        in_t = tf >= 0
        sig_reco = pr & (rf >= 0)
        if pop is not None:
            in_t, sig_reco = in_t & pop, sig_reco & pop
        pair_rows, bkg_rows = sig_reco & in_t, sig_reco & ~in_t
        uniq, comp = np.unique(cell[sig_reco], return_inverse=True)
        c = np.full(cell.size, -1, np.int64)
        c[sig_reco] = comp.ravel()
        n_c = uniq.size
        a, bh = ~is_b, is_b
        pairs = did.Pairs.build(c[pair_rows], tf[pair_rows], run.n_fine)
        pairs_a = did.Pairs.build(c[pair_rows & a], tf[pair_rows & a], run.n_fine)
        pairs_b = did.Pairs.build(c[pair_rows & bh], tf[pair_rows & bh], run.n_fine) if swap else None
        h = {}
        for ws in sets:
            r = rw[ws]
            wtr, wrr = wt * r, wr * r
            if pop is None:
                u, ua, ub = run.h[ws]["u"], run.h[ws]["split"]["u_a"], run.h[ws]["split"]["u_b"]
            else:
                u = np.bincount(tf[in_t], weights=wtr[in_t], minlength=run.n_fine)
                ua = 2.0 * np.bincount(tf[in_t & a], weights=wtr[in_t & a], minlength=run.n_fine)
                ub = 2.0 * np.bincount(tf[in_t & bh], weights=wtr[in_t & bh], minlength=run.n_fine)
            h[ws] = {"u": u, "y": np.bincount(c[sig_reco], weights=wrr[sig_reco], minlength=n_c),
                     "b": np.bincount(c[bkg_rows], weights=wrr[bkg_rows], minlength=n_c),
                     "P": pairs.sums(wrr[pair_rows]),
                     "split": {"u_a": ua, "u_b": ub,
                               "y_b": 2.0 * np.bincount(c[sig_reco & bh], weights=wrr[sig_reco & bh], minlength=n_c),
                               "b_a": 2.0 * np.bincount(c[bkg_rows & a], weights=wrr[bkg_rows & a], minlength=n_c),
                               "P_a": 2.0 * pairs_a.sums(wrr[pair_rows & a])}}
            if swap:  # the halves exchanged: response from B, data from A (the noise band only)
                h[ws]["split"].update({
                    "y_a": 2.0 * np.bincount(c[sig_reco & a], weights=wrr[sig_reco & a], minlength=n_c),
                    "b_b": 2.0 * np.bincount(c[bkg_rows & bh], weights=wrr[bkg_rows & bh], minlength=n_c),
                    "P_b": 2.0 * pairs_b.sums(wrr[pair_rows & bh])})
            del wtr, wrr
        cells = np.flatnonzero(h["nominal"]["y"] > 0)  # D-ID: the occupied cells of the nominal fold
        remap = -np.ones(n_c, dtype=np.int64)
        remap[cells] = np.arange(cells.size)
        for p in (pairs, pairs_a, pairs_b):
            if p is not None:
                p.reco = remap[p.reco]
                if np.any(p.reco < 0):
                    raise did.AdmissionFailure("a signal pair lies outside the occupied reco cells")
        for x in h.values():
            for k in ("y", "b"):
                x[k] = x[k][cells]
            for k in ("y_b", "b_a", "y_a", "b_b"):
                if k in x["split"]:
                    x["split"][k] = x["split"][k][cells]
        return {"h": h, "pairs": pairs, "pairs_a": pairs_a, "pairs_b": pairs_b, "n_reco": int(cells.size),
                "n_cells_raw": int(n_c)}

    def problem(self, H: dict, grid: str, ws: str, role: str) -> dict:
        """D-ID's ``Diagnostic.problem`` with the nominal weighting, on a configuration's histograms (``swap``: the
        split with the halves exchanged)."""
        did, run = self.did, self.run
        g, h, h0 = run.G[grid], H["h"][ws], H["h"]["nominal"]
        if role == "same":
            u_w, r = h0["u"], did.response(g, H["pairs"], h0["P"], h0["u"], H["n_reco"])
            y, b, prior = h["y"], h0["b"], did.coarse_sum(g, h0["u"])
            truth_f, t_bin = run.f_true(h["u"]), did.coarse_sum(g, h["u"])
        elif role == "split":
            s, s0 = h["split"], h0["split"]
            u_w, r = s0["u_a"], did.response(g, H["pairs_a"], s0["P_a"], s0["u_a"], H["n_reco"])
            y, b, prior = s["y_b"], s0["b_a"], did.coarse_sum(g, s0["u_a"])
            truth_f, t_bin = run.f_true(s["u_b"]), did.coarse_sum(g, s["u_b"])
        elif role == "swap":
            s, s0 = h["split"], h0["split"]
            u_w, r = s0["u_b"], did.response(g, H["pairs_b"], s0["P_b"], s0["u_b"], H["n_reco"])
            y, b, prior = s["y_a"], s0["b_b"], did.coarse_sum(g, s0["u_b"])
            truth_f, t_bin = run.f_true(s["u_a"]), did.coarse_sum(g, s["u_a"])
        else:
            raise ValueError(role)
        maps = did.functional_matrix(run.U_kappa, g, u_w)
        return {"R": r, "y": y, "b": b, "prior": prior, "truth_f": truth_f, "t_bin": t_bin, "maps": maps}

    def residuals(self, pb: dict) -> dict:
        did = self.did
        ks = tuple(self.cfg["iterations"]["record"])
        res = did.ibu(pb["R"], pb["y"], pb["b"], pb["prior"], max(ks), maps=pb["maps"], record=ks)
        return {k: did.rel(row, pb["truth_f"]) for k, row in zip(sorted(set(ks)), res.trajectory)}

    def widths(self, pb: dict) -> np.ndarray:
        did = self.did
        f = did.fisher(pb["R"], pb["t_bin"], pb["b"])
        values, vectors = np.linalg.eigh(f)
        norms = np.linalg.norm(pb["maps"], axis=1)
        sigma = np.full(pb["maps"].shape[0], np.nan)
        ok = norms > 0
        sigma[ok], _ = did.widths_from_eig(values, vectors, pb["maps"][ok])
        value = pb["maps"] @ pb["t_bin"]
        return np.divide(sigma, np.abs(value), out=np.full_like(sigma, np.nan), where=np.abs(value) > 0)

    def evaluate(self, name: str, cell: np.ndarray, roles: tuple, keep_arrays: bool,
                 enu: bool = True) -> tuple[dict, dict]:
        cfg = self.cfg
        self.budget.check(0.0)
        t = time.time()
        H = self.hist(cell, None, cfg["weight_sets"], swap="swap" in roles)
        rec = {"n_reco_cells": H["n_reco"], "n_cells_with_rows": H["n_cells_raw"], "roles": {}}
        arrays = {}
        for role in roles:
            rr = {"resid": {}, "width": {}}
            for ws in cfg["weight_sets"]:
                r = self.residuals(self.problem(H, "T2", ws, role))
                rr["resid"][ws] = {str(k): {g: resid_stats(v[idx]) for g, idx in self.groups.items()} for k, v in r.items()}
                if keep_arrays:
                    arrays[f"{name}/{role}/{ws}/r_K5"] = r[5]
            for grid in ("T1", "T2"):
                s = self.widths(self.problem(H, grid, "nominal", role))
                rr["width"][grid] = {g: width_stats(s[idx]) for g, idx in self.groups.items()}
                arrays[f"{name}/{role}/{grid}/sigma_rel"] = s
            rec["roles"][role] = rr
            self.budget.check(0.0)
        del H  # memory: the restricted population's histograms are built only after
        if not enu:
            return rec, arrays
        # E_nu < 20 GeV (descriptive, DECLARATION section 6): GiBUU and its nominal reference, residuals only
        Hp = self.hist(cell, self.enu_lt20, ["nominal", "gibuu"], swap=False)
        rec["enu_lt20_descriptive"] = {
            role: {ws: {str(k): {"J": resid_stats(v[self.J])} for k, v in
                        self.residuals(self.problem(Hp, "T2", ws, role)).items()} for ws in ("nominal", "gibuu")}
            for role in ("split", "same")}
        del Hp
        rec["seconds"] = time.time() - t
        rec["cpu_s_cumulative"] = self.budget.used_s()
        rec["peak_rss_bytes"] = self.budget.peak_rss_bytes()
        return rec, arrays

    def cells(self) -> dict:
        """Every declared configuration's reco cell per row (-1 off the reco grid), built on demand (memory)."""
        cfg = self.cfg
        x = np.load(self.extra_path, allow_pickle=False)
        m_idx = self.rows["m_idx"]
        raw = {b: np.asarray(x[b], float)[m_idx] for b in cfg["extract"]["branches"]}
        self.enu_lt20 = np.asarray(x["E_nu_MeV"], float)[m_idx] < cfg["enu_cut_MeV"]
        self.out["variables"]["enu_lt20_rows"] = int(self.enu_lt20.sum())
        use = self.rows["pr"] & (self.rows["rf_fine"] >= 0)
        wnom = self.rows["wr"] * self.rw["nominal"]
        bins = {}
        for v in ("C1", "C2", "C3", "C4"):
            bins[v], self.out["variables"][v] = tertile_bins(derived_variable(v, raw), wnom, use)
        del raw, x
        rf1, rf2, rf4 = self.rf[1], self.rf[2], self.rf[4]
        on = rf1 >= 0
        seed = int(cfg["null_seed"])
        made = {
            "f1": lambda: rf1,
            "null3@f1": lambda: np.where(on, rf1 * 4 + np.minimum(
                (np.random.default_rng([seed, 0]).random(rf1.size) * 3).astype(np.int64), 2), -1),
            "f2": lambda: rf2,
            "f4": lambda: rf4,
            "C2xC3@f1": lambda: np.where(on, rf1 * 16 + bins["C2"].astype(np.int64) * 4 + bins["C3"], -1),
        }
        for v in ("C1", "C2", "C3", "C4"):
            made[f"{v}@f1"] = lambda v=v: np.where(on, rf1 * 4 + bins[v], -1)
            made[f"{v}@f2"] = lambda v=v: np.where(on, rf2 * 4 + bins[v], -1)
        out = {}
        decisive = [k for k in made if k not in ("f1", "null3@f1")]
        for i, k in enumerate(decisive, start=1):
            out[k] = {"make": made[k], "decisive": True, "twin": f"{k}~null"}
            out[f"{k}~null"] = {"make": lambda k=k, i=i: permuted_within(rf1, made[k](), [seed, i]),
                                "decisive": False, "twin": None}
        out["f1"] = {"make": made["f1"], "decisive": False, "twin": None}
        out["null3@f1"] = {"make": made["null3@f1"], "decisive": False, "twin": None}
        missing = sorted(set(out) ^ set(cfg["order"]))
        if missing:
            raise ValueError(f"config order and declared configurations differ: {missing}")
        return out

    def go(self) -> int:
        try:
            return self._go()
        except Exception as exc:  # noqa: BLE001  any raise: INCOMPLETE, and what was done is kept
            self.out["status"] = "INCOMPLETE"
            self.out["exception"] = {"type": type(exc).__name__, "message": str(exc),
                                     "traceback": traceback.format_exc()}
            self.save()
            if self.arrays:
                np.savez_compressed(self.outdir / "r10_tables.npz", **self.arrays)
            return 4

    def controls_only(self) -> int:
        """K0, K1 and K2 on the real events, before any extraction: D-ID's own figures and the generic path's equality
        to them at f = 1. Only the control outcomes are recorded; no R10 readout is kept or printed."""
        try:
            self._build_did()
            self.control_did()
            rec, arrays = self.evaluate("f1", self.rf[1], ("split", "same"), keep_arrays=True, enu=False)
            self.control_generic(arrays)
            self.out["status"] = "controls-only: pass"
            rc = 0
        except Exception as exc:  # noqa: BLE001
            self.out["status"] = "controls-only: FAIL"
            self.out["exception"] = {"type": type(exc).__name__, "message": str(exc)}
            rc = 4
        self.out = {k: self.out[k] for k in ("schema", "status", "code_sha256", "controls", "admission", "exception")
                    if k in self.out}
        self.save()
        return rc

    def _go(self) -> int:
        cfg = self.cfg
        self._build_did()
        self.save()
        self.control_did()
        self.save()
        cfgs = self.cells()
        arrays = self.arrays
        for name in cfg["order"]:
            c = cfgs[name]
            roles = ("split", "same", "swap") if name in ("f1", "null3@f1") else ("split", "same")
            rec, arr = self.evaluate(name, c["make"](), roles, keep_arrays=name == "f1")
            rec.update({k: c[k] for k in ("decisive", "twin")})
            self.out["configs"][name] = rec
            arrays.update(arr)
            print(name, json.dumps({"n_reco_cells": rec["n_reco_cells"], "seconds": round(rec["seconds"], 1),
                                    "peak_rss_GB": round(rec["peak_rss_bytes"] / 1e9, 2)}), flush=True)
            if name == "f1":
                self.control_generic(arrays)
            self.save()
        view = {k: self.rule_view(k, "split") for k in self.out["configs"]}
        null_check = global_null(view["f1"], self.rule_view("f1", "swap"), view["null3@f1"], cfg["rule"])
        self.out["verdict"] = verdict(view, cfg["rule"], null_check)
        self.out["status"] = "complete"
        np.savez_compressed(self.outdir / "r10_tables.npz", **arrays)
        self.save()
        return 0

    def control_generic(self, arrays: dict) -> None:
        """K2: the generic path at f = 1 equals D-ID's machinery bitwise, on the full arrays: the K = 5 residual of
        every functional for every weight set in the same and split roles, the same-role widths at T1 and T2
        (D-ID's ``widths``), and the split-role widths (this file's Fisher on D-ID's own split problem)."""
        run, cfg = self.run, self.cfg
        out = {}
        for ws in cfg["weight_sets"]:
            for role in ("same", "split"):
                tr = run.run_trajectory("T2", ws, role, "nom", keep_all=False)
                out[f"r5_{role}_{ws}"] = bool(np.array_equal(arrays[f"f1/{role}/{ws}/r_K5"], tr["r"][tr["K"].index(5)],
                                                             equal_nan=True))
        for grid in ("T1", "T2"):
            out[f"width_same_{grid}"] = bool(np.array_equal(arrays[f"f1/same/{grid}/sigma_rel"],
                                                            run.widths(grid, "nominal", "nom")["sigma_rel"], equal_nan=True))
            out[f"width_split_{grid}"] = bool(np.array_equal(arrays[f"f1/split/{grid}/sigma_rel"],
                                                             self.widths(run.problem(grid, "nominal", "split", "nom")),
                                                             equal_nan=True))
        out["pass"] = all(out.values())
        self.out["controls"]["K2_generic_equals_did_at_f1"] = out
        if not out["pass"]:
            raise self.did.AdmissionFailure(f"K2: generic path differs from D-ID at f = 1: {out}")

    def rule_view(self, name: str, role: str) -> dict:
        c = self.out["configs"][name]["roles"][role]
        return {"width": c["width"]["T2"]["J"], "resid": {d: c["resid"][d]["5"]["J"]["median"] for d in DEPARTURES},
                "twin": self.out["configs"][name]["twin"], "decisive": self.out["configs"][name]["decisive"]}


def check_extract_receipt(rc: dict, extra: Path, cfg: dict, extract_code: Path) -> list[str]:
    """Why an extraction receipt does not admit ``extra`` (empty list = admitted)."""
    bad = []
    if rc.get("exit") != 0:
        bad.append("exit is not 0")
    if rc.get("rows", {}).get("complete") is not True:
        bad.append("rows not complete")
    pls = rc.get("playlists", {})
    if sorted(pls) != sorted(cfg["extract"]["playlists"]) or not all(p.get("pass") for p in pls.values()):
        bad.append("not every declared playlist admitted")
    if rc.get("code", {}).get("r10_extract.py") != sha256(extract_code):
        bad.append("r10_extract.py differs from the extraction's")
    of = rc.get("inputs", {}).get(cfg["extract"]["inputs"]["of_inputs"], {})
    if of.get("sha256") != cfg["extract"]["of_inputs_sha256"]:
        bad.append("of_inputs_5d sha256 differs")
    if sha256(extra) != rc.get("output", {}).get("sha256"):
        bad.append("r10_extra.npz differs from the receipt's output")
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--config", type=Path, default=CONFIG)
    ap.add_argument("--inputs", type=Path, required=True, help="directory holding nd-unfolding/of_inputs_5d.npz")
    ap.add_argument("--extra", type=Path, default=None, help="r10_extra.npz from r10_extract.py")
    ap.add_argument("--extract-receipt", type=Path, default=None, help="r10_extract_receipt.json of that run")
    ap.add_argument("--controls-only", action="store_true",
                    help="K0-K2 on the real events before any extraction; records only the control outcomes")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    cfg = json.loads(a.config.read_text())
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        if os.environ.get(var) != str(cfg["limits"]["threads"]):
            print(f"refusing: {var} must be {cfg['limits']['threads']} (D-ID's run record)", file=sys.stderr)
            return 2
    if (a.out / "r10_results.json").exists():
        print("refusing to overwrite r10_results.json", file=sys.stderr)
        return 3
    if a.controls_only:
        return R10(cfg, a.inputs, None, a.out).controls_only()
    if a.extra is None or a.extract_receipt is None:
        print("refusing: --extra and --extract-receipt are required for the run", file=sys.stderr)
        return 2
    bad = check_extract_receipt(json.loads(a.extract_receipt.read_text()), a.extra, cfg, HERE / "r10_extract.py")
    if bad:
        print(f"refusing: the extraction receipt does not admit this r10_extra.npz: {bad}", file=sys.stderr)
        return 2
    return R10(cfg, a.inputs, a.extra, a.out).go()


if __name__ == "__main__":
    sys.exit(main())
