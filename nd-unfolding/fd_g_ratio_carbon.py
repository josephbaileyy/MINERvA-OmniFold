#!/usr/bin/env python3
"""Redraw the ratio figure with committed carbon-only analysis predictions.

Uses fd_g_figures.ratio_model and paint, the printed figure's producer. Only
NuWro and GiBUU predictions and their legend qualifiers change. No event files,
release packages, covariance construction or generator calculations are used.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

import fd_g_figures as figures

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / (
    "docs/orchestration/state/measurement-paper/5d-community-20261024/"
    "fd/gencmp/carbon-figure"
)
CARBON_NAMES = ("nuwro", "gibuu")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_inputs() -> tuple[dict, dict, dict]:
    records = json.loads((RECORD / "inputs.json").read_text())
    paths = {key: ROOT / record["path"] for key, record in records.items()}
    for key, path in paths.items():
        if _sha256(path) != records[key]["sha256"]:
            raise ValueError(f"Input digest differs: {key}")
    contents = {key: json.loads(path.read_text()) for key, path in paths.items()}
    definitions = contents["carbon_definitions"]
    if definitions["rebuild_json_sha256"] != records["rebuild"]["sha256"]:
        raise ValueError("Carbon definitions do not reference the committed rebuild")
    pins = {key: records[key]["sha256"] for key in figures.INPUTS}
    readouts = figures.load(SimpleNamespace(**paths), pins)
    figures.check_chain(
        readouts, pins, name="C_resp + C_PL5D", predictions=contents["predictions"]
    )
    assembly = contents["assembly"]
    if any(
        readouts[key]["inputs_sha256"]["s1_npz"] != assembly["assembly_sha256"]
        for key in figures.INPUTS[:5]
    ):
        raise ValueError("Readouts do not reference the same estimator assembly")
    if assembly["meta"]["code_sha256"]["s1_assemble.py"] != _sha256(
        ROOT / "nd-unfolding/s1_assemble.py"
    ):
        raise ValueError("Estimator-validation code differs from the assembly record")
    return records, contents, readouts


def _check_carbon(model: dict, readouts: dict, definitions: dict) -> None:
    plotted = figures.by_gid(model)
    predictions = {
        prediction["name"]: prediction
        for prediction in readouts["g_readout"]["predictions"]
    }
    for name in CARBON_NAMES:
        source = definitions["generators"][name]["carbon"]
        source = source["analysis_definitions"]["chi2"]["reported"]
        ratio = np.array(source["f"]) / source["g"]
        error = ratio * predictions[name]["sigma_total_over_f"]
        for field, expected, gid in (
            ("y", ratio, f"ratio:{name}"),
            ("lo", ratio - error, f"ratio:{name}:err"),
            ("hi", ratio + error, f"ratio:{name}:err"),
        ):
            if not np.array_equal(plotted[gid][field], expected):
                raise ValueError(f"Carbon ratio or error differs: {gid}.{field}")
        legend = plotted[f"ratio:{name}:legend"]["text"]
        if "carbon only" not in legend or ": CH" in legend:
            raise ValueError(f"Carbon legend differs: {name}")


def main(argv: list[str] | None = None) -> int:
    """Render and verify the carbon-only ratio figure from pinned readouts.

    Parameters
    ----------
    argv : list[str] or None
        Command-line arguments; ``--out-dir`` must name a new directory.

    Returns
    -------
    int
        Zero after all provenance, array, layout and rendering checks pass.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.out_dir.exists():
        raise FileExistsError(args.out_dir)
    records, contents, readouts = _load_inputs()
    figures.use_prediction_set("gencmp-chdefs")
    figures.MF.style()
    parent = contents["parent_model"]
    parent_model = figures.ratio_model(
        readouts, "data-over-prediction", "separate", "C_resp + C_PL5D"
    )
    if parent_model != parent["plotted"]:
        raise ValueError("Producer does not exactly reproduce the printed parent model")
    parent_pdf = ROOT / records["parent_model"]["path"]
    if _sha256(parent_pdf.with_suffix(".pdf")) != parent["pdf_sha256"]:
        raise ValueError("Parent sidecar does not describe the committed PDF")
    model = figures.ratio_model(
        readouts, "data-over-prediction", "separate", "C_resp + C_PL5D",
        carbon=contents["carbon_definitions"],
    )
    # Keep the printed geometry and limits; readback also refuses clipped points.
    model["axes"] = deepcopy(parent_model["axes"])
    before, after = figures.by_gid(parent_model), figures.by_gid(model)
    changed = {
        f"ratio:{name}{suffix}"
        for name in CARBON_NAMES
        for suffix in ("", ":err", ":legend")
    }
    if set(before) != set(after):
        raise ValueError("Figure items differ from the printed parent")
    for gid in before.keys() - changed:
        if before[gid] != after[gid]:
            raise ValueError(f"Unchanged item differs: {gid}")
    for key in parent_model.keys() - {"items"}:
        if parent_model[key] != model[key]:
            raise ValueError(f"Figure layout differs: {key}")
    _check_carbon(model, readouts, contents["carbon_definitions"])
    figures.check_gibuu(model)
    figures.check_panels(model)
    figure = figures.paint(model)
    figures.readback(figure, model)
    pdf = figures.render(figure)
    figures.plt.close(figure)
    repeated = figures.paint(model)
    figures.check_pdf("ratio-carbon", pdf, figures.render(repeated))
    figures.plt.close(repeated)
    sidecar = {
        "schema": "fd-g-carbon-figure/1",
        "file": "fd_g_fig_ratio.pdf",
        "pdf_sha256": hashlib.sha256(pdf).hexdigest(),
        "inputs": records,
        "code_sha256": {
            path.name: _sha256(path)
            for path in (
                Path(__file__), Path(figures.__file__),
                Path(figures.MF.__file__), ROOT / "nd-unfolding/s1_assemble.py",
            )
        },
        "checks": {
            "parent_model_reproduced_exactly": True,
            "unchanged_items_equal_parent": sorted(before.keys() - changed),
            "carbon_ratios_and_error_endpoints_exact": True,
            "width_fonts_geometry_limits_unchanged": True,
            "artist_readback_and_no_overlaps": True,
            "repeat_render_identical": True,
        },
        "plotted": model,
    }
    args.out_dir.mkdir(parents=True)
    (args.out_dir / sidecar["file"]).write_bytes(pdf)
    (args.out_dir / "fd_g_fig_ratio.json").write_text(
        json.dumps(sidecar, indent=2, allow_nan=False) + "\n"
    )
    print(f"Carbon-only ratio: {sidecar['pdf_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
