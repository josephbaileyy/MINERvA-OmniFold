#!/usr/bin/env python3
"""Freeze existing scalar-5D products as cell integrals; never run an unfold.

Use --raw-root with the logical s5e/ and s5p/{conv,num,prior}/ cache layout,
--remote-hashes with an independently read remote SHA-256 inventory, and --out.
The reducer imports no production module. Definitions are bound to source hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def _read(path: Path) -> Any:
    return json.loads(path.read_text())


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, record: Any) -> None:
    path.write_text(json.dumps(record, indent=2, allow_nan=False) + "\n")


class Projection:
    """Integrate differential cross sections on aligned, fixed reporting cells.

    Parameters
    ----------
    definition : dict
        Fine and reporting edges, supported J cells and reporting flags.
    """

    def __init__(self, definition: dict[str, Any]) -> None:
        self.axes = list(definition["fine"])
        fine = [np.asarray(definition["fine"][axis]) for axis in self.axes]
        self.shape = tuple(len(edge) - 1 for edge in fine)
        widths = np.meshgrid(*(np.diff(edge) for edge in fine), indexing="ij")
        self.volume = np.prod(widths, axis=0).ravel()
        indices = np.indices(self.shape).reshape(5, -1)
        self.cells = {"EW": indices[2] * self.shape[4] + indices[4]}
        self.counts = {"EW": self.shape[2] * self.shape[4]}
        self.keep = {"EW": np.arange(self.counts["EW"])}
        self.slices: dict[str, list[tuple[slice, ...]]] = {}
        for name in ("J", "H2"):
            edges = [np.asarray(definition["partitions"][name][a]) for a in self.axes]
            boundary = []
            coarse_indices = []
            for axis, (small, big) in enumerate(zip(fine, edges, strict=True)):
                if big[0] != small[0] or big[-1] != small[-1]:
                    raise ValueError("Reporting domain must equal the fine domain")
                positions = np.searchsorted(small, big)
                if not np.array_equal(small[positions], big):
                    raise ValueError("Reporting edge cuts a fine bin")
                boundary.append(positions)
                coarse_indices.append(
                    np.searchsorted(positions[1:], indices[axis], side="right")
                )
            shape = tuple(len(e) - 1 for e in edges)
            self.cells[name] = np.ravel_multi_index(coarse_indices, shape)
            self.counts[name] = int(np.prod(shape))
            self.keep[name] = (
                np.asarray(definition["supported_J"])
                if name == "J"
                else np.arange(self.counts[name])
            )
            self.slices[name] = [
                tuple(
                    slice(boundary[a][i], boundary[a][i + 1])
                    for a, i in enumerate(coord)
                )
                for coord in np.ndindex(shape)
            ]
        self.names = (
            [f"EW{i}" for i in self.keep["EW"]]
            + [f"J{i}" for i in self.keep["J"]]
            + [f"H2_{i}" for i in self.keep["H2"]]
        )
        self.groups = np.asarray(["EW"] * 42 + ["J"] * 109 + ["H2"] * 32)
        self.reported = np.concatenate(
            [definition["reported"][p] for p in ("EW", "J", "H2")]
        ).astype(bool)
        self.ew_area = np.outer(np.diff(fine[2]), np.diff(fine[4])).ravel()

    def integrate(self, density: FloatArray, *, crosscheck: bool = False) -> FloatArray:
        """Return cell integrals, checking rate conservation and optionally slices.

        Parameters
        ----------
        density : ndarray
            C-order density over the full fine grid.
        crosscheck : bool
            Also integrate tensor slices, independently of the index map.

        Returns
        -------
        ndarray
            EW, supported J and all H2 integrals in cm²/nucleon.
        """
        if (
            density.shape != (int(np.prod(self.shape)),)
            or not np.isfinite(density).all()
        ):
            raise ValueError("Invalid fine-grid operand")
        weighted = density * self.volume
        output = []
        for name in ("EW", "J", "H2"):
            integrated = np.bincount(
                self.cells[name], weights=weighted, minlength=self.counts[name]
            )
            np.testing.assert_allclose(
                integrated.sum(), weighted.sum(), rtol=2e-13, atol=0
            )
            if crosscheck:
                cube = weighted.reshape(self.shape)
                alternative = (
                    cube.sum(axis=(0, 1, 3)).ravel()
                    if name == "EW"
                    else np.array([cube[s].sum() for s in self.slices[name]])
                )
                np.testing.assert_allclose(
                    integrated, alternative, rtol=2e-13, atol=1e-55
                )
            output.append(integrated[self.keep[name]])
        return np.concatenate(output)


def _metadata(meta: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "schema",
        "construction",
        "truth",
        "amplitude",
        "pseudo_seed",
        "split_key",
        "fixed_split_seed",
        "bootstrap_seed",
        "jitter_seed",
        "jitter_f32",
        "coords",
        "estimator_seed",
        "iters",
        "capacity",
        "config",
        "bkg_mode",
        "no_background",
        "missed",
        "input_npz_sha256",
        "bkg_dump_sha256",
        "ratio_sha256",
        "eavail_ratio_sha256",
        "ratio_nd_sha256",
        "ratio_file",
        "prior",
        "code_sha256",
        "estimator_params",
        "seconds_load",
        "seconds_build",
        "seconds_unfold",
        "threads",
        "slurm_job",
    )
    record = {key: meta.get(key) for key in keys}
    record["refinement"] = {
        key: meta.get("refinement", {}).get(key)
        for key in ("ran", "reason", "classifier_params")
    }
    record["producer_commit"] = meta.get("git_head")
    record["nuisance_construction"] = (
        "no physical systematic draws; see source schema/contract for event and MC resampling"
    )
    record["units"] = "projected cell integral: cm2/nucleon"
    return record


def _freeze(raw: Path, remote: dict[str, Any], out: Path) -> None:
    definition = _read(PACKAGE / "definition.json")
    for path, expected in definition["source_sha256"].items():
        if _sha(ROOT / path) != expected:
            raise ValueError(f"Source identity mismatch: {path}")
    projection = Projection(definition)
    receipt = _read(ROOT / "docs/orchestration/state/s5p/stage2/stage2_receipt.json")
    envelope = _read(ROOT / "docs/orchestration/state/s5p/stage3/envelope-receipt.json")
    archive: dict[str, Any] = {
        "names": np.asarray(projection.names),
        "groups": projection.groups,
        "reported": projection.reported,
    }
    inventory: list[dict[str, Any]] = []
    selected: set[str] = set()
    stage1 = _read(ROOT / "docs/orchestration/state/s5p/stage1/stage1_inspect.json")
    reviewed = _read(
        ROOT / "docs/orchestration/state/s5e/cand/review2/r2_integrity.json"
    )
    review_by_path = {"s5e/" + row["key"] + ".npz": row for row in reviewed["rows"]}

    def load(relative: str, role: str) -> tuple[Any, dict[str, Any]]:
        path = raw / relative
        identity = _sha(path)
        if identity != remote["files"][relative]["sha256"]:
            raise ValueError(f"Copy differs from remote: {relative}")
        selected.add(relative)
        product = np.load(path, allow_pickle=False)
        meta = json.loads(str(product["meta"])) if "meta" in product else {}
        if meta:
            if meta.get("input_npz_sha256") != stage1["inputs"]["npz_sha256"]:
                raise ValueError(f"Input identity mismatch: {relative}")
            if meta.get("bkg_dump_sha256") != stage1["inputs"]["bkg_sha256"]:
                raise ValueError(f"Background identity mismatch: {relative}")
        if relative in review_by_path:
            original = review_by_path[relative]
            for field in (
                "truth",
                "amplitude",
                "pseudo_seed",
                "bootstrap_seed",
                "iters",
            ):
                if meta.get(field) != original.get(field):
                    raise ValueError(f"Reviewed metadata mismatch: {relative}: {field}")
            if meta.get("eavail_ratio_sha256") != original["ratio_sha"]:
                raise ValueError(f"Truth identity mismatch: {relative}")
        inventory.append(
            {
                "path": relative,
                "sha256": identity,
                "bytes": path.stat().st_size,
                "role": role,
                "completion": (
                    "partial checkpoint, metadata absent"
                    if ".partial." in relative
                    else "complete product"
                ),
                "metadata": _metadata(meta),
            }
        )
        return product, meta

    def stack(key: str, paths: list[str], role: str, *, truth: bool = False) -> None:
        estimates, truths, seeds = [], [], []
        for index, relative in enumerate(paths):
            product, meta = load(relative, role)
            if meta.get("iters") != 5 or meta.get("estimator_seed") != 42:
                raise ValueError(f"Unexpected estimator setting: {relative}")
            for params in meta.get("estimator_params", []):
                if (params["n_estimators"], params["num_leaves"]) != (100, 8):
                    raise ValueError("Classifier capacity mismatch")
            params = meta.get("refinement", {}).get("classifier_params", {})
            if params and (params["n_estimators"], params["num_leaves"]) != (400, 31):
                raise ValueError("Refinement capacity mismatch")
            estimates.append(
                projection.integrate(product["xsec_flat"], crosscheck=index == 0)
            )
            seeds.append(
                [
                    meta.get(k, -1) if meta.get(k) is not None else -1
                    for k in ("pseudo_seed", "bootstrap_seed", "jitter_seed")
                ]
            )
            if truth:
                truths.append(
                    projection.integrate(product["xtrue_flat"], crosscheck=index == 0)
                )
        archive[key] = np.asarray(estimates)
        archive[key + "_seeds"] = np.asarray(seeds)
        if truth:
            if len({int(s[0]) for s in seeds}) != len(seeds):
                raise ValueError("Repeated pseudo seed within ensemble")
            archive[key + "_truth"] = np.asarray(truths)

    for point, (start, count, stem) in {
        "nominal": (800000, 40, "nominal_a0"),
        "eavail_gibuu": (801000, 20, "eavail_shape_a1"),
        "q3": (802000, 20, "q3_given_eavail_w_a0.3"),
        "W1": (803000, 20, "eavail_shape_a1"),
        "W2": (804000, 20, "ratio_nd_a1"),
        "W3": (805000, 20, "ratio_nd_a1"),
    }.items():
        stack(
            "assessment_" + point,
            [
                f"s5e/assess/{point}/{stem}_s{s}.npz"
                for s in range(start, start + count)
            ],
            "assessment reused as development; no pooling across truths",
            truth=True,
        )
    stack(
        "sigma",
        [f"s5e/dev/sigma/boot_b{b}.npz" for b in range(1, 101)],
        "fixed historical interval width at pseudo seed 700000",
    )
    stack(
        "data_boot",
        [f"s5e/assess/data/boot/boot_b{b}.npz" for b in range(1, 51)],
        "unjittered bootstrap partners, reused once",
    )
    stack(
        "data_jitter",
        [f"s5p/num/data/data_b-_j{j}.npz" for j in range(1, 21)],
        "base data jitters",
    )
    stack(
        "data_boot_jitter",
        [f"s5p/num/data/data_b{b}_j{100+b}.npz" for b in range(1, 51)],
        "paired bootstrap jitters",
    )
    stack(
        "data_base", ["s5p/num/data/data_b-_j-.npz"], "base of numerical-overlap design"
    )
    for tag in (
        "CV",
        "prior_d0",
        "prior_d1",
        "prior_d2",
        "prior_d3",
        "prior_d4",
        "prior_d5",
    ):
        relative = f"s5p/prior/prior_R5fix_{tag}.npz"
        product, meta = load(
            relative, "historical prior sensitivity; not current generator differences"
        )
        expected = next(
            (
                h
                for p, h in envelope["products"].items()
                if Path(p).name == Path(relative).name
            ),
            None,
        )
        if expected is not None and _sha(raw / relative) != expected:
            raise ValueError("Prior product changed from receipt")
        archive[tag] = projection.integrate(product["xsec_flat"], crosscheck=True)

    full, meta = load("s5p/conv/k_b0_nominal.npz", "noise-free nominal reference")
    functional_names = meta["functional_names"]
    positions = [functional_names.index(name) for name in projection.names]
    scale = np.r_[projection.ew_area, np.ones(141)]
    archive["trace_nominal_truth"] = full["fn_true"][positions] * scale
    for family in ("b0", "cap10"):
        for truth, summary in receipt["study_K"][family]["runs"].items():
            relative = f"s5p/conv/k_{family}_{truth}.npz"
            if not (raw / relative).exists():
                relative += ".partial.npz"
            product, meta = load(
                relative, "noise-free trace; restricted to committed receipt range"
            )
            limit = summary["K"]
            true_key = "fn_true" if "fn_true" in product else "fn_true_A"
            true = product[true_key][positions] * scale
            estimate = product["fn_push"][:limit, positions] * scale
            archive[f"trace_{family}_{truth}"] = estimate
            archive[f"trace_{family}_{truth}_truth"] = true
            inventory[-1]["available_iterations"] = product["fn_push"].shape[0]
            inventory[-1]["included_iterations"] = limit
            if "xsec_flat" in product:
                np.testing.assert_allclose(
                    projection.integrate(product["xsec_flat"], crosscheck=True),
                    estimate[-1],
                    rtol=2e-12,
                    atol=1e-53,
                )
                np.testing.assert_allclose(
                    projection.integrate(product["xtrue_flat"]),
                    true,
                    rtol=2e-12,
                    atol=1e-53,
                )
            for k, metrics in summary["series"].items():
                residual = (
                    np.divide(
                        estimate[int(k) - 1],
                        true,
                        out=np.ones_like(true),
                        where=true > 0,
                    )
                    - 1
                )
                reference = archive["trace_nominal_truth"]
                departure = (
                    np.divide(
                        true, reference, out=np.ones_like(true), where=reference > 0
                    )
                    - 1
                )
                for group in ("EW", "J", "H2"):
                    mask = (projection.groups == group) & projection.reported
                    actual = np.median(np.abs(residual[mask])) * 100
                    np.testing.assert_allclose(
                        actual, metrics[group]["median_abs_pct"], rtol=2e-10, atol=1e-10
                    )
                    eligible = mask & (np.abs(departure) > 0.01)
                    if truth != "nominal" and eligible.any():
                        ratio = np.median(
                            np.abs(residual[eligible] / departure[eligible])
                        )
                        np.testing.assert_allclose(
                            ratio, metrics[group]["T2_proxy"], rtol=2e-10, atol=1e-10
                        )
    # The same nominal trace is used for both the reference and trace series.
    inventory = list({row["path"]: row for row in inventory}.values())
    exclusions = []
    for path, identity in remote["files"].items():
        if path in selected:
            continue
        reason = "outside selected synthesis operands; not an independent confirmation"
        if "prior_R5_" in path:
            reason = "superseded prior denominator implementation"
        elif ".partial." in path:
            reason = "duplicate checkpoint of a completed product"
        exclusions.append({"path": path, **identity, "reason": reason})
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "operands.npz", **archive)
    _write(
        out / "inventory.json",
        {
            "baseline_commit": definition["baseline_commit"],
            "remote_observed_utc": remote["observed_utc"],
            "remote_copy_matches": True,
            "selected": inventory,
            "excluded_available": exclusions,
            "outside_inventory": [
                "current s5p production ensembles: intentionally not read",
                "raw event inputs: digests inherited, not re-extracted",
                "old checkpoint bytes: superseded in place; present prefixes reproduce committed metrics",
                "later checkpoint iterations: excluded, absent run metadata",
            ],
            "operands_sha256": _sha(out / "operands.npz"),
        },
    )
    print(
        f"Preserved {len(inventory)} products as projected operands; {len(exclusions)} exclusions"
    )


def main() -> None:
    """Parse the command line and freeze checked operands."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--remote-hashes", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=PACKAGE / "inputs")
    args = parser.parse_args()
    _freeze(args.raw_root, _read(args.remote_hashes), args.out)


if __name__ == "__main__":
    main()
