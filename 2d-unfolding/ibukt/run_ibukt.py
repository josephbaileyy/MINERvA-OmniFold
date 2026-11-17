"""Prepare identity-checked inputs and run the declared IBUKT paired screen.

All input arguments name staged copies. Production inputs are hash checked;
protected shared reads require O_NOATIME. A separate audited connect/launcher
binding is required before this code is used on a cluster.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, cast
from unittest import mock

import numpy as np

import ibukt as core

REPO = Path(__file__).resolve().parents[2]


def digest(path: Path) -> str:
    """Hash a file through an O_NOATIME descriptor on the production platform."""
    flag = getattr(os, "O_NOATIME", None)
    if flag is None:
        raise RuntimeError("production reads require O_NOATIME")
    result = hashlib.sha256()
    with os.fdopen(os.open(path, os.O_RDONLY | flag), "rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 24), b""):
            result.update(chunk)
    return result.hexdigest()


def read_json(path: Path) -> Any:
    """Read a protected receipt through an O_NOATIME descriptor."""
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOATIME), "r") as stream:
        return json.load(stream)


def write_json(path: Path, value: Any) -> None:
    """Write a new receipt, refusing overwrite and nonfinite JSON."""
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def dependencies() -> tuple[Any, Any, Any]:
    """Load the production driver and C2 machinery from this checkout."""
    sys.path.insert(0, str(REPO / "2d-unfolding"))
    sys.path.insert(0, str(REPO / "2d-unfolding/ref_c2c1"))
    import ref_c2c1 as comparison

    driver, helper = comparison.load_driver()
    return comparison, driver, helper


def require_close(
    actual: np.ndarray[Any, Any],
    expected: np.ndarray[Any, Any],
    label: str,
    tol: float = 1e-8,
) -> float:
    """Refuse a nonfinite, misaligned, or relatively different identity operand."""
    if actual.shape != expected.shape or not all(
        np.all(np.isfinite(x)) for x in (actual, expected)
    ):
        raise ValueError(f"{label}: invalid identity operands")
    scale = np.maximum(np.abs(expected), np.max(np.abs(expected)) * 1e-12)
    error = float(np.max(np.abs(actual - expected) / np.maximum(scale, 1e-300)))
    if error > tol:
        raise ValueError(f"{label}: {error} > {tol}")
    return error


def ratios(cfg: dict[str, Any]) -> dict[str, np.ndarray[Any, Any]]:
    """Read the pinned generator-shape stresses and require the exact grid."""
    result = {}
    for name, rel in cfg["ratios"].items():
        path = REPO / rel
        if digest(path) != cfg["code_sha256"][rel]:
            raise ValueError("ratio pin differs")
        obj = json.loads(path.read_text())
        if obj["schema"] != "pv2d-ratio/1" or any(
            obj[k] != cfg[k] for k in ("pt_edges", "pz_edges")
        ):
            raise ValueError("ratio schema/grid differs")
        values = np.asarray(obj["r"], float)
        if (
            values.shape != (14, 16)
            or not np.all(np.isfinite(values))
            or np.any(values <= 0)
        ):
            raise ValueError("invalid generator ratio")
        result[name] = values
    return result


def read_npz(path: Path) -> dict[str, np.ndarray[Any, Any]]:
    """Load a staged array product without changing its access time."""
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOATIME), "rb") as stream:
        with np.load(stream, allow_pickle=False) as product:
            return {key: product[key] for key in product.files}


def root_vector(path: Path, name: str, comparison: Any) -> np.ndarray[Any, Any]:
    """Read one staged ROOT histogram in the driver's pT-major order."""
    import ROOT

    source = ROOT.TFile.Open(str(path), "READ")
    if not source or source.IsZombie() or not source.Get(name):
        raise ValueError(f"missing histogram {name}")
    try:
        return cast(
            np.ndarray[Any, Any], comparison.th2_vector(source.Get(name), 14, 16)
        )
    finally:
        source.Close()


def prepare(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    """Capture the unchanged real-data pipeline and verify both recorded centrals.

    The simulation bank is frozen only after identity and full-truth completeness
    controls pass. No training/sample split is claimed.
    """
    comparison, driver, helper = dependencies()
    for role, pin in cfg["inputs"].items():
        path = args.stage / pin["filename"]
        if digest(path) != pin["sha256"]:
            raise ValueError(f"input identity: {role}")
    if driver.PT_EDGES != cfg["pt_edges"] or driver.PZ_EDGES != cfg["pz_edges"]:
        raise ValueError("driver grid changed")
    import ROOT

    if ROOT.gSystem.Load(str(args.stage / cfg["inputs"]["library"]["filename"])) < 0:
        raise ValueError("RooUnfold library failed to load")
    captured: dict[str, Any] = {}
    original = helper.omnifold

    def observe(
        gen: Any,
        reco: Any,
        measured: Any,
        pr: Any,
        pt: Any,
        pm: Any,
        iterations: Any,
        **kw: Any,
    ) -> Any:
        captured.update(
            gen=gen.copy(),
            reco=reco.copy(),
            pr=pr.copy(),
            pt=pt.copy(),
            wt=kw["MCgen_weights"].copy(),
            wr=kw["MCreco_weights"].copy(),
        )
        problem = comparison.binned_problem(
            gen,
            reco,
            measured,
            pr,
            pt,
            kw["MCgen_weights"],
            kw["MCreco_weights"],
            kw["measured_weights"],
            driver.PT_EDGES,
            driver.PZ_EDGES,
        )
        truth, matrix, target, _ = problem
        captured["ibu"] = comparison.roounfold_bayes(
            matrix, truth, target, [5, 10], str(args.stage / "libRooUnfold.so")
        )
        numpy_ibu = comparison.dagostini(matrix, truth, target, [5, 10])
        for k in (5, 10):
            require_close(captured["ibu"][k], numpy_ibu[k], "RooUnfold/NumPy", 1e-9)
        return original(gen, reco, measured, pr, pt, pm, iterations, **kw)

    def record_loader(name: str, key: str) -> Any:
        function = getattr(driver, name)

        def wrapped(*pos: Any, **kw: Any) -> Any:
            result = function(*pos, **kw)
            captured[key] = result
            return result

        return wrapped

    argv = [
        "--omnifile",
        str(args.stage / "cv.root"),
        "--mcfile",
        str(args.stage / "flux.root"),
        *cfg["argv"],
    ]
    with contextlib.ExitStack() as stack:
        stack.enter_context(mock.patch.object(helper, "omnifold", observe))
        for name, key in (
            ("fill_bkg_reco_2d", "background"),
            ("collect_truth_denom_arrays", "den"),
        ):
            stack.enter_context(
                mock.patch.object(driver, name, record_loader(name, key))
            )
        capture = comparison.run_driver(
            driver, helper, argv, args.out / "identity.root", staging=args.stage
        )
    extraction, keywords = capture["extract"]
    unit = driver.make_th2d(
        "ibukt_unit", "unit counts", driver.PT_EDGES, driver.PZ_EDGES
    )
    for ip in range(1, 15):
        for iz in range(1, 17):
            unit.SetBinContent(ip, iz, 1)
    factor = comparison.th2_vector(
        driver.extract_cross_section_2d(unit, *extraction, **keywords), 14, 16
    )
    completeness = comparison.th2_vector(extraction[0], 14, 16)
    er = root_vector(args.out / "identity.root", "hXSec2D", comparison)
    er_ref = root_vector(args.stage / "er.root", "hXSec2D", comparison)
    c2 = read_npz(args.stage / "c2.npz")
    import compare_to_paper_fullcov as paper

    published = ROOT.TFile.Open(str(args.stage / "paper.root"), "READ")
    selected = np.flatnonzero(
        np.diag(paper.tmatrix_to_numpy(published.Get("StatOnlyCovariance"))) > 0
    )
    published.Close()
    if selected.size != 205:
        raise ValueError("reporting mask must contain exactly 205 cells")
    checks = {"E_R": require_close(er[selected], er_ref[selected], "E_R")}
    for k in (5, 10):
        idx = list(c2["ks"]).index(k)
        checks[f"C2_K{k}"] = require_close(
            (captured["ibu"][k] * factor)[selected],
            c2["xsec"][idx][selected],
            f"C2 K{k}",
        )
    checks["completeness"] = require_close(
        completeness[selected], np.ones(205), "full truth completeness"
    )
    if np.any(captured["pr"] & ~captured["pt"]):
        raise ValueError(
            "unexpected signal fakes; declared background contract is post-Phase-18"
        )
    den = captured["den"]
    means = core.moments(den["truth_pt"], den["truth_pz"], den["w_truth"], cfg)
    gen, wt, pt = captured["gen"], captured["wt"], captured["pt"]
    rdefs = ratios(cfg)
    truths = {}
    for name in cfg["truths"]:
        fd = core.truth_factor(
            name, den["truth_pt"], den["truth_pz"], means, cfg, rdefs
        )
        fs = core.truth_factor(name, gen[:, 0], gen[:, 1], means, cfg, rdefs)
        full = core.histogram(
            den["truth_pt"], den["truth_pz"], den["w_truth"] * fd, cfg
        )
        subset = core.histogram(gen[pt, 0], gen[pt, 1], wt[pt] * fs[pt], cfg)
        checks[f"truth_{name}"] = require_close(
            subset[selected], full[selected], f"full truth {name}"
        )
        truths[name] = full * factor * completeness
    background = captured["background"]
    bank = {key: captured[key] for key in ("gen", "reco", "pr", "pt", "wt", "wr")}
    bank.update(
        bkg=np.column_stack(background[:2]),
        bw=background[2],
        means=means,
        factor=factor,
        selected=selected,
        **{f"truth_{key}": value for key, value in truths.items()},
    )
    np.savez(args.out / "bank.npz", **bank)
    write_json(
        args.out / "identity.json",
        {
            "status": "PASS",
            "checks": checks,
            "bank_sha256": digest(args.out / "bank.npz"),
            "config_sha256": digest(core.CONFIG),
        },
    )


def pair(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    """Unfold one Poisson pseudo-dataset with both frozen K=5 estimators."""
    identity = read_json(args.identity)
    if identity["status"] != "PASS" or identity["config_sha256"] != digest(core.CONFIG):
        raise ValueError("identity control not passed for this configuration")
    if digest(args.bank) != identity["bank_sha256"]:
        raise ValueError("bank differs from identity control")
    bank = read_npz(args.bank)
    comparison, driver, helper = dependencies()
    gen, reco, pt, pr = (bank[key] for key in ("gen", "reco", "pt", "pr"))
    factors = core.truth_factor(
        args.truth, gen[:, 0], gen[:, 1], bank["means"], cfg, ratios(cfg)
    )
    keep = pt & pr
    # The response is untouched; only the positive fake-data signal is reweighted.
    feat = np.concatenate((reco[keep], bank["bkg"], bank["bkg"]))
    signed = np.concatenate((bank["wr"][keep] * factors[keep], bank["bw"], -bank["bw"]))
    measured, signed = core.poisson_target(feat, signed, cfg["seeds"][args.trial])
    refined, _, clipped = driver.refine_stay_positive(
        measured,
        signed,
        estimator="lgbm",
        device="cpu",
        params={"random_state": 45, "n_estimators": 400, "num_leaves": 31},
    )
    if refined.sum() <= 0:
        raise ValueError("empty refined target")
    truth, matrix, target, _ = comparison.binned_problem(
        gen,
        reco,
        measured,
        pr,
        pt,
        bank["wt"],
        bank["wr"],
        refined,
        cfg["pt_edges"],
        cfg["pz_edges"],
    )
    ibu = comparison.roounfold_bayes(
        matrix, truth, target, [5, 10], str(args.stage / "libRooUnfold.so")
    )
    _, push = helper.omnifold(
        gen,
        reco,
        measured,
        pr,
        pt,
        np.ones(len(measured), bool),
        5,
        MCgen_weights=bank["wt"],
        MCreco_weights=bank["wr"],
        measured_weights=refined,
        classifier1_params={"random_state": 42},
        classifier2_params={"random_state": 43},
        regressor_params={"random_state": 44},
        parameter_format="dict",
        estimator="lgbm",
        device="cpu",
    )
    unfolded = (
        core.histogram(gen[pt, 0], gen[pt, 1], bank["wt"][pt] * push, cfg)
        * bank["factor"]
    )
    if not np.all(np.isfinite(unfolded)):
        raise ValueError("nonfinite unfolded result")
    np.savez(
        args.out / "pair.npz",
        omnifold=unfolded,
        ibu5=ibu[5] * bank["factor"],
        ibu10=ibu[10] * bank["factor"],
        truth=bank[f"truth_{args.truth}"],
        prior=bank["truth_nominal"],
        selected=bank["selected"],
    )
    write_json(
        args.out / "pair.json",
        {
            "truth": args.truth,
            "trial": args.trial,
            "seed": cfg["seeds"][args.trial],
            "bank_sha256": identity["bank_sha256"],
            "config_sha256": digest(core.CONFIG),
            "product_sha256": digest(args.out / "pair.npz"),
            "signed_sum": float(signed.sum()),
            "refined_sum": float(refined.sum()),
            "clipped_fraction": float(clipped),
            "status": "PASS",
        },
    )


def score(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    """Read all 35 complete pairs; emit every per-cell reading without selection."""
    readout = {}
    bank_pins = set()
    for name in cfg["truths"]:
        values = []
        for trial in range(5):
            directory = args.products / f"{name}-{trial}"
            record = read_json(directory / "pair.json")
            if (
                record["status"],
                record["truth"],
                record["trial"],
                record["seed"],
                record["config_sha256"],
            ) != ("PASS", name, trial, cfg["seeds"][trial], digest(core.CONFIG)):
                raise ValueError("missing or mismatched pair receipt")
            if record["product_sha256"] != digest(directory / "pair.npz"):
                raise ValueError("pair digest differs")
            bank_pins.add(record["bank_sha256"])
            values.append(read_npz(directory / "pair.npz"))
        first = values[0]
        selected = first["selected"]
        for item in values[1:]:
            for key in ("truth", "prior", "selected"):
                if not np.array_equal(item[key], first[key]):
                    raise ValueError(
                        "truth or cell identity differs across paired trials"
                    )
        readout[name] = {
            method: core.recoveries(
                np.array([v[method][selected] for v in values]),
                first["truth"][selected],
                first["prior"][selected],
            )
            for method in ("omnifold", "ibu5", "ibu10")
        }
        readout[name]["cells"] = selected.tolist()
    if len(bank_pins) != 1:
        raise ValueError("mixed simulation banks")
    write_json(
        args.out / "readout.json",
        {
            "schema": "ibukt-recovery/1",
            "truths": readout,
            "licence": "conditional finite-simulation per-cell recovery; five draws, no coverage or method adoption",
        },
    )


def main() -> None:
    """Execute a single declared stage inside an exclusive scratch output root."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "pair", "score"))
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--bank", type=Path)
    parser.add_argument("--identity", type=Path)
    parser.add_argument("--truth", choices=core.configuration()["truths"])
    parser.add_argument("--trial", type=int, choices=range(5))
    parser.add_argument("--products", type=Path)
    args = parser.parse_args()
    if args.mode == "pair" and any(
        getattr(args, k) is None for k in ("bank", "identity", "truth", "trial")
    ):
        parser.error("pair requires bank, identity, truth and trial")
    if args.mode == "score" and args.products is None:
        parser.error("score requires products")
    for path in (args.out, args.stage):
        if not path.resolve().is_relative_to(Path("/pscratch")):
            parser.error("production stage/output must be on pscratch")
    cfg = core.configuration()
    for rel, expected in cfg["code_sha256"].items():
        if digest(REPO / rel) != expected:
            raise ValueError(f"dependency changed: {rel}")
    if digest(args.stage / "libRooUnfold.so") != cfg["inputs"]["library"]["sha256"]:
        raise ValueError("library identity changed")
    if os.environ.get("OMP_NUM_THREADS") != "64" or any(
        os.environ.get(key) != "1"
        for key in ("MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS")
    ):
        raise ValueError("requires recorded thread environment 64/1/1")
    if len(os.sched_getaffinity(0)) != 64:
        raise ValueError("requires 64 allocated CPUs")
    args.out.mkdir(parents=True, exist_ok=False)
    comparison, _, _ = dependencies()
    with comparison.read_guards(
        (Path("/pscratch"), Path("/global/cfs")),
        (REPO, args.stage, args.out),
        (args.out,),
    ):
        {"prepare": prepare, "pair": pair, "score": score}[args.mode](args, cfg)


if __name__ == "__main__":
    main()
