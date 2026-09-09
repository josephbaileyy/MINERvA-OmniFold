#!/usr/bin/env python3
"""Compare projected 2D uncertainty components with available published sources."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import uproot

from plot_2d_comparison import Array, PAPER, TEAL, INK, read_comparison, save

HERE = Path(__file__).resolve().parent
CATEGORIES = [
    "Total",
    "Flux",
    "Muon reconstruction",
    "Normalization",
    "Hadronic response",
    "Models",
    "Statistical",
    "ML",
]


def category_for_band(name: str) -> str:
    """Use the canonical analyze_universes.py grouping for systematic bands."""
    clean = name.removeprefix("full_")
    if clean == "Flux":
        return "Flux"
    if clean == "__Normalization_flat":
        return "Normalization"
    if clean.startswith(("Fr", "MFP_", "GEANT_")):
        return "Hadronic response"
    if clean.startswith(("Muon_", "BeamAngle")) or clean in {
        "MuonResolution",
        "MinosEfficiency",
    }:
        return "Muon reconstruction"
    return "Models"


def projected_fraction(
    covariance: Array, comparison: dict[str, Any], axis: int, *, paper: bool
) -> Array:
    """Propagate full component covariance before dividing by its own central value."""
    prefix = "paper_" if paper else ""
    pt_width = np.diff(comparison[prefix + "pt_edges"])
    pz_width = np.diff(comparison[prefix + "pz_edges"])
    mask = comparison["mask"]
    mapping = np.zeros((mask.shape[axis], int(mask.sum())))
    for index, (ipt, ipz) in enumerate(zip(*np.nonzero(mask), strict=True)):
        mapping[ipt if axis == 0 else ipz, index] = (
            pz_width[ipz] if axis == 0 else pt_width[ipt]
        )
    values = comparison["published" if paper else "ours"][mask]
    variance = np.diag(mapping @ covariance @ mapping.T)
    if np.any(variance < -1e-12 * np.max(np.abs(variance))):
        raise ValueError("Negative projected variance")
    return np.asarray(
        100 * np.sqrt(np.maximum(variance, 0)) / (mapping @ values), dtype=np.float64
    )


def measure_sources() -> dict[str, Any]:
    """Read source matrices, verify their sum, and return projected fractional errors."""
    comparison = read_comparison()
    mask = comparison["mask"].ravel()
    indices = np.flatnonzero(mask)
    ours = {
        category: np.zeros((205, 205)) for category in CATEGORIES if category != "Total"
    }
    energy_scale = np.zeros((205, 205))
    band_groups = {}
    with uproot.open(HERE / "inputs/ours_2d_systematics.root") as root:
        for name in root.keys(cycle=False):
            if not name.startswith("hCov_universe_") or name == "hCov_universe_total":
                continue
            band = name.removeprefix("hCov_universe_")
            category = category_for_band(band)
            band_groups[band] = category
            component = root[name].values()
            ours[category] += component
            if band.removeprefix("full_") in {
                "Muon_Energy_MINOS",
                "Muon_Energy_MINERvA",
            }:
                energy_scale += component
        np.testing.assert_allclose(
            sum(ours.values()),
            root["hCov_universe_total"].values(),
            rtol=1e-10,
            atol=1e-94,
        )
    for category, filename in [
        ("Statistical", "ours_2d_bootstrap.root"),
        ("ML", "ours_2d_ml.root"),
    ]:
        with uproot.open(HERE / "inputs" / filename) as root:
            ours[category] = root["hCov2D_reported"].values()
    ours["Total"] = np.sum(np.stack(list(ours.values())), axis=0)
    np.testing.assert_allclose(
        ours["Total"],
        comparison["ours_covariance"][np.ix_(indices, indices)],
        rtol=1e-10,
        atol=1e-94,
    )
    ours["Muon energy scale"] = energy_scale
    published = {}
    with uproot.open(HERE / "inputs/published_2d.root") as root:
        for label, name in [
            ("Total", "TotalCovariance"),
            ("Flux", "FluxCovariance"),
            ("Statistical", "StatOnlyCovariance"),
            ("Muon energy scale", "MuonEnergyScaleCovariance"),
        ]:
            obj = root[name]
            covariance = np.asarray(obj.member("fElements")).reshape(224, 224)
            published[label] = covariance[np.ix_(indices, indices)]
    result: dict[str, Any] = {
        "band_groups": band_groups,
        "projections": {},
        "definition": "Median across projected bins of 100 sqrt(diag(P C_component P.T)) / own projected central value. Medians and standard deviations are not additive.",
        "energy_scale_subset": ["full_Muon_Energy_MINOS", "full_Muon_Energy_MINERvA"],
        "limits": "Published source release provides total, flux, statistical and muon-energy-scale matrices only. No missing category is assigned zero. Own bin widths used for each result.",
    }
    for axis, name in enumerate(["pt", "pz"]):
        result["projections"][name] = {}
        for label, components in [("ours", ours), ("paper", published)]:
            result["projections"][name][label] = {}
            for category, covariance in components.items():
                values = projected_fraction(
                    covariance, comparison, axis, paper=label == "paper"
                )
                result["projections"][name][label][category] = {
                    "median": float(np.median(values)),
                    "max": float(np.max(values)),
                    "per_bin": values.tolist(),
                }
    metadata = json.loads((HERE / "measurements/two_d_uncertainty.json").read_text())
    source = metadata["sources"][0]
    summary = subprocess.check_output(
        ["git", "show", f"{source['revision']}:{source['path']}"],
        cwd=HERE.parents[2],
        text=True,
    )
    for name in ("pt", "pz"):
        section = summary.split(f"{name} projection:\n", 1)[1].split("\n\n", 1)[0]
        expected = re.findall(
            r"^\s+(.+?)\s+median=\s*([\d.]+)%\s+max=\s*([\d.]+)%",
            section,
            flags=re.MULTILINE,
        )
        checked = 0
        for category, median, maximum in expected:
            if category in result["projections"][name]["ours"]:
                measured = result["projections"][name]["ours"][category]
                np.testing.assert_allclose(
                    [measured["median"], measured["max"]],
                    [float(median), float(maximum)],
                    rtol=0,
                    atol=0.00051,
                )
                checked += 1
        if checked != len(CATEGORIES):
            raise ValueError(
                "Not all uncertainty categories matched the committed summary"
            )
    return result


def plot_sources(record: dict[str, Any], *, matched_only: bool = False) -> None:
    """Draw category medians without implying that missing paper components vanish."""
    categories = (
        ["Total", "Flux", "Muon energy scale", "Statistical"]
        if matched_only
        else CATEGORIES
    )
    figure, axes = plt.subplots(
        1, 2, figsize=(12.7, 4.5), sharex=True, sharey=True, layout="constrained"
    )
    positions = np.arange(len(categories))[::-1]
    for axis, name, title in zip(
        axes,
        ["pt", "pz"],
        [r"$p_T$ projection", r"$p_{\parallel}$ projection"],
        strict=True,
    ):
        rows = record["projections"][name]
        own_values = [rows["ours"][category]["median"] for category in categories]
        axis.barh(
            positions, own_values, height=0.52, color=TEAL, alpha=0.8, label="This work"
        )
        paper_positions = [
            position
            for position, category in zip(positions, categories, strict=True)
            if category in rows["paper"]
        ]
        paper_values = [
            rows["paper"][category]["median"]
            for category in categories
            if category in rows["paper"]
        ]
        axis.scatter(
            paper_values,
            paper_positions,
            marker="D",
            s=42,
            color=INK,
            edgecolor=PAPER,
            zorder=3,
            label="Published source",
        )
        for position, value in zip(positions, own_values, strict=True):
            axis.text(
                value + 0.12,
                position + 0.1,
                f"{value:.2f}",
                va="center",
                fontsize=10,
                color=TEAL,
            )
        for position, value in zip(paper_positions, paper_values, strict=True):
            axis.text(
                value + 0.12,
                position - 0.18,
                f"{value:.2f}",
                va="center",
                fontsize=10,
                color=INK,
            )
        axis.set_title(title, fontsize=15)
        axis.set_yticks(positions, categories, fontsize=11)
        axis.set_xlim(0, 7.6)
        axis.set_xlabel("Median projected fractional uncertainty (%)", fontsize=11)
        axis.spines[["top", "right", "left"]].set_visible(False)
        axis.tick_params(axis="y", length=0)
        axis.grid(axis="x", alpha=0.15)
        axis.set_axisbelow(True)
    axes[1].legend(frameon=False, loc="lower right", fontsize=10)
    save(
        figure, "uncertainty_sources_matched" if matched_only else "uncertainty_sources"
    )


def main() -> None:
    """Build the full budget and comparable-source figures with numeric exports."""
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "text.color": INK,
            "axes.facecolor": PAPER,
            "figure.facecolor": PAPER,
        }
    )
    record = measure_sources()
    (HERE / "measurements/uncertainty_sources.json").write_text(
        json.dumps(record, indent=2) + "\n"
    )
    plot_sources(record)
    plot_sources(record, matched_only=True)
    print("Built uncertainty source comparisons from validated 2D matrices")


if __name__ == "__main__":
    main()
