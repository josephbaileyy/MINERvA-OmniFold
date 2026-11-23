#!/usr/bin/env python3
"""IBUB's readout at one tune (IBUB-DECLARATION.md sections 2 and 4-6), on a login node at 0 node-h.

It reads:
- OmniFold's 300 stored toy outputs, COV2D's committed records and the tune's truth_xsec.npz, every one through
  ``cov2d_readout.Run``. That is COV2D's own harness: an open audit that refuses any plain open under /pscratch or
  /global/cfs, private O_NOATIME copies checked against their digests, and the atime ledger.
- the IBU units' products, checked against their done-markers' digests.

It then makes three things:
- C-OF, C-TRUTH, C-COMPLETE, C-DATA and C-CELLS (section 5);
- the readings of section 4, on the pre-surrogate errors, at K = 10 and at K = 5;
- the descriptive readouts of section 6.

The COV2D code is imported unchanged: ``cov2d_score.errors`` and ``lateral_deltas``, ``cov2d_readouts.bias`` and
``spread_alone``, and ``cov2d_readout``'s ``Run``, ``completeness``, ``plan``, ``inventory_paths``, ``read_pinned`` and
``read_provenance``.

  python ibub_readout.py --truth G18 --units DIR --out DIR [--run-dir O]

It writes ``ibub_<T>.json`` (the record, through ``Run.finish``) and ``ibub_<T>_errors.npz`` (the per-toy errors).

MEASURES: the declared readings at one tune. CANNOT AUTHORIZE: any statement beyond section 7; the readings go to
the director.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import tempfile
from pathlib import Path
from statistics import NormalDist

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for p in (HERE, REPO / "2d-unfolding" / "cov2d", REPO / "nd-unfolding"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import cov2d as c  # noqa: E402
import cov2d_blocks as cb  # noqa: E402
import cov2d_readout as rd  # noqa: E402
import cov2d_readouts as cr  # noqa: E402
import cov2d_score as cs  # noqa: E402
import ibub_unit as iu  # noqa: E402

NX, NY = 14, 16
SCHEMA = "ibub-readout/1"
COND_MAX = 1e12


# ------------------------------------------------------------------------------------------- the tests (section 4)


def test_matrix(flat, area) -> tuple[np.ndarray, list]:
    """W (cells x tests) and the tests' labels: each reported cell, then the 14 p_T bands, the 16 p_par bands and the
    total, each band the area-weighted integral of its reported cells (section 4)."""
    flat, area = np.asarray(flat), np.asarray(area, np.float64)
    n = flat.size
    cols, labels = [np.eye(n)], [f"cell:{int(g)}" for g in flat]
    for name, key, count in (("pt", flat // NY, NX), ("pz", flat % NY, NY)):
        for b in range(count):
            m = key == b
            if not m.any():
                raise c.Refusal(f"band {name}:{b} has no reported cell")
            cols.append(np.where(m, area, 0.0)[:, None])
            labels.append(f"{name}:{b}")
    cols.append(area[:, None])
    labels.append("total")
    return np.hstack(cols), labels


def z_star(alpha: float, tests: int) -> float:
    return NormalDist().inv_cdf(1 - alpha / 2 / tests)


def bootstrap_counts(n: int, B: int, seed: list) -> np.ndarray:
    """(B, n): how often each toy index is drawn in each of B resamples with replacement, from default_rng(seed)."""
    idx = np.random.default_rng(seed).integers(0, n, size=(B, n))
    counts = np.zeros((B, n))
    np.add.at(counts, (np.arange(B)[:, None], idx), 1.0)
    return counts


def ratio(a, b) -> np.ndarray:
    """a / b elementwise; where b is 0 it is 0 if a is 0, else +-inf with a's sign (never a silent NaN)."""
    a, b = np.broadcast_arrays(np.asarray(a, np.float64), np.asarray(b, np.float64))
    out = np.divide(a, b, out=np.zeros(a.shape), where=b != 0)
    zero = (b == 0) & (a != 0)
    out[zero] = np.copysign(np.inf, a[zero])
    return out


def per_test(Y: np.ndarray, counts: np.ndarray, zs: float, xt: np.ndarray, sigma: np.ndarray) -> dict:
    """The mean over the toys of Y (toys x tests), its toy-bootstrap SE (the same resamples for every caller), the
    analytic SE, and the mean in % of the mean truth, in sigma and in SE."""
    n = Y.shape[0]
    mean = Y.mean(axis=0)
    se_boot = (counts @ Y / n).std(axis=0, ddof=1)
    se_an = Y.std(axis=0, ddof=1) / np.sqrt(n)
    z = ratio(mean, se_boot)
    return {"mean": mean, "se_boot": se_boot, "se_analytic": se_an, "rel_pct": 100 * ratio(mean, xt),
            "in_sigma": ratio(mean, sigma), "z": z, "resolved": np.abs(z) > zs}


def hotelling(D: np.ndarray) -> dict:
    """Descriptive only (section 4): T^2 = n dbar' S^-1 dbar on the cells, with S the paired differences' sample
    covariance (ddof 1), F = (n - p) / (p (n - 1)) T^2 against F(p, n - p), and S's condition number."""
    from scipy import stats
    n, p = D.shape
    S = np.cov(D, rowvar=False, ddof=1)
    dbar = D.mean(axis=0)
    cond = float(np.linalg.cond(S))
    none = {"T2": None, "F": None, "p_value": None, "df": [p, n - p], "cond_S": cond, "read_by": "nothing"}
    if not np.isfinite(cond) or cond > COND_MAX:   # COV2D's null-subspace threshold, 1e-12 of the largest eigenvalue
        return dict(none, why=f"S is ill-conditioned (cond {cond:.3g} > {COND_MAX:g})")
    try:
        t2 = float(n * dbar @ np.linalg.solve(S, dbar))
    except np.linalg.LinAlgError as e:
        return dict(none, why=f"S is singular ({e})")
    F = (n - p) / (p * (n - 1)) * t2
    return {"T2": t2, "F": F, "p_value": float(stats.f.sf(F, p, n - p)) if n > p else None, "df": [p, n - p],
            "cond_S": cond, "read_by": "nothing"}


def statistics(E_of: np.ndarray, E_ibu: np.ndarray, x_true: np.ndarray, W: np.ndarray, labels: list, C_T: np.ndarray,
               counts: np.ndarray, alpha: float, n_cells: int) -> dict:
    """Section 4 at one K: each method's bias per test, the paired difference (the truth cancels toy by toy), and the
    rule over the family of all tests."""
    from scipy import stats
    n, tests = E_of.shape[0], W.shape[1]
    zs = z_star(alpha, tests)
    xt = (x_true @ W).mean(axis=0)
    sigma = np.sqrt(np.einsum("ct,cd,dt->t", W, C_T, W))
    Y = {"OF": E_of @ W, "IBU": E_ibu @ W}
    m = {k: per_test(v, counts, zs, xt, sigma) for k, v in Y.items()}
    d = per_test(Y["IBU"] - Y["OF"], counts, zs, xt, sigma)
    d["resolution_rel_pct"] = 100 * zs * ratio(d["se_boot"], np.abs(xt))
    d["unpaired_ratio"] = ratio(np.abs(m["IBU"]["mean"] - m["OF"]["mean"]),
                                np.sqrt(m["IBU"]["se_boot"] ** 2 + m["OF"]["se_boot"] ** 2))
    flagged = [i for i in range(tests) if abs(d["z"][i]) > zs]
    cells = slice(0, n_cells)
    summary = {}
    for k in ("OF", "IBU"):
        r = m[k]["rel_pct"][cells]
        summary[k] = {"rms_rel_pct": float(np.sqrt(np.mean(r ** 2))), "median_abs_rel_pct": float(np.median(np.abs(r))),
                      "bias_resolved": [labels[i] for i in range(tests) if m[k]["resolved"][i]]}
    summary["cells_ibu_smaller_abs_bias"] = int(np.sum(np.abs(m["IBU"]["mean"][cells]) < np.abs(m["OF"]["mean"][cells])))
    ba = ratio(d["se_boot"], d["se_analytic"])
    return {
        "reading": "DIFFER" if flagged else "NOT RESOLVED APART",
        "differ_at": [{"test": labels[i], "d": float(d["mean"][i]), "se_boot": float(d["se_boot"][i]),
                       "z": float(d["z"][i]), "sign": "IBU above OF" if d["mean"][i] > 0 else "IBU below OF"}
                      for i in flagged],
        "z_star": zs, "t_quantile_299": float(stats.t.ppf(1 - alpha / 2 / tests, n - 1)), "tests": tests, "alpha": alpha,
        "labels": labels, "mean_truth": xt.tolist(), "sigma": sigma.tolist(),
        "method": {k: {q: np.asarray(v).tolist() for q, v in m[k].items()} for k in m},
        "difference": {q: np.asarray(v).tolist() for q, v in d.items()},
        "summary": summary,
        "bootstrap_over_analytic_se": {"median": float(np.median(ba)), "min": float(np.min(ba)), "max": float(np.max(ba))},
        "hotelling": hotelling(Y["IBU"][:, cells] - Y["OF"][:, cells]),
    }


# ------------------------------------------------------------------------------------------- the controls (section 5)


def c_of(E_post: np.ndarray, C_T: np.ndarray, C_model_abs: np.ndarray, score: dict, tol: float = 1e-12) -> dict:
    """C-OF: COV2D's bias and spread_alone readouts, rebuilt from the stored outputs and the recorded surrogates, equal
    the committed record's. p_hat is a count and must agree exactly; the other fields agree to tol."""
    sigma = np.sqrt(np.diag(C_T))
    got = {"bias": cr.bias(E_post, sigma), **cr.spread_alone(E_post, C_T, C_model_abs)}
    want = {"bias": score["bias"], **{k: score["spread_alone"][k] for k in ("p_hat", "pull_mean", "pull_sd")}}
    out = {}
    for k in ("bias", "pull_mean", "pull_sd", "p_hat"):
        a, b = np.asarray(got[k], np.float64), np.asarray(want[k], np.float64)
        diff = float(np.max(np.abs(a - b))) if a.shape == b.shape else float("inf")
        out[k] = {"max_abs_diff": diff, "pass": bool(diff == 0.0 if k == "p_hat" else diff <= tol)}
    out["pass"] = all(v["pass"] for v in out.values())
    return out


def ibu_products(run, units: Path, truth: str, shas: dict, ks_want: list, rep: np.ndarray, cells, cfg: dict,
                 bound: dict) -> dict:
    """C-COMPLETE, C-TRUTH's IBU side, C-DATA and C-CELLS over the 300 IBU toy units, and their cross sections at
    K = 10 (hXSec2D) and K = 5 (the npz row), on the 205 cells.

    A unit that is absent, not PASS, unreadable at its marker's digests, or of another K scan is missing (the tune
    reads INCOMPLETE), with its problem named. A readable unit that names another toy, data file, job, runner or
    config, or lacks or fails a declared control, is a problem (the tune reads INVALID). ``bound`` is the job id and
    the runner's and config's sha256 the units must all carry."""
    c2 = cfg["c2"]
    missing, problems, x10, x5, k10 = [], [], [], [], []
    for s in c.TOY_SEEDS[truth]:
        name = f"toy_{truth}_{s}"
        try:
            marker = json.loads(cb.read_noatime(units / f"{name}.done")[0])
        except OSError:
            missing.append(s)
            continue
        if marker.get("verdict") != "PASS":
            missing.append(s)
            problems.append(f"{name}: verdict {marker.get('verdict')}")
            continue
        try:
            npz = run.copy(units / f"{name}.npz", marker["sha256"], f"{name}.npz")
            root = run.copy(units / f"{name}.root", marker["root_sha256"], f"{name}.root")
        except (c.Refusal, OSError, KeyError) as e:
            missing.append(s)
            problems.append(f"{name}: its products are not its marker's ({e})")
            continue
        z = np.load(npz)
        meta = json.loads(str(z["meta"]))
        if list(z["ks"]) != ks_want:
            missing.append(s)
            problems.append(f"{name}: K scan {list(z['ks'])}")
            continue
        if (meta.get("kind"), meta.get("tune"), meta.get("seed")) != ("toy", truth, s):
            problems.append(f"{name}: meta names {meta.get('kind')} {meta.get('tune')} {meta.get('seed')}")
        if meta.get("data_sha256") != shas[s] or marker.get("data_sha256") != shas[s]:
            problems.append(f"{name}: its data file is not toy {s}'s")
        prov = rd.read_provenance(root)
        if prov.get("dataFileSha256") != shas[s]:
            problems.append(f"{name}: dataFileSha256 {prov.get('dataFileSha256')} is not toy {s}'s")
        ctl = meta.get("controls", {})
        if set(ctl) != iu.CONTROLS["toy"]:
            problems.append(f"{name}: controls {sorted(ctl)} are not the declared {sorted(iu.CONTROLS['toy'])}")
        if not all(v.get("pass") for v in ctl.values()):
            problems.append(f"{name}: a unit control failed")
        for k in ("slurm_job", "runner_sha256", "config_sha256"):
            if str(meta.get(k)) != str(bound[k]):
                problems.append(f"{name}: {k} {meta.get(k)} is not the bound {bound[k]}")
        h = np.asarray(cells.vec(root), np.float64)
        row10 = np.asarray(z["xsec"][ks_want.index(c2["primary"])], np.float64)[rep]
        k10.append(iu.max_rel(row10, h))
        x10.append(h)
        x5.append(np.asarray(z["xsec"][ks_want.index(c2["second"])], np.float64)[rep])
    out = {"missing": missing, "problems": problems}
    if not missing:
        x10, x5 = np.stack(x10), np.stack(x5)
        out.update(x10=x10, x5=x5, k10_vs_root_max_rel=float(max(k10)),
                   nonfinite={"K10": int((~np.isfinite(x10)).sum()), "K5": int((~np.isfinite(x5)).sum())},
                   negative={"K10": int((x10 < 0).sum()), "K5": int((x5 < 0).sum())})
    return out


# ------------------------------------------------------------------------------------------- the readout


def readout(truth: str, units: Path, out: Path, run_dir: str, job: str) -> dict:
    # every plain read of the repository happens here, before Run installs the open audit
    cfg = iu.load_config()
    iu.check_code(cfg)
    rcfg, pins = cfg["readout"], cfg["cov2d_records"][truth]
    shas, rep_cfg = iu.toy_shas(cfg, truth), iu.reported_cells(cfg)
    own = {"schema": SCHEMA, "units": str(units), "config_sha256": iu.rc.sha256(iu.CONFIG),
           "readout_sha256": iu.rc.sha256(Path(__file__).resolve()), "unit_sha256": iu.rc.sha256(Path(iu.__file__)),
           "job": str(job)}
    bound = {"slurm_job": str(job), "runner_sha256": own["unit_sha256"], "config_sha256": own["config_sha256"]}
    guarded = tuple(os.path.realpath(g) for g in cb.GUARDED)
    real_out = os.path.realpath(out)
    if any(real_out == g or real_out.startswith(g + os.sep) for g in guarded):
        raise c.Refusal(f"--out {out} is under {cb.GUARDED}: the open audit refuses every plain open there")
    out.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:     # the private copies, as phase_score's
        run = rd.Run(truth, run_dir, Path(td))
        rec = run.rec
        rec.update(own)
        try:
            B = dict(np.load(io.BytesIO(rd.read_pinned(REPO / pins["blocks"], pins["blocks_sha256"]))))
            score = json.loads(rd.read_pinned(REPO / pins["score"], pins["score_sha256"]))
            cells = run.er_cells()
            rep = np.asarray(cells.rep, bool)
            # C-TRUTH: one set of cells everywhere
            if not (np.array_equal(rep, B["rep"].astype(bool)) and np.array_equal(rep, rep_cfg)):
                raise c.Refusal("E_R's cells differ from the blocks record's or the config's")
            flat = [int(i) for i in np.flatnonzero(rep)]
            comp = rd.completeness(truth)
            pl = rd.plan(truth, comp)
            files = {lab: run.copy(f"{run_dir}/out/{lab}/xsec.root", comp[lab]["sha256"], f"{lab}.root")
                     for lab in pl["toy"]}
            x_of = np.stack([cells.vec(files[lab]) for lab in pl["toy"]])
            txs = np.load(io.BytesIO(rd.read_pinned(rd.inventory_paths(run_dir, truth)["truth_xsec_npz"],
                                                    pins["truth_xsec_sha256"])))
            pa = json.loads(rd.read_pinned(rd.REC / "pseudo" / truth / "pseudo_a.json", rd.PSEUDO_A_SHA[truth]))
            natures = pa["natures"]
            nseeds = [int(s) for s in txs["seeds"]]
            if nseeds != [n["seed"] for n in natures]:
                raise c.Refusal("C-TRUTH: truth_xsec.npz's rows are not pseudo_a's natures in order")
            if [n["seed"] for n in natures if n["role"] == "toy"] != list(c.TOY_SEEDS[truth]):
                raise c.Refusal("C-TRUTH: pseudo_a's toys are not the declared seeds in order")
            if pl["toy"] != [f"T_{truth}_{s}" for s in c.TOY_SEEDS[truth]]:
                raise c.Refusal("C-TRUTH: the OmniFold labels are not the declared seeds in order")
            xs = np.asarray(txs["xsec"], np.float64).reshape(len(nseeds), -1)[:, rep]
            x_true = xs[[nseeds.index(s) for s in c.TOY_SEEDS[truth]]]
            bands = {k[len("band__"):]: v for k, v in B.items() if k.startswith("band__")}
            deltas = cs.lateral_deltas(bands, B["minos_x"])
            E_post, _ = cs.errors(x_of, x_true, natures, deltas, B["C_T"])
            E_of = x_of - x_true
            rec["C-OF"] = c_of(E_post, B["C_T"], B["C_model_abs"], score["readouts"])
            if not rec["C-OF"]["pass"]:
                rec["controls_failed"].append("C-OF")
            ibu = ibu_products(run, units, truth, shas, list(cfg["c2"]["scan"]), rep, cells, cfg, bound)
            rec["C-COMPLETE"] = {"units": len(c.TOY_SEEDS[truth]) - len(ibu["missing"]), "missing": ibu["missing"]}
            rec["C-DATA"] = {"problems": ibu["problems"]}
            if ibu["problems"]:
                rec["controls_failed"].append(f"C-DATA/C-TRUTH: {len(ibu['problems'])} problems")
            if ibu["missing"]:
                rec["verdict"] = "INCOMPLETE"
                return run.finish(out, f"ibub_{truth}.json")
            rec["C-K10"] = {"max_rel": ibu["k10_vs_root_max_rel"], "rtol": rcfg["k10_vs_root_rtol"],
                            "pass": ibu["k10_vs_root_max_rel"] <= rcfg["k10_vs_root_rtol"]}
            rec["C-CELLS"] = {"nonfinite": ibu["nonfinite"], "negative": ibu["negative"],
                              "pass": ibu["nonfinite"] == {"K10": 0, "K5": 0}}
            for k in ("C-K10", "C-CELLS"):
                if not rec[k]["pass"]:
                    rec["controls_failed"].append(k)
            if rec["controls_failed"]:
                return run.finish(out, f"ibub_{truth}.json")
            W, labels = test_matrix(flat, cells.area)
            if W.shape[1] != rcfg["tests"]:
                raise c.Refusal(f"{W.shape[1]} tests, not the declared {rcfg['tests']}")
            boot_seed = [rcfg["bootstrap_seed"], rcfg["tune_index"][truth]]
            counts = bootstrap_counts(len(x_true), rcfg["bootstrap_B"], boot_seed)
            rec["bootstrap"] = {"B": rcfg["bootstrap_B"], "seed": boot_seed}
            E5, E10 = ibu["x5"] - x_true, ibu["x10"] - x_true
            rec["readings"] = {f"K{k}": statistics(E_of, E, x_true, W, labels, B["C_T"], counts, rcfg["alpha"],
                                                   len(flat)) for k, E in ((10, E10), (5, E5))}
            sigma = np.sqrt(np.diag(B["C_T"]))
            named = {}
            for g in score["grade"]["flagged_cells"]:
                i = flat.index(int(g))
                named[str(g)] = {f"K{k}": {"b_OF": float(E_of[:, i].mean()), "b_IBU": float(E[:, i].mean()),
                                           "d": float((E - E_of)[:, i].mean())} for k, E in ((10, E10), (5, E5))}
            ratio_rec = json.loads(rd.read_pinned(*rd.C2_RECORD))
            rec["descriptive"] = {
                "surrogate_realized_mean_in_sigma": ((E_post - E_of).mean(axis=0) / sigma).tolist(),
                "cov2d_flagged_cells": named,
                "weakened_cells": c.weakened_cells(ratio_rec["b"][truth]["variance_ratio"]["option_1_clipped"],
                                                   ratio_rec["efficiency"]["cells205"])}
            np.savez_compressed(out / f"ibub_{truth}_errors.npz", seeds=np.array(list(c.TOY_SEEDS[truth])),
                                flat=np.array(flat), E_of=E_of, E_ibu10=E10, E_ibu5=E5, x_true=x_true, x_of=x_of)
            rec["reading"] = {k: v["reading"] for k, v in rec["readings"].items()}
        except Exception:
            cb.AUDIT is not None and cb.AUDIT.uninstall()
            raise
        return run.finish(out, f"ibub_{truth}.json")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--truth", required=True, choices=sorted(c.TOY_SEEDS))
    ap.add_argument("--units", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--run-dir", default=rd.RUN_DIR)
    ap.add_argument("--job", required=True, help="the bound job's id, which every unit must have run under")
    a = ap.parse_args(argv)
    rec = readout(a.truth, a.units, a.out, a.run_dir, a.job)
    print(f"IBUB-READOUT {a.truth} {rec['verdict']} reading={rec.get('reading')} "
          f"controls_failed={len(rec['controls_failed'])} stops={len(rec['stop'])}")
    return 0 if rec["verdict"] == "PASS" else 3


if __name__ == "__main__":
    sys.exit(main())
