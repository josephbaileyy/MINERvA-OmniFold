#!/usr/bin/env python3
"""Run-lane-only check on the pinned, non-input real MnvH1D object.

This command neither reads declared RPD dumps nor runs the diagnostic campaign.
It must run in the existing pinned MAT environment. A plain TH1 cannot pass.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND))
import fd_rpd_reco as r  # noqa: E402

PROBE_SHA256 = "d9704aa45c016b044284d9e3cfc8c6d5c07cda0835a445866d5f792c8ac82840"


def check(probe: Path, run: Path) -> dict[str, Any]:
    """Compare the production evaluator with ROOT at interpolation and zero cases."""
    r.require_output_root(run)
    root, environment = r.checked_mat_environment()
    staged = r.stage_copy(probe, run / "non-input-probe.root", PROBE_SHA256)
    spectrum = r.read_flux_histogram(staged, "flux_E_cvweighted", root=root)
    with r.guarded_tfile(root, [staged]):
        file = root.TFile.Open(str(staged), "READ")
        try:
            original = file.Get("flux_E_cvweighted")
            clones = [
                original.Clone(f"rpd_probe_{name}")
                for name in ("own", "target", "generated")
            ]
            for histogram in clones:
                histogram.SetDirectory(0)
        finally:
            file.Close()
    own, target, generated = clones
    r.require(
        all(hist.InheritsFrom("PlotUtils::MnvH1D") for hist in clones),
        "MAT_MNVH1D",
        "clone lost real class",
    )
    for i in range(own.GetNbinsX() + 2):
        own.SetBinContent(i, 2 + i / 10)
        target.SetBinContent(i, 7 + i / 5)
        generated.SetBinContent(i, 3 + i / 20)
    axis = own.GetXaxis()
    low, high = float(axis.GetXmin()), float(axis.GetXmax())
    r.require(
        low < 74.999 and high > 75.001,
        "FLUX_LAYOUT",
        "probe does not cover the 75 GeV boundary",
    )
    # Pick an off-center point explicitly; the expected value calls real ROOT.
    index = max(2, min(own.GetNbinsX() - 1, int(own.FindBin(20.0))))
    off_center = float(axis.GetBinLowEdge(index)) + 0.31 * float(
        axis.GetBinWidth(index)
    )
    energies = np.array([off_center, 74.999, 75.0, 75.001])
    factors, outside, patterns = r.mat_flux_swap(energies, own, target, generated)
    expected = []
    for energy in energies:
        values = [
            (
                float(hist.GetBinContent(hist.FindBin(float(energy))))
                if energy > 75.0
                else float(hist.Interpolate(float(energy)))
            )
            for hist in clones
        ]
        n_own, n_target, denominator = values
        w_own = 1.0 if n_own == 0 or denominator == 0 else n_own / denominator
        w_target = 1.0 if n_target == 0 or denominator == 0 else n_target / denominator
        expected.append(w_target / w_own)
    np.testing.assert_allclose(factors, expected, rtol=1e-12, atol=0)
    step = target.GetBinContent(target.FindBin(off_center)) / own.GetBinContent(
        own.FindBin(off_center)
    )
    r.require(
        abs(float(factors[0]) - step) > 1e-12,
        "FLUX_SUPPORT",
        "probe does not discriminate interpolation",
    )
    zero_results = []
    for pattern in range(8):
        values = [
            0.0 if pattern & (1 << i) else value
            for i, value in enumerate((2.0, 6.0, 4.0))
        ]
        for histogram, value in zip(clones, values):
            for i in range(histogram.GetNbinsX() + 2):
                histogram.SetBinContent(i, value)
        measured, _, codes = r.mat_flux_swap(energies, own, target, generated)
        w_own = 1.0 if values[0] == 0 or values[2] == 0 else values[0] / values[2]
        w_target = 1.0 if values[1] == 0 or values[2] == 0 else values[1] / values[2]
        np.testing.assert_allclose(measured, w_target / w_own, rtol=1e-12, atol=0)
        np.testing.assert_array_equal(codes, np.full(len(energies), pattern))
        zero_results.append({"pattern": pattern, "factor": measured.tolist()})
    return {
        "schema": "fd-rpd-reco-real-mnv-check/1",
        "status": "PASS",
        "scope": "non-input real-class fixture; no campaign input or P0 permission",
        "probe_sha256": PROBE_SHA256,
        "code_sha256": r.digest(Path(r.__file__)),
        "class_name": spectrum["class_name"],
        "environment": environment,
        "energy": energies.tolist(),
        "factors": factors.tolist(),
        "expected": expected,
        "outside": outside.tolist(),
        "patterns": patterns.tolist(),
        "zero_results": zero_results,
    }


def main() -> int:
    """Write a PASS receipt only when all real-class checks succeed."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = check(args.probe, args.run)
        r.write_json(args.run / "real-mnv-check.json", result)
    except (r.Refused, OSError, ValueError, AssertionError, ImportError) as error:
        print(f"STOP REAL_MNV_CHECK: {error}", file=sys.stderr)
        return 4
    print(json.dumps({"status": result["status"], "class_name": result["class_name"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
