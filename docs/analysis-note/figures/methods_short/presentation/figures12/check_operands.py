#!/usr/bin/env python3
"""Audit fetched Figure 1/2 operands against the committed printed assets.

This reads local files only, never draws a figure, and never contacts the cluster.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[6]
OUT = Path(__file__).resolve().parent
RESTYLE = ROOT / "docs/orchestration/state/2d-closeout/stageF/methods/fig-restyle-20261031"


def sha(path: Path) -> str:
    """Return the exact byte identity of a local file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    """Verify fetched bytes, then record why the printed figures cannot be redrawn."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operands", type=Path, default=Path("/private/tmp/minerva-figs12-operands"))
    args = parser.parse_args()
    manifest = json.loads((ROOT / "publication/release/figs/_data/fig_arrays.npz.manifest.json").read_text())
    wanted = {"fig_arrays.npz": manifest["npz_sha256"]}
    for key in ("ours_2d", "paper_cov", "tune_v1_txt"):
        source = manifest["sources"][key]
        wanted[Path(source["path"]).name] = source["sha256"]
    pins = {}
    for name, expected in wanted.items():
        path = args.operands / name
        actual = sha(path)
        if actual != expected:
            raise ValueError(f"Fetched operand differs: {name}")
        pins[str(path)] = actual
    (OUT / "inputs.json").write_text(json.dumps(pins, indent=2) + "\n")

    fig1 = ROOT / "docs/analysis-note/figures/paper_fig1_validation.pdf"
    printed = subprocess.run(["pdftotext", str(fig1), "-"], check=True, capture_output=True, text=True).stdout
    match = re.search(r"mean\s*=\s*([+-]?\d+\.\d+),?\s*RMS\s*=\s*(\d+\.\d+)", printed)
    if not match:
        raise ValueError("Printed Figure 1 summary cannot be read")
    with np.load(args.operands / "fig_arrays.npz", allow_pickle=False) as arrays:
        mask = arrays["mask_reported"].astype(bool)
        sigma = np.sqrt(np.diag(arrays["cov_total"])[mask])
        pull = (arrays["ours_v"][mask] - arrays["paper_v"][mask]) / sigma
        computed = {"mean": float(pull.mean()), "sd": float(pull.std()), "bins": int(mask.sum())}
        own_covariance_present = "cov_ours" in arrays.files
    printed_summary = {"mean": match[1], "sd": match[2]}
    matches = all(f"{computed[key]:.3f}" == printed_summary[key] for key in ("mean", "sd"))
    if matches:
        raise ValueError("Figure 1 identity finding has changed; reassess before proceeding")

    inputs = (RESTYLE / "run-a2/after/logs/inputs.sha256").read_text().splitlines()
    required_sha, required_path = next(line.split(None, 1) for line in inputs if line.endswith("/ER/xsec.root"))
    digest_rows = [line.split("\t") for line in (RESTYLE / "DIGESTS.tsv").read_text().splitlines()]
    installed_sha = next(row[4] for row in digest_rows if row[0] == "tension_chi2_map.pdf")
    fig2 = ROOT / "docs/analysis-note/figures/tension_chi2_map.pdf"
    assert sha(fig2) == installed_sha
    fetched_sha = pins[str(args.operands / "2d_crossSection_omnifold_MEFHC_5iter.root")]
    if fetched_sha == required_sha:
        raise ValueError("Figure 2 identity finding has changed; reassess before proceeding")
    report = {
        "figure1": {"status": "STOP: base archive does not reproduce printed figure",
                    "printed_pdf_sha256": sha(fig1), "printed_summary": printed_summary,
                    "base_archive_summary": computed, "base_archive_has_cov_ours": own_covariance_present,
                    "required_entry_point": "2d-unfolding/re2/partc/re2c_fig1.py --arm refined"},
        "figure2": {"status": "STOP: fetched estimator differs from printed asset producer input",
                    "printed_pdf_sha256": installed_sha, "required_ours_path": required_path,
                    "required_ours_sha256": required_sha, "fetched_ours_sha256": fetched_sha},
    }
    (OUT / "identity-check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
