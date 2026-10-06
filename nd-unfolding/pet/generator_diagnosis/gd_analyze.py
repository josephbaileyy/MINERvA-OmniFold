"""Why do the PET finalists lose to GBDT on generator-model reweightings? (PLAN-20261006.md)

Report-only reductions of existing outputs: the preserved PET run arrays (copied read-only from CFS) and the
committed GBDT, DEV and scalar tables. Nothing is fitted or trained here.

    python gd_analyze.py --raw <dir holding s4f/ and s4s/ run copies> --out results/diagnosis.json

Controls (PLAN, "Controls"): C-b digests of every copied array against the committed score files, and C-a the
re-scored E_avail recovery at K (and the oracle anchor) against the committed values to <= 1e-9. A run that fails a
control is excluded from every question and listed.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import resource
import statistics as st
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PET = HERE.parent
sys.path.insert(0, str(PET / "final_design" / "analysis"))
import score_design as sd  # noqa: E402  (the study's own scorer: binning and the recovery statistic)

SCORES = PET / "final_design" / "results" / "final" / "scored_fb"
GBDT = PET / "gbdt_comparison" / "results" / "gbdt_fb_compact.jsonl.gz"
DEVT = PET / "final_design" / "dev" / "DEV_TABLES-20260927.json"
AUS = PET / "final_design" / "scalar" / "results" / "SCALAR_AUSSIE_MATCHED-20260925.json"
D5T = PET / "improvement_campaign" / "phase_e" / "calibration" / "d5_tables.json"

FINALISTS = {"H2S1T24K5": 5, "L128S1T24K4": 4}
CASES = ("D5_nuwro", "D5p_nuwro", "D5_gibuu")
DRAWS = range(8)
TOL = 1e-9
MIN_CELL_ROWS = 50                      # PLAN Q2: 3D cells with fewer prior truth-passing rows are pooled
REGIONS = ("low_acceptance", "moderate", "good")


def run_name(design: str, case: str | None, r: int) -> str:
    return f"S4F-{design}-FB{r}" if case is None else f"S4S-{design}-FB{r}-{case}"


def run_dir(raw: Path, name: str) -> Path:
    return raw / ("s4f" if name.startswith("S4F") else "s4s") / name


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ----------------------------------------------------------------------------------------- reductions
def movement(prior: np.ndarray, unfolded: np.ndarray, target: np.ndarray) -> dict:
    """On unit-normalized spectra: m = <moved, injected>/|injected|^2 (the scorer's `overshoot_projection`)
    and the orthogonal residual |moved - m injected| / |injected|."""
    p, u, t = (np.asarray(a, float) / np.sum(a) for a in (prior, unfolded, target))
    d, mv = t - p, u - p
    dd = float(d @ d)
    m = float(mv @ d) / dd
    return {"m": m, "orth": float(np.linalg.norm(mv - m * d) / math.sqrt(dd))}


def rec(prior, unfolded, target) -> float | None:
    return sd.recovery_stats(prior, unfolded, target, keep_spectra=False)["recovery_raw"]


def weight_agreement(w: np.ndarray, oracle: np.ndarray, mask: np.ndarray, base: np.ndarray) -> dict:
    """Weighted (by the base weight) Pearson r and least-squares slope of log w on log oracle."""
    m = mask & (w > 0) & (oracle > 0) & np.isfinite(w) & np.isfinite(oracle)
    x, y, b = np.log(oracle[m]), np.log(w[m]), base[m] / base[m].sum()
    mx, my = b @ x, b @ y
    cxx, cyy, cxy = b @ (x - mx) ** 2, b @ (y - my) ** 2, b @ ((x - mx) * (y - my))
    return {"r": float(cxy / math.sqrt(cxx * cyy)), "slope": float(cxy / cxx), "n": int(m.sum())}


class D5Bins:
    """The generator table's own (p_T, p_par, E_avail) edges (PLAN Q2); out-of-range rows -> one overflow cell."""

    def __init__(self, path: Path):
        e = json.loads(path.read_text())["tables"]["nuwro"]["edges"]
        self.pt, self.pp, self.ea = (np.asarray(e[k], float) for k in ("pt", "pparallel", "eavail"))
        self.n = (self.pt.size - 1) * (self.pp.size - 1) * (self.ea.size - 1)

    @staticmethod
    def _code(x, edges):
        i = np.searchsorted(edges, x, side="right") - 1
        i[x == edges[-1]] = edges.size - 2
        i[~np.isfinite(x) | (x < edges[0]) | (x > edges[-1])] = -1
        return i

    def codes(self, truth: np.ndarray) -> dict[str, np.ndarray]:
        ipt, ipp, iea = self._code(truth[:, 0], self.pt), self._code(truth[:, 1], self.pp), self._code(truth[:, 2], self.ea)
        cell = (ipt * (self.pp.size - 1) + ipp) * (self.ea.size - 1) + iea
        cell[(ipt < 0) | (ipp < 0) | (iea < 0)] = self.n            # overflow cell
        npt, npp = self.pt.size - 1, self.pp.size - 1
        return {"pt": np.where(ipt < 0, npt, ipt), "ppar": np.where(ipp < 0, npp, ipp), "d5_3d": cell,
                "_n": {"pt": npt + 1, "ppar": npp + 1, "d5_3d": self.n + 1}}


def hist(codes, w, mask, n):
    return np.bincount(codes[mask], weights=w[mask], minlength=n)[:n]


def reductions(A, pushes: dict, pulls: dict, bins: "D5Bins", K: int, k_op: int | None = None,
               reco_muon: dict | None = None) -> dict:
    """Q1-Q3 reductions of one run's arrays for any estimator's per-iteration (push, pull) over the prior rows.
    Q1 and Q2 are taken at the operating point `k_op` (default K); Q3 runs over k = 1..K."""
    k_op = K if k_op is None else k_op
    out: dict = {}
    pt_, ps_ = A["prior_truth"], A["pseudo_truth"]
    keep_p = A["prior_pass_truth"].astype(bool) & np.isfinite(pt_[:, 2])
    keep_s = A["pseudo_pass_truth"].astype(bool) & np.isfinite(ps_[:, 2])
    eb_p, eb_s = sd.eavail_codes(pt_[:, 2]), sd.eavail_codes(ps_[:, 2])
    eb_p[~keep_p], eb_s[~keep_s] = -1, -1
    wt_p, wt_s = A["prior_w_truth"].astype(float), A["pseudo_w_truth"].astype(float)
    dist, oracle = A["pseudo_distortion"].astype(float), A["prior_oracle"].astype(float)
    N = sd.N_EAV
    prior_e = sd.hist(eb_p, wt_p, N)
    target_e = sd.hist(eb_s, wt_s * dist, N)
    # Q1 (regions from the raw arrays too, for the movement fraction)
    reg_p, reg_s = np.asarray(A["prior_region"]), np.asarray(A["pseudo_region"])
    q1 = {"eavail": movement(prior_e, sd.hist(eb_p, wt_p * pushes[k_op], N), target_e)}
    for rg in REGIONS:
        c = sd.REGION_CODES[rg]
        pe = sd.hist(np.where(reg_p == c, eb_p, -1), wt_p, N)
        te = sd.hist(np.where(reg_s == c, eb_s, -1), wt_s * dist, N)
        ue = sd.hist(np.where(reg_p == c, eb_p, -1), wt_p * pushes[k_op], N)
        q1[rg] = {**movement(pe, ue, te), "R": rec(pe, ue, te)}
    q1["oracle_eavail"] = movement(prior_e, sd.hist(eb_p, wt_p * oracle, N), target_e)
    out["Q1"] = q1
    # Q2: other truth variables and the weight-level agreement
    cp, cs = bins.codes(pt_), bins.codes(ps_)
    q2 = {}
    for h in ("pt", "ppar", "d5_3d"):
        n = cp["_n"][h]
        pr, tg = hist(cp[h], wt_p, keep_p, n), hist(cs[h], wt_s * dist, keep_s, n)
        un, orc = hist(cp[h], wt_p * pushes[k_op], keep_p, n), hist(cp[h], wt_p * oracle, keep_p, n)
        if h == "d5_3d":                                   # pool sparse cells (PLAN Q2)
            cnt = np.bincount(cp[h][keep_p], minlength=n)[:n]
            dense = cnt >= MIN_CELL_ROWS
            pool = lambda a: np.append(a[dense], a[~dense].sum())
            pr, tg, un, orc = pool(pr), pool(tg), pool(un), pool(orc)
            q2["d5_3d_cells_used"] = int(dense.sum())
        q2[h] = {"R": rec(pr, un, tg), "R_oracle": rec(pr, orc, tg), **movement(pr, un, tg)}
    q2["weights"] = weight_agreement(pushes[k_op], oracle, keep_p, wt_p)
    out["Q2"] = q2
    # Q3 / Q4: per iteration
    rr_p = keep_p & A["prior_pass_reco"].astype(bool)
    rr_s = keep_s & A["pseudo_pass_reco"].astype(bool)
    pr1 = sd.hist(np.where(rr_p, eb_p, -1), wt_p, N)
    tg1 = sd.hist(np.where(rr_s, eb_s, -1), wt_s * dist, N)
    rp_p, rp_s = A["prior_pass_reco"].astype(bool), A["pseudo_pass_reco"].astype(bool)
    rb_p, rb_s = sd.eavail_codes(A["prior_reco_eavail"]), sd.eavail_codes(A["pseudo_reco_eavail"])
    rb_p[~rp_p], rb_s[~rp_s] = -1, -1
    wr_p, wr_s = A["prior_w_reco"].astype(float), A["pseudo_w_reco"].astype(float)
    prr, tgr = sd.hist(rb_p, wr_p, N), sd.hist(rb_s, wr_s * dist, N)
    # ADDITION after seeing T3 (not in the frozen plan; REPORT says so): detector-level closure in the reco muon
    # p_T and p_par marginals, on the table's p_T / p_par edges, same weights as the reco E_avail closure.
    mu = {}
    if reco_muon is not None:
        for v, edges in (("pt", bins.pt), ("ppar", bins.pp)):
            cpr = D5Bins._code(reco_muon[f"prior_{v}"], edges)
            cps = D5Bins._code(reco_muon[f"pseudo_{v}"], edges)
            nb = edges.size - 1
            cpr = np.where(cpr < 0, nb, cpr)
            cps = np.where(cps < 0, nb, cps)
            pr_, tg_ = hist(cpr, wr_p, rp_p, nb + 1), hist(cps, wr_s * dist, rp_s, nb + 1)
            mu[v] = (cpr, pr_, tg_, nb + 1)
    per_k = []
    for k in range(1, K + 1):
        per_k.append({
            "k": k,
            "step2_R": rec(prior_e, sd.hist(eb_p, wt_p * pushes[k], N), target_e),
            "step1_truth_R": rec(pr1, sd.hist(np.where(rr_p, eb_p, -1), wt_p * pulls[k], N), tg1),
            "step1_reco_R": rec(prr, sd.hist(rb_p, wr_p * pulls[k], N), tgr),
            **{f"step1_reco_{v}_R": rec(pr_, hist(cpr, wr_p * pulls[k], rp_p, nb), tg_)
               for v, (cpr, pr_, tg_, nb) in mu.items()},
            "step2_weights": weight_agreement(pushes[k], oracle, keep_p, wt_p),
        })
    out["Q3"] = {"per_k": per_k, "oracle_step1_truth_R": rec(pr1, sd.hist(np.where(rr_p, eb_p, -1), wt_p * oracle, N), tg1),
                 "reco_muon_injected_l1": {v: float(np.abs(tg_ / tg_.sum() - pr_ / pr_.sum()).sum())
                                           for v, (cpr, pr_, tg_, nb) in mu.items()}}
    return out


# ----------------------------------------------------------------------------------------- one PET run
def reco_muon_for(A, reco_scalars) -> dict | None:
    """Reco muon p_T, p_par (GeV) at the run's rows from the inventory's `reco_scalars`; its column 2 must equal
    the run's reco E_avail on every reco-passing row (the gather check `gbdt_comparison/pgc_fb.py` applies)."""
    if reco_scalars is None:
        return None
    out = {}
    for side in ("prior", "pseudo"):
        rs = np.asarray(reco_scalars[A[f"{side}_rows"]], dtype=np.float64)
        rp = A[f"{side}_pass_reco"].astype(bool)
        if not np.array_equal(rs[rp, 2].astype(np.float32), A[f"{side}_reco_eavail"][rp].astype(np.float32)):
            raise SystemExit(f"{side}: reco_scalars column 2 differs from the run's reco E_avail")
        out[f"{side}_pt"], out[f"{side}_ppar"] = rs[:, 0], rs[:, 1]
    return out


def analyze_run(raw: Path, name: str, K: int, bins: D5Bins, reco_scalars=None) -> dict:
    committed = json.loads((SCORES / f"{name}.design_scores.json").read_text())
    d = run_dir(raw, name)
    out: dict = {"run": name, "controls": {}}
    # C-b: digests
    ra = d / "replicate_arrays.npz"
    ok_digest = sha256(ra) == committed["provenance"]["replicate_arrays_sha256"]
    it_rec = committed["iterations"][-1]
    ok_iter = sha256(d / "iterations" / it_rec["iteration_file"]) == it_rec["iteration_file_sha256"]
    out["controls"]["digests"] = bool(ok_digest and ok_iter)
    A = np.load(ra)
    pt_, ps_ = A["prior_truth"], A["pseudo_truth"]
    keep_p = A["prior_pass_truth"].astype(bool) & np.isfinite(pt_[:, 2])
    keep_s = A["pseudo_pass_truth"].astype(bool) & np.isfinite(ps_[:, 2])
    eb_p, eb_s = sd.eavail_codes(pt_[:, 2]), sd.eavail_codes(ps_[:, 2])
    eb_p[~keep_p], eb_s[~keep_s] = -1, -1
    wt_p, wt_s = A["prior_w_truth"].astype(float), A["pseudo_w_truth"].astype(float)
    dist, oracle = A["pseudo_distortion"].astype(float), A["prior_oracle"].astype(float)
    N = sd.N_EAV
    prior_e = sd.hist(eb_p, wt_p, N)
    target_e = sd.hist(eb_s, wt_s * dist, N)
    pushes, pulls = {}, {}
    for k in range(1, K + 1):
        with np.load(d / "iterations" / f"iter{k - 1:02d}.npz") as z:
            pushes[k], pulls[k] = z["push"].astype(float), z["pull"].astype(float)
    # C-a: re-score E_avail R at K and the oracle anchor
    rK = rec(prior_e, sd.hist(eb_p, wt_p * pushes[K], N), target_e)
    rO = rec(prior_e, sd.hist(eb_p, wt_p * oracle, N), target_e)
    want_K = it_rec["histograms"]["eavail"]["recovery_raw"]
    want_O = committed["oracle_anchor"]["eavail"]["recovery_raw"]
    out["controls"]["rescore"] = {"R_K": rK, "committed": want_K, "oracle": rO, "committed_oracle": want_O,
                                  "pass": abs(rK - want_K) <= TOL and abs(rO - want_O) <= TOL}
    if not (out["controls"]["digests"] and out["controls"]["rescore"]["pass"]):
        out["excluded"] = True
        return out
    out.update(reductions(A, pushes, pulls, bins, K, reco_muon=reco_muon_for(A, reco_scalars)))
    out["spectra"] = {"prior": (prior_e / prior_e.sum()).tolist(), "target": (target_e / target_e.sum()).tolist()}
    return out


# ----------------------------------------------------------------------------------------- committed tables
def gbdt_records() -> dict[str, dict]:
    out = {}
    with gzip.open(GBDT, "rt") as f:
        for line in f:
            r = json.loads(line)
            out[r["name"]] = r
    return out


def gbdt_unit(g: dict, case: str | None, r: int, prior_norm: list, target_norm: list) -> dict:
    rec_ = g[f"GBDT-S4F-FB{r}-dev"] if case is None else g[f"GBDT-S4S-FB{r}-{case}"]
    its = {i["k"]: i for i in rec_["iterations"]}
    out = {"R_by_k": {k: its[k]["hist"]["eavail"]["recovery_raw"] for k in sorted(its)}}
    h7 = its[7]["hist"]["eavail"]
    inj = np.asarray(target_norm) - np.asarray(prior_norm)
    out["injected_matches_pet"] = bool(np.allclose(inj, h7["injected_per_bin"], atol=1e-12))
    out["Q1"] = {"eavail": movement(np.asarray(prior_norm), np.asarray(h7["unfolded_norm"]), np.asarray(target_norm))}
    for rg in REGIONS:
        hr = its[7]["hist"][f"eavail@{rg}"]
        out["Q1"][rg] = {"R": hr["recovery_raw"]}
    return out


def design_dependence() -> dict:
    t = json.loads(DEVT.read_text())["D5 NuWro R"]
    pet = {des: {k: v["mean"] for k, v in rows.items() if v["n"]} for des, rows in t.items()}
    a = json.loads(AUS.read_text())["per_case"]["D5_nuwro"]
    scalar = {k: v.get("mean_R") for k, v in a.items()}
    return {"pet_dev_D5_nuwro_R_by_k": pet, "scalar_matched_D5_nuwro_mean_R": scalar,
            "sources": [str(DEVT.relative_to(PET.parent.parent)), str(AUS.relative_to(PET.parent.parent))]}


# ----------------------------------------------------------------------------------------- summary
def summarize(vals):
    v = [x for x in vals if x is not None]
    return {"mean": st.fmean(v), "sd": st.stdev(v) if len(v) > 1 else None, "min": min(v), "max": max(v), "n": len(v)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--reco-scalars", type=Path, default=None, help="inventory reco_scalars.npy (reco muon closure)")
    a = ap.parse_args(argv)
    t0, bins, g = time.time(), D5Bins(D5T), gbdt_records()
    reco_scalars = np.load(a.reco_scalars, mmap_mode="r") if a.reco_scalars else None
    runs, excluded = {}, []
    for design, K in FINALISTS.items():
        for case in (None,) + CASES:
            for r in DRAWS:
                name = run_name(design, case, r)
                res = analyze_run(a.raw, name, K, bins, reco_scalars)
                if res.get("excluded"):
                    excluded.append(name)
                else:
                    res["gbdt"] = gbdt_unit(g, case, r, res["spectra"]["prior"], res["spectra"]["target"])
                runs[name] = res
                print(name, "R_K", round(res["controls"]["rescore"]["R_K"], 4),
                      "controls", res["controls"]["digests"], res["controls"]["rescore"]["pass"], flush=True)
    summary = {}
    for design in FINALISTS:
        for case in ("dev",) + CASES:
            rs = [runs[run_name(design, None if case == "dev" else case, r)] for r in DRAWS]
            rs = [x for x in rs if not x.get("excluded")]
            s = {"n": len(rs)}
            s["pet_R_K"] = summarize([x["controls"]["rescore"]["R_K"] for x in rs])
            s["oracle_R"] = summarize([x["controls"]["rescore"]["oracle"] for x in rs])
            s["gbdt_R_k7"] = summarize([x["gbdt"]["R_by_k"][7] for x in rs])
            s["Q1_m"] = {"pet": summarize([x["Q1"]["eavail"]["m"] for x in rs]),
                         "gbdt_k7": summarize([x["gbdt"]["Q1"]["eavail"]["m"] for x in rs]),
                         "oracle": summarize([x["Q1"]["oracle_eavail"]["m"] for x in rs])}
            s["Q1_orth"] = {"pet": summarize([x["Q1"]["eavail"]["orth"] for x in rs]),
                            "gbdt_k7": summarize([x["gbdt"]["Q1"]["eavail"]["orth"] for x in rs])}
            s["Q1_region_R"] = {rg: {"pet": summarize([x["Q1"][rg]["R"] for x in rs]),
                                     "gbdt_k7": summarize([x["gbdt"]["Q1"][rg]["R"] for x in rs])} for rg in REGIONS}
            s["Q2"] = {h: {"pet_R": summarize([x["Q2"][h]["R"] for x in rs]),
                           "oracle_R": summarize([x["Q2"][h]["R_oracle"] for x in rs]),
                           "pet_m": summarize([x["Q2"][h]["m"] for x in rs])} for h in ("pt", "ppar", "d5_3d")}
            s["Q2"]["weights_slope"] = summarize([x["Q2"]["weights"]["slope"] for x in rs])
            s["Q2"]["weights_r"] = summarize([x["Q2"]["weights"]["r"] for x in rs])
            K = FINALISTS[design]
            s["Q3"] = {k: {key: summarize([x["Q3"]["per_k"][k - 1][key] for x in rs])
                           for key in ("step2_R", "step1_truth_R", "step1_reco_R", "step1_reco_pt_R",
                                       "step1_reco_ppar_R") if key in rs[0]["Q3"]["per_k"][0]}
                       for k in range(1, K + 1)}
            for k in range(1, K + 1):
                s["Q3"][k]["step2_slope"] = summarize([x["Q3"]["per_k"][k - 1]["step2_weights"]["slope"] for x in rs])
            s["Q3_oracle_step1_truth_R"] = summarize([x["Q3"]["oracle_step1_truth_R"] for x in rs])
            s["Q4_gbdt_R_by_k"] = {k: summarize([x["gbdt"]["R_by_k"][k] for x in rs]) for k in range(1, 11)}
            s["injected_matches_pet"] = all(x["gbdt"]["injected_matches_pet"] for x in rs)
            summary[f"{design}|{case}"] = s
    ru = resource.getrusage(resource.RUSAGE_SELF)
    doc = {"schema": "pet-generator-diagnosis/1", "plan": "PLAN-20261006.md", "excluded": excluded,
           "summary": summary, "Q5": design_dependence(), "runs": runs,
           "cost": {"wall_seconds": time.time() - t0, "cpu_core_hours": (ru.ru_utime + ru.ru_stime) / 3600}}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(doc, indent=1, default=float) + "\n")
    print("excluded:", excluded, "| cpu core-h:", round(doc["cost"]["cpu_core_hours"], 4))
    return 0 if not excluded else 2


if __name__ == "__main__":
    raise SystemExit(main())
