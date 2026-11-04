"""Recheck committed diagnosis inputs; never fit or alter an estimator.

Run from the repository root with threads capped. Only small committed JSON,
CSV and text records are read. Output contains dimensionless diagnostics.
"""

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

import numpy as np


FD = Path("docs/orchestration/state/measurement-paper/5d-community-20261024/fd")
RE2 = Path("docs/orchestration/state/2d-closeout/stageF/methods/re2")
BASELINE = "c5e42840a"


def recheck(repo: Path) -> dict:
    """Return arithmetic and geometric checks with input byte identities."""
    inputs = {}

    def read(path: Path) -> str:
        content = (repo / path).read_bytes()
        inputs[path.as_posix()] = hashlib.sha256(content).hexdigest()
        return content.decode()

    fake = json.loads(read(FD / "with-cpl/readout/fd_f0b_readout.json"))
    before_pl = json.loads(read(FD / "readout/fd_f0b_readout.json"))
    model = json.loads(read(Path("nd-unfolding/pv-ladder/readouts/cmodel_5d.json")))
    assert fake["cells"] == [f"R{i:02d}" for i in range(16)]
    assert [cell["id"] for cell in model["cells"]] == list(range(16))
    assert model["vertices"] == ["genie_mec", "nuwro", "gibuu"]
    shifts = np.asarray(model["S"], dtype=float)
    assert shifts.shape == (3, 16) and np.isfinite(shifts).all()
    cells = list(csv.DictReader(read(
        FD / "with-cpl/data-product/fd_data_product_cpl_cells.csv"
    ).splitlines()))
    assert [row["cell"] for row in cells] == fake["cells"]
    central = np.asarray([float(row["f"]) for row in cells])
    matrix_rows = list(csv.reader(read(
        FD / "with-cpl/data-product/fd_data_product_cpl_C_model_abs.csv"
    ).splitlines()))
    assert matrix_rows[0][1:] == fake["cells"]
    assert [row[0] for row in matrix_rows[1:]] == fake["cells"]
    absolute_model = np.asarray([row[1:] for row in matrix_rows[1:]], dtype=float)
    fractional_model = absolute_model / np.outer(central, central)
    np.testing.assert_allclose(shifts.T @ shifts, fractional_model, rtol=1e-10, atol=1e-15)

    bias_results = {}
    for name in ("A7_gibuu", "q3"):
        truth = next(row for row in fake["truths"] if row["name"] == name)
        older = next(row for row in before_pl["truths"] if row["name"] == name)
        bias = np.asarray(truth["bias"], dtype=float)
        pulls = np.asarray(truth["grade"]["z"], dtype=float)
        spans = {}
        for label, own in (
            ("all_vertices", None),
            ("grade_vertices", truth["own_vertex"]),
        ):
            keep = [i for i, vertex in enumerate(model["vertices"]) if vertex != own]
            _, singular, basis = np.linalg.svd(shifts[keep], full_matrices=False)
            assert singular.min() > 1e-12 * singular.max()
            coefficients = basis @ bias
            outside = bias - basis.T @ coefficients
            square_norm = float(bias @ bias)
            inside_shares = coefficients**2 / square_norm
            outside_share = float(outside @ outside / square_norm)
            assert abs(float(inside_shares.sum()) + outside_share - 1) < 1e-12
            assert np.linalg.norm(basis @ outside) < 1e-12
            spans[label] = {
                "vertices": [model["vertices"][i] for i in keep],
                "eigenvalues_descending": (singular**2).tolist(),
                "bias_square_norm_share_per_mode": inside_shares.tolist(),
                "bias_square_norm_share_outside_span": outside_share,
            }
        bias_results[name] = {
            "n_experiments": truth["n_experiments"],
            "grade_matrix": truth["grade_matrix"],
            "grade": truth["grade"],
            "sum_diagonal_z_squared": float(pulls @ pulls),
            "R02_R06_z_squared": float(pulls[2]**2 + pulls[6]**2),
            "relative_bias_by_cell": truth["bias"],
            "model_span_geometry": spans,
        }
        if "p_parallel_lt_4p5" in truth:
            bias_results[name]["eight_cells_with_PL"] = truth["p_parallel_lt_4p5"]
            bias_results[name]["eight_cells_without_PL"] = older["p_parallel_lt_4p5"]

    tension = read(RE2 / "run/partc_r2/partc-r2/receipts/figs/tension_report.txt")
    paper = read(RE2 / "run/partc_r2/partc-r2/receipts/chi2_paperonly.txt")
    producer = read(Path("2d-unfolding/compare_to_paper_fullcov.py"))
    eigen_chi2 = float(re.search(r"sum_k c_k\^2/lambda_k = ([\d.]+)", tension)[1])
    assert "ndf = n_keep" in producer
    assert "ndf = 205   chi2/ndf =   2.270" in paper
    assert round(eigen_chi2 / 205, 3) == 2.270
    assert "modes kept by pinv (rcond=1e-15) = 205" in tension
    assert "1e-12        2.270     204" in tension

    rpd = json.loads(read(FD / "receipts-rpd/run/readout/fd_rpd.json"))
    stage0 = json.loads(read(FD / "receipts-rpd/run/stage0.json"))
    assert abs(stage0["s0"] / stage0["sigma0"] - stage0["z"]) < 1e-12
    assert rpd["stage0"]["s0"] == stage0["s0"]
    assert abs(rpd["R2"]["p_flux"] * rpd["R2"]["n_partitions"]["flux"] - 1) < 1e-12
    return {
        "baseline": BASELINE,
        "method": (
            "Post hoc descriptive arithmetic and unweighted fractional-coordinate "
            "geometry; no new significance or coverage test."
        ),
        "controls": {
            "real_cell_order_and_vertex_order": "PASS",
            "S_gram_equals_committed_fractional_C_model": "PASS",
            "span_orthogonality_and_norm_conservation": "PASS",
            "paper_receipt_arithmetic_and_ndf_source": "PASS",
            "stage0_z_and_R2_partition_arithmetic": "PASS",
        },
        "A": bias_results,
        "B": {
            "recorded_eigenmode_chi2": eigen_chi2,
            "recorded_reported_bins": 205,
            "recomputed_ratio": eigen_chi2 / 205,
            "ndf_convention": "positive-diagonal bin count; not recalculated eigenvalue rank",
            "limitation": (
                "Original ROOT inversion not rerun; source text and receipt "
                "reductions checked."
            ),
        },
        "C": {
            "stage0": {key: stage0[key] for key in ("branch", "s0", "sigma0", "z")},
            "R1_outcome": rpd["R1"]["outcome"],
            "R1_classes": rpd["R1"]["classes"],
            "R2": {key: rpd["R2"][key] for key in ("outcome", "p_flux", "alpha", "beta1")},
            "N0": {key: rpd["N0"][key] for key in ("SIZE_BIAS_g", "SIZE_BIAS_t", "note")},
        },
        "inputs_sha256": inputs,
    }


def main() -> None:
    """Write the bounded recheck to the explicitly named output file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = recheck(args.repo)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
