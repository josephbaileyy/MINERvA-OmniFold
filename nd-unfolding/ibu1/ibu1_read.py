#!/usr/bin/env python3
"""IBU-1 readout and reading rule (frozen with the declaration; run once every unit is terminal).

Reads the ``ibu1.py`` products, the committed OmniFold receipts and the two OmniFold data products, and
applies the rule of ``.../methods/ibu1/DECLARATION.md`` section "Reading rule" (tags ``IA-n``).

MEASURES: per truth, the IBU and OmniFold residuals and below-gate counts on the J functionals, and the
reading the declared rule assigns. CANNOT AUTHORIZE: a coverage claim for OmniFold beyond its receipts, a
measured cross section, or any change to a claim.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "nd-unfolding"))
import s5c_samplesize as ss  # noqa: E402

GATES = (0.66, 0.94)
Z = (1.0, 1.96)
FAMILY_ALPHA = 0.05 / 459  # IA-10: the OmniFold Tier-S per-comparison level, so the counts are comparable
FACTOR = 2.0
SMALL = 2  # IA-10: counts both <= SMALL are "within a factor 2"
COUNT_DECISIVE_N = 400  # IA-10 (admission repair): below this n the count is descriptive (see count_interval)
BOOT = 2000
BOOT_SEED = 20261022

# The paired comparisons that carry the rule (IA-1, IA-2). "corrected" = the amendment-4 construction.
DEFORMED = {
    "tilt": {"unit": "P_tilt", "sigma": "P_sigma", "beta": "P_d1", "mode": "corrected",
             "of": ("interim", "eavail_tilt")},
    "gibuu": {"unit": "N_gibuu", "sigma": "N_sigma_s5n", "beta": None, "mode": "uncorrected",
              "of": ("s5n", "C4_eavail_shape"), "paired": [301000, 301059]},
    "w1": {"unit": "N_w1", "sigma": "N_sigma_R", "beta": None, "mode": "uncorrected", "of": ("R", "W1"),
           "paired": [803000, 803019]},
    "w2": {"unit": "N_w2", "sigma": "N_sigma_R", "beta": None, "mode": "uncorrected", "of": ("R", "W2"),
           "paired": [804000, 804019]},
    "w3": {"unit": "N_w3", "sigma": "N_sigma_R", "beta": None, "mode": "uncorrected", "of": ("R", "W3"),
           "paired": [805000, 805019]},
}
REFERENCE = {
    "nominal": {"unit": "P_nominal", "sigma": "P_sigma", "beta": "P_d1", "mode": "corrected",
                "of": ("interim", "nominal")},
    "nominal_N": {"unit": "N_nominal_dev", "sigma": "N_sigma_s5n", "beta": None, "mode": "uncorrected",
                  "of": ("s5n", "C3_nominal"), "paired": [300000, 300059]},
    "nominal_R": {"unit": "N_nominal_R", "sigma": "N_sigma_R", "beta": None, "mode": "uncorrected",
                  "of": ("R", "nominal"), "paired": [800000, 800039]},
    "gibuu_R": {"unit": "N_gibuu_R", "sigma": "N_sigma_R", "beta": None, "mode": "uncorrected",
                "of": ("R", "eavail_gibuu"), "paired": [801000, 801019]},
}
IBU_OWN = {  # IA-12: IBU's own corrected coverage at 400 seeds, no OmniFold comparator, no rule
    "nominal_N": "N_nominal_val", "gibuu": "N_gibuu", "w1": "N_w1", "w2": "N_w2", "w3": "N_w3"}


def load_unit(outdir: Path, name: str, variant: str, seeds: list[int] | None = None) -> dict:
    files = sorted(outdir.glob(f"{name}_s[0-9]*.npz"), key=lambda p: int(p.stem.rsplit("_s", 1)[1]))
    rows = []
    for f in files:
        z = np.load(f, allow_pickle=True)
        meta = json.loads(str(z["meta"]))
        if seeds is not None and not (seeds[0] <= meta["pseudo_seed"] <= seeds[1]):
            continue
        rows.append((meta, z[f"F_{variant}"], z["f_true"], z["f_of"] if "f_of" in z.files else None, z["ks"],
                     z["f_oracle"], z["f_true_A"]))
    if not rows:
        raise SystemExit(f"no products for unit {name}")
    ks = rows[0][4]
    return {"unit": name, "seeds": [r[0]["pseudo_seed"] for r in rows], "F": np.array([r[1] for r in rows]),
            "t": np.array([r[2] for r in rows]),
            "of": None if any(r[3] is None for r in rows) else np.array([r[3] for r in rows]),
            "gates": [r[0]["comparator"] for r in rows], "ks": [int(k) for k in ks],
            "oracle": np.array([r[5] for r in rows]), "t_A": np.array([r[6] for r in rows])}


def require_of(unit: dict) -> np.ndarray:
    """The paired OmniFold estimates; a paired comparison without them fails here, naming the unit (reader fix,
    BINDING-READER-FIX.md condition 2)."""
    if unit["of"] is None:
        raise AssertionError(f"unit {unit['unit']}: a paired product has no f_of (OmniFold comparator estimate)")
    return unit["of"]


def load_boot(outdir: Path, name: str, variant: str) -> dict:
    z = np.load(outdir / f"{name}.npz", allow_pickle=True)
    return {"F": z[f"F_{variant}"], "meta": json.loads(str(z["meta"])), "ks": [int(k) for k in z["ks"]]}


def sigma_of(boot: dict) -> np.ndarray:
    """(K, F): the ddof=1 SD over replicas, as ``s5c_coverage.stat_covariance`` takes it."""
    return boot["F"].std(axis=0, ddof=1)


def beta_of(unit: dict) -> tuple[np.ndarray, np.ndarray]:
    """(K, F) mean relative residual and its SE, as ``s5c_analyze_d1.group`` (amendment 4)."""
    rel = unit["F"] / unit["t"][:, None, :] - 1.0
    n = rel.shape[0]
    return rel.mean(0), rel.std(0, ddof=1) / np.sqrt(n)


def hits(est: np.ndarray, truth: np.ndarray, sigma: np.ndarray, corr=None) -> np.ndarray:
    """(2, F) experiments covered at 68% and 95%: ``s5c_coverage.evaluate`` with or without amendment 4."""
    out = np.zeros((2, est.shape[1]), int)
    for e, t in zip(est, truth):
        fh, sig = e, sigma
        if corr is not None:
            fh = e / (1.0 + corr[0])
            sig = np.sqrt(sigma ** 2 + (corr[1] * fh) ** 2)
        d = np.abs(fh - t)
        out[0] += d <= Z[0] * sig
        out[1] += d <= Z[1] * sig
    return out


def count_interval(h: np.ndarray, n: int, rows: np.ndarray) -> dict:
    """IA-10: on the J rows, ``definite`` = functionals whose one-sided CP UPPER bound at FAMILY_ALPHA is below
    a gate (the Tier-S futility count), ``possible`` = whose CP LOWER bound is below a gate, ``point`` = whose
    point coverage is below a gate. The count is ``definite``; its interval is [definite, possible]."""
    definite = possible = point = 0
    for f in rows:
        below_ucb = any(ss.cp_upper(int(h[i, f]), n, FAMILY_ALPHA) < g for i, g in enumerate(GATES))
        below_lcb = any(ss.cp_lower(int(h[i, f]), n, FAMILY_ALPHA) < g for i, g in enumerate(GATES))
        below_pt = any(h[i, f] / n < g for i, g in enumerate(GATES))
        definite += below_ucb
        possible += below_lcb
        point += below_pt
    return {"definite": int(definite), "possible": int(possible), "point": int(point), "n": int(n)}


def count_relation(ci: int, co: int) -> str:
    if max(ci, co) <= SMALL or max(ci, co) <= FACTOR * min(ci, co):
        return "within"
    return "better" if ci < co else "worse"


def count_reading(cI: dict, cO: dict) -> dict:
    """IA-10. At n < COUNT_DECISIVE_N the count is DESCRIPTIVE: at n = 20 and 60 the CP lower bound at
    FAMILY_ALPHA of a functional covered in every experiment (0.634, 0.859) is already below a gate (0.66,
    0.94), so ``possible`` is every J functional whatever the coverage and the count can never resolve
    (admission review, finding 2). It is reported with its interval and does not enter the reading."""
    corners = {count_relation(a, b) for a in (cI["definite"], cI["possible"]) for b in (cO["definite"], cO["possible"])}
    if {"better", "worse"} <= corners:  # the box interior then holds equal counts (re-review, NEW finding)
        corners.add("within")
    rel = count_relation(cI["definite"], cO["definite"])
    decisive = min(cI["n"], cO["n"]) >= COUNT_DECISIVE_N
    return {"relation": rel, "resolved": corners == {rel}, "corners": sorted(corners), "decisive": decisive}


def residual_relation(ratio: float) -> str:
    if ratio < 1 / FACTOR:
        return "better"
    if ratio > FACTOR:
        return "worse"
    return "within"


def residual_reading(relI: np.ndarray, relO: np.ndarray, rows: np.ndarray) -> dict:
    """IA-4: m = median over the J rows of |mean over experiments of f_hat/f_true - 1|; the ratio IBU/OmniFold
    with a paired seed-bootstrap 95% interval. Resolved if the interval lies inside one relation's region."""
    def med(a, idx):
        return float(np.median(np.abs(a[idx][:, rows].mean(0))))

    n = relI.shape[0]
    allidx = np.arange(n)
    mI, mO = med(relI, allidx), med(relO, allidx)
    ratio = mI / mO
    rng = np.random.default_rng(BOOT_SEED)
    r = []
    for _ in range(BOOT):
        idx = rng.integers(0, n, n)
        r.append(med(relI, idx) / med(relO, idx))
    lo, hi = (float(x) for x in np.percentile(r, [2.5, 97.5]))
    rel = residual_relation(ratio)
    spanned = {residual_relation(lo), residual_relation(hi), rel}
    if lo < 1 / FACTOR and hi > FACTOR:
        spanned.add("within")
    return {"median_abs_ibu": mI, "median_abs_of": mO, "max_abs_ibu": float(np.max(np.abs(relI[:, rows].mean(0)))),
            "max_abs_of": float(np.max(np.abs(relO[:, rows].mean(0)))), "ratio": ratio, "ratio_ci95": [lo, hi],
            "relation": rel, "possible": sorted(spanned), "resolved": spanned == {rel}}


WORD = {"within": "consistent", "better": "IBU better", "worse": "IBU worse"}


def word_of(res_rel: str, cnt_rel: str | None) -> str:
    if cnt_rel is None:  # the count is descriptive at this n: the residual decides
        return WORD[res_rel]
    return WORD[res_rel] if res_rel == cnt_rel else "mixed"


def truth_reading(res: dict, cnt: dict) -> dict:
    """IA-10: per truth. ``possible`` = every word the metrics' unresolved ranges allow; the reading is the
    point word when ``possible`` holds only it, else "unresolved (<point word> at the point values)"."""
    c_point = cnt["relation"] if cnt["decisive"] else None
    c_set = set(cnt["corners"]) if cnt["decisive"] else {None}
    point = word_of(res["relation"], c_point)
    possible = {word_of(r, c) for r in res["possible"] for c in c_set}
    reading = point if possible == {point} else f"unresolved ({point} at the point values)"
    return {"reading": reading, "point": point, "possible": sorted(possible)}


def overall(per_truth: dict) -> str:
    """The spec's rule on the per-truth ``possible`` sets: inverse-problem limited if every deformed truth can
    only be consistent; implementation specific if GiBUU and the rate change can only be "IBU better";
    unresolved if either is still possible; mixed otherwise (decided even when some truths are unresolved)."""
    sets = {k: set(v["possible"]) for k, v in per_truth.items()}
    if all(s == {"consistent"} for s in sets.values()):
        return "inverse-problem limited"
    if sets["gibuu"] == {"IBU better"} and sets["tilt"] == {"IBU better"}:
        return "implementation specific"
    if all("consistent" in s for s in sets.values()) or ("IBU better" in sets["gibuu"] and "IBU better" in sets["tilt"]):
        return "unresolved"
    return "mixed"


def of_hits(src: tuple, receipts: dict, names: list[str], n: int) -> np.ndarray:
    kind, key = src
    if kind == "interim":
        g = next(x for x in receipts["interim"]["grid"] if x["truth"] == key)
        if g["n_present"] != n:
            raise SystemExit(f"interim {key} n {g['n_present']} != {n}")
        return np.array([g["hits68"], g["hits95"]])
    if kind == "s5n":
        p = receipts["s5n"]["grid"][key]["per_functional"]
        nn = receipts["s5n"]["grid"][key]["n_experiments"]
    else:
        p = receipts["R"]["points"][key]["per_functional"]
        nn = receipts["R"]["points"][key]["n"]
    if nn != n:
        raise SystemExit(f"{kind} {key} n {nn} != {n}")
    return np.rint(np.array([p["cov68"], p["cov95"]]) * n).astype(int)


def of_receipt_controls(src: tuple, receipts: dict, unit: dict, k5: int, corr_of=None) -> dict:
    """The paired OmniFold estimates in our products reproduce the committed receipt (population check)."""
    kind, key = src
    relO = require_of(unit) / unit["t"] - 1.0
    if kind == "interim":
        sig = np.asarray(receipts["interim"]["sigma"], float)
        h = hits(require_of(unit), unit["t"], sig, corr_of)
        g = next(x for x in receipts["interim"]["grid"] if x["truth"] == key)
        return {"hits_equal_receipt": bool(np.array_equal(h, np.array([g["hits68"], g["hits95"]])))}
    p = (receipts["s5n"]["grid"][key] if kind == "s5n" else receipts["R"]["points"][key])["per_functional"]
    return {"mean_rel_max_abs_diff": float(np.max(np.abs(relO.mean(0) - np.asarray(p["mean_rel"], float))))}


def evaluate(outdir: Path, receipts: dict, names: list[str], variant: dict, k_list: list[int]) -> dict:
    J = np.array([i for i, n in enumerate(names) if n.startswith("J")])
    out = {"per_K": {}}
    boots = {u: load_boot(outdir, u, variant[u[0]]) for u in ("P_sigma", "N_sigma_s5n", "N_sigma_R")}
    d1 = load_unit(outdir, "P_d1", variant["P"])
    bc = receipts["bias_correction"]
    corr_of = (np.asarray(bc["beta"], float), np.asarray(bc["se"], float))
    cache = {}
    for K in k_list:
        res_K = {"deformed": {}, "reference": {}}
        for group, table in (("deformed", DEFORMED), ("reference", REFERENCE)):
            for truth, spec in table.items():
                arm = spec["unit"][0]
                key = (spec["unit"], tuple(spec.get("paired", [])) or None)
                if key not in cache:
                    cache[key] = load_unit(outdir, spec["unit"], variant[arm], spec.get("paired"))
                u = cache[key]
                iu = u["ks"].index(K)  # index the stored K axis by value (admission review, finding 1)
                est, t = u["F"][:, iu, :], u["t"]
                sig = sigma_of(boots[spec["sigma"]])[boots[spec["sigma"]]["ks"].index(K)]
                corr = None
                if spec["mode"] == "corrected":
                    b, se = beta_of(d1)
                    corr = (b[d1["ks"].index(K)], se[d1["ks"].index(K)])
                n = est.shape[0]
                hI = hits(est, t, sig, corr)
                hO = of_hits(spec["of"], receipts, names, n)
                rows = J[np.all(t[:, J] != 0, axis=0)]  # IA-4: the 109 supported cells all have truth (checked)
                cI, cO = count_interval(hI, n, rows), count_interval(hO, n, rows)
                relI, relO = est / t - 1.0, require_of(u) / t - 1.0
                res = residual_reading(relI, relO, rows)
                cnt = count_reading(cI, cO)
                floor = (u["oracle"] / u["t_A"] - 1.0)[:, rows].mean(0)
                entry = {"n": n, "J_rows_used": int(rows.size), "residual": res, "count_ibu": cI, "count_of": cO, "count": cnt,
                         **truth_reading(res, cnt),
                         "oracle_floor": {"median_abs": float(np.median(np.abs(floor))), "max_abs": float(np.max(np.abs(floor)))},
                         "gates_passed": int(sum(bool(g and g["pass"]) for g in u["gates"])),
                         "gates_total": len(u["gates"])}
                if K == 5:
                    entry["of_receipt_control"] = of_receipt_controls(spec["of"], receipts, u, iu,
                                                                      corr_of if spec["mode"] == "corrected" else None)
                res_K[group][truth] = entry
        res_K["verdict"] = overall(res_K["deformed"])
        own = {}
        sN = sigma_of(boots["N_sigma_s5n"])[boots["N_sigma_s5n"]["ks"].index(K)]
        nd = load_unit(outdir, "N_nominal_dev", variant["N"])
        bN, seN = beta_of(nd)
        ind = nd["ks"].index(K)
        for truth, unit_name in IBU_OWN.items():
            u = cache.setdefault((unit_name, None), load_unit(outdir, unit_name, variant["N"]))
            h = hits(u["F"][:, u["ks"].index(K), :], u["t"], sN, (bN[ind], seN[ind]))
            own[truth] = {"n": len(u["seeds"]), "count": count_interval(h, len(u["seeds"]), J),
                          "cov68_median_J": float(np.median(h[0, J] / len(u["seeds"]))),
                          "cov95_median_J": float(np.median(h[1, J] / len(u["seeds"])))}
        res_K["ibu_own_corrected_400"] = own
        out["per_K"][str(K)] = res_K
    return out


def data_comparison(outdir: Path, names: list[str], U: np.ndarray, a_root: Path, e_npz: Path, variant: dict) -> dict:
    """IA-11: per J cell, IBU at K = 5 over configurations (a) (purity, the central value) and (e)."""
    import uproot

    J = np.array([i for i, n in enumerate(names) if n.startswith("J")])
    fa = U @ np.asarray(uproot.open(a_root)["hXSecND_flat"].values(), float)
    fe = U @ np.asarray(np.load(e_npz, allow_pickle=True)["xsec_flat"], float)
    out = {}
    for unit, ref, label in (("D_P", fa, "(a)"), ("D_N", fe, "(e)")):
        z = np.load(outdir / f"{unit}.npz", allow_pickle=True)
        ks = [int(k) for k in z["ks"]]
        F = z[f"F_{variant[unit[2]]}"][ks.index(5)]
        r = F[J] / ref[J]
        out[unit] = {"against": label, "ratio_median": float(np.median(r)), "ratio_min": float(r.min()),
                     "ratio_max": float(r.max()), "abs_dev_median": float(np.median(np.abs(r - 1))),
                     "per_J": dict(zip([names[j] for j in J], r.tolist()))}
    return out


def preconditions(outdir: Path, result: dict, cfg: dict) -> dict:
    """IA-13: a result exists only if every paired experiment passed its gate, every bootstrap its base gate
    and controls, every truth used all 109 J cells, and the paired OmniFold estimates reproduce the
    committed receipts (hits exactly; mean residuals to 1e-12)."""
    k5 = result["primary"]["per_K"]["5"]
    entries = list(k5["deformed"].values()) + list(k5["reference"].values())
    boots = {}
    for u in ("P_sigma", "N_sigma_s5n", "N_sigma_R"):
        meta = json.loads(str(np.load(outdir / f"{u}.npz", allow_pickle=True)["meta"]))
        boots[u] = bool(meta["comparator"]["pass"]) and all(c["pass"] for c in meta["controls"].values())
    gates = all(e["gates_passed"] == e["gates_total"] for e in entries)
    rows = all(e["J_rows_used"] == cfg["functionals"]["J_count"] for e in entries)
    receipts = all(e["of_receipt_control"].get("hits_equal_receipt", True)
                   and e["of_receipt_control"].get("mean_rel_max_abs_diff", 0.0) <= 1e-12 for e in entries)
    return {"pairing_gates": gates, "bootstrap_gates": boots, "J_rows_109": rows, "omnifold_receipts_reproduced": receipts,
            "pass": bool(gates and rows and receipts and all(boots.values()))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--products", type=Path, required=True)
    ap.add_argument("--a-root", type=Path, required=True)
    ap.add_argument("--e-npz", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    import ibu1  # noqa: E402  (digest pins and the functional rows)

    cfg = json.loads(ibu1.CONFIG.read_text())
    rec_paths = cfg["receipts"]
    receipts = {}
    for key, r in rec_paths.items():
        p = REPO / r["path"]
        if ibu1.sha256(p) != r["expect_sha256"]:
            raise SystemExit(f"receipt {key} digest differs from config.json")
        receipts[key] = json.loads(p.read_text())
    for key, path in (("a_root", a.a_root), ("e_npz", a.e_npz)):
        if ibu1.sha256(path) != cfg["data_comparators"][key]["expect_sha256"]:
            raise SystemExit(f"{key} digest differs from config.json")
    prod = ibu1.Producers(cfg)
    contract = json.loads((REPO / cfg["contract"]["path"]).read_text())
    U, names = prod.s5c_coverage.reported_functionals(contract)
    if names != receipts["interim"]["functional_names"]:
        raise SystemExit("functional names differ from the Tier-S receipt")
    variant = {arm: v["primary"] for arm, v in cfg["variants"].items()}
    secondary = {arm: v["secondary"] for arm, v in cfg["variants"].items()}
    k_list = cfg["iterations"]["reported"]
    result = {"schema": "ibu1-read/1", "primary_K": cfg["iterations"]["primary"],
              "primary": evaluate(a.products, receipts, names, variant, k_list),
              "secondary_variants": evaluate(a.products, receipts, names, secondary, [5]),
              "data": data_comparison(a.products, names, U, a.a_root, a.e_npz, variant)}
    result["preconditions"] = preconditions(a.products, result, cfg)
    result["verdict"] = (result["primary"]["per_K"]["5"]["verdict"] if result["preconditions"]["pass"]
                         else "INCOMPLETE")
    a.out.write_text(json.dumps(result, indent=1, default=float) + "\n")
    k5 = result["primary"]["per_K"]["5"]
    print(json.dumps({"verdict": result["verdict"],
                      "per_truth": {t: v["reading"] for t, v in k5["deformed"].items()}}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
