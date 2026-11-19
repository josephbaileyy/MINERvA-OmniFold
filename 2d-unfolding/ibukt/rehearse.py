"""Run independent IBUKT producer checks on tiny fixtures without Slurm."""

from __future__ import annotations

import argparse
from array import array
from hashlib import file_digest
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any
from unittest.mock import patch

SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
GUARD = REPO / "nd-unfolding/mnv_guarded_run.py"
GUARD_SHA = "30162f57771c9d5a1206eae623a7eb3fc80ac3f0bb150c82fb561be7254b510b"
RUNNER_SHA = "ff1b0c35ccc0ff2c71c9001e049e5efdba555f9dba11fd3def858e14c333a00f"
CONFIG_SHA = "35f344676d83b93ecdf458d8683263f869d7f66522b58950ea3db3faebaf4206"
CORE_SHA = "f98fc9930e4bbdcb60328553d9e0b9ce267be14542f84b3ecafa0f5ff642a7c0"
REF_CONFIG_SHA = "dc9b242f9b7eef7dc808c6ef4fb94c4ec8baa6027dc3ee78c549f6d4f0f72a23"
PROBES = (
    "paper-mask",
    "references",
    "prepare",
    "pair-nominal",
    "pair-poisson",
    "score",
)


def digest(path: Path) -> str:
    """Hash a file without changing its access time."""
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOATIME), "rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def stage_input(source: Path, target: Path, expected: str) -> None:
    """Copy and verify a protected input without changing its access time."""
    before = source.stat().st_atime_ns
    with os.fdopen(os.open(source, os.O_RDONLY | os.O_NOATIME), "rb") as src:
        with target.open("xb") as dest:
            shutil.copyfileobj(src, dest)
    if digest(target) != expected or source.stat().st_atime_ns != before:
        raise ValueError(f"staged input failed identity or atime check: {target.name}")


def paper_mask(path: Path) -> None:
    import numpy as np
    import ROOT

    import run_ibukt as runner

    with ROOT.TFile.Open(str(path), "READ") as source:
        matrix = source.Get("StatOnlyCovariance")
        n = matrix.GetNrows()
        # Match compare_to_paper_fullcov.tmatrix_to_numpy followed by the old mask.
        dense = np.empty((n, n))
        for row in range(n):
            for col in range(n):
                dense[row, col] = matrix(row, col)
    legacy = np.flatnonzero(np.diag(dense) > 0)
    direct = runner._reporting_cells(path)
    np.testing.assert_array_equal(direct, legacy)
    print(json.dumps({"paper_sha256": digest(path), "selected": direct.tolist()}))


def event_fixture(cfg: dict[str, Any]) -> tuple[Any, Any, Any, Any]:
    import numpy as np

    pt, pz = (np.asarray(cfg[key]) for key in ("pt_edges", "pz_edges"))
    low_pt, low_pz = np.meshgrid(pt[:-1], pz[:-1], indexing="ij")
    high_pt, high_pz = np.meshgrid(pt[1:], pz[1:], indexing="ij")
    angle = np.tan(np.deg2rad(20))
    valid = low_pt < angle * high_pz
    selected = np.flatnonzero(valid)
    pz_floor = np.maximum(low_pz[valid], low_pt[valid] / angle)
    sample_pz = (pz_floor + high_pz[valid]) / 2
    pt_floor = low_pt[valid]
    pt_width = np.minimum(high_pt[valid], angle * sample_pz) - pt_floor
    fractions = np.linspace(0.125, 0.875, 32)
    gen = np.column_stack(
        [
            (pt_floor[:, None] + pt_width[:, None] * fractions).ravel(),
            np.repeat(sample_pz, len(fractions)),
        ]
    )
    # Prefer lower-pT entries within each cell so the within-cell stress moves reco.
    passed = np.tile(np.arange(len(fractions)) < 24, selected.size)
    return gen, passed, gen[:: len(fractions)].copy(), selected


def prepare_references(stage: Path, cfg: dict[str, Any]) -> None:
    """Stage a small full-grid ROOT fixture and compute its reference vectors."""
    import numpy as np
    import ROOT

    import run_ibukt as runner

    gen, passed, bkg, _ = event_fixture(cfg)
    truth = {"MC": gen[:, 0], "MC_pz": gen[:, 1], "w_truth": np.ones(len(gen))}
    signal = {
        **truth,
        "sim": gen[:, 0],
        "sim_pz": gen[:, 1],
        "sim_pass": passed.astype(np.uint8),
        "w_reco": np.ones(len(gen)),
    }
    background = {
        "sim_background": bkg[:, 0],
        "sim_background_pz": bkg[:, 1],
        "sim_background_pass": np.ones(len(bkg), np.uint8),
        "w_bkg": np.ones(len(bkg)),
    }
    data = {
        "measured": gen[passed, 0],
        "measured_pz": gen[passed, 1],
        "measured_pass": np.ones(passed.sum(), np.uint8),
    }
    with ROOT.TFile.Open(str(stage / "cv.root"), "NEW"):
        trees = []
        for name, columns in (
            ("mc_signal_reco", signal),
            ("mc_background", background),
            ("data", data),
            ("mc_truth_denom", truth),
        ):
            tree = ROOT.TTree(name, name)
            buffers = {}
            for key, values in columns.items():
                code, leaf = ("B", "b") if values.dtype == np.uint8 else ("d", "D")
                buffers[key] = array(code, [0])
                tree.Branch(key, buffers[key], f"{key}/{leaf}")
            for row in zip(*columns.values(), strict=True):
                for buf, value in zip(buffers.values(), row, strict=True):
                    buf[0] = value.item()
                tree.Fill()
            tree.Write()
            trees.append(tree)
        ROOT.TParameter("double")("dataPOTUsed", 1.0e20).Write()
        ROOT.TParameter("double")("mcPOTUsed", 4.0e20).Write()
        ROOT.TParameter("int")("hasTruthOnlyMisses", 1).Write()
    with ROOT.TFile.Open(str(stage / "flux.root"), "NEW"):
        flux = ROOT.TH1D(
            "pTmu_reweightedflux_integrated", "", 14, array("d", cfg["pt_edges"])
        )
        for cell in range(1, 15):
            flux.SetBinContent(cell, 0.01)
        flux.Write()

    comparison, driver, helper = runner.dependencies()
    original = helper.omnifold
    estimates = {}
    ks = [5, 10]

    def observe(
        gen: Any,
        reco: Any,
        measured: Any,
        pr: Any,
        pt: Any,
        pm: Any,
        iterations: int,
        **kwargs: Any,
    ) -> Any:
        truth, matrix, target, _ = comparison.binned_problem(
            gen,
            reco,
            measured,
            pr,
            pt,
            kwargs["MCgen_weights"],
            kwargs["MCreco_weights"],
            kwargs["measured_weights"],
            driver.PT_EDGES,
            driver.PZ_EDGES,
        )
        estimates.update(comparison.dagostini(matrix, truth, target, ks))
        return original(gen, reco, measured, pr, pt, pm, iterations, **kwargs)

    argv = [
        "--omnifile",
        str(stage / "cv.root"),
        "--mcfile",
        str(stage / "flux.root"),
        *cfg["argv"],
    ]
    with patch.object(helper, "omnifold", staticmethod(observe)):
        capture = comparison.run_driver(
            driver, helper, argv, stage / "er.root", staging=stage
        )
    unit = driver.make_th2d("rehearsal_unit", "", driver.PT_EDGES, driver.PZ_EDGES)
    for ip in range(1, 15):
        for iz in range(1, 17):
            unit.SetBinContent(ip, iz, 1)
    args, kwargs = capture["extract"]
    factor = comparison.th2_vector(
        driver.extract_cross_section_2d(unit, *args, **kwargs), 14, 16
    )
    np.savez(stage / "c2.npz", ks=ks, xsec=[estimates[k] * factor for k in ks])


def pair_inputs(
    work: Path, cfg: dict[str, Any], *, ensemble: bool
) -> argparse.Namespace:
    """Create independent, fully receipted smoke-test operands."""
    import numpy as np

    import ibukt as core
    import run_ibukt as runner

    gen, passed, bkg, selected = event_fixture(cfg)
    weights = np.ones(len(gen))
    means = core.moments(gen[:, 0], gen[:, 1], weights, cfg)
    ratios = runner.ratios(cfg)
    truths = {}
    for name in cfg["truths"]:
        factors = core.truth_factor(name, gen[:, 0], gen[:, 1], means, cfg, ratios)
        truths[name] = core.histogram(gen[:, 0], gen[:, 1], factors, cfg)
    bank = work / "bank.npz"
    bank_arrays: dict[str, Any] = dict(
        gen=gen,
        reco=gen,
        pt=np.ones(len(gen), bool),
        pr=passed,
        wt=weights,
        wr=weights,
        bkg=bkg,
        bw=np.full(len(bkg), 0.125),
        means=means,
        factor=np.ones(224),
        selected=selected,
    )
    bank_arrays.update({f"truth_{name}": truth for name, truth in truths.items()})
    np.savez(bank, **bank_arrays)
    pins = {"bank_sha256": digest(bank), "config_sha256": digest(core.CONFIG)}
    identity = work / "identity.json"
    runner.write_json(identity, {"status": "PASS", **pins})
    products = work / "products"
    control_dir = products / "nominal-control"
    control_dir.mkdir(parents=True)

    def product(directory: Path, name: str, receipt: dict[str, Any]) -> None:
        truth = truths[name]
        output = directory / "pair.npz"
        np.savez(
            output,
            truth=truth,
            prior=truths["nominal"],
            selected=selected,
            omnifold=truth,
            ibu5=truth,
            ibu10=truth,
        )
        runner.write_json(
            directory / "pair.json",
            {
                "status": "PASS",
                "truth": name,
                "product_sha256": digest(output),
                **pins,
                **receipt,
            },
        )

    product(
        control_dir,
        "nominal",
        {"sampling": "noise-free", "nominal_tolerance": core.RECOVERY_TOLERANCE},
    )
    control = control_dir / "pair.json"
    if ensemble:
        control_pin = digest(control)
        for name in cfg["truths"]:
            for trial, seed in enumerate(cfg["seeds"]):
                directory = products / f"{name}-{trial}"
                directory.mkdir()
                product(
                    directory,
                    name,
                    {
                        "sampling": "poisson",
                        "trial": trial,
                        "seed": seed,
                        "control_sha256": control_pin,
                    },
                )
    return argparse.Namespace(
        bank=bank, identity=identity, control=control, products=products
    )


def run_probe(probe: str, workspace: Path) -> None:
    import ROOT

    import ibukt as core
    import run_ibukt as runner

    if not ROOT.gROOT.GetVersion().startswith("6.28/"):
        raise ValueError("requires ROOT 6.28")
    cfg = core.configuration()
    stage = workspace / "stage"
    work = workspace / probe
    work.mkdir()
    if probe == "paper-mask":
        paper_mask(stage / "paper.root")
        return

    comparison, _, _ = runner.dependencies()
    with comparison.read_guards(
        (Path("/pscratch"), Path("/global/cfs")), (REPO, workspace), (workspace,)
    ):
        if probe == "references":
            prepare_references(stage, cfg)
            return
        out = work / "out"
        out.mkdir()
        if probe == "prepare":
            # Only the fixture data hashes differ. The library, mask, configuration
            # of the estimators and producer implementation remain pinned.
            for role in ("cv", "flux", "er", "c2"):
                pin = cfg["inputs"][role]
                pin["sha256"] = digest(stage / pin["filename"])
            runner.prepare(argparse.Namespace(stage=stage, out=out), cfg)
            return
        ensemble = probe == "score"
        args = pair_inputs(work, cfg, ensemble=ensemble)
        args.stage = stage
        args.out = out
        if ensemble:
            runner.score(args, cfg)
        else:
            args.noise_free = probe == "pair-nominal"
            args.truth = "nominal" if args.noise_free else "within_plus"
            args.trial = 0
            runner.pair(args, cfg)


def launch(expected_sha: str) -> int:
    """Run each probe in an independently guarded and logged interpreter."""
    if sys.platform != "linux" or "SLURM_JOB_ID" in os.environ:
        raise ValueError("the rehearsal requires a Linux login-node shell")
    expected_python = Path.home() / ".conda/envs/root_6_28/bin/python3"
    if (
        Path(sys.executable).resolve() != expected_python.resolve()
        or Path(os.environ["CONDA_PREFIX"]).resolve()
        != expected_python.parent.parent.resolve()
    ):
        raise ValueError("activate the pinned root_6_28 environment")
    config = SCRIPT.with_name("config.json")
    ref_config = REPO / "2d-unfolding/ref_c2c1/config.json"
    for path, expected in (
        (SCRIPT, expected_sha),
        (GUARD, GUARD_SHA),
        (SCRIPT.with_name("run_ibukt.py"), RUNNER_SHA),
        (SCRIPT.with_name("ibukt.py"), CORE_SHA),
        (config, CONFIG_SHA),
        (ref_config, REF_CONFIG_SHA),
    ):
        if digest(path) != expected:
            raise ValueError(f"rehearsal code or configuration changed: {path.name}")
    cfg = json.loads(config.read_text())
    ref = json.loads(ref_config.read_text())
    for relative, pin in cfg["code_sha256"].items():
        if digest(REPO / relative) != pin:
            raise ValueError(f"rehearsal dependency changed: {relative}")
    scratch = Path(os.environ["SCRATCH"]).resolve(strict=True)
    if not scratch.is_relative_to(Path("/pscratch")) or not scratch.is_dir():
        raise ValueError("requires a scratch directory on /pscratch")
    cpus = sorted(os.sched_getaffinity(0))
    if len(cpus) < 64:
        raise ValueError("login-node affinity cannot reproduce the job's 64 CPUs")
    os.sched_setaffinity(0, set(cpus[:64]))
    os.umask(0o077)
    workspace = Path(tempfile.mkdtemp(prefix="ibukt-rehearsal-", dir=scratch))
    print(f"IBUKT rehearsal artifacts: {workspace}", flush=True)
    stage = workspace / "stage"
    stage.mkdir()
    for role, source in (
        ("paper", ref["publication"]["path"]),
        ("library", ref["inputs"]["roounfold_lib"]),
    ):
        pin = cfg["inputs"][role]
        stage_input(Path(source), stage / pin["filename"], pin["sha256"])

    results = {}
    for probe in PROBES:
        runtime = workspace / f"{probe}-runtime"
        runtime.mkdir()
        env = os.environ.copy()
        for key in ("PYTHONPATH", "PYTHONHOME", "BASH_ENV"):
            env.pop(key, None)
        for variable, suffix in (
            ("TMPDIR", "tmp"),
            ("MPLCONFIGDIR", "mpl"),
            ("XDG_CACHE_HOME", "cache"),
        ):
            folder = runtime / suffix
            folder.mkdir()
            env[variable] = str(folder)
        env.update(
            OMP_NUM_THREADS="64",
            MKL_NUM_THREADS="1",
            OPENBLAS_NUM_THREADS="1",
            NUMEXPR_NUM_THREADS="1",
            PYTHONNOUSERSITE="1",
            PYTHONDONTWRITEBYTECODE="1",
            CUDA_VISIBLE_DEVICES="",
        )
        inventory = runtime / "imports.jsonl"
        command = [
            sys.executable,
            "-B",
            str(GUARD),
            "--expect-root",
            str(REPO),
            "--inventory",
            str(inventory),
            "--label",
            f"ibukt-rehearsal-{probe}",
            "--",
            str(SCRIPT),
            "--probe",
            probe,
            "--workspace",
            str(workspace),
        ]
        with (runtime / "probe.log").open("x") as log:
            try:
                status = subprocess.run(
                    command,
                    cwd=REPO,
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,
                    check=False,
                    timeout=120,
                ).returncode
            except subprocess.TimeoutExpired:
                status = 124
        records = (
            [json.loads(line) for line in inventory.read_text().splitlines()]
            if inventory.is_file()
            else []
        )
        outcomes = [row["outcome"] for row in records]
        results[probe] = {
            "exit": status,
            "outcomes": outcomes,
            "refusals": [
                {
                    "argv": row["offending_argv"],
                    "reason": row["launch_refusal"],
                    "verdict": row["verdict"],
                }
                for row in records
                if row["launch_refusal"] or row["outcome"].startswith("refused")
            ],
            "complete": status == 0 and outcomes == ["ok"],
        }
        print(json.dumps({probe: results[probe]}), flush=True)
    passed = all(result["complete"] for result in results.values())
    with (workspace / "summary.json").open("x") as stream:
        json.dump(
            {
                "status": "PASS" if passed else "STOP",
                "node_hours": 0,
                "probes": results,
            },
            stream,
            indent=2,
        )
    return 0 if passed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expect-sha256")
    parser.add_argument("--probe", choices=PROBES)
    parser.add_argument("--workspace", type=Path)
    args = parser.parse_args()
    if args.probe:
        if args.workspace is None:
            parser.error("--probe requires --workspace")
        run_probe(args.probe, args.workspace)
        return 0
    if not args.expect_sha256:
        parser.error("--expect-sha256 is required")
    return launch(args.expect_sha256)


if __name__ == "__main__":
    status = main()
    if status:
        raise SystemExit(status)
