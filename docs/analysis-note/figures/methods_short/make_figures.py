#!/usr/bin/env python3
"""Draw short-paper diagnostics from committed readouts; never run an unfold.

Run from any directory. Outputs and the exact input pins are beside this script.
The numerical producers are fd_f0_regrade.py and gbdt_model_dependence/analyze.py.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/"
GBDT = "nd-unfolding/gbdt_model_dependence/"
PINS = json.loads((OUT / "inputs.json").read_text())
TRUTHS = [
    ("nominal", "simulation prior*"),
    ("A7_mnvtune", "Tune v1, hybrid*"),
    ("A7_genie_cv", "GENIE CV, hybrid"),
    ("A7_genie_mec", "GENIE + MEC, hybrid"),
    ("W2", r"GENIE + MEC, $(E_{\rm avail},W)$ shape"),
    ("A7_nuwro", "NuWro, hybrid"),
    ("W1", r"NuWro, $E_{\rm avail}$ shape"),
    ("W3", r"NuWro, $(p_T,p_\parallel,E_{\rm avail})$ shape"),
    ("closure_nuwro", "NuWro shape, noise-free closure"),
    ("stage0c_gibuu", r"GiBUU, $E_{\rm avail}$ shape"),
    ("A7_gibuu", "GiBUU, hybrid"),
    ("q3", r"synthetic $q_3$ tilt"),
]


def checked(relative: str) -> Path:
    """Refuse any operand whose bytes differ from the committed pin."""
    path = ROOT / relative
    if hashlib.sha256(path.read_bytes()).hexdigest() != PINS[relative]:
        raise ValueError(f"Changed figure input: {relative}")
    return path


def read(relative: str) -> dict:
    return json.loads(checked(relative).read_text())


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(OUT / f"{name}.pdf", metadata={"CreationDate": None, "ModDate": None})
    fig.savefig(OUT / f"{name}.png", dpi=180)
    plt.close(fig)


def outline_threshold() -> float:
    """Read the threshold from the pinned numerical producer."""
    producer = checked("nd-unfolding/fd_f0_regrade.py").read_text()
    match = re.search(r"Z_TRIGGER, P_TRIGGER = ([0-9.]+)", producer)
    if not match:
        raise ValueError("Numerical producer no longer declares Z_TRIGGER")
    return float(match[1])


def check_against(paper_body: str, values_tex: str) -> list[str]:
    """Check current manuscript text against the frozen plotted data.

    Parameters
    ----------
    paper_body : str
        Contents of the current paper_body.tex, not a path.
    values_tex : str
        Contents of the current values_fived16.tex, not a path.

    Returns
    -------
    list[str]
        Failures for the integrator's check_round; an empty list means agreement.
        Input identity failures still raise ValueError.
    """
    failures = []
    label = r"\label{tab:fd16}"
    if label not in paper_body:
        failures.append("Table 2 label tab:fd16 missing")
    else:
        table = paper_body.split(label, 1)[1].split(r"\end{table*}", 1)[0]
        order = re.findall(r"\\fvval\{f0b-(\w+)-chi2int\}", table)
        if order != [k for k, _ in TRUTHS]:
            failures.append("Table 2 truth order differs from plotted order")
    match = re.search(r"\\@namedef\{fv@trig-z\}\{([^}]+)\}", values_tex)
    if not match or float(match[1]) != outline_threshold():
        failures.append("trig-z differs from plotted outline threshold")
    for index, path in enumerate(("with-cpl/readout/fd_f0b_readout.json",
                                  "readout/fd_f0b_readout.json")):
        truths = {t["name"]: t for t in read(FD + path)["truths"] if t["graded"]}
        suffix = "-nopl" if index else ""
        for key, _ in TRUTHS:
            maximum = max(abs(z) for z in truths[key]["grade"]["z"])
            pattern = (r"\\@namedef\{fv@f0b-" + key
                       + r"-zmax" + suffix + r"\}\{([^}]+)\}")
            printed = re.search(pattern, values_tex)
            if not printed or printed[1] != f"{maximum:.2f}":
                failures.append(f"Maximum z differs for {key}{suffix}")
    return failures


def bias_figure() -> dict:
    """Plot the mean fractional residual over its uncertainty; preserve the producer's leave-out grading."""
    arms = [read(FD + p) for p in (
        "with-cpl/readout/fd_f0b_readout.json", "readout/fd_f0b_readout.json")]
    threshold = outline_threshold()
    arrays, checks = [], []
    selected = []
    for index, arm in enumerate(arms):
        truths = {t["name"]: t for t in arm["truths"] if t["graded"]}
        assert set(truths) == {k for k, _ in TRUTHS}
        selected.append(truths)
        data = np.array([truths[k]["grade"]["z"] for k, _ in TRUTHS])
        assert data.shape == (12, 16)
        assert all(truths[k]["grade"]["cells"] == [f"R{i:02}" for i in range(16)] for k, _ in TRUTHS)
        for k, _ in TRUTHS:
            grade = truths[k]["grade"]
            flagged = [f"R{i:02}" for i, z in enumerate(grade["z"]) if abs(z) > threshold]
            assert flagged == grade["cells_abs_z_gt_2"]
            checks.append({"truth": k, "arm": index,
                           "max_abs_z": max(abs(z) for z in grade["z"])})
        arrays.append(data)
    for k, _ in TRUTHS:
        np.testing.assert_array_equal(selected[0][k]["bias"], selected[1][k]["bias"])
    fig, axes = plt.subplots(1, 2, figsize=(508 / 72, 5.8), sharey=True, layout="constrained")
    limit = max(float(np.abs(a).max()) for a in arrays)
    for ax, data, title in zip(axes, arrays, (
        "Reported covariance\n" + r"$C_{\rm total}+C_{\rm resp}+C_{\rm PL,5D}$",
        "Without run-period block\n" + r"$C_{\rm total}+C_{\rm resp}$"), strict=True):
        artist = ax.imshow(data, cmap="RdBu_r", vmin=-limit, vmax=limit, aspect="auto")
        for row, col in np.argwhere(np.abs(data) > threshold):
            ax.add_patch(Rectangle((col-.5, row-.5), 1, 1, fill=False, ec="black", lw=1.4))
        ax.set_title(title, fontsize=8.6)
        for row, col in enumerate(np.argmax(np.abs(data), axis=1)):
            if abs(data[row, col]) > threshold:
                ax.text(col, row, f"{data[row, col]:.2f}", ha="center", va="center",
                        fontsize=8.2, rotation=90, color="white" if abs(data[row, col]) > 3 else "black")
        ax.set_xticks(range(0, 16, 2), [f"R{i:02}" for i in range(0, 16, 2)])
        ax.set_xlabel("Reported cell")
    axes[0].set_yticks(range(12), [label.replace(", ", ",\n", 1) for _, label in TRUTHS])
    fig.colorbar(artist, ax=axes, label="z: signed mean fractional residual / uncertainty", shrink=.85)
    save(fig, "paper_bias_cells")
    return {"checks": checks, "z_reported": arrays[0].tolist(), "z_without_period": arrays[1].tolist()}


def prior_figure() -> dict:
    """Use the note producer's prior reduction, with journal-sized annotations."""
    spec = importlib.util.spec_from_file_location("prior_producer", checked(GBDT + "analyze.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    inventory = read(GBDT + "inputs/inventory.json")
    assert PINS[GBDT + "inputs/operands.npz"] == inventory["operands_sha256"]
    prior = next(r for r in inventory["selected"] if r["path"] == "s5p/prior/prior_R5fix_prior_d4.npz")
    meta = prior["metadata"]
    assert (meta["config"], meta["iters"], meta["estimator_seed"]) == ("R", 5, 42)
    assert meta["code_sha256"]["candidate_refine_override"] == {"n_estimators": 400, "num_leaves": 31}
    with np.load(checked(GBDT + "inputs/operands.npz"), allow_pickle=False) as operands:
        rows = module._prior_rows(operands)
    with checked(GBDT + "results/prior.csv").open() as stream:
        frozen_rows = list(csv.DictReader(stream))
    assert len(rows) == len(frozen_rows)
    for row, frozen in zip(rows, frozen_rows, strict=True):
        assert (row["map"], row["functional"]) == (frozen["map"], frozen["functional"])
        for key in ("W3_bias_pct", "d4_shift_pct"):
            np.testing.assert_equal(row[key], float(frozen[key]))
    fig, axes = plt.subplots(1, 3, figsize=(508 / 72, 3.1), layout="constrained")
    result = {}
    for ax, group, label in zip(axes, ("J", "H2", "EW"), ("(a) Joint cells", "(b) Coarser joint cells", r"(c) $(E_{\rm avail},W)$ cells"), strict=True):
        use = [r for r in rows if r["map"] == group]
        x = np.array([-r["W3_bias_pct"] for r in use])
        y = np.array([r["d4_shift_pct"] for r in use])
        ax.scatter(x, y, s=10, color="#2878a5", alpha=.7)
        lo, hi = min(x.min(), y.min()), max(x.max(), y.max())
        ax.plot([lo, hi], [lo, hi], color=".4", ls=":", lw=.8, label=r"$y=x$")
        ax.legend(fontsize=8.3, frameon=False, loc="lower right")
        ax.set_title(label, fontsize=8.6)
        ax.set_xlabel("Minus noise-free residual (%)")
        ax.grid(alpha=.15)
        result[group] = {"minus_residual_pct": x.tolist(), "prior_shift_pct": y.tolist(), "correlation": float(np.corrcoef(x,y)[0,1]), "fraction_shift_ge_residual": float(np.mean(abs(y) >= abs(x)))}
    axes[0].set_ylabel("Data shift under changed prior (%)")
    save(fig, "paper_prior_response")
    return result


def rounding_figure() -> dict:
    """Draw the A3 distribution solely from the committed per-quantity CSV."""
    base = "docs/orchestration/state/s5e/"
    csv_path = base + "cand/a3-rounding-shifts-20261109/cluster/a3_rounding_shifts.csv"
    record = read(base + "cand/a3-rounding-shifts-20261109/cluster/a3_rounding_shifts.json")
    assessment = read(base + "cand/assess_receipt.json")
    contract = read(base + "contract-amendment-3-candidate-R-and-assessment.json")
    assert contract["candidate"]["name"] == assessment["candidate"] == "R"
    assert "--refine-capacity 400,31" in contract["candidate"]["implementation"]
    assert record["csv"]["sha256"] == PINS[csv_path]
    assert record["gate"] and all(record["match"].values())
    integrity = read(base + "cand/review2/r2_integrity.json")
    used_keys = {"assess/data/data_R_upcast", "assess/data/data_R_jitteredge1",
                 "assess/data/data_R_jitteredge2"}
    used_keys.update(f"assess/data/boot/boot_b{i}" for i in range(1, 101))
    metadata = {row["key"]: row for row in integrity["rows"] if row["key"] in used_keys}
    assert set(metadata) == used_keys and len(record["inputs"]) == len(used_keys)
    for row in metadata.values():
        assert (row["iters"], row["est_seed"]) == (5, 42)
        assert row["est_nest"] == [100] and row["est_leaves"] == [8]
        assert (row["ref_n_est"], row["ref_leaves"], row["ref_rs"]) == (400, 31, 45)
    for seed in (1, 2):
        meta = metadata[f"assess/data/data_R_jitteredge{seed}"]["meta_excerpt"]
        assert (meta["jitter_f32"], meta["jitter_mode"], meta["coords"]) == (seed, "edge_safe", "float64")
    with checked(csv_path).open() as stream:
        rows = list(csv.DictReader(stream))
    names = [row["name"] for row in rows]
    assert [int(row["index"]) for row in rows] == list(range(153))
    assert names == assessment["functional_names"]
    assert names[:42] == [f"EW{i}" for i in range(42)]
    assert names[42] == "EW_all_ones" and names[-1] == "total_integrated"
    assert all(name.startswith("J") for name in names[43:-1])
    shifts = np.array([float(row["shift_over_data_sigma"]) for row in rows])
    assert np.isfinite(shifts).all() and (shifts >= 0).all()
    measured = {"median": float(np.median(shifts)), "max": float(shifts.max()),
                "argmax": names[int(shifts.argmax())]}
    expected = assessment["A3"]["data_rounding_probe_over_data_sigma"]
    assert measured == expected == record["computed"]
    study_replicas = assessment["data"]["data_boot_replicas"]
    reported_replicas = read(
        "docs/orchestration/state/measurement-paper/5d-community-20261024/s1/readout/s1_assembly.json"
    )["meta"]["stat_replicas"]
    assert study_replicas == 100 and reported_replicas == 50
    definition = read("nd-unfolding/gbdt_model_dependence/definition.json")
    assert len(definition["reported"]["EW"]) == 42
    assert sum(definition["reported"]["EW"]) == 39
    criteria = contract["criteria"]
    median_limit = criteria["rounding_median_max_sigma"]
    maximum_limit = criteria["rounding_max_sigma"]
    ordered = np.sort(shifts)
    fraction = np.arange(1, len(shifts) + 1) / len(shifts)
    fig, ax = plt.subplots(figsize=(245 / 72, 3.6), layout="constrained")
    ax.step(np.r_[0, ordered], np.r_[0, fraction], where="post", color="#2878a5", lw=1.3)
    ax.axvline(median_limit, color="#a85420", ls="--", lw=1,
               label=f"Median requirement: ≤ {median_limit:g}")
    ax.axvline(maximum_limit, color="#63529a", ls=":", lw=1.2,
               label=f"Maximum requirement: ≤ {maximum_limit:.1f}")
    middle = len(shifts) // 2
    ax.plot(ordered[middle], fraction[middle], "o", color="#2878a5", ms=4)
    ax.annotate(f"Median {measured['median']:.1f}",
                xy=(ordered[middle], fraction[middle]), xytext=(1.3, .36),
                textcoords="data", fontsize=8.5,
                arrowprops={"arrowstyle": "-", "color": "0.4", "lw": .6})
    ax.plot(measured["max"], 1, "o", color="#2878a5", ms=4)
    ax.annotate(f"Largest shift\n{measured['max']:.1f}",
                xy=(measured["max"], 1), xytext=(-8, -39),
                textcoords="offset points", ha="right", fontsize=8.5,
                arrowprops={"arrowstyle": "-", "color": "0.4", "lw": .6})
    ax.set(xlim=(0, measured["max"] * 1.15), ylim=(0, 1.055),
           xlabel="Larger absolute shift of two perturbations\n/ statistical σ",
           ylabel="Fraction of 153 quantities")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.01),
              borderaxespad=0, fontsize=8.3, frameon=True,
              facecolor="white", edgecolor="none", framealpha=.95)
    ax.grid(alpha=.15)
    save(fig, "paper_rounding_shifts")
    return {"summary": measured, "study_bootstrap_replicas": study_replicas,
            "reported_stat_replicas": reported_replicas, "median_limit": median_limit,
            "maximum_limit": maximum_limit, "names": names,
            "shift_over_data_sigma": shifts.tolist()}


def main() -> None:
    """Verify frozen inputs, then render figures and their numerical audit."""
    for relative in PINS:
        checked(relative)
    failures = check_against(
        (ROOT / "docs/analysis-note/paper_body.tex").read_text(),
        (ROOT / "docs/analysis-note/values_fived16.tex").read_text(),
    )
    if failures:
        raise ValueError("; ".join(failures))
    plt.rcParams.update({"font.family": "serif", "mathtext.fontset": "cm", "font.size": 8.5,
                         "axes.labelsize": 9.3, "xtick.labelsize": 8.3, "ytick.labelsize": 8.3,
                         "axes.linewidth": .6, "pdf.fonttype": 42})
    numbers = {"bias": bias_figure(), "prior": prior_figure(), "rounding": rounding_figure()}
    (OUT / "numbers.json").write_text(json.dumps(numbers, indent=2) + "\n")
    presentation = read("docs/analysis-note/figures/methods_short/presentation_original_arrays.json")
    assert hashlib.sha256((OUT / "numbers.json").read_bytes()).hexdigest() == presentation["methods_short_numbers_sha256"], "presentation changed numerical audit"



if __name__ == "__main__":
    main()
