"""Render the committed `results/*.json` as the markdown tables of `PHASE_E_SCALAR-20260922.md`.

    python make_tables.py [--results-dir results] [--which identifiability references ...]

The document's tables are generated from the result files rather than transcribed, so a number in
the prose and the number in the machine-readable record cannot drift apart.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent


def _f(x: Any, n: int = 3) -> str:
    return "--" if x is None else f"{float(x):.{n}f}"


def _ms(node: Any, n: int = 3) -> str:
    """mean +- sd over replicates."""
    if not node:
        return "--"
    sd = node.get("sd")
    return f"{node['mean']:.{n}f}" + (f" ± {sd:.{n}f}" if sd is not None else "")


def identifiability(path: Path) -> str:
    d = json.loads(path.read_text())
    null = d["null"]
    out = [f"Null (20 equal-model splits): mean {null['mean']:+.5f}, sd {null['sd']:.5f}, "
           f"95th-percentile band [{null['q2.5']:+.5f}, {null['q97.5']:+.5f}], "
           f"max {null['max']:+.5f}; reco E_avail L1 between two undistorted samples "
           f"{null['reco_eavail_l1_mean']:.4f} (max {null['reco_eavail_l1_max']:.4f}).", "",
           "| distortion | AUC − 0.5 | threshold (ESS-scaled) | distinguishable | reco E_avail L1 "
           "(pool T) | truth injected L1 (pool T) |", "|---|---:|---:|---|---:|---:|"]
    for name in sorted(d["distortions"]):
        r = d["distortions"][name]
        flag = ("yes" if r["distinguishable_vs_scaled_null"] else
                ("raw-only" if r["distinguishable_vs_raw_null"] else "**no**"))
        star = "" if r.get("predeclared", True) else " *(post-hoc)*"
        out.append(f"| `{name}`{star} | {r['auc_minus_half']:+.5f} | "
                   f"{r['threshold_ess_scaled']:.5f} | {flag} | "
                   f"{r['population_reco_eavail_l1']:.4f} | "
                   f"{r['population_truth_eavail_injected_l1']:.4f} |")
    for name, p in d.get("permutation_null", {}).items():
        out += ["", f"Permutation null for `{name}` ({p['splits']} splits): mean "
                    f"{p['mean']:+.5f}, max {p['max']:+.5f}, against the ESS-scaled threshold "
                    f"{p['predicted_scaled_threshold']:.5f} and the observed "
                    f"{p['observed']:+.5f}."]
    return "\n".join(out)


def references(path: Path) -> str:
    d = json.loads(path.read_text())
    across = d["across_replicates"]
    out = ["| case | IBU carry k=3 | k=10 | best | IBU eff.-corr. k=3 | k=10 | best | "
           "GBDT k=3 | k=10 |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name in sorted(across):
        a = across[name]
        c, e, g = a["ibu/carry_misses"], a["ibu/efficiency_corrected"], a["gbdt_omnifold"]
        star = "" if d["cases"][name].get("predeclared", True) else " *(post-hoc)*"
        out.append(f"| `{name}`{star} | {_ms(c['k3'])} | {_ms(c['k10'])} | "
                   f"{_ms(c['best'])} @{_f(c['best_k']['mean'], 0)} | {_ms(e['k3'])} | "
                   f"{_ms(e['k10'])} | {_ms(e['best'])} @{_f(e['best_k']['mean'], 0)} | "
                   f"{_ms(g['k3'])} | {_ms(g['k10'])} |")
    out += ["", "Per region at k = 3 (low / moderate / good), mean over replicates:", "",
            "| case | IBU carry | IBU eff.-corr. | GBDT |", "|---|---|---|---|"]
    for name in sorted(across):
        cells = []
        for est in ("ibu/carry_misses", "ibu/efficiency_corrected", "gbdt_omnifold"):
            reg = across[name][est]["regions"].get("k3", {})
            cells.append(" / ".join(_f(reg.get(r, {}).get("mean")) for r in
                                    ("low_acceptance", "moderate", "good")))
        out.append(f"| `{name}` | " + " | ".join(cells) + " |")
    return "\n".join(out)


def spurious(path: Path) -> str:
    """The response-only cases: displacement of the unfolded spectrum from the undistorted target."""
    d = json.loads(path.read_text())
    out = ["| response case | estimator | unfolded − target L1 | prior − target L1 | "
           "unfolded − prior L1 |", "|---|---|---:|---:|---:|"]
    for name in sorted(d["cases"]):
        if d["cases"][name]["case"]["truth"] is not None:
            continue
        for est, label in (("ibu", "IBU carry k=3"), ("gbdt_omnifold", "GBDT k=3")):
            vals = []
            for rep in d["cases"][name]["replicates"].values():
                node = (rep["ibu"]["carry_misses"] if est == "ibu" else rep[est])
                row = next((r for r in node["iterations"] if r["iteration"] == 3), None)
                if row and "spurious" in row:
                    vals.append(row["spurious"])
            if not vals:
                continue
            m = {k: sum(v[k] for v in vals) / len(vals) for k in
                 ("unfolded_minus_target_l1", "prior_minus_target_l1", "unfolded_minus_prior_l1")}
            out.append(f"| `{name}` | {label} | {m['unfolded_minus_target_l1']:.4f} | "
                       f"{m['prior_minus_target_l1']:.4f} | {m['unfolded_minus_prior_l1']:.4f} |")
    return "\n".join(out)


def assessment(path: Path) -> str:
    d = json.loads(path.read_text())
    ref = d["reference_model"]["curve"]
    out = ["| estimator | size | k=1 | k=3 | k=10 | k=20 | k=30 |", "|---|---|---:|---:|---:|---:|---:|"]
    for est, label in (("muon_eavail/carry_misses", "IBU reco E_avail, misses carried"),
                       ("muon_eavail/efficiency_corrected", "IBU reco E_avail, eff.-corrected"),
                       ("diag/carry_misses", "*reference model realized (`diag`)*")):
        for size in sorted(d["summary"].get(est, {})):
            row = d["summary"][est][size]
            out.append(f"| {label} | {size} | "
                       + " | ".join(_ms(row.get(f"k{k}")) for k in (1, 3, 10, 20, 30)) + " |")
    out.append("| *analytic reference model* `1-(1-a)^k` | population | "
               + " | ".join(_f(ref["aggregate"][k - 1]) for k in (1, 3, 10, 20, 30)) + " |")
    for size, rec in d["draws"].items():
        out += ["", f"{size} draws: {rec['design']['n_prior']} prior + {rec['design']['n_pseudo']} "
                    f"pseudodata events per replicate, disjoint={rec['design']['disjoint']}, "
                    f"max pairwise overlap {rec['overlap']['max_pairwise_fraction']:.3f}."]
    return "\n".join(out)


def toy(path: Path) -> str:
    d = json.loads(path.read_text())
    out = ["| smearing σ/(x+0.1) | estimator | k=1 | k=3 | k=10 | k=30 |",
           "|---|---|---:|---:|---:|---:|"]
    for f in d["smearing_fractions"]:
        for mode, label in (("carry_misses", "IBU, misses carried (engine norm.)"),
                            ("carry_misses/rate_matched", "IBU, misses carried (rate-matched)"),
                            ("efficiency_corrected", "IBU, efficiency-corrected (engine norm.)"),
                            ("reference_model", "*reference model* `1-(1-a)^k`")):
            key = f"sigma_frac={f:.2f}/{mode}"
            if key not in d["expected"]:
                continue
            rows = d["expected"][key]["iterations"]
            out.append(f"| {f:.2f} | {label} | "
                       + " | ".join(_f(rows[k - 1]["recovery"]) for k in (1, 3, 10, 30)) + " |")
    fin = d.get("finite_sample", {})
    if fin:
        import statistics
        out += ["", "Finite sample (the historical size, σ/(x+0.1) = 0.15, 3 draws):", "",
                "| estimator | k=3 | k=10 | k=30 |", "|---|---:|---:|---:|"]
        for mode, label in (("carry_misses", "misses carried"),
                            ("efficiency_corrected", "efficiency-corrected")):
            cells = []
            for k in (3, 10, 30):
                vals = [v["iterations"][k - 1]["recovery"] for key, v in fin.items()
                        if key.endswith(mode)]
                cells.append(f"{statistics.mean(vals):.3f} ± {statistics.stdev(vals):.3f}"
                             if len(vals) > 1 else _f(vals[0] if vals else None))
            out.append(f"| {label} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def absolute(path: Path, cases: tuple[str, ...] = (
        "D1_p0.350", "D1_p0.175", "D4d_n_up", "D4d_n_down", "D4c_p_up", "D4c_p_down",
        "R2_x0.99", "R3_s0.10", "R2_x1.01", "R1_x1.05")) -> str:
    """Absolute L1 distances on the normalized seven-bin spectra, mean over replicates:
    injected = |target - prior|, residual = |unfolded - target|. For a case whose injected L1 is
    at the sampling floor the RATIO (recovery) is noise; the absolute residual is not."""
    d = json.loads(path.read_text())
    out = ["| case | injected L1 | IBU carry residual k=3 / k=10 | IBU eff.-corr. residual k=3 / "
           "k=10 | GBDT residual k=3 / k=10 |", "|---|---:|---|---|---|"]
    for name in cases:
        if name not in d["cases"]:
            continue
        reps = d["cases"][name]["replicates"].values()

        def l1(node: dict, k: int, key: str) -> float | None:
            row = next((r for r in node["iterations"] if r["iteration"] == k), None)
            return None if row is None or key not in row else sum(abs(v) for v in row[key])

        def mean(vals: list) -> float | None:
            vals = [v for v in vals if v is not None]
            return sum(vals) / len(vals) if vals else None

        inj = mean([l1(r["ibu"]["carry_misses"], 3, "injected_per_bin") for r in reps])
        cells = []
        for pick in (lambda r: r["ibu"]["carry_misses"], lambda r: r["ibu"]["efficiency_corrected"],
                     lambda r: r["gbdt_omnifold"]):
            cells.append(" / ".join(_f(mean([l1(pick(r), k, "signed_residual_per_bin")
                                             for r in reps]), 4) for k in (3, 10)))
        out.append(f"| `{name}` | {_f(inj, 4)} | " + " | ".join(cells) + " |")
    return "\n".join(out)


RENDERERS = {"identifiability": ("identifiability.json", identifiability),
             "references": ("references.json", references),
             "spurious": ("references.json", spurious),
             "absolute": ("references.json", absolute),
             "assessment": ("reference_assessment.json", assessment),
             "toy": ("toy_reference.json", toy)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results-dir", type=Path, default=HERE / "results")
    ap.add_argument("--which", nargs="*", default=sorted(RENDERERS))
    args = ap.parse_args()
    for name in args.which:
        filename, fn = RENDERERS[name]
        path = args.results_dir / filename
        if not path.exists():
            print(f"### {name}: {path} not present yet\n")
            continue
        print(f"### {name}\n")
        print(fn(path))
        print()


if __name__ == "__main__":
    main()
