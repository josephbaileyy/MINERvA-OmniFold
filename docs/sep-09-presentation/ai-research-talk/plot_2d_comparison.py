#!/usr/bin/env python3
"""Replot the frozen 2D result against the original published histogram.

Both ROOT files must match the committed agreement receipt before use. The
projection plot includes both standalone total covariances; no covariance of
the difference, independent-measurement significance, or new unfolding is made.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import numpy as np
import numpy.typing as npt
import uproot

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
INK, TEAL, PAPER = "#182A35", "#147D83", "#FAF9F5"
Array = npt.NDArray[np.float64]


def read_comparison() -> dict[str, Any]:
    """Read matched ROOT objects and reproduce the committed agreement operands."""
    metadata = json.loads((HERE / "measurements/metrics.json").read_text())
    receipt_path = (
        "docs/orchestration/receipts/RECEIPT-2d-agreement-windows-20260821.json"
    )
    receipt = json.loads(
        subprocess.check_output(
            ["git", "show", f"{metadata['revision']}:{receipt_path}"], cwd=REPO
        )
    )
    for filename, key in (("ours_2d.root", "ours"), ("published_2d.root", "paper")):
        digest = hashlib.sha256((HERE / "inputs" / filename).read_bytes()).hexdigest()
        if digest != receipt["sources"][key]["sha256"]:
            raise ValueError(f"{filename} does not match the committed receipt")
    with uproot.open(HERE / "inputs/ours_2d.root") as root:
        ours, pt_edges, pz_edges = root["hXSec2D"].to_numpy()
    with uproot.open(HERE / "inputs/published_2d.root") as root:
        published_transpose, paper_pz, paper_pt = root["pt_pl_cross_section"].to_numpy()
        published = published_transpose.T
        matrices = {}
        for key in ("TotalCovariance", "StatOnlyCovariance"):
            obj = root[key]
            matrices[key] = np.asarray(obj.member("fElements")).reshape(
                obj.member("fNrows"), obj.member("fNcols")
            )
    expected_edges = np.array(
        [
            0,
            0.075,
            0.15,
            0.25,
            0.325,
            0.4,
            0.475,
            0.55,
            0.7,
            0.85,
            1,
            1.25,
            1.5,
            2.5,
            4.5,
        ]
    )
    np.testing.assert_array_equal(paper_pt, expected_edges)
    if np.flatnonzero(pt_edges != paper_pt).tolist() != [1, 4, 6]:
        raise ValueError("The recorded three-boundary difference changed")
    np.testing.assert_array_equal(pz_edges, paper_pz)
    if ours.shape != published.shape or ours.shape != (14, 16):
        raise ValueError("Unexpected 2D orientation")
    mask = (np.diag(matrices["StatOnlyCovariance"]) > 0).reshape(ours.shape)
    if int(mask.sum()) != 205 or np.any(published[mask] <= 0):
        raise ValueError("Reported-bin denominator differs from the receipt")
    ratios = np.full(ours.shape, np.nan)
    ratios[mask] = ours[mask] / published[mask]
    counts = [
        int(np.sum(np.abs(ratios[mask] - 1) <= cutoff)) for cutoff in (0.05, 0.1, 0.2)
    ]
    if counts != [159, 193, 202]:
        raise ValueError(f"Per-bin agreement failed reproduction: {counts}")
    areas = np.diff(pt_edges)[:, None] * np.diff(pz_edges)[None, :]
    totals = receipt["headline_totals_oi130"]["values"]
    paper_areas = np.diff(paper_pt)[:, None] * np.diff(paper_pz)[None, :]
    measured_totals = [
        float(np.sum(areas[mask] * ours[mask])),
        float(np.sum(paper_areas[mask] * published[mask])),
    ]
    np.testing.assert_allclose(
        measured_totals,
        [totals["integral_ours_reported"], totals["integral_paper_reported"]],
        rtol=1e-12,
        atol=0,
    )
    covariance = matrices["TotalCovariance"]
    np.testing.assert_allclose(covariance, covariance.T, rtol=1e-10, atol=1e-90)
    if np.any(np.diag(covariance)[mask.ravel()] <= 0):
        raise ValueError("Reported total covariance has a non-positive diagonal")
    comparison = {
        "ours": ours,
        "published": published,
        "pt_edges": pt_edges,
        "pz_edges": pz_edges,
        "paper_pt_edges": paper_pt,
        "paper_pz_edges": paper_pz,
        "mask": mask,
        "ratios": ratios,
        "covariance": covariance,
        "counts": counts,
        "totals": measured_totals,
        "revision": metadata["revision"],
        "source_hashes": {
            key: receipt["sources"][key]["sha256"] for key in ("ours", "paper")
        },
    }
    comparison["ours_covariance"] = read_ours_covariance(comparison)
    return comparison


def read_ours_covariance(comparison: dict[str, Any]) -> Array:
    """Load the adopted 2D budget and check its bin pairing and component identity."""
    record = json.loads((HERE / "measurements/two_d_uncertainty.json").read_text())
    for source in record["sources"]:
        content = subprocess.check_output(
            ["git", "show", f"{source['revision']}:{source['path']}"], cwd=REPO
        )
        if hashlib.sha256(content).hexdigest() != source["sha256"]:
            raise ValueError("Committed uncertainty source changed")
    for source in record["inputs"]:
        content = (HERE / "inputs" / source["local"]).read_bytes()
        if hashlib.sha256(content).hexdigest() != source["sha256"]:
            raise ValueError(f"Uncertainty input digest changed: {source['local']}")
    mask = comparison["mask"]
    np.testing.assert_array_equal(comparison["ours"] > 0, mask)
    with uproot.open(HERE / "inputs/ours_2d_systematics.root") as root:
        combined = root["hCov_combined"].values()
        systematic = root["hCov_universe_total"].values()
        sigma, pt, pz = root["hSigma_combined"].to_numpy()
        np.testing.assert_array_equal(pt, comparison["pt_edges"])
        np.testing.assert_array_equal(pz, comparison["pz_edges"])
        np.testing.assert_array_equal(sigma > 0, mask)
        np.testing.assert_allclose(
            sigma[mask] ** 2, np.diag(combined), rtol=1e-12, atol=0
        )
    components = []
    for filename in ("ours_2d_bootstrap.root", "ours_2d_ml.root"):
        with uproot.open(HERE / "inputs" / filename) as root:
            covariance = root["hCov2D_reported"].values()
            sigma, pt, pz = root["hStd2D"].to_numpy()
            np.testing.assert_array_equal(pt, comparison["pt_edges"])
            np.testing.assert_array_equal(pz, comparison["pz_edges"])
            np.testing.assert_array_equal(sigma > 0, mask)
            np.testing.assert_allclose(
                sigma[mask] ** 2, np.diag(covariance), rtol=1e-12, atol=0
            )
            components.append(covariance)
    bootstrap, ml = components
    # The systematic-file combined object already contains the bootstrap block.
    np.testing.assert_allclose(combined, systematic + bootstrap, rtol=1e-11, atol=1e-95)
    adopted = combined + ml
    if adopted.shape != (205, 205):
        raise ValueError("Unexpected reported-bin covariance dimensions")
    np.testing.assert_allclose(adopted, adopted.T, rtol=1e-12, atol=1e-95)
    eigenvalues = np.linalg.eigvalsh(adopted)
    if eigenvalues[0] < -1e-10 * eigenvalues[-1]:
        raise ValueError("The adopted covariance is not positive semidefinite")
    expanded = np.zeros((mask.size, mask.size))
    indices = np.flatnonzero(mask.ravel())
    expanded[np.ix_(indices, indices)] = adopted
    return expanded


def project_ours_errors(comparison: dict[str, Any], axis: int) -> Array:
    """Project our full covariance and reproduce the committed fractional summary."""
    mask = comparison["mask"]
    mapping = np.zeros((mask.shape[axis], mask.size))
    widths = np.diff(comparison["pz_edges"] if axis == 0 else comparison["pt_edges"])
    for ipt, ipz in np.ndindex(mask.shape):
        if mask[ipt, ipz]:
            mapping[ipt if axis == 0 else ipz, ipt * mask.shape[1] + ipz] = widths[
                ipz if axis == 0 else ipt
            ]
    projected = mapping @ comparison["ours_covariance"] @ mapping.T
    errors = np.sqrt(np.diag(projected))
    _, central, _, _ = project(comparison, axis)
    relative = 100 * errors / central
    expected = (6.220, 8.037) if axis == 0 else (5.901, 14.994)
    np.testing.assert_allclose(
        [np.median(relative), np.max(relative)], expected, rtol=0, atol=0.00051
    )
    return errors


def save(figure: Any, name: str) -> None:
    """Export a plotting figure as PNG and vector PDF."""
    for suffix in ("png", "pdf"):
        figure.savefig(HERE / "figures" / f"{name}.{suffix}", dpi=220, facecolor=PAPER)
    plt.close(figure)


def project(comparison: dict[str, Any], axis: int) -> tuple[Array, Array, Array, Array]:
    """Integrate the other axis, propagating the complete published covariance."""
    mask = comparison["mask"]
    pt_width, pz_width = np.diff(comparison["pt_edges"]), np.diff(
        comparison["pz_edges"]
    )
    mapping = np.zeros((mask.shape[axis], mask.size))
    paper_mapping = np.zeros_like(mapping)
    paper_pt_width = np.diff(comparison["paper_pt_edges"])
    paper_pz_width = np.diff(comparison["paper_pz_edges"])
    for ipt, ipz in np.ndindex(mask.shape):
        if mask[ipt, ipz]:
            index = ipt if axis == 0 else ipz
            global_index = ipt * mask.shape[1] + ipz
            mapping[index, global_index] = pz_width[ipz] if axis == 0 else pt_width[ipt]
            paper_mapping[index, global_index] = (
                paper_pz_width[ipz] if axis == 0 else paper_pt_width[ipt]
            )
    edges = comparison["pt_edges"] if axis == 0 else comparison["pz_edges"]
    paper_edges = (
        comparison["paper_pt_edges"] if axis == 0 else comparison["paper_pz_edges"]
    )
    published = paper_mapping @ comparison["published"].ravel()
    ours = mapping @ comparison["ours"].ravel()
    errors = np.sqrt(
        np.diag(paper_mapping @ comparison["covariance"] @ paper_mapping.T)
    )
    for values, widths, total in zip(
        (ours, published),
        (np.diff(edges), np.diff(paper_edges)),
        comparison["totals"],
        strict=True,
    ):
        np.testing.assert_allclose(values @ widths, total, rtol=1e-12, atol=0)
    return edges, ours, published, errors


def overlay(
    top: Any,
    bottom: Any,
    edges: Array,
    ours: Array,
    published: Array,
    errors: Array,
    xlabel: str,
    *,
    scale: float,
    log_x: bool = False,
    reference_edges: Array | None = None,
    ours_errors: Array | None = None,
) -> None:
    """Draw central values and a reference-uncertainty band with an aligned ratio."""
    reference_edges = edges if reference_edges is None else reference_edges
    centers = (reference_edges[:-1] + reference_edges[1:]) / 2
    valid = published > 0
    top.stairs(
        np.where(valid, ours / scale, np.nan),
        edges,
        color=TEAL,
        linewidth=2,
        label=(
            "This work · total uncertainty"
            if ours_errors is not None
            else "This work · OmniFold"
        ),
    )
    if ours_errors is not None:
        top.stairs(
            (ours + ours_errors) / scale,
            edges,
            baseline=(ours - ours_errors) / scale,
            fill=True,
            color=TEAL,
            alpha=0.22,
            linewidth=0,
        )
    top.errorbar(
        centers[valid],
        published[valid] / scale,
        yerr=errors[valid] / scale,
        fmt="o",
        markersize=3.5,
        color=INK,
        elinewidth=1,
        capsize=2,
        label="Published · total uncertainty",
        zorder=3,
    )
    ratio = np.divide(ours, published, out=np.full_like(ours, np.nan), where=valid)
    relative = np.divide(
        errors, published, out=np.full_like(errors, np.nan), where=valid
    )
    bottom.stairs(
        1 + relative,
        reference_edges,
        baseline=1 - relative,
        fill=True,
        color="#C8CDCB",
        alpha=0.7,
        linewidth=0,
    )
    bottom.axhline(1, color=INK, linewidth=0.8)
    bottom.stairs(ratio, reference_edges, color=TEAL, linewidth=2)
    bottom.plot(centers[valid], ratio[valid], ".", color=TEAL, markersize=4)
    bottom.set_xlabel(xlabel)
    bottom.set_ylabel("Ours / paper")
    extent = max(
        0.13,
        float(np.nanmax(np.abs(ratio - 1))) * 1.1,
        float(np.nanmax(relative)) * 1.05,
    )
    if ours_errors is not None:
        ratio_errors = ours_errors / published
        bottom.errorbar(
            centers[valid],
            ratio[valid],
            yerr=ratio_errors[valid],
            fmt="o",
            markersize=3,
            color=TEAL,
            elinewidth=1.2,
            capsize=2,
        )
        extent = max(extent, float(np.nanmax(np.abs(ratio - 1) + ratio_errors)) * 1.05)
    bottom.set_ylim(max(0, 1 - extent), 1 + extent)
    for panel in (top, bottom):
        panel.set_xlim(edges[0], edges[-1])
        panel.spines[["top", "right"]].set_visible(False)
        panel.grid(axis="y", alpha=0.15)
        panel.set_axisbelow(True)
        if log_x:
            panel.set_xscale("log")
            panel.xaxis.set_minor_formatter(NullFormatter())
    top.tick_params(axis="x", which="both", labelbottom=False)


def plot_projections(comparison: dict[str, Any]) -> None:
    """Show both physical projections, retaining bin widths and all reported bins."""
    figure, axes = plt.subplots(
        2,
        2,
        figsize=(12.7, 4.8),
        sharex="col",
        gridspec_kw={"height_ratios": [2.4, 1]},
        layout="constrained",
    )
    for index, (label, scale, power) in enumerate(
        [(r"$p_T$ (GeV/$c$)", 1e-38, -38), (r"$p_{\parallel}$ (GeV/$c$)", 1e-39, -39)]
    ):
        overlay(
            axes[0, index],
            axes[1, index],
            *project(comparison, index),
            label,
            scale=scale,
            ours_errors=project_ours_errors(comparison, index),
            reference_edges=(
                comparison["paper_pt_edges"]
                if index == 0
                else comparison["paper_pz_edges"]
            ),
        )
        axes[0, index].set_ylabel(
            rf"$d\sigma/dp$ ($10^{{{power}}}$ cm$^2$/(GeV/$c$)/nucleon)", fontsize=10
        )
    axes[0, 0].legend(frameon=False, fontsize=10)
    save(figure, "two_d_projections")


def plot_ratio_map(comparison: dict[str, Any]) -> None:
    """Show every reported 2D bin, labelling large residuals and color saturation."""
    figure, axis = plt.subplots(figsize=(12.7, 4.7), layout="constrained")
    deviations = 100 * (comparison["ratios"] - 1)
    cmap = plt.get_cmap("RdBu_r").copy()
    cmap.set_bad("#D8DBD8")
    drawn = axis.imshow(
        deviations, origin="lower", aspect="auto", cmap=cmap, vmin=-20, vmax=20
    )
    for ipt, ipz in np.ndindex(deviations.shape):
        value = deviations[ipt, ipz]
        if np.isfinite(value) and abs(value) > 10:
            axis.text(
                ipz,
                ipt,
                f"{value:+.0f}",
                ha="center",
                va="center",
                fontsize=8,
                color="white" if abs(value) > 16 else INK,
            )
    pt_edges, pz_edges = comparison["pt_edges"], comparison["pz_edges"]
    axis.set_yticks(
        range(14),
        [f"{a:g}–{b:g}" for a, b in zip(pt_edges[:-1], pt_edges[1:], strict=True)],
        fontsize=9,
    )
    axis.set_xticks(
        range(16),
        [f"{a:g}–{b:g}" for a, b in zip(pz_edges[:-1], pz_edges[1:], strict=True)],
        rotation=35,
        ha="right",
        fontsize=9,
    )
    axis.set_xlabel(r"$p_{\parallel}$ bin (GeV/$c$); equal display width per bin")
    axis.set_ylabel(r"$p_T$ bin (GeV/$c$)")
    colorbar = figure.colorbar(drawn, ax=axis, pad=0.025, extend="both")
    colorbar.set_label("100 × (OmniFold / published − 1) (%)", fontsize=11)
    save(figure, "two_d_ratio_map")


def plot_slices(comparison: dict[str, Any], *, all_slices: bool = False) -> None:
    """Draw fixed pT slices; representative indices are chosen by axis coverage."""
    indices = list(range(14)) if all_slices else [2, 7, 10, 13]
    columns, groups = (7, 2) if all_slices else (4, 1)
    figure, axes = plt.subplots(
        2 * groups,
        columns,
        figsize=(17, 7.5) if all_slices else (12.7, 4.5),
        gridspec_kw={"height_ratios": [2.4, 1] * groups},
        layout="constrained",
    )
    errors = np.sqrt(np.diag(comparison["covariance"])).reshape((14, 16))
    own_errors = np.sqrt(np.diag(comparison["ours_covariance"])).reshape((14, 16))
    for panel, ipt in enumerate(indices):
        row, column = (panel // columns) * 2, panel % columns
        mask = comparison["mask"][ipt]
        ours = np.where(mask, comparison["ours"][ipt], np.nan)
        published = np.where(mask, comparison["published"][ipt], np.nan)
        scale = 10 ** np.floor(np.log10(np.nanmax(published)))
        overlay(
            axes[row, column],
            axes[row + 1, column],
            comparison["pz_edges"],
            ours,
            published,
            errors[ipt],
            r"$p_{\parallel}$ (GeV/$c$)",
            scale=scale,
            log_x=True,
            ours_errors=own_errors[ipt],
        )
        low, high = comparison["pt_edges"][ipt : ipt + 2]
        paper_low, paper_high = comparison["paper_pt_edges"][ipt : ipt + 2]
        title = rf"${low:g} < p_T < {high:g}$ GeV/$c$"
        if low != paper_low or high != paper_high:
            title += f"\npaper: {paper_low:g}–{paper_high:g}"
        axes[row, column].set_title(title, fontsize=10)
        axes[row, column].set_ylabel(
            rf"$d^2\sigma/(dp_T dp_{{\parallel}})$ / $10^{{{int(np.log10(scale))}}}$",
            fontsize=9,
        )
        axes[row + 1, column].set_xticks(
            [2, 5, 10, 20, 60], ["2", "5", "10", "20", "60"]
        )
        axes[row + 1, column].tick_params(labelsize=9)
        axes[row, column].tick_params(labelsize=9)
    save(figure, "two_d_all_slices" if all_slices else "two_d_slices")


def main() -> None:
    """Build the four direct-comparison plots and export the plotted bin values."""
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "text.color": INK,
            "axes.labelcolor": INK,
            "axes.facecolor": PAPER,
            "figure.facecolor": PAPER,
        }
    )
    comparison = read_comparison()
    plot_projections(comparison)
    plot_ratio_map(comparison)
    plot_slices(comparison)
    plot_slices(comparison, all_slices=True)
    with (HERE / "measurements/two_d_bins.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "pt_low",
                "pt_high",
                "paper_pt_low",
                "paper_pt_high",
                "pz_low",
                "pz_high",
                "reported",
                "ours",
                "published",
                "ratio",
            ]
        )
        for ipt, ipz in np.ndindex(comparison["ours"].shape):
            writer.writerow(
                [
                    *comparison["pt_edges"][ipt : ipt + 2],
                    *comparison["paper_pt_edges"][ipt : ipt + 2],
                    *comparison["pz_edges"][ipz : ipz + 2],
                    bool(comparison["mask"][ipt, ipz]),
                    comparison["ours"][ipt, ipz],
                    comparison["published"][ipt, ipz],
                    comparison["ratios"][ipt, ipz],
                ]
            )
    record = {
        "source_hashes": comparison["source_hashes"],
        "source_revision": comparison["revision"],
        "reported_bins": int(comparison["mask"].sum()),
        "agreement_counts": comparison["counts"],
        "integrals": comparison["totals"],
        "selected_pt_indices_zero_based": [2, 7, 10, 13],
        "slice_selection_rule": "Four slices spanning the available range with exactly equal physical boundaries; all 14 supplied in backup.",
        "ours_pt_edges": comparison["pt_edges"].tolist(),
        "published_pt_edges": comparison["paper_pt_edges"].tolist(),
        "edge_difference": "At boundary indices 1,4,6: ours .07,.33,.47; published .075,.325,.475. Bin ratios are index matched; each projection uses its own physical widths.",
        "map_color_limits_percent": [-20, 20],
        "unreported_cells": 19,
        "limits": "Projections show our total errors and published reference errors separately; ratio error bars are sigma_ours / paper central. Slices also display our total errors and the separate paper reference errors. No covariance or significance of the difference is constructed.",
    }
    (HERE / "measurements/two_d_validation.json").write_text(
        json.dumps(record, indent=2) + "\n"
    )
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
