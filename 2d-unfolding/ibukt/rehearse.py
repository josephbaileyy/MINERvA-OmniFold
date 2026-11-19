"""Run guarded IBUKT checks on tiny fixtures without Slurm.

Expected load is five chains of up to 16 LightGBM fits each (80 total),
at eight threads. The topology, paper-mask and score probes do no fits.
Per-probe limits are 110 seconds for fitting and 30 seconds otherwise.
Probe work has a 580-second overall deadline and the launcher a 600-second limit.
"""

from __future__ import annotations

import argparse
from array import array
from contextlib import suppress
from hashlib import file_digest, sha256
from importlib.metadata import version
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
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
SCRATCH_ROOT = Path("/pscratch")
WORKSPACE_PREFIX = "ibukt-rehearsal-"
FIT_THREADS = 8
FIT_PROBES = ("references", "prepare", "pair-nominal", "pair-poisson")
PROBES = (
    "topology",
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


def verified_config(path: Path, expected: str) -> dict[str, Any]:
    """Parse the same O_NOATIME bytes that were checked against the pin."""
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOATIME), "rb") as stream:
        source = stream.read()
    if sha256(source).hexdigest() != expected:
        raise ValueError(f"rehearsal configuration changed: {path.name}")
    return dict(json.loads(source))


def stage_input(source: Path, target: Path, expected: str) -> None:
    """Copy and verify a protected input without changing its access time."""
    source = source.resolve(strict=True)
    print(json.dumps({"staged_input": target.name, "source": str(source)}), flush=True)
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

    gen, passed, bkg, selected = event_fixture(cfg)
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
    with ROOT.TFile.Open(str(stage / "paper.root"), "NEW"):
        covariance = ROOT.TMatrixDSym(224)
        covariance.Zero()
        for cell in selected:
            covariance[int(cell)][int(cell)] = 1.0
        covariance.Write("StatOnlyCovariance")

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


def scratch_directory() -> Path:
    scratch = Path(os.environ["SCRATCH"]).resolve(strict=True)
    if (
        not scratch.is_dir()
        or not scratch.is_relative_to(SCRATCH_ROOT)
        or scratch == SCRATCH_ROOT
    ):
        raise ValueError("requires a scratch directory on /pscratch")
    return scratch


def validated_workspace(probe: str, workspace: Path) -> Path:
    """Accept only the private directory this launcher created for this probe."""
    scratch = scratch_directory()
    parent = Path(os.environ.get("IBUKT_REHEARSAL_ROOT", ""))
    if (
        parent.parent != scratch
        or not parent.name.startswith(WORKSPACE_PREFIX)
        or workspace != parent / probe
        or Path.cwd() != workspace
    ):
        raise ValueError("probe workspace must belong to the fresh scratch rehearsal")
    for directory in (parent, workspace, workspace / "stage"):
        if directory.resolve(strict=True) != directory:
            raise ValueError("probe workspace cannot follow symlinks")
        info = directory.lstat()
        if (
            not stat.S_ISDIR(info.st_mode)
            or info.st_uid != os.getuid()
            or info.st_mode & 0o077
        ):
            raise ValueError("probe workspace must be a private owned directory")
    for variable, suffix in (
        ("TMPDIR", "tmp"),
        ("MPLCONFIGDIR", "mpl"),
        ("XDG_CACHE_HOME", "cache"),
    ):
        folder = workspace / suffix
        if (
            os.environ.get(variable) != str(folder)
            or folder.resolve(strict=True) != folder
            or not folder.is_dir()
        ):
            raise ValueError(f"{variable} must refer to the probe's private directory")
    return workspace


def topology() -> None:
    """Resolve the production estimators' default thread count without fitting."""
    import joblib
    import lightgbm
    from joblib.externals import loky
    from joblib.externals.loky.backend import context

    affinity = sorted(os.sched_getaffinity(0))
    if len(affinity) != 64:
        raise ValueError("topology probe requires 64 CPUs of affinity")
    physical = context._count_physical_cores
    run = subprocess.run
    evidence: dict[str, Any] = {
        "versions": {
            "lightgbm": version("lightgbm"),
            "joblib": joblib.__version__,
            "loky": loky.__version__,
        },
        "affinity": affinity,
        "physical_core_branch": False,
        "lscpu_attempted": False,
        "effective_n_jobs": {},
    }

    def count_physical() -> Any:
        evidence["physical_core_branch"] = True
        return physical()

    def record_process(argv: Any, *args: Any, **kwargs: Any) -> Any:
        if (
            isinstance(argv, (tuple, list))
            and argv
            and Path(os.fsdecode(argv[0])).name == "lscpu"
        ):
            evidence["lscpu_attempted"] = True
        return run(argv, *args, **kwargs)

    try:
        with patch.object(
            context, "_count_physical_cores", count_physical
        ), patch.object(subprocess, "run", record_process):
            for model in (lightgbm.LGBMClassifier(), lightgbm.LGBMRegressor()):
                evidence["effective_n_jobs"][type(model).__name__] = (
                    model._process_n_jobs(model.n_jobs)
                )
    finally:
        print(json.dumps(evidence), flush=True)


def run_probe(probe: str, workspace: Path) -> None:
    if probe == "topology":
        topology()
        return
    import ROOT

    import run_ibukt as runner

    if not ROOT.gROOT.GetVersion().startswith("6.28/"):
        raise ValueError("requires ROOT 6.28")
    cfg = verified_config(SCRIPT.with_name("config.json"), CONFIG_SHA)
    stage = workspace / "stage"
    if probe == "paper-mask":
        paper_mask(stage / "paper.root")
        return

    comparison, _, _ = runner.dependencies()
    with comparison.read_guards(
        (SCRATCH_ROOT, Path("/global/cfs")), (REPO, workspace), (workspace,)
    ):
        if probe == "score":
            args = pair_inputs(workspace, cfg, ensemble=True)
            args.out = workspace / "out"
            args.out.mkdir()
            runner.score(args, cfg)
            return
        from lightgbm.sklearn import LGBMModel

        process_n_jobs = LGBMModel._process_n_jobs

        def limit_threads(model: Any, _n_jobs: Any) -> int:
            return int(process_n_jobs(model, FIT_THREADS))

        with patch.object(LGBMModel, "_process_n_jobs", limit_threads):
            out = workspace / "out"
            out.mkdir()
            if probe in ("references", "prepare"):
                prepare_references(stage, cfg)
                if probe == "prepare":
                    # Only the synthetic data identities differ from the production pins.
                    for role in ("cv", "flux", "er", "c2", "paper"):
                        pin = cfg["inputs"][role]
                        pin["sha256"] = digest(stage / pin["filename"])
                    runner.prepare(argparse.Namespace(stage=stage, out=out), cfg)
                return
            args = pair_inputs(workspace, cfg, ensemble=False)
            args.stage = stage
            args.out = out
            args.noise_free = probe == "pair-nominal"
            args.truth = "nominal" if args.noise_free else "within_plus"
            args.trial = 0
            runner.pair(args, cfg)


def probe_result(inventory: Path, status: int) -> dict[str, Any]:
    """Keep valid inventory rows even when another row is incomplete."""
    outcomes = []
    refusals = []
    errors = []
    try:
        with os.fdopen(os.open(inventory, os.O_RDONLY | os.O_NOATIME), "rb") as stream:
            lines = stream.read().splitlines()
    except OSError as exc:
        errors.append(str(exc))
        lines = []
    for index, line in enumerate(lines, 1):
        try:
            row = json.loads(line)
            outcome = row["outcome"]
            refusal = row["launch_refusal"]
            verdict = row["verdict"]
            argv = row["offending_argv"]
            if not isinstance(outcome, str) or not isinstance(verdict, str):
                raise ValueError("inventory outcome and verdict must be text")
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f"line {index}: {exc}")
            continue
        outcomes.append(outcome)
        if refusal or outcome.startswith("refused"):
            refusals.append({"argv": argv, "reason": refusal, "verdict": verdict})
    if not outcomes:
        errors.append("no usable inventory rows")
    return {
        "exit": status,
        "outcomes": outcomes,
        "refusals": refusals,
        "inventory_errors": errors,
        "complete": status == 0
        and not errors
        and not refusals
        and all(row == "ok" for row in outcomes),
    }


def run_child(
    command: list[str], runtime: Path, env: dict[str, str], timeout: float
) -> int:
    """Stop the whole probe process group when its wall budget expires."""
    if timeout <= 0:
        return 124
    with (runtime / "probe.log").open("x") as log:
        with subprocess.Popen(
            command,
            cwd=runtime,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        ) as child:
            try:
                return child.wait(timeout=timeout)
            except (subprocess.TimeoutExpired, TimeoutError):
                with suppress(ProcessLookupError):
                    os.killpg(child.pid, signal.SIGKILL)
                child.wait()
                return 124


def launch(expected_sha: str, deadline: float) -> int:
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
    ):
        if digest(path) != expected:
            raise ValueError(f"rehearsal code or configuration changed: {path.name}")
    cfg = verified_config(config, CONFIG_SHA)
    ref = verified_config(ref_config, REF_CONFIG_SHA)
    for relative, pin in cfg["code_sha256"].items():
        if digest(REPO / relative) != pin:
            raise ValueError(f"rehearsal dependency changed: {relative}")
    scratch = scratch_directory()
    cpus = sorted(os.sched_getaffinity(0))
    if len(cpus) < 64:
        raise ValueError("login-node affinity cannot reproduce the job's 64 CPUs")
    os.umask(0o077)
    workspace = Path(tempfile.mkdtemp(prefix=WORKSPACE_PREFIX, dir=scratch))
    print(f"IBUKT rehearsal artifacts: {workspace}", flush=True)
    results = {}
    for probe in PROBES:
        runtime = workspace / probe
        runtime.mkdir()
        stage = runtime / "stage"
        stage.mkdir()
        threads = (
            64 if probe == "topology" else FIT_THREADS if probe in FIT_PROBES else 1
        )
        os.sched_setaffinity(0, set(cpus[:threads]))
        env = os.environ.copy()
        for key in (
            "PYTHONPATH",
            "PYTHONHOME",
            "BASH_ENV",
            "LOKY_MAX_CPU_COUNT",
            "OMP_THREAD_LIMIT",
        ):
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
            IBUKT_REHEARSAL_ROOT=str(workspace),
            OMP_NUM_THREADS=str(threads),
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
            str(runtime),
        ]
        timeout = min(110 if probe in FIT_PROBES else 30, deadline - time.monotonic())
        try:
            if timeout > 0 and probe in (
                "paper-mask",
                "prepare",
                "pair-nominal",
                "pair-poisson",
            ):
                role, source = (
                    ("paper", ref["publication"]["path"])
                    if probe == "paper-mask"
                    else ("library", ref["inputs"]["roounfold_lib"])
                )
                pin = cfg["inputs"][role]
                stage_input(Path(source), stage / pin["filename"], pin["sha256"])
                timeout = min(timeout, deadline - time.monotonic())
            status = run_child(command, runtime, env, timeout)
        except (OSError, ValueError) as exc:
            print(f"{probe}: cannot stage or launch probe: {exc}", file=sys.stderr)
            status = 125
        results[probe] = probe_result(inventory, status)
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
        try:
            workspace = validated_workspace(args.probe, args.workspace)
        except (ValueError, OSError, KeyError) as exc:
            parser.error(str(exc))
        run_probe(args.probe, workspace)
        return 0
    if not args.expect_sha256:
        parser.error("--expect-sha256 is required")

    def deadline_expired(_signum: int, _frame: Any) -> None:
        raise TimeoutError("rehearsal exceeded the 600-second wall limit")

    signal.signal(signal.SIGALRM, deadline_expired)
    signal.alarm(600)
    try:
        return launch(args.expect_sha256, time.monotonic() + 580)
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    status = main()
    if status:
        raise SystemExit(status)
