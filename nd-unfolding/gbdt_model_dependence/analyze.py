#!/usr/bin/env python3
"""Reproduce scalar-5D diagnostic tables and figures from frozen cell integrals.

No production code is imported, no training is performed, and no covariance is adopted.
The uncertainty bars describe finite-ensemble estimation, conditional on the saved MC.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.stats import beta, chi2, t

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
POINTS = ("nominal", "eavail_gibuu", "q3", "W1", "W2", "W3")
LABELS = (
    "Nominal",
    "D1 historical",
    "q3 stress",
    "W1 historical",
    "W2 historical",
    "W3 historical",
)
FloatArray = NDArray[np.float64]


def _json(path: Path) -> Any:
    return json.loads(path.read_text())


def _csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _divide(numerator: FloatArray, denominator: FloatArray) -> FloatArray:
    return np.divide(
        numerator, denominator, out=np.zeros_like(numerator), where=denominator > 0
    )


def _binomial_interval(success: int, count: int) -> tuple[float, float]:
    return (
        float(beta.ppf(0.025, success, count - success + 1)) if success else 0.0,
        (
            float(beta.ppf(0.975, success + 1, count - success))
            if success < count
            else 1.0
        ),
    )


def _ensemble_rows(operands: Any) -> list[dict[str, Any]]:
    names, groups = operands["names"], operands["groups"]
    sigma = operands["sigma"].std(axis=0, ddof=1)
    rows = []
    receipt = _json(ROOT / "docs/orchestration/state/s5e/cand/assess_receipt.json")
    for point in POINTS:
        estimate, truth = (
            operands["assessment_" + point],
            operands["assessment_" + point + "_truth"],
        )
        residual = _divide(estimate - truth, truth)
        count = len(estimate)
        bias, spread = residual.mean(axis=0), residual.std(axis=0, ddof=1)
        se = spread / np.sqrt(count)
        pull = _divide(estimate - truth, sigma)
        coverage = np.abs(pull) <= 1
        for index, name in enumerate(names):
            if truth[:, index].min() <= 0:
                continue
            hits = int(coverage[:, index].sum())
            low, high = _binomial_interval(hits, count)
            hits95 = int((np.abs(pull[:, index]) <= 1.96).sum())
            low95, high95 = _binomial_interval(hits95, count)
            row = {
                "truth": point,
                "functional": str(name),
                "map": str(groups[index]),
                "supported": bool(operands["reported"][index]),
                "n": count,
                "bias_pct": bias[index] * 100,
                "bias_ci95_low_pct": (bias[index] - t.ppf(0.975, count - 1) * se[index])
                * 100,
                "bias_ci95_high_pct": (
                    bias[index] + t.ppf(0.975, count - 1) * se[index]
                )
                * 100,
                "residual_sd_pct": spread[index] * 100,
                "sd_ci95_low_pct": spread[index]
                * np.sqrt((count - 1) / chi2.ppf(0.975, count - 1))
                * 100,
                "sd_ci95_high_pct": spread[index]
                * np.sqrt((count - 1) / chi2.ppf(0.025, count - 1))
                * 100,
                "rmse_pct": np.sqrt(np.mean(residual[:, index] ** 2)) * 100,
                "fixed_sigma_pct_mean_truth": 100
                * sigma[index]
                / truth[:, index].mean(),
                "hits68": hits,
                "coverage68": hits / count,
                "coverage68_ci95_low": low,
                "coverage68_ci95_high": high,
                "hits95": hits95,
                "coverage95": hits95 / count,
                "coverage95_ci95_low": low95,
                "coverage95_ci95_high": high95,
            }
            rows.append(row)
            if name in receipt["functional_names"]:
                j = receipt["functional_names"].index(name)
                expected = receipt["points"][point]["per_functional"]
                np.testing.assert_allclose(
                    bias[index], expected["mean_rel"][j], rtol=1e-7, atol=1e-13
                )
                np.testing.assert_allclose(
                    spread[index], expected["rel_sd"][j], rtol=1e-9, atol=1e-13
                )
                np.testing.assert_allclose(
                    hits / count, expected["cov68"][j], atol=1e-14
                )
                np.testing.assert_allclose(
                    hits95 / count, expected["cov95"][j], atol=1e-14
                )
    return rows


def _trace_rows(operands: Any) -> list[dict[str, Any]]:
    rows = []
    nominal = operands["trace_nominal_truth"]
    for key in operands.files:
        if not key.startswith(("trace_b0_", "trace_cap10_")) or key.endswith("_truth"):
            continue
        _, family, truth_name = key.split("_", 2)
        truth = operands[key + "_truth"]
        departure = _divide(truth, nominal) - 1
        for iteration, estimate in enumerate(operands[key], 1):
            residual = _divide(estimate, truth) - 1
            for group in ("EW", "J", "H2"):
                mask = (
                    (operands["groups"] == group) & operands["reported"] & (truth > 0)
                )
                eligible = mask & (np.abs(departure) > 0.01)
                absolute = np.abs(residual[mask]) * 100
                rows.append(
                    {
                        "family": family,
                        "truth": truth_name,
                        "iteration": iteration,
                        "map": group,
                        "n_cells": int(mask.sum()),
                        "median_abs_pct": np.median(absolute),
                        "p90_abs_pct": np.percentile(absolute, 90),
                        "max_abs_pct": absolute.max(),
                        "median_signed_pct": np.median(residual[mask]) * 100,
                        "T2_proxy": (
                            float(
                                np.median(
                                    np.abs(residual[eligible] / departure[eligible])
                                )
                            )
                            if eligible.any() and truth_name != "nominal"
                            else ""
                        ),
                        "departure_cells": int(eligible.sum()),
                    }
                )
    return rows


def _prior_rows(operands: Any) -> list[dict[str, Any]]:
    cv = operands["CV"]
    shifts = np.array([_divide(operands[f"prior_d{i}"] - cv, cv) for i in range(1, 6)])
    np.testing.assert_allclose(operands["prior_d0"], cv, rtol=1e-5, atol=1e-53)
    sigma = _divide(operands["data_boot"].std(axis=0, ddof=1), cv)
    bias = _divide(operands["trace_b0_w3"][4], operands["trace_b0_w3_truth"]) - 1
    envelope = _json(ROOT / "docs/orchestration/state/s5p/stage3/envelope-receipt.json")
    rows = []
    for group in ("EW", "J", "H2"):
        mask = (operands["groups"] == group) & operands["reported"]
        for key, use in [
            ("envelope_D1_D5", shifts),
            ("envelope_without_D1", shifts[1:]),
        ]:
            actual = np.max(np.abs(use[:, mask]), axis=0) * 100
            np.testing.assert_allclose(
                actual,
                envelope[key][group]["h_pct_per_reported_cell"],
                rtol=1e-10,
                atol=1e-10,
            )
        for index in np.flatnonzero(mask):
            rows.append(
                {
                    "map": group,
                    "functional": str(operands["names"][index]),
                    "envelope_all_pct": np.max(np.abs(shifts[:, index])) * 100,
                    "envelope_without_D1_pct": np.max(np.abs(shifts[1:, index])) * 100,
                    "data_boot_sigma_pct": sigma[index] * 100,
                    "W3_bias_pct": bias[index] * 100,
                    **{f"d{i+1}_shift_pct": shifts[i, index] * 100 for i in range(5)},
                }
            )
    return rows


def _overlap_rows(operands: Any) -> list[dict[str, Any]]:
    base = operands["data_base"][0]
    jitters, boot, paired = (
        operands["data_jitter"],
        operands["data_boot"],
        operands["data_boot_jitter"],
    )
    s_num, s_boot = jitters.std(0, ddof=1), boot.std(0, ddof=1)
    s_pair = ((paired - boot) / np.sqrt(2)).std(0, ddof=1)
    receipt = _json(ROOT / "docs/orchestration/state/s5p/stage2/stage2_receipt.json")[
        "study_N"
    ]["N1_data"]
    rows = []
    for group in ("EW", "J", "H2"):
        indexes = np.flatnonzero(operands["groups"] == group)
        np.testing.assert_allclose(
            _divide(s_num[indexes], base[indexes]),
            receipt[group]["sigma_num_base_rel"],
            rtol=1e-10,
            atol=1e-12,
        )
        np.testing.assert_allclose(
            _divide(s_pair[indexes], base[indexes]),
            receipt[group]["sigma_num_rep_rel"],
            rtol=1e-10,
            atol=1e-12,
        )
        for index in indexes:
            if not operands["reported"][index]:
                continue
            rows.append(
                {
                    "map": group,
                    "functional": str(operands["names"][index]),
                    "n_jitters": len(jitters),
                    "n_pairs": len(boot),
                    "base_rounding_sd_pct": 100 * s_num[index] / base[index],
                    "bootstrap_sd_pct": 100 * s_boot[index] / base[index],
                    "paired_rounding_sd_pct": 100 * s_pair[index] / base[index],
                    "consistency": s_pair[index] / s_num[index],
                    "variance_share": (s_pair[index] / s_boot[index]) ** 2,
                }
            )
    return rows


def _figures(
    out: Path,
    traces: list[dict[str, Any]],
    ensembles: list[dict[str, Any]],
    priors: list[dict[str, Any]],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "svg.hashsalt": "gbdt-synthesis",
        }
    )
    colors = {"gibuu": "#4477aa", "q3": "#cc6677", "w1": "#228833", "w3": "#aa3377"}
    titles = {
        "J": "J: 109 supported joint cells",
        "H2": "H2: 27 supported joint cells",
        "EW": "EW: 39 supported projected cells",
    }

    def save(fig: Any, name: str) -> None:
        fig.savefig(
            out / (name + ".pdf"),
            bbox_inches="tight",
            metadata={"CreationDate": None, "ModDate": None},
        )
        svg = out / (name + ".svg")
        fig.savefig(svg, bbox_inches="tight", metadata={"Date": None})
        svg.write_text(
            "\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n"
        )
        plt.close(fig)

    fig, axes = plt.subplots(2, 3, figsize=(10.2, 6), layout="constrained")
    for col, group in enumerate(("J", "H2", "EW")):
        for truth, color in colors.items():
            for family in ("b0", "cap10"):
                subset = [
                    r
                    for r in traces
                    if r["map"] == group
                    and r["truth"] == truth
                    and r["family"] == family
                ]
                if not subset:
                    continue
                label = (
                    {
                        "gibuu": "D1 historical",
                        "q3": "q3 stress",
                        "w1": "W1 historical",
                        "w3": "W3 historical",
                    }[truth]
                    if family == "b0"
                    else None
                )
                style = "-" if family == "b0" else "--"
                axes[0, col].plot(
                    [r["iteration"] for r in subset],
                    [r["median_abs_pct"] for r in subset],
                    style,
                    color=color,
                    label=label,
                )
                valid = [r for r in subset if r["T2_proxy"] != ""]
                axes[1, col].plot(
                    [r["iteration"] for r in valid],
                    [r["T2_proxy"] for r in valid],
                    style,
                    color=color,
                )
        axes[0, col].set_title(titles[group])
        axes[1, col].axhline(0.25, color="0.5", lw=0.8, ls=":")
        for ax in axes[:, col]:
            ax.set_xscale("log")
            ax.set_xticks(
                [1, 5, 10, 30, 100, 200], ["1", "5", "10", "30", "100", "200"]
            )
            ax.grid(alpha=0.15)
        axes[1, col].set_xlabel("Iteration (available ranges only)")
    axes[0, 0].set_ylabel("Median absolute residual (%)")
    axes[1, 0].set_ylabel("Historical recovery proxy")
    axes[0, 0].legend(fontsize=8)
    fig.suptitle(
        "Noise-free development traces: solid 100 trees / 8 leaves; dashed 400 / 31\nNo repeat-variance axis; historical truth ratios, fixed detector response",
        fontsize=11,
    )
    save(fig, "gbdt_recovery")

    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.6), layout="constrained")
    for ax, point in zip(axes, ("nominal", "W2", "W3"), strict=True):
        for group, color, marker in [("J", "#4477aa", "o"), ("H2", "#cc6677", "s")]:
            subset = [
                r
                for r in ensembles
                if r["truth"] == point and r["map"] == group and r["supported"]
            ]
            bias = np.array([r["bias_pct"] for r in subset])
            sd = np.array([r["residual_sd_pct"] for r in subset])
            xerr = np.array(
                [
                    [r["bias_pct"] - r["bias_ci95_low_pct"] for r in subset],
                    [r["bias_ci95_high_pct"] - r["bias_pct"] for r in subset],
                ]
            )
            yerr = np.array(
                [
                    [r["residual_sd_pct"] - r["sd_ci95_low_pct"] for r in subset],
                    [r["sd_ci95_high_pct"] - r["residual_sd_pct"] for r in subset],
                ]
            )
            ax.errorbar(
                bias,
                sd,
                xerr=xerr,
                yerr=yerr,
                fmt=marker,
                ms=2.5,
                lw=0.5,
                alpha=0.45,
                color=color,
                label=group,
            )
        ax.set_title(f'{point}: n = {40 if point=="nominal" else 20}')
        ax.set_xlabel("Mean signed relative residual (%)")
        ax.set_yscale("log")
        ax.grid(alpha=0.15)
    axes[0].set_ylabel("Repeat SD of relative residual (%)")
    axes[0].legend()
    fig.suptitle(
        "One setting: R, five iterations; different cells estimate different quantities\n95% pointwise t / normal-model SD intervals; development reuse",
        fontsize=11,
    )
    save(fig, "gbdt_bias_spread")

    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.5), layout="constrained")
    for ax, group in zip(axes, ("J", "H2", "EW"), strict=True):
        subset = [r for r in priors if r["map"] == group]
        x = np.array([-r["W3_bias_pct"] for r in subset])
        y = np.array([r["d4_shift_pct"] for r in subset])
        ax.scatter(x, y, s=12, color="#4477aa", alpha=0.7)
        low = min(x.min(), y.min())
        high = max(x.max(), y.max())
        ax.plot([low, high], [low, high], color="0.5", ls=":")
        fraction = np.mean(np.abs(y) >= np.abs(x))
        ax.set_title(
            f"{group}: r = {np.corrcoef(x,y)[0,1]:.2f}; |shift| ≥ |bias|: {fraction:.0%}"
        )
        ax.set_xlabel("Minus noise-free W3 residual (%)")
        ax.grid(alpha=0.15)
    axes[0].set_ylabel("Data shift under W3 prior (%)")
    fig.suptitle(
        "Historical W3 at five iterations: correlation is not a per-cell bias bound",
        fontsize=11,
    )
    save(fig, "gbdt_prior_response")

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(10.2, 3.7),
        layout="constrained",
        gridspec_kw={"width_ratios": [1.65, 1]},
    )
    matrix = np.array(
        [
            [
                next(
                    r["coverage68"]
                    for r in ensembles
                    if r["truth"] == point and r["functional"] == f"EW{i}"
                )
                for i in range(42)
            ]
            for point in POINTS
        ]
    )
    im = axes[0].imshow(matrix, vmin=0, vmax=1, cmap="viridis", aspect="auto")
    axes[0].set_yticks(
        range(6),
        [f"{label} (n={40 if i==0 else 20})" for i, label in enumerate(LABELS)],
    )
    axes[0].set_xlabel("EW cell index (all 42 historical functionals)")
    fig.colorbar(im, ax=axes[0], label="Fraction in fixed ±σ interval", shrink=0.8)
    for offset, name, color in [(-0.12, "EW7", "#4477aa"), (0.12, "EW41", "#cc6677")]:
        subset = [
            next(
                r for r in ensembles if r["truth"] == point and r["functional"] == name
            )
            for point in POINTS
        ]
        y = np.array([r["coverage68"] for r in subset])
        err = np.array(
            [
                [r["coverage68"] - r["coverage68_ci95_low"] for r in subset],
                [r["coverage68_ci95_high"] - r["coverage68"] for r in subset],
            ]
        )
        axes[1].errorbar(
            np.arange(6) + offset, y, yerr=err, fmt="o", ms=3, color=color, label=name
        )
    axes[1].axhline(0.6827, ls=":", color="0.4")
    axes[1].set_ylim(-0.04, 1.04)
    axes[1].set_xticks(range(6), ["Nom.", "D1", "q3", "W1", "W2", "W3"])
    axes[1].legend()
    axes[1].set_ylabel("Coverage with 95% pointwise exact bounds")
    fig.suptitle(
        "Historical R statistical intervals: σ from 100 replicas of nominal seed 700000\nReused assessment samples; no per-experiment or total-coverage claim",
        fontsize=11,
    )
    save(fig, "gbdt_coverage")


def main() -> None:
    """Check identities and reproduce all diagnostic outputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=PACKAGE / "results")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    path = PACKAGE / "inputs/operands.npz"
    inventory = _json(PACKAGE / "inputs/inventory.json")
    if hashlib.sha256(path.read_bytes()).hexdigest() != inventory["operands_sha256"]:
        raise ValueError("Frozen operand identity mismatch")
    for source, expected in _json(PACKAGE / "definition.json")["source_sha256"].items():
        if hashlib.sha256((ROOT / source).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Source changed: {source}")
    with np.load(path, allow_pickle=False) as operands:
        ensembles = _ensemble_rows(operands)
        traces = _trace_rows(operands)
        priors = _prior_rows(operands)
        overlap = _overlap_rows(operands)
        for name, rows in [
            ("ensembles", ensembles),
            ("recovery", traces),
            ("prior", priors),
            ("overlap", overlap),
        ]:
            _csv(args.out / (name + ".csv"), rows)
        _figures(args.out, traces, ensembles, priors)
    receipt = _json(ROOT / "docs/orchestration/state/s5p/stage2/stage2_receipt.json")
    costs = [
        {
            "construction": key,
            **value,
            "scope": "measured seconds_unfold; mixed tasks, no billing inference",
        }
        for key, value in receipt["costs"].items()
    ]
    _csv(args.out / "costs.csv", costs)
    summary: dict[str, Any] = {
        "tradeoff_established": False,
        "reason": "No matched repeat ensembles across iteration/capacity settings. Noise-free recovery is truth dependent; aggregation changes the functional.",
        "groups": {},
    }
    for group in ("J", "H2", "EW"):
        pr = [r for r in priors if r["map"] == group]
        nr = [r for r in overlap if r["map"] == group]
        summary["groups"][group] = {
            "historical_prior_envelope_median_pct": float(
                np.median([r["envelope_all_pct"] for r in pr])
            ),
            "historical_without_D1_median_pct": float(
                np.median([r["envelope_without_D1_pct"] for r in pr])
            ),
            "rounding_sd_median_pct": float(
                np.median([r["base_rounding_sd_pct"] for r in nr])
            ),
            "bootstrap_sd_median_pct": float(
                np.median([r["bootstrap_sd_pct"] for r in nr])
            ),
            "consistency_median": float(np.median([r["consistency"] for r in nr])),
            "variance_share_median": float(
                np.median([r["variance_share"] for r in nr])
            ),
            "W3_prior_bounds_fraction": float(
                np.mean([abs(r["d4_shift_pct"]) >= abs(r["W3_bias_pct"]) for r in pr])
            ),
        }
    (args.out / "summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
