"""Reduce the final-bank GBDT fill-in and the committed PET look-1 scores to the frozen comparison.

    pgc_compare.py compact --gbdt-dir OUT --out results/gbdt_fb_compact.jsonl.gz
    pgc_compare.py compare --pet-source SRC --gbdt results/gbdt_fb_compact.jsonl.gz \
        --tasks tasks-20261005.json --out results/comparison.json

`compact` keeps, per task and k, every histogram's recovery, residual and injected L1, and the
unfolded spectra of the endpoint histograms. The prior and target spectra are byte-identical to the
committed PET score of the same run, and `compare` checks that the injected per-bin vectors agree.

`compare` implements `PLAN-20261005.md` section 5:
- endpoint summaries per method;
- per-draw paired differences, with t intervals and the bank-effect bound;
- per-bin bias, RMS and MSE of (unfolded - own target);
- B1-B4 analogues and N1 analogues.

A case enters only when every one of its declared draws completed for the GBDT.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import pgc_run_fb  # noqa: E402

SCORED_FB = "nd-unfolding/pet/final_design/results/final/scored_fb"
PET = {"H2S1T24K5": 5, "L128S1T24K4": 4}
ANCHORS = {"CTLrefK3": 3, "CrefK3": 3}            # old PET (historical CTL and C), not GBDT
GBDT_K = {"primary": 7, "secondary": (3, 10)}
SPECTRA = ("eavail", "eavail@low_acceptance", "eavail@moderate", "eavail@good",
           "eavail_x_proton", "eavail_x_neutron", "eavail_x_q3")
SPECTRA_K = (3, 7, 10)
BANK_FRACTION = 0.227
REGIONS = ("low_acceptance", "moderate", "good")
ENDPOINTS = {  # name: (stage, case as named in runs, histogram)
    "E0": ("S4F", "dev", "eavail"),
    "E1_low_acceptance": ("S4F", "dev", "eavail@low_acceptance"),
    "E1_moderate": ("S4F", "dev", "eavail@moderate"),
    "E1_good": ("S4F", "dev", "eavail@good"),
    "E3": ("S4F", "D1_m0.350", "eavail"),
    "E4": ("S4S", "D4c_p_up", "eavail_x_proton"),
    "E5": ("S4S", "D3_p0.35", "eavail_x_q3"),
}


# --------------------------------------------------------------------------------------------- #
def compact(a: argparse.Namespace) -> int:
    files = sorted(glob.glob(str(a.gbdt_dir / "GBDT-*.json")))
    n = 0
    with gzip.open(a.out, "wt") as out:
        for f in files:
            d = json.loads(Path(f).read_text())
            its = []
            for it in d["iterations"]:
                h = it["histograms"]
                rec = {"k": it["k"], "stability": it["stability"],
                       "fit": {s: {x: it["fit"][s].get(x) for x in ("n_iter", "val_logloss",
                                                                    "saturated")}
                               for s in ("step1", "step2")},
                       "hist": {name: {x: v.get(x) for x in ("recovery", "recovery_raw",
                                                             "defined", "injected_l1",
                                                             "residual_l1")}
                                for name, v in h.items()}}
                if it["k"] in SPECTRA_K:
                    for name in SPECTRA:
                        rec["hist"][name]["unfolded_norm"] = h[name]["unfolded_norm"]
                        rec["hist"][name]["injected_per_bin"] = h[name]["injected_per_bin"]
                its.append(rec)
            row = {"name": d["name"], "run": d["task"]["run"], "seed": d["task"]["seed"],
                   "case": d["case"], "recipe": d["recipe"],
                   "replicate_arrays_sha256": d["provenance"]["replicate_arrays_sha256"],
                   "pet_source": d["provenance"]["pet_source"], "versions": d["versions"],
                   "wall_seconds": d["wall_seconds"], "cpu_seconds": d["cpu_seconds"],
                   "threads": d["threads"], "charge_core_hours": d["charge_core_hours"],
                   "n": d["n"], "iterations": its}
            out.write(json.dumps(row, allow_nan=False) + "\n")
            n += 1
    print(f"{n} tasks -> {a.out}")
    return 0


# --------------------------------------------------------------------------------------------- #
def t_summary(x: np.ndarray) -> dict[str, Any]:
    x = np.asarray([v for v in x if v is not None and np.isfinite(v)], float)
    n = x.size
    if n == 0:
        return {"n": 0}
    m = float(x.mean())
    sd = float(x.std(ddof=1)) if n > 1 else None
    out = {"n": n, "mean": m, "sd": sd}
    if n > 1:
        se = sd / math.sqrt(n)
        q = float(stats.t.ppf(0.975, n - 1))
        out.update({"se": se, "ci95": [m - q * se, m + q * se]})
    return out


def paired(pet: dict[int, float], gb: dict[int, float]) -> dict[str, Any]:
    draws = sorted(set(pet) & set(gb))
    d = np.array([pet[r] - gb[r] for r in draws], float)
    s = t_summary(d)
    s["draws"] = draws
    s["n_pet_higher"] = int((d > 0).sum())
    if s.get("sd") is not None:
        s["bank_effect_bound"] = math.sqrt(BANK_FRACTION) * s["sd"]
    return s


def load_pet(src: Path, design: str, run_suffix: str) -> dict[str, Any] | None:
    f = src / SCORED_FB / f"{design_run(design, run_suffix)}.design_scores.json"
    if not f.exists():
        return None
    return json.loads(f.read_text())


def design_run(design: str, run_suffix: str) -> str:
    stage, rest = run_suffix.split("-", 1)
    return f"{stage}-{design}-{rest}"


def compare(a: argparse.Namespace) -> int:
    gb_rows = [json.loads(line) for line in gzip.open(a.gbdt, "rt")]
    gb = {r["run"]: r for r in gb_rows}
    tasks = json.loads(a.tasks.read_text())["tasks"]
    # completeness per (stage, case): every declared draw present
    declared: dict[tuple[str, str], list[int]] = defaultdict(list)
    for t in tasks:
        p = pgc_run_fb.parse_run(t["run"])
        declared[(p["stage"], p["case"])].append(p["fb"])
    complete = {key for key, draws in declared.items()
                if all(f"{key[0]}-H2S1T24K5-FB{r}" + ("" if key[1] == "dev" else f"-{key[1]}")
                       in gb for r in draws)}
    problems: list[str] = []

    def runs_of(stage: str, case: str) -> list[tuple[int, str]]:
        return [(r, f"{stage}-H2S1T24K5-FB{r}" + ("" if case == "dev" else f"-{case}"))
                for r in sorted(declared[(stage, case)])]

    def pet_hist(design: str, run: str) -> dict[str, Any]:
        doc = json.loads((a.pet_source / SCORED_FB /
                          f"{run.replace('H2S1T24K5', design)}.design_scores.json").read_text())
        k = {**PET, **ANCHORS}[design]
        it = [x for x in doc["iterations"] if x["k"] == k][0]
        if doc["provenance"]["replicate_arrays_sha256"] != gb[run]["replicate_arrays_sha256"]:
            problems.append(f"{run}/{design}: replicate arrays differ")
        return {"hist": it["histograms"], "stability": it["stability"]}

    def gb_hist(run: str, k: int) -> dict[str, Any]:
        return [x for x in gb[run]["iterations"] if x["k"] == k][0]

    out: dict[str, Any] = {"schema": "pet-gbdt-comparison/comparison/1",
                           "plan": "PLAN-20261005.md", "gbdt_recipe": gb_rows[0]["recipe"],
                           "pet_k": PET, "anchors_k": ANCHORS,
                           "complete_cases": sorted(f"{s}:{c}" for s, c in complete),
                           "incomplete_cases": sorted(f"{s}:{c}" for s, c in declared
                                                      if (s, c) not in complete),
                           "endpoints": {}, "per_bin": {}, "rules": {}, "weights": {},
                           "k_trajectory": {}, "library": {}}
    ks = (GBDT_K["primary"],) + GBDT_K["secondary"]

    # ---- designated endpoints: summaries and paired differences ------------------------- #
    for ep, (stage, case, hname) in ENDPOINTS.items():
        if (stage, case) not in complete:
            out["endpoints"][ep] = {"status": "INCOMPLETE"}
            continue
        vals: dict[str, dict[int, float]] = defaultdict(dict)
        for r, run in runs_of(stage, case):
            for d in (*PET, *ANCHORS):
                if stage == "S4S" and d in ANCHORS:
                    continue
                vals[d][r] = pet_hist(d, run)["hist"][hname]["recovery"]
            for k in range(1, 11):
                vals[f"GBDT@k{k}"][r] = gb_hist(run, k)["hist"][hname]["recovery"]
        rec = {"stage": stage, "case": case, "histogram": hname,
               "summary": {m: t_summary(np.array(list(v.values()), dtype=float))
                           for m, v in vals.items()},
               "paired": {}}
        for d in PET:
            for k in ks:
                rec["paired"][f"{d} - GBDT@k{k}"] = paired(vals[d], vals[f"GBDT@k{k}"])
        rec["paired"]["H2S1T24K5 - L128S1T24K4 (context only)"] = paired(vals["H2S1T24K5"],
                                                                          vals["L128S1T24K4"])
        out["endpoints"][ep] = rec
        out["k_trajectory"][ep] = {k: rec["summary"][f"GBDT@k{k}"] for k in range(1, 11)}
        out["k_trajectory"][ep]["pet"] = {d: rec["summary"][d] for d in PET}
        out["k_trajectory"][ep]["per_draw"] = {m: {str(r): x for r, x in v.items()}
                                               for m, v in vals.items()}

    # ---- per-bin bias / RMS / MSE of (unfolded - own target) ---------------------------- #
    for ep in ("E0", "E4", "E5"):
        stage, case, hname = ENDPOINTS[ep]
        if (stage, case) not in complete:
            continue
        resid: dict[str, list[np.ndarray]] = defaultdict(list)
        for r, run in runs_of(stage, case):
            ref = pet_hist("H2S1T24K5", run)["hist"][hname]
            target = np.asarray(ref["target_norm"])
            for d in PET:
                h = pet_hist(d, run)["hist"][hname]
                if not np.allclose(h["target_norm"], target, rtol=0, atol=1e-15):
                    problems.append(f"{run}: {d} target differs")
                resid[d].append(np.asarray(h["unfolded_norm"]) - target)
            for k in SPECTRA_K:
                g = gb_hist(run, k)["hist"][hname]
                if not np.allclose(g["injected_per_bin"], ref["injected_per_bin"], rtol=0,
                                   atol=1e-12):
                    problems.append(f"{run}: GBDT k{k} injection differs from PET's")
                resid[f"GBDT@k{k}"].append(np.asarray(g["unfolded_norm"]) - target)
        pb = {}
        for m, rs in resid.items():
            R = np.vstack(rs)
            mean = R.mean(axis=0)
            var = R.var(axis=0, ddof=1)
            pb[m] = {"n": int(R.shape[0]), "mean_signed_residual": mean.tolist(),
                     "se_mean": (np.sqrt(var / R.shape[0])).tolist(),
                     "rms_residual": np.sqrt((R ** 2).mean(axis=0)).tolist(),
                     "mse": (mean ** 2 + var).tolist(),
                     "l1_of_mean_residual": float(np.abs(mean).sum()),
                     "mean_per_draw_l1": float(np.abs(R).sum(axis=1).mean()),
                     "sum_mse": float((mean ** 2 + var).sum())}
        out["per_bin"][ep] = {"histogram": hname, "note": "target = each draw's own pseudodata "
                              "truth; spread is of (estimate - own target), not the "
                              "unconditional estimator variance", "methods": pb}

    # ---- B2 / B3 / B4 analogues (report only; frozen rules do not apply to the GBDT) ------ #
    def resid_minus_inj(method: str, case: str) -> dict[int, float]:
        o = {}
        for r, run in runs_of("S4S", case):
            h = (pet_hist(method, run)["hist"]["eavail"] if method in PET
                 else gb_hist(run, int(method.split("k")[1]))["hist"]["eavail"])
            o[r] = h["residual_l1"] - h["injected_l1"]
        return o

    methods = list(PET) + [f"GBDT@k{k}" for k in ks]
    for case in ("D4d_n_down", "null"):
        if ("S4S", case) in complete:
            v = {m: resid_minus_inj(m, case) for m in methods}
            out["rules"][f"B2:{case}"] = {
                "quantity": "mean(E_avail residual L1 - injected L1); frozen PET threshold 0.010",
                "summary": {m: t_summary(np.array(list(x.values()))) for m, x in v.items()},
                "paired": {f"{d} - GBDT@k{k}": paired(v[d], v[f"GBDT@k{k}"])
                           for d in PET for k in ks}}
    if ("S4S", "null") in complete:
        b3 = {}
        for m in methods:
            e, j, fl = [], [], []
            for r, run in runs_of("S4S", "null"):
                h = (pet_hist(m, run)["hist"] if m in PET
                     else gb_hist(run, int(m.split("k")[1]))["hist"])
                e.append(h["eavail"]["residual_l1"])
                j.append(h["eavail_x_proton"]["residual_l1"])
                fl.append(h["eavail_x_proton"]["injected_l1"])
            b3[m] = {"mean_eavail_spurious_l1": float(np.mean(e)),
                     "mean_eavail_x_proton_spurious_l1": float(np.mean(j)),
                     "eavail_x_proton_null_floor": float(np.mean(fl))}
        out["rules"]["B3"] = {"quantity": "null spurious L1; frozen PET thresholds 0.012 and "
                              "3 x floor", "methods": b3}
    resp = [c for c in ("R1_x1.05_D1_p0.350", "R1_x0.95_D1_p0.350", "R2_x1.01_D1_p0.350")
            if ("S4S", c) in complete]
    if ("S4S", "D1_p0.350") in complete and resp:
        b4, b4p = {}, {}
        for c in resp:
            b4[c], per = {}, {}
            for m in methods:
                e8 = {}
                for (r, run), (_r2, base) in zip(runs_of("S4S", c), runs_of("S4S", "D1_p0.350")):
                    get = ((lambda x: pet_hist(m, x)["hist"]["eavail"]["recovery"]) if m in PET
                           else (lambda x: gb_hist(x, int(m.split("k")[1]))["hist"]["eavail"]
                                 ["recovery"]))
                    e8[r] = get(run) - get(base)
                per[m] = e8
                b4[c][m] = t_summary(np.array(list(e8.values())))
            b4p[c] = {f"{d} - GBDT@k7": paired(per[d], per["GBDT@k7"]) for d in PET}
        out["rules"]["B4"] = {"quantity": "E8 = R_E0(R + D1) - R_E0(D1) by draw (the response-"
                              "specific change); frozen PET threshold |mean| <= 0.15 applies to "
                              "R1 only", "cases": b4, "paired": b4p}

    # ---- library: natural-histogram R per case and moves-away units (B1 analogue) -------- #
    lib_cases = sorted({c for (s, c) in declared if s == "S4S"})
    for case in lib_cases:
        if ("S4S", case) not in complete:
            out["library"][case] = {"status": "INCOMPLETE"}
            continue
        nat = gb[runs_of("S4S", case)[0][1]]["case"]["natural"]
        per, by_draw = {}, {}
        for m in methods:
            xs = {}
            for r, run in runs_of("S4S", case):
                h = (pet_hist(m, run)["hist"][nat] if m in PET
                     else gb_hist(run, int(m.split("k")[1]))["hist"][nat])
                xs[r] = h["recovery"]
            defined = [x for x in xs.values() if x is not None]
            by_draw[m] = {r: x for r, x in xs.items() if x is not None}
            per[m] = {**t_summary(np.array(defined, float)), "n_defined": len(defined),
                      "n_moves_away": int(sum(x < 0 for x in defined))}
        pairs = {f"{d} - GBDT@k7": paired(by_draw[d], by_draw["GBDT@k7"]) for d in PET
                 if by_draw[d] and by_draw["GBDT@k7"]}
        out["library"][case] = {"natural_histogram": nat, "draws": len(runs_of("S4S", case)),
                                "methods": per, "paired": pairs}

    # ---- weights (N1 analogue) ---------------------------------------------------------- #
    if ("S4F", "dev") in complete:
        for m in methods:
            ess, p999 = [], []
            for r, run in runs_of("S4F", "dev"):
                st = (pet_hist(m, run)["stability"] if m in PET
                      else gb_hist(run, int(m.split("k")[1]))["stability"])
                ess.append(st["final_truth_weight_ess_over_n"])
                p999.append(st["push_p999"])
            wmax = []
            for run in gb:
                st = (pet_hist(m, run)["stability"] if m in PET
                      else gb_hist(run, int(m.split("k")[1]))["stability"])
                wmax.append(st["push_max"])
            out["weights"][m] = {"median_ess_over_n_E0": float(np.median(ess)),
                                 "median_push_p999_E0": float(np.median(p999)),
                                 "max_push_over_completed_runs": float(np.max(wmax)),
                                 "runs": len(wmax)}

    # ---- cost of the fill-in --------------------------------------------------------------- #
    out["gbdt_cost"] = {"tasks": len(gb_rows),
                        "charged_core_hours": float(sum(r["charge_core_hours"] for r in gb_rows)),
                        "cpu_core_hours": float(sum(r["cpu_seconds"] for r in gb_rows) / 3600),
                        "median_wall_seconds": float(np.median([r["wall_seconds"]
                                                                for r in gb_rows])),
                        "threads_per_task": sorted({r["threads"] for r in gb_rows})}
    out["integrity_problems"] = problems
    a.out.write_text(json.dumps(out, indent=1, allow_nan=False) + "\n")
    print(f"complete cases {len(complete)}/{len(declared)}; problems {len(problems)}")
    for ep, rec in out["endpoints"].items():
        if "summary" not in rec:
            print(ep, rec)
            continue
        s = rec["summary"]
        pd = rec["paired"]
        print(f"{ep}: H2 {s['H2S1T24K5']['mean']:.3f} L128 {s['L128S1T24K4']['mean']:.3f} "
              f"GBDT k3/k7/k10 {s['GBDT@k3']['mean']:.3f}/{s['GBDT@k7']['mean']:.3f}/"
              f"{s['GBDT@k10']['mean']:.3f} | H2-G7 {pd['H2S1T24K5 - GBDT@k7']['mean']:+.3f} "
              f"{[round(x, 3) for x in pd['H2S1T24K5 - GBDT@k7']['ci95']]} "
              f"L128-G7 {pd['L128S1T24K4 - GBDT@k7']['mean']:+.3f} "
              f"{[round(x, 3) for x in pd['L128S1T24K4 - GBDT@k7']['ci95']]} n={s['GBDT@k7']['n']}")
    return 1 if problems else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compact")
    c.add_argument("--gbdt-dir", type=Path, required=True)
    c.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("compare")
    p.add_argument("--pet-source", type=Path, required=True)
    p.add_argument("--gbdt", type=Path, required=True)
    p.add_argument("--tasks", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    return compact(a) if a.cmd == "compact" else compare(a)


if __name__ == "__main__":
    sys.exit(main())
