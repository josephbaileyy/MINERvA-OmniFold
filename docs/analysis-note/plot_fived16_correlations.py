#!/usr/bin/env python3
"""Build or verify the sixteen-cell correlation heatmap for the analysis note.

Run with --output pointing to a candidate PDF before installing it. The
default check verifies the installed annotations and the TeX caption.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

NOTE = Path(__file__).resolve().parent
PRODUCT = NOTE.parents[1] / (
    "docs/orchestration/state/measurement-paper/5d-community-20261024/"
    "fd/with-vf/data-product/fd_data_product_vf.json"
)
PRODUCT_SHA256 = "1a37b0820017f9e515f6e46dbf4009d0a76ef8f542975654d0c61e0a015d84e8"
MATRIX = "C_total_plus_C_resp_plus_C_PL5D_plus_DeltaC_e"
LABEL = "fig:sixteen-cell-correlations"
PDF = NOTE / "figures/fived16_correlations.pdf"
CAPTION = (
    r"The reported covariance $\CrepFiveD$ correlates the sixteen cell integrals. "
    r"The heatmap shows the strict lower triangle in R00--R15 order, with correlations "
    r"printed to two decimal places on a diverging color scale centered at zero. "
    r"The diagonal entries are unity."
)
CELLS = [f"R{i:02d}" for i in range(16)]


def correlations() -> list[list[float]]:
    payload = PRODUCT.read_bytes()
    if hashlib.sha256(payload).hexdigest() != PRODUCT_SHA256:
        raise ValueError(f"Reported covariance source hash mismatch: {PRODUCT}")
    record = json.loads(payload)
    if [row["cell"] for row in record["cells"]] != CELLS or record["correlation_of"] != MATRIX:
        raise ValueError("Unexpected region order or reported covariance key")
    covariance = record["matrices"][MATRIX]
    rho = [
        [
            covariance[i][j] / (covariance[i][i] * covariance[j][j]) ** 0.5
            for j in range(len(CELLS))
        ]
        for i in range(len(CELLS))
    ]
    for i, row in enumerate(rho):
        for j, coefficient in enumerate(row):
            if not abs(coefficient - record["correlation"][i][j]) < 1e-12:
                raise ValueError(f"Recorded correlation differs at {CELLS[i]}, {CELLS[j]}")
    return rho


def checked_annotations(rho: list[list[float]]) -> list[list[str]]:
    values = (NOTE / "values_fived16.tex").read_text()
    old_values = dict(
        re.findall(r"\\@namedef\{fv@(corr-R\d\d-R\d\d)\}\{((?:\$\-\$)?\d\.\d\d)\}", values)
    )
    expected_keys = [[f"corr-{cell}-{column}" for column in CELLS[:i]] for i, cell in enumerate(CELLS)]
    tex = (NOTE / "appC_supplementary.tex").read_text()
    old_table = re.search(
        r"\\label\{tab:sixteen-cell-correlations\}(.*?)\\end\{table\}",
        tex if rf"\label{{{LABEL}}}" not in tex else "",
        re.S,
    )
    if old_table:
        old_rows = re.findall(r"^ +(?P<row>R\d\d) &(?P<cells>[^\n]+)", old_table[1], re.M)
        expected_rows = [
            (cell, keys) for cell, keys in zip(CELLS, expected_keys) if keys
        ]
        actual_rows = [
            (cell, re.findall(r"\\fvval\{(corr-R\d\d-R\d\d)\}", body))
            for cell, body in old_rows
        ]
        if actual_rows != expected_rows:
            raise ValueError("The source table does not contain the expected lower triangle")
    elif rf"\caption{{{CAPTION}}}" + "\n" + rf"  \label{{{LABEL}}}" not in tex:
        raise ValueError("The heatmap caption and label differ from the producer")

    annotations = []
    for i, row in enumerate(expected_keys):
        printed = []
        for j, key in enumerate(row):
            label = f"{rho[i][j]:.2f}"
            if old_values[key].replace("$-$", "-") != label:
                raise ValueError(f"{key}: heatmap {label} differs from the table macro {old_values[key]}")
            printed.append(label)
        annotations.append(printed)
    return annotations


def draw(rho: list[list[float]], annotations: list[list[str]], output: Path) -> None:
    import sys
    import matplotlib
    matplotlib.use("Agg")
    sys.path.insert(0, str(NOTE.parents[1]))
    import note_print_style as nps  # the style the other fived16 figures use: DejaVu Serif, Computer Modern math

    nps.apply()  # PRINT_RC, which also sets pdf.fonttype 42
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.colors import TwoSlopeNorm

    n = len(CELLS)
    data = np.ma.masked_array(rho, mask=np.triu(np.ones((n, n), dtype=bool)))
    norm = TwoSlopeNorm(vmin=-1, vcenter=0, vmax=1)
    fig, ax = plt.subplots(figsize=(7.0, 7.25))
    fig.subplots_adjust(left=0.092, right=0.98, bottom=0.12, top=0.95)
    mesh = ax.pcolormesh(data, cmap="RdBu_r", norm=norm, shading="flat", edgecolors="white", linewidth=0.3)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    positions = np.arange(n) + 0.5
    ax.set_xticks(positions, labels=CELLS, fontsize=8)
    ax.set_yticks(positions, labels=CELLS, fontsize=8)
    ax.xaxis.tick_top()
    ax.tick_params(axis="both", length=0, pad=4)
    for spine in ax.spines.values():
        spine.set_visible(False)

    for i, row in enumerate(annotations):
        for j, label in enumerate(row):
            r, g, b, _ = mesh.cmap(norm(rho[i][j]))
            lightness = 0.2126 * r + 0.7152 * g + 0.0722 * b
            ax.text(
                j + 0.5, i + 0.5, label.replace("-", "−"),
                ha="center", va="center", fontsize=8,
                color="white" if lightness < 0.46 else "#111111",
            )
    colorbar = fig.colorbar(mesh, ax=ax, orientation="horizontal", shrink=0.74, fraction=0.045, pad=0.04)
    colorbar.set_label("Correlation coefficient", fontsize=10)
    colorbar.set_ticks([-1, -0.5, 0, 0.5, 1])
    colorbar.ax.tick_params(labelsize=8)
    fig.savefig(output, bbox_inches="tight", pad_inches=0.08, metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


def check_pdf(pdf: Path, annotations: list[list[str]]) -> None:
    extracted = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
    extracted = extracted.replace("−", "-")
    actual_rows = re.findall(r"^[ \t]*(R\d\d)[ \t]+((?:-?\d\.\d\d[ \t]*)+)$", extracted, re.M)
    parsed = [(cell, re.findall(r"-?\d\.\d\d", row)) for cell, row in actual_rows]
    expected = [(cell, row) for cell, row in zip(CELLS, annotations) if row]
    if parsed != expected:
        raise ValueError(f"PDF annotations differ from the source table in {pdf}")
    print(f"CORRELATION HEATMAP :: PASS ({sum(map(len, annotations))} exact two-decimal entries)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--output", type=Path, help="render a candidate PDF, then verify its annotations")
    mode.add_argument("--check", action="store_true", help="verify the installed PDF (default)")
    args = parser.parse_args()

    rho = correlations()
    annotations = checked_annotations(rho)
    if args.output is not None:
        draw(rho, annotations, args.output)
    check_pdf(args.output or PDF, annotations)


if __name__ == "__main__":
    main()
