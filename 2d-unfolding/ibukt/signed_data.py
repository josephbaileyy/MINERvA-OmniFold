"""Compare signed and archived refined real-data IBU on the REF-C2C1 basis."""

from __future__ import annotations

import argparse
import importlib
import os
from pathlib import Path
import sys
from typing import Any, cast
from unittest import mock

import numpy as np
from numpy.typing import NDArray

import ibukt as core
import run_ibukt as runner

KS = (5, 10)
REFERENCE_COMMIT = "77d76cfc2d621f8faa010b75006811868494652a"
REFERENCE_DRIVER = "938c53c5a018d20f5b148f6bdc2949e987a60085c5d0b7913ccdd5bb438b5a3b"
FAILED_CELLS = [*(16 * ipt + 15 for ipt in range(12)), 8 * 16, 9 * 16 + 1]


def _signed_histogram(path: Path) -> tuple[core.Array, list[dict[str, int | float]]]:
    import ROOT

    with ROOT.TFile.Open(str(path), "READ") as source:
        histograms = [
            source.Get(name) for name in ("hMeasSub2D", "hDataReco2D", "hBkgReco2D")
        ]
        if any(
            not hist or (hist.GetNbinsX(), hist.GetNbinsY()) != (14, 16)
            for hist in histograms
        ):
            raise ValueError("missing or misaligned E_R reco histogram")
        signed, data, background = (
            np.array([[h.GetBinContent(i, j) for j in range(18)] for i in range(16)])
            for h in histograms
        )
    if not np.array_equal(signed, data - background):
        raise ValueError("E_R signed histogram differs from data minus background")
    flow = [
        {
            "pt_root_bin": int(i),
            "pz_root_bin": int(j),
            "signed_count": float(signed[i, j]),
        }
        for i, j in np.ndindex(signed.shape)
        if i in (0, 15) or j in (0, 17)
    ]
    return signed[1:-1, 1:-1].reshape(-1), flow


def _publication(
    path: Path, cp: Any
) -> tuple[core.Array, core.Array, NDArray[np.intp]]:
    import ROOT

    with ROOT.TFile.Open(str(path), "READ") as source:
        published = cp.flatten_th2d(source.Get("pt_pl_cross_section"))
        covariance = cp.tmatrix_to_numpy(source.Get("TotalCovariance"))
        stat = cp.tmatrix_to_numpy(source.Get("StatOnlyCovariance"))
    if any(
        x.shape != (224, 224) or not np.all(np.isfinite(x)) for x in (covariance, stat)
    ):
        raise ValueError("invalid published covariance")
    mask = np.diag(stat) > 0
    if mask.sum() != 205 or not np.array_equal(mask, np.diag(covariance) > 0):
        raise ValueError("published statistical and total covariance masks differ")
    return published, covariance, np.flatnonzero(mask)


def _readings(
    cp: Any,
    covariance: core.Array,
    published: core.Array,
    er: core.Array,
    selected: NDArray[np.intp],
    refined: dict[int, core.Array],
    signed: dict[int, core.Array],
) -> dict[str, Any]:
    def distance(delta: core.Array) -> dict[str, int | float]:
        chi2, ndf, _ = cp.chi2_with_cov(delta, covariance, "", report=False)
        if ndf != len(selected) or not np.isfinite(chi2):
            raise ValueError("invalid publication distance")
        return {"chi2": chi2, "ndf": ndf, "chi2_ndf": chi2 / ndf}

    er_distance = distance(er - published)
    if not np.isclose(er_distance["chi2"], 465.41527219152636, rtol=1e-8, atol=0):
        raise ValueError("E_R publication distance differs")
    if not set(FAILED_CELLS).issubset(selected):
        raise ValueError("historical control cells are outside the reporting mask")
    readings: dict[str, Any] = {"E_R": er_distance}
    for k, expected in zip(KS, (0.83, 1.03), strict=True):
        signed_distance = distance(signed[k] - published)
        refined_distance = distance(refined[k] - published)
        if round(refined_distance["chi2_ndf"], 2) != expected:
            raise ValueError(f"REF-C2C1 K={k} publication distance differs")
        shift = signed[k] - refined[k]
        subset = shift[FAILED_CELLS]
        largest = int(np.argmax(np.abs(subset)))
        readings[str(k)] = {
            "signed_vs_publication": signed_distance,
            "refined_vs_publication": refined_distance,
            "signed_minus_refined_chi2_ndf": signed_distance["chi2_ndf"]
            - refined_distance["chi2_ndf"],
            "er_vs_signed": distance(er - signed[k]),
            "er_vs_refined": distance(er - refined[k]),
            "signed_minus_refined": shift[selected].tolist(),
            "er_minus_signed": (er - signed[k])[selected].tolist(),
            "er_minus_refined": (er - refined[k])[selected].tolist(),
            "historical_control_cells": {
                "indices": FAILED_CELLS,
                "shifts": subset.tolist(),
                "median": float(np.median(subset)),
                "max_absolute": float(abs(subset[largest])),
                "max_index": FAILED_CELLS[largest],
            },
        }
    return readings


def run(stage: Path, out: Path, reference: Path, cfg: dict[str, Any]) -> None:
    """Use checked staged copies and the exact historical driver without fitting."""
    pins = cfg["inputs"]
    for pin in pins.values():
        if runner.digest(stage / pin["filename"]) != pin["sha256"]:
            raise ValueError(f"staged input changed: {pin['filename']}")
    comparison = importlib.import_module("ref_c2c1")
    helper_path = "unbinned_unfolding/python/omnifold.py"
    driver_path = reference / "2d-unfolding/re2/re2_driver.py"
    assert comparison.__file__ is not None
    for path, expected in (
        (driver_path, REFERENCE_DRIVER),
        (reference / helper_path, cfg["code_sha256"][helper_path]),
        (
            Path(comparison.__file__),
            cfg["code_sha256"]["2d-unfolding/ref_c2c1/ref_c2c1.py"],
        ),
    ):
        if runner.digest(path) != expected:
            raise ValueError(f"REF-C2C1 implementation changed: {path.name}")
    with mock.patch.multiple(
        comparison, RE2=driver_path, HELPER=(reference / helper_path).parent
    ):
        driver, helper = comparison.load_driver()
    cp = importlib.import_module("compare_to_paper_fullcov")
    expected_cp = cfg["code_sha256"]["2d-unfolding/compare_to_paper_fullcov.py"]
    assert cp.__file__ is not None
    if runner.digest(Path(cp.__file__)) != expected_cp:
        raise ValueError("publication comparison implementation changed")
    if driver.PT_EDGES != cfg["pt_edges"] or driver.PZ_EDGES != cfg["pz_edges"]:
        raise ValueError("REF-C2C1 grid changed")
    with comparison.read_guards(
        (Path("/pscratch"), Path("/global/cfs")),
        (stage, out, reference, runner.REPO),
        (out,),
    ):
        _measure(stage, out, cfg, comparison, driver, helper, cp)


def _measure(
    stage: Path,
    out: Path,
    cfg: dict[str, Any],
    comparison: Any,
    driver: Any,
    helper: Any,
    cp: Any,
) -> None:
    target, flow = _signed_histogram(stage / "er.root")
    published, cov, selected = _publication(stage / "paper.root", cp)
    archived = runner.read_npz(stage / "c2.npz")
    library = str(stage / "libRooUnfold.so")
    checks = {}

    def archived_unfold(
        matrix: core.Array, prior: core.Array, _target: core.Array, ks: list[int]
    ) -> dict[int, core.Array]:
        checks["archived_prior"] = runner.require_close(
            prior, archived["T"], "archived prior"
        )
        return cast(
            dict[int, core.Array],
            comparison.roounfold_bayes(matrix, prior, archived["y"], ks, library),
        )

    def pass_signed(
        _rows: core.Array, weights: core.Array, **_kwargs: Any
    ) -> tuple[core.Array, None, float]:
        return weights, None, 0.0

    with mock.patch.object(driver, "refine_stay_positive", pass_signed):
        capture = comparison.run_driver(
            driver,
            helper,
            [
                "--omnifile",
                str(stage / "cv.root"),
                "--mcfile",
                str(stage / "flux.root"),
                *cfg["argv"],
            ],
            out / "historical_identity.root",
            ibu={"unfolder": archived_unfold, "ks": list(KS), "primary": 5},
            staging=stage,
        )
    response, prior = capture["M"], capture["T"]
    refined = comparison.xsec_at_every_k(driver, capture, KS)
    for k in KS:
        checks[f"archived_K{k}"] = runner.require_close(
            refined[k][selected],
            archived["xsec"][list(archived["ks"]).index(k)][selected],
            f"archived K={k}",
        )
    failed = core.signed_target_violations(target, response.sum(axis=1))
    unsupported_truth = selected[
        (prior[selected] <= 0) | (response.sum(axis=0)[selected] <= 0)
    ]
    if failed or unsupported_truth.size:
        runner.write_json(
            out / "STOP.json",
            {
                "status": "STOP",
                "reason": "inadmissible real-data target",
                "reco_bins": failed,
                "truth_indices": unsupported_truth.tolist(),
                "flow": flow,
                "checks": checks,
            },
        )
        raise ValueError("inadmissible signed data target or truth support")
    capture["traj"] = comparison.roounfold_bayes(
        response, prior, target, list(KS), library
    )
    signed = comparison.xsec_at_every_k(driver, capture, KS)
    capture["traj"] = comparison.dagostini(response, prior, target, KS)
    numpy_signed = comparison.xsec_at_every_k(driver, capture, KS)
    for k in KS:
        checks[f"agreement_K{k}"] = runner.require_close(
            signed[k][selected],
            numpy_signed[k][selected],
            f"signed RooUnfold/NumPy K={k}",
            1e-9,
        )
    er = runner.root_vector(stage / "er.root", "hXSec2D", comparison)
    readings = _readings(cp, cov, published, er, selected, refined, signed)
    output = out / "signed_data.npz"
    np.savez(
        output,
        signed_y=target,
        refined_y=archived["y"],
        response=response,
        prior=prior,
        cells=selected,
        er=er,
        ks=KS,
        signed_xsec=[signed[k] for k in KS],
        refined_xsec=[refined[k] for k in KS],
    )
    runner.write_json(
        out / "readout.json",
        {
            "status": "PASS",
            "checks": checks,
            "flow": flow,
            "cells": selected.tolist(),
            "input_sha256": {
                role: pin["sha256"] for role, pin in cfg["inputs"].items()
            },
            "reference_commit": REFERENCE_COMMIT,
            "driver_sha256": REFERENCE_DRIVER,
            "script_sha256": runner.digest(Path(__file__)),
            "config_sha256": runner.digest(core.CONFIG),
            "python_version": sys.version,
            "root_version": importlib.import_module("ROOT").gROOT.GetVersion(),
            "numpy_version": np.__version__,
            "product_sha256": runner.digest(output),
            "distances": readings,
        },
    )


def main() -> None:
    """Run the study from a guarded CPU login-node session with fresh output."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--reference", required=True, type=Path)
    args = parser.parse_args()
    stage, out, reference = (
        path.resolve() for path in (args.stage, args.out, args.reference)
    )
    if not all(
        path.is_relative_to(Path("/pscratch")) for path in (stage, out, reference)
    ):
        parser.error("all study paths must be on pscratch")
    if os.environ.get("SLURM_JOB_ID"):
        parser.error("the declared login study uses zero allocated node-hours")
    out.mkdir(mode=0o700, parents=False, exist_ok=False)

    sys.path.insert(0, str(runner.REPO / "2d-unfolding"))
    sys.path.insert(0, str(runner.REPO / "2d-unfolding/ref_c2c1"))
    try:
        run(stage, out, reference, core.configuration())
    except Exception as exc:
        if not (out / "STOP.json").exists():
            runner.write_json(out / "STOP.json", {"status": "STOP", "reason": str(exc)})
        raise


if __name__ == "__main__":
    main()
