"""Measure the frozen IBUKT nominal edge term from prepare's signal bank.

Run on one login CPU, with BLAS threads set to one and an outer
`timeout --kill-after=15 300`. No fits or scheduler calls are made.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, BinaryIO, Iterator

import numpy as np
from numpy.typing import NDArray

RUN_NAME = "ibukt-20261119-c"
PREPARE_SHA = "056b4d0d0d00df5f41d809ed1ac5da5e63089b64013dca1f01e0ed8b2d819a7b"
CONNECT_SHA = "d2c1843c4124a4257a2769fe55994347ce7729fce079f9ade05f5b9bc5110935"
BOUND_COMMIT = "d93ab9ad8be8d68fe4337d4b2edf7d730a39344e"
CONFIG_SHA = "35f344676d83b93ecdf458d8683263f869d7f66522b58950ea3db3faebaf4206"
BANK_PATH = "prepare/out/bank.npz"
IDENTITY_PATH = "prepare/out/identity.json"
SCRATCH_ROOT = Path("/pscratch")


@contextmanager
def verified_input(path: Path, expected: str) -> Iterator[BinaryIO]:
    """Read the same verified, no-atime file descriptor used for hashing."""
    if path.resolve(strict=True) != path:
        raise ValueError(f"input cannot follow symlinks: {path}")
    with os.fdopen(
        os.open(path, os.O_RDONLY | os.O_NOATIME | os.O_NOFOLLOW), "rb"
    ) as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != expected:
            raise ValueError(f"input digest differs: {path}")
        stream.seek(0)
        yield stream


def cell_indices(
    ipt: NDArray[np.int64], ipz: NDArray[np.int64], npt: int, npz: int
) -> NDArray[np.int64]:
    """Match C2's lower-inclusive, upper-exclusive flattened grid."""
    valid = (0 <= ipt) & (ipt < npt) & (0 <= ipz) & (ipz < npz)
    return np.where(valid, ipt * npz + ipz, -1)


def boundary_rows(
    coordinates: NDArray[np.float64],
    ipt: NDArray[np.int64],
    ipz: NDArray[np.int64],
    reco_cell: NDArray[np.int64],
    weights: NDArray[np.float64],
    selected: NDArray[np.int64],
    edges: tuple[NDArray[np.float64], NDArray[np.float64]],
) -> dict[str, Any]:
    """Count exact coordinates by axis-bin pair and by reported reco cell."""
    npt, npz = (len(axis) - 1 for axis in edges)
    stride = npz + 2
    bins_with_flow = (ipt + 1) * stride + (ipz + 1)
    result = {}
    for axis, name in enumerate(("pt", "pz")):
        values = coordinates[:, axis]
        maximum = float(values.max())
        records = []
        for value in sorted(set(edges[axis]) | {maximum}):
            mask = values == value
            counts = np.bincount(bins_with_flow[mask], minlength=(npt + 2) * stride)
            sums = np.bincount(
                bins_with_flow[mask], weights=weights[mask], minlength=counts.size
            )
            in_reco = mask & (reco_cell >= 0)
            reco_counts = np.bincount(reco_cell[in_reco], minlength=npt * npz)
            reco_sums = np.bincount(
                reco_cell[in_reco], weights=weights[in_reco], minlength=npt * npz
            )
            records.append(
                {
                    "value": float(value),
                    "count": int(mask.sum()),
                    "wr_sum": float(weights[mask].sum()),
                    "by_bin": [
                        [
                            int(cell // stride - 1),
                            int(cell % stride - 1),
                            int(counts[cell]),
                            float(sums[cell]),
                        ]
                        for cell in np.flatnonzero(counts)
                    ],
                    "by_reported_reco_cell": [
                        [int(cell), int(reco_counts[cell]), float(reco_sums[cell])]
                        for cell in selected[reco_counts[selected] > 0]
                    ],
                }
            )
        result[name] = {
            "maximum": maximum,
            "maximum_count": int(np.count_nonzero(values == maximum)),
            "values": records,
        }
    return result


def measure(bank: Any, cfg: dict[str, Any]) -> dict[str, Any]:
    """Build the signed-target, response-row-sum and edge decomposition."""
    gen, reco = (bank[name] for name in ("gen", "reco"))
    pt, pr, wr = (bank[name] for name in ("pt", "pr", "wr"))
    selected = bank["selected"]
    pt_edges = np.asarray(cfg["pt_edges"], dtype=float)
    pz_edges = np.asarray(cfg["pz_edges"], dtype=float)
    npt, npz = len(pt_edges) - 1, len(pz_edges) - 1
    size = npt * npz
    if (npt, npz) != (14, 16) or (
        selected.shape != (205,)
        or selected.dtype.kind not in "iu"
        or np.any(selected < 0)
        or np.any(selected >= size)
        or np.any(selected[1:] <= selected[:-1])
    ):
        raise ValueError("invalid bank reporting grid")
    rows = len(wr)
    if not (
        pt.shape == pr.shape == wr.shape == (rows,)
        and gen.shape == reco.shape == (rows, 2)
    ):
        raise ValueError("invalid bank signal shapes")
    if pt.dtype.kind != "b" or pr.dtype.kind != "b" or np.any(pr & ~pt):
        raise ValueError("invalid signal pass masks or unexpected signal fakes")
    keep = pt & pr
    gen, reco, wr = gen[keep], reco[keep], wr[keep]
    if not wr.size or not (
        np.all(np.isfinite(gen))
        and np.all(np.isfinite(reco))
        and np.all(np.isfinite(wr) & (wr >= 0))
    ):
        raise ValueError("invalid nominal sample")

    axes = (pt_edges, pz_edges)
    tipt, tipz = (
        np.searchsorted(edge, gen[:, axis], side="right") - 1
        for axis, edge in enumerate(axes)
    )
    ript, ripz = (
        np.searchsorted(edge, reco[:, axis], side="right") - 1
        for axis, edge in enumerate(axes)
    )
    truth = cell_indices(tipt, tipz, npt, npz)
    reco_cell = cell_indices(ript, ripz, npt, npz)
    rec_valid = reco_cell >= 0
    matched = rec_valid & (truth >= 0)
    leaked = rec_valid & (truth < 0)
    # The identical positive and negative background rows cancel bin by bin.
    signed = np.bincount(reco_cell[rec_valid], weights=wr[rec_valid], minlength=size)
    matrix = np.zeros((size, size))
    np.add.at(matrix, (reco_cell[matched], truth[matched]), wr[matched])
    folded = matrix.sum(axis=1)
    counts = np.bincount(reco_cell[leaked], minlength=size)
    edge = np.bincount(reco_cell[leaked], weights=wr[leaked], minlength=size)
    residual = signed - folded
    return {
        "sample": {
            "rows": int(wr.size),
            "truth_outside_reco_inside": int(leaked.sum()),
            "truth_outside_reco_inside_wr_sum": float(edge.sum()),
            "reco_outside": int((~rec_valid).sum()),
        },
        "selected_cells": [
            {
                "ipt": int(cell // npz),
                "ipz": int(cell % npz),
                "y_signed": float(signed[cell]),
                "response_row_sum": float(folded[cell]),
                "y_signed_minus_response": float(residual[cell]),
                "outside_truth_count": int(counts[cell]),
                "outside_truth_wr_sum": float(edge[cell]),
                "roundoff": float(residual[cell] - edge[cell]),
            }
            for cell in selected
        ],
        "boundary_layout": {
            "by_bin": ["ipt", "ipz", "count", "wr_sum"],
            "by_reported_reco_cell": ["cell", "count", "wr_sum"],
            "flow": {"underflow": -1, "pt_overflow": npt, "pz_overflow": npz},
            "note": "Exact equality on stored coordinates. Binning edges and stored maxima are enumerated; the driver's strict truth-angle gate excludes its boundary from this sample.",
        },
        "truth_boundaries": boundary_rows(
            gen, tipt, tipz, reco_cell, wr, selected, axes
        ),
        "reco_boundaries": boundary_rows(
            reco, ript, ripz, reco_cell, wr, selected, axes
        ),
        "refinement": {
            "y_refined_minus_y_signed": None,
            "status": "unavailable",
            "reason": "The frozen bank has signal and background inputs, not pair refinement weights. The stopped pair product holds the unfolded vectors, truth, prior and mask.",
            "required_if_authorized": "One pinned Stay-Positive LightGBM fit (400 trees, 31 leaves, CPU), followed by a histogram. Its isolated wall time was not recorded; the full stopped control job used 466 s on one node (0.1294 node-h).",
        },
    }


def run(expected_sha: str) -> dict[str, str]:
    """Verify frozen identities and write one diagnostic into a fresh scratch root."""
    script = Path(__file__).resolve(strict=True)
    with verified_input(script, expected_sha):
        pass
    if "SLURM_JOB_ID" in os.environ:
        raise ValueError("diagnostic requires a login node without a Slurm allocation")
    scratch = Path(os.environ["SCRATCH"]).resolve(strict=True)
    if (
        scratch == SCRATCH_ROOT
        or not scratch.is_dir()
        or not scratch.is_relative_to(SCRATCH_ROOT)
    ):
        raise ValueError("requires a private scratch directory on /pscratch")
    root = scratch / RUN_NAME
    with verified_input(root / "prepare/PASS.json", PREPARE_SHA) as stream:
        receipt = json.load(stream)
    if (
        receipt["status"],
        receipt["action"],
        receipt["script_sha256"],
        receipt["bound_commit"],
        receipt["run_root"],
    ) != ("PASS", "prepare", CONNECT_SHA, BOUND_COMMIT, str(root)):
        raise ValueError("prepare receipt identity differs")
    artifacts = receipt["artifacts"]
    with verified_input(root / IDENTITY_PATH, artifacts[IDENTITY_PATH]) as stream:
        identity = json.load(stream)
    if (identity["status"], identity["bank_sha256"], identity["config_sha256"]) != (
        "PASS",
        artifacts[BANK_PATH],
        CONFIG_SHA,
    ):
        raise ValueError("prepare identity operands differ")
    with verified_input(
        root / "deploy/2d-unfolding/ibukt/config.json", CONFIG_SHA
    ) as stream:
        cfg = json.load(stream)
    with verified_input(root / BANK_PATH, artifacts[BANK_PATH]) as stream:
        with np.load(stream, allow_pickle=False) as bank:
            report = measure(bank, cfg)
            report["bank_members"] = sorted(bank.files)
    report.update(
        schema="ibukt-nominal-edge-diagnosis/1",
        diagnostic_sha256=expected_sha,
        prepare_sha256=PREPARE_SHA,
        bank_sha256=artifacts[BANK_PATH],
        config_sha256=CONFIG_SHA,
    )
    os.umask(0o077)
    workspace = Path(tempfile.mkdtemp(prefix="ibukt-nominal-diagnostic-", dir=scratch))
    target = workspace / "report.json"
    payload = (json.dumps(report, indent=2, allow_nan=False) + "\n").encode()
    with target.open("xb") as stream:
        stream.write(payload)
    return {"report": str(target), "sha256": hashlib.sha256(payload).hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expect-sha256", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.expect_sha256)), flush=True)


if __name__ == "__main__":
    main()
