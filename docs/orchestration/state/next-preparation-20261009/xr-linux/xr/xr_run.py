#!/usr/bin/env python3
"""XR wrapper: run one frozen central-reproduction run (X0, X0p, X1, L0, L1) under strict provenance.

    xr_run.py --run X0 --attempt 1 --admission ADMISSION.json [--require-provenance]

``--run PF`` is the preflight (kind ``preflight``). On the production inputs it takes every step a
run takes before its first fit, for the helper and the drivers of all five runs. It then runs the
five configurations end to end, in this process, on a tiny synthetic fixture written inside the
attempt directory (the run's own driver, argv template, backend and seeds; fits and predictions
included), repeats L0 to show the path is deterministic, and exercises the refusal controls. It
writes ``preflight-receipt.json`` (schema ``xr-preflight-receipt/2``, status ``preflight-pass`` or
``preflight-fail``) and exits. It never calls a driver's ``main`` on the production inputs, and its
fixture products are not results: no comparison can use them.

The run's driver, argv template, inputs, backend and seeds come only from ``manifest/runs.json``
(bound by the admission); nothing on the command line can change them. In order, before any input
is read:

1. the helper ``unbinned_unfolding/python/omnifold.py`` and then the run's driver are executed
   from hashed bytes of this checkout (``n2/execution.py``), the helper registered as
   ``sys.modules["omnifold"]`` first, so the driver's rooted ``sys.path`` insert of the canonical
   cluster checkout never resolves the import (OI-136; the production driver is not edited);
2. strict mode requires the OI-136 guard on this checkout, the admitted commit, and every executed
   file at HEAD with its stated digest;
3. the working directory must be ``<checkout>/2d-unfolding`` (the driver's relative defaults);
4. the output and receipt are ``<outroot>/<RUN>/a<attempt>/``: the path must be lexically equal to
   its realpath (no symlink anywhere), outside the checkout and the canonical cluster tree, not a
   frozen reference product, and new (created exclusively);
5. both inputs are hashed and must equal the frozen digests;
6. the admission must name the outroot frozen in ``runs.json``.

From the environment check to the end of the fit path, any attempt to start a child process is
refused and recorded (``LaunchSpy``): nothing in this window may launch one, and the OI-136 guard
refuses the launches that have been found here before (``ldconfig`` from threadpoolctl, ``lscpu``
from loky). Inside that window, before any fit:

* the interpreter, ROOT and package versions must equal ``runs.json``'s frozen environment
  (exit 6); module origins are recorded, and the loaded OpenMP/BLAS libraries and their own thread
  counts are read from ``/proc/self/maps`` without starting a process. That record is supporting
  evidence only;
* the thread plan (``thread_plan``): ``OMP_NUM_THREADS`` is the kind's; on Linux the CPU affinity
  equals the kind's CPU count and is below the node's, and ``LOKY_MAX_CPU_COUNT`` is unset, so
  joblib's count (which LightGBM's default ``n_jobs`` uses) is the affinity count and never reaches
  the physical-core query; that count must equal the kind's CPUs. No estimator setting is changed.

During the run, every ``fit`` of the four GBDT classes is recorded with its class and
``random_state``; a LightGBM fit also with the thread count LightGBM resolves for it (before
training) and the ``num_threads`` its booster was trained with (after), and every LightGBM
prediction with the count it resolves. A fit of a class the run does not expect, a wrong
``random_state``, or a LightGBM thread count other than the plan's stops the run (exit 6), before
training where the check can precede it. After it: the fit counts, the inputs (re-hashed), the
output's normalization parameters and reported-cell set are checked against the frozen references,
and the output's sha256 is recorded.

Exit: 0 complete; 3 provenance or path refusal; 6 backend, thread, launch, normalization or cell
refusal; 1 other.
"""

import argparse
import datetime
import hashlib
import json
import os
import sys
import time
import traceback
from pathlib import Path

_SELF_BYTES = Path(__file__).read_bytes()
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
sys.path.insert(0, str(REPO / "2d-unfolding" / "uq" / "coverage_fixed_truth"))
from n2 import execution as gx  # noqa: E402

HELPER_REL = "unbinned_unfolding/python/omnifold.py"
HELPER_SHA256 = "e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a"
RUNS_REL = (HERE / "manifest" / "runs.json").relative_to(REPO).as_posix()
REFS_REL = (HERE / "manifest" / "references.json").relative_to(REPO).as_posix()
CANONICAL = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
PARAMS = ("dataPOT", "mcPOT", "potScale", "nIterations", "fluxIntegral_m2_per_POT",
          "fluxIntegral_cm2_per_POT", "nNucleons")
EXIT_BACKEND = 6
GBDT = {"exact": ("GradientBoostingClassifier", "GradientBoostingRegressor"),
        "lgbm": ("LGBMClassifier", "LGBMRegressor")}
#: Shared objects whose own thread getters are read for the supporting runtime record.
RUNTIME_LIBS = (("openmp", ("libgomp", "libomp", "libiomp5"), ("omp_get_max_threads",)),
                ("blas", ("libopenblas", "libscipy_openblas", "libmkl_rt", "libblis", "libflexiblas"),
                 ("openblas_get_num_threads", "openblas_get_num_threads64_", "scipy_openblas_get_num_threads",
                  "scipy_openblas_get_num_threads64_", "MKL_Get_Max_Threads", "bli_thread_get_num_threads",
                  "flexiblas_get_num_threads")),
                ("lightgbm", ("lib_lightgbm",), ()))
EXACT_THREADS_BASIS = ("sklearn's exact GradientBoosting{Classifier,Regressor} take no thread parameter and "
                       "build their trees serially, so the exact runs train on one thread")


class BackendRefusal(RuntimeError):
    """The run did not execute the backend, seeds, threads, normalization or cells it is frozen to."""


class LaunchRefusal(BackendRefusal):
    """A child process was about to be started inside the no-launch window."""


def require_no_launch(spy):
    """Refuse when the window recorded a launch, even one a library caught and survived (loky
    swallows a failed ``lscpu`` and falls back)."""
    if spy.calls:
        raise LaunchRefusal(f"{len(spy.calls)} child launch(es) in the no-launch window: "
                            f"{[c['call'] + ' ' + c['argv'] for c in spy.calls]}")


def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 22), b""):
            h.update(block)
    return h.hexdigest()


def stat_record(path):
    st = os.stat(path)
    return {"path": str(path), "size": st.st_size, "mtime_ns": st.st_mtime_ns, "ino": st.st_ino}


def frozen_paths(refs):
    return {str(Path(r["path"])) for r in refs["references"].values()}


def check_out_path(path, repo, refs, extra_forbidden=()):
    """Refuse an output path that is aliased, inside a code tree, or a frozen product."""
    p = Path(path)
    if not p.is_absolute():
        raise gx.ProvenanceRefusal(f"output {p} is not absolute")
    real = Path(os.path.realpath(p))
    if str(real) != os.path.normpath(str(p)):
        raise gx.ProvenanceRefusal(f"output {p} resolves to {real}: a symlink or alias is in the path")
    for root in (Path(repo).resolve(), Path(CANONICAL), *map(Path, extra_forbidden)):
        try:
            real.relative_to(root)
        except ValueError:
            continue
        raise gx.ProvenanceRefusal(f"output {real} is inside {root}")
    if str(real) in frozen_paths(refs):
        raise gx.ProvenanceRefusal(f"output {real} is a frozen reference product")
    return real


def run_drivers(run, runs):
    """(driver, digest) of the run; for the preflight, of every run it stands in front of."""
    if "preflight_of" in run:
        return sorted({runs["runs"][o]["driver"]: runs["runs"][o]["driver_digest"] for o in run["preflight_of"]}.items())
    return [(run["driver"], run["driver_digest"])]


def load_code(run, expect, runs):
    """The helper, the run's drivers and, for the preflight, the fixture writer, from verified bytes."""
    records = [gx.file_record(__file__, _SELF_BYTES, REPO),
               gx.bootstrap_record(sys.modules["n2"], REPO), gx.bootstrap_record(gx, REPO)]
    helper, rec = gx.load_verified("omnifold", REPO / HELPER_REL, REPO, expect["modules"].get(HELPER_REL))
    if rec["sha256"] != HELPER_SHA256:
        raise gx.ProvenanceRefusal(f"{HELPER_REL} has sha256 {rec['sha256']}; XR pins {HELPER_SHA256}")
    records.append(rec)
    drivers = {}
    for rel, digest in run_drivers(run, runs):
        name = "xr_driver_" + Path(rel).name.split(".")[0]
        driver, rec = gx.load_verified(name, REPO / rel, REPO, expect["modules"].get(rel))
        if rec["sha256"] != digest:
            raise gx.ProvenanceRefusal(f"{rel} has sha256 {rec['sha256']}; the run pins {digest}")
        records.append(rec)
        drivers[rel] = driver
    extra = {}
    if "preflight_of" in run:
        fx = runs["preflight"]["fixture"]
        extra["maker"], rec = gx.load_verified("xr_fixture_maker", REPO / fx["maker"], REPO,
                                               expect["modules"].get(fx["maker"]))
        if rec["sha256"] != fx["maker_digest"]:
            raise gx.ProvenanceRefusal(f"{fx['maker']} has sha256 {rec['sha256']}; the preflight pins {fx['maker_digest']}")
        records.append(rec)
        compare_rel = (HERE / "xr_compare.py").relative_to(REPO).as_posix()
        extra["compare"], rec = gx.load_verified("xr_compare_verified", REPO / compare_rel, REPO,
                                                 expect["modules"].get(compare_rel))
        records.append(rec)
    return helper, drivers, extra, records


class LaunchSpy:
    """While active, refuse and record every attempt to start a child process from Python.

    It replaces ``subprocess.Popen`` and the ``os`` launch primitives, so ``subprocess.run``,
    ``ctypes.util.find_library``'s ``ldconfig`` and loky's ``lscpu`` are stopped before they reach
    the OI-136 guard's hooks, and restores them on exit. It narrows what may run; it never admits
    anything the guard would refuse."""

    NAMES = (("subprocess", "Popen"), ("os", "system"), ("os", "popen"), ("os", "posix_spawn"),
             ("os", "posix_spawnp"), ("os", "execv"), ("os", "execve"), ("os", "execvp"), ("os", "execvpe"),
             ("os", "fork"), ("os", "forkpty"), ("os", "spawnv"), ("os", "spawnve"))

    def __init__(self):
        self.calls = []
        self._saved = []

    def __enter__(self):
        import subprocess
        mods = {"subprocess": subprocess, "os": os}
        for mod_name, attr in self.NAMES:
            mod = mods[mod_name]
            if not hasattr(mod, attr):
                continue
            self._saved.append((mod, attr, getattr(mod, attr)))
            setattr(mod, attr, self._refuser(f"{mod_name}.{attr}"))
        return self

    def __exit__(self, *exc):
        for mod, attr, orig in reversed(self._saved):
            setattr(mod, attr, orig)
        self._saved = []
        return False

    def _refuser(self, name):
        def refuse(*args, **kwargs):
            argv = args[0] if args else kwargs.get("args")
            stack = [f"{Path(f.filename).name}:{f.lineno}:{f.name}" for f in traceback.extract_stack()[-8:-1]]
            self.calls.append({"call": name, "argv": repr(argv)[:300], "stack": stack})
            raise LaunchRefusal(f"{name}({argv!r}) inside the no-launch window")
        return refuse


def loaded_libraries(maps_text):
    """The distinct file paths of mapped shared objects in a ``/proc/<pid>/maps`` text."""
    out = set()
    for line in maps_text.splitlines():
        parts = line.split(None, 5)
        if len(parts) == 6 and ".so" in Path(parts[5].strip()).name:
            out.add(parts[5].strip())
    return sorted(out)


def runtime_record():
    """The loaded OpenMP, BLAS and LightGBM libraries and the thread count each reports, child-free.

    Read from ``/proc/self/maps`` and from each library's own getter through ``ctypes.CDLL`` on its
    absolute path with ``RTLD_NOLOAD`` (no ``find_library``, so no ``ldconfig``). Supporting
    evidence only: the estimator's thread count is the thread plan and the fit recorder's."""
    rec = {"source": None, "pools": [],
           "basis": "supporting record only; the estimator's threads are established by thread_plan and the fit recorder"}
    maps = Path("/proc/self/maps")
    if not maps.is_file():
        rec["source"] = f"unavailable on {sys.platform} (no /proc/self/maps)"
        return rec
    import ctypes
    rec["source"] = "/proc/self/maps"
    for path in loaded_libraries(maps.read_text()):
        name = Path(path).name
        for api, prefixes, getters in RUNTIME_LIBS:
            if not any(name.startswith(p) for p in prefixes):
                continue
            entry = {"path": path, "api": api, "getter": None, "num_threads": None}
            try:
                lib = ctypes.CDLL(path, mode=os.RTLD_NOLOAD)
            except OSError as exc:
                entry["error"] = str(exc)
                lib = None
            for g in getters if lib is not None else ():
                try:
                    fn = getattr(lib, g)
                except AttributeError:
                    continue
                fn.restype = ctypes.c_int
                entry.update(getter=g, num_threads=int(fn()))
                break
            rec["pools"].append(entry)
    return rec


def check_environment(want):
    """Refuse (before any fit) an interpreter, ROOT or package version other than the frozen one."""
    import importlib
    import platform
    import ROOT
    have = {"python": platform.python_version(), "root": str(ROOT.gROOT.GetVersion()), "packages": {}, "origins": {}}
    for name in want["packages"]:
        mod = importlib.import_module(name)
        have["packages"][name] = mod.__version__
        have["origins"][name] = getattr(mod, "__file__", None)
    have["origins"]["ROOT"] = getattr(ROOT, "__file__", None)
    bad = [k for k in ("python", "root") if have[k] != want[k]]
    bad += [n for n, v in want["packages"].items() if have["packages"][n] != v]
    if bad:
        raise BackendRefusal(f"environment differs from the frozen one in {bad}: {have}")
    have["runtime"] = runtime_record()
    return have


def thread_plan(kind):
    """The threads this kind's estimators use, established before any fit; refuse anything else.

    LightGBM's default ``n_jobs`` resolves to ``joblib.cpu_count(only_physical_cores=True)`` at every
    fit and prediction. joblib returns the user-limited count (affinity, cgroup quota,
    ``LOKY_MAX_CPU_COUNT``) when it is below the OS count, and otherwise asks for physical cores in a
    child process (``lscpu``), which the guard refuses and whose fallback undercounts a two-socket
    node. On Linux the plan therefore requires ``LOKY_MAX_CPU_COUNT`` unset, the affinity equal to
    the kind's CPUs and below the node's count, and joblib's answer equal to the kind's CPUs: the
    count an unguarded run in the same allocation gets. Off Linux (the tests) ``LOKY_MAX_CPU_COUNT``
    stands in for the affinity and must equal the kind's CPUs."""
    import joblib
    want = kind["cpus_per_task"]
    rec = {"OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"), "kind_omp_threads": kind["omp_threads"],
           "kind_cpus": want, "os_cpu_count": os.cpu_count(),
           "affinity": len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
           "LOKY_MAX_CPU_COUNT": os.environ.get("LOKY_MAX_CPU_COUNT"), "platform": sys.platform}
    if rec["OMP_NUM_THREADS"] != str(kind["omp_threads"]):
        raise BackendRefusal(f"OMP_NUM_THREADS={rec['OMP_NUM_THREADS']!r}; the kind sets {kind['omp_threads']}")
    if sys.platform.startswith("linux"):
        if rec["LOKY_MAX_CPU_COUNT"] is not None:
            raise BackendRefusal(f"LOKY_MAX_CPU_COUNT={rec['LOKY_MAX_CPU_COUNT']!r} is set; the frozen runs leave "
                                 "joblib's count to the allocation")
        if rec["affinity"] != want:
            raise BackendRefusal(f"CPU affinity {rec['affinity']} differs from the kind's {want} CPUs")
        if not rec["affinity"] < rec["os_cpu_count"]:
            raise BackendRefusal(f"CPU affinity {rec['affinity']} is not below the node's {rec['os_cpu_count']}: joblib "
                                 "would query physical cores through lscpu, which the guard refuses")
    elif rec["LOKY_MAX_CPU_COUNT"] != str(want):
        raise BackendRefusal(f"off Linux LOKY_MAX_CPU_COUNT must equal the kind's {want} CPUs, "
                             f"not {rec['LOKY_MAX_CPU_COUNT']!r}")
    rec["joblib_cpu_count_physical"] = joblib.cpu_count(only_physical_cores=True)
    rec["joblib_cpu_count_logical"] = joblib.cpu_count()
    if rec["joblib_cpu_count_physical"] != want:
        raise BackendRefusal(f"joblib resolves {rec['joblib_cpu_count_physical']} cores; the kind has {want} CPUs")
    rec["lgbm_num_threads"] = want
    rec["exact_estimator_threads"] = 1
    rec["exact_estimator_basis"] = EXACT_THREADS_BASIS
    return rec


class FitRecorder:
    """Wrap ``fit`` of the four GBDT classes and LightGBM's ``predict``; refuse an unexpected class,
    seed or LightGBM thread count. ``uninstall`` restores the classes, so runs can follow each other
    in one process (the preflight's fixture)."""

    def __init__(self, backend, threads):
        self.backend = backend
        self.threads = threads
        self.fits = []
        self.predicts = {"calls": 0, "num_threads": []}
        self.want = dict(zip(GBDT[backend["estimator"]], ("classifier", "regressor")))
        self._saved = []

    def expected_seed(self, cls_name, n_classifier_fits):
        rs = self.backend["random_state"]
        if self.want[cls_name] == "regressor":
            return rs["regressor"]
        return rs["step1"] if n_classifier_fits % 2 == 0 else rs["step2"]

    @staticmethod
    def lgbm_threads(est):
        """The thread count LightGBM resolves for this estimator (``n_jobs`` None: joblib's count)."""
        try:
            return int(est._process_n_jobs(est.get_params().get("n_jobs")))
        except AttributeError as exc:
            raise BackendRefusal(f"cannot resolve LightGBM's thread count: {exc}") from None

    def _patch(self, cls, attr, fn):
        self._saved.append((cls, attr, attr in cls.__dict__, cls.__dict__.get(attr)))
        fn.__xr_wrapped__ = getattr(cls, attr)
        setattr(cls, attr, fn)

    def install(self):
        import sklearn.ensemble as ske
        import lightgbm
        import lightgbm.sklearn as lgbm_sk
        classes = {"GradientBoostingClassifier": ske.GradientBoostingClassifier,
                   "GradientBoostingRegressor": ske.GradientBoostingRegressor,
                   "LGBMClassifier": lightgbm.LGBMClassifier, "LGBMRegressor": lightgbm.LGBMRegressor}
        for cls_name, cls in classes.items():
            orig = cls.fit

            def fit(est, *a, _orig=orig, _name=cls_name, **k):
                if _name not in self.want:
                    raise BackendRefusal(f"{_name}.fit called; run expects {self.backend['estimator']}")
                n_cls = sum(1 for f in self.fits if self.want[f["class"]] == "classifier")
                seed = est.get_params().get("random_state")
                want = self.expected_seed(_name, n_cls)
                if seed != want:
                    raise BackendRefusal(f"{_name}.fit with random_state={seed!r}; expected {want!r}")
                entry = {"class": _name, "random_state": seed, "n_rows": int(len(a[0])) if a else None,
                         "num_threads": None}
                if _name.startswith("LGBM"):
                    planned = self.lgbm_threads(est)
                    if planned != self.threads:
                        raise BackendRefusal(f"{_name}.fit would train on {planned} threads; the plan is {self.threads}")
                out = _orig(est, *a, **k)
                if _name.startswith("LGBM"):
                    used = est.booster_.params.get("num_threads")
                    if used != planned:
                        raise BackendRefusal(f"{_name} trained with num_threads={used!r}; resolved {planned}")
                    entry["num_threads"] = used
                self.fits.append(entry)
                return out
            self._patch(cls, "fit", fit)
        orig_predict = lgbm_sk.LGBMModel.predict

        def predict(est, *a, _orig=orig_predict, **k):
            n = self.lgbm_threads(est)
            self.predicts["calls"] += 1
            if n not in self.predicts["num_threads"]:
                self.predicts["num_threads"].append(n)
            if n != self.threads:
                raise BackendRefusal(f"{type(est).__name__}.predict would run on {n} threads; the plan is {self.threads}")
            return _orig(est, *a, **k)
        self._patch(lgbm_sk.LGBMModel, "predict", predict)

    def uninstall(self):
        for cls, attr, had, orig in reversed(self._saved):
            if had:
                setattr(cls, attr, orig)
            else:
                delattr(cls, attr)
        self._saved = []

    def verify_counts(self):
        it = self.backend["iterations"]
        n_c = sum(1 for f in self.fits if self.want[f["class"]] == "classifier")
        n_r = sum(1 for f in self.fits if self.want[f["class"]] == "regressor")
        if n_c != 2 * it or n_r != it:
            raise BackendRefusal(f"{n_c} classifier and {n_r} regressor fits; expected {2 * it} and {it}")
        if self.backend["estimator"] == "lgbm" and (not self.predicts["calls"] or self.predicts["num_threads"] != [self.threads]):
            raise BackendRefusal(f"LightGBM predictions {self.predicts}; expected every one on {self.threads} threads")
        return {"classifier_fits": n_c, "regressor_fits": n_r}


def read_product(path):
    """Normalization parameters, reported cells (paper GlobalID) and runConfig of an output."""
    import ROOT
    import numpy as np
    f = ROOT.TFile.Open(str(path))
    if not f or f.IsZombie():
        raise BackendRefusal(f"cannot open output {path}")
    params = {}
    for n in PARAMS:
        o = f.Get(n)
        params[n] = float(o.GetVal()) if o else None
    h = f.Get("hXSec2D")
    if not h:
        f.Close()
        raise BackendRefusal(f"output {path} has no hXSec2D")
    x = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(h.GetNbinsY())] for i in range(h.GetNbinsX())])
    rc = f.Get("runConfig")
    run_config = rc.GetTitle() if rc else None
    f.Close()
    return {"params": params, "cells": [int(i * 16 + j) for i, j in np.argwhere(x > 0)], "runConfig": run_config}


def read_output(path, refs):
    prod = read_product(path)
    want = refs["references"]["E_C"]
    bad = [n for n in PARAMS if prod["params"][n] != want["params"][n]]
    if bad:
        raise BackendRefusal(f"normalization differs from the frozen reference in {bad}: {prod['params']}")
    if prod["cells"] != want["reported_globalid"]:
        raise BackendRefusal(f"reported cells differ from the frozen 205: {len(prod['cells'])} cells")
    return {"params": prod["params"], "n_reported": len(prod["cells"]), "runConfig": prod["runConfig"]}


def execute(run, driver, subst, rec):
    """The fit path: the run's driver ``main`` on its frozen argv, under ``rec`` (installed here and
    uninstalled afterwards). Returns the driver argv and the fit counts."""
    argv = [tok.format(**subst) for tok in run["argv"]]
    rec.install()
    try:
        sys.argv = [str(driver.__file__), *argv]
        rc = driver.main()
        if rc not in (None, 0):
            raise RuntimeError(f"driver main() returned {rc!r}")
        return argv, rec.verify_counts()
    finally:
        rec.uninstall()


def fixture_stage(runs, drivers, extra, rundir, threads):
    """Every configuration end to end on a tiny synthetic fixture, then the refusal controls.

    Not a result: the fixture is synthetic, its products live only in ``<attempt>/fixture/`` and no
    comparison reads them. What it shows is the Linux fit path under the guard: the five drivers,
    their classes, seeds and fit counts, LightGBM's thread count at every fit and prediction, the
    output read-back, repeatability (L0 twice, to the frozen 1e-8 criterion; the count of
    bitwise-equal cells is recorded), the comparator in both directions, and refusals."""
    pf, maker = runs["preflight"]["fixture"], extra["maker"]
    fx = rundir / "fixture"
    fx.mkdir()
    out = {"not_a_result": "synthetic fixture: it checks the code path only", "runs": {}, "checks": {}, "controls": {}}
    t = time.perf_counter()
    omni = fx / "fixture-omni.root"
    out["inputs"] = {"omnifile": maker.write_fixture(str(omni), rows=pf["rows"], extra=pf["extra"], seed=pf["seed"]),
                     "mcfile": maker.write_flux(str(fx / "fixture-flux.root"))}
    out["inputs"]["omnifile_sha256"] = sha256_file(omni)
    out["inputs"]["write_s"] = time.perf_counter() - t
    order = list(runs["runs"]["PF"]["preflight_of"]) + [pf["repeat"] + "-repeat"]
    for name in order:
        base = name.split("-")[0]
        spec = runs["runs"][base]
        prod = fx / f"FX-{name}.root"
        rec = FitRecorder(spec["backend"], threads["lgbm_num_threads"])
        r = {"driver": spec["driver"], "status": "running"}
        t = time.perf_counter()
        try:
            r["argv"], r["fit_counts"] = execute(spec, drivers[spec["driver"]],
                                                 {"omnifile": str(omni), "mcfile": out["inputs"]["mcfile"], "out": str(prod)}, rec)
            p = read_product(prod)
            r.update(status="complete", params=p["params"], n_cells=len(p["cells"]), cells=p["cells"],
                     sha256=sha256_file(prod))
        except BaseException as exc:  # noqa: BLE001 - recorded; the stage fails below
            r.update(status="error", error=f"{type(exc).__name__}: {exc}")
        r.update(fits=rec.fits, predicts=rec.predicts, wall_s=time.perf_counter() - t)
        out["runs"][name] = r
    done = {k: v for k, v in out["runs"].items() if v["status"] == "complete"}
    ck = out["checks"]
    ck["all_complete"] = len(done) == len(order)
    if ck["all_complete"]:
        first = done[order[0]]
        ck["one_normalization_and_cell_set"] = all(v["params"] == first["params"] and v["cells"] == first["cells"]
                                                   for v in done.values()) and len(first["cells"]) > 0
        ck["frozen_classes_and_seeds"] = all(fit_sequence(done[n]["fits"], runs["runs"][n.split("-")[0]]["backend"])
                                             for n in order)
        ck["lgbm_threads_at_every_fit_and_predict"] = all(
            all(f["num_threads"] == threads["lgbm_num_threads"] for f in v["fits"])
            and v["predicts"]["num_threads"] == [threads["lgbm_num_threads"]]
            for n, v in done.items() if runs["runs"][n.split("-")[0]]["backend"]["estimator"] == "lgbm")
        cells = first["cells"]
        rep = pf["repeat"]
        same = extra["compare"].compare(fx / f"FX-{rep}-repeat.root", fx / f"FX-{rep}.root", cells)
        diff = extra["compare"].compare(fx / "FX-X0.root", fx / f"FX-{rep}.root", cells)
        out["comparator"] = {f"{rep}-repeat_vs_{rep}": same, f"X0_vs_{rep}": diff}
        ck["repeat_reproduces_to_the_criterion"] = same["verdict"] == "PASS"
        out["repeat_exactly_equal_cells"] = [same.get("exactly_equal_cells"), same.get("n_cells")]
        ck["comparator_fails_different_estimators"] = diff["verdict"] == "FAIL"
    out["controls"] = fixture_controls(runs, drivers, omni, out["inputs"]["mcfile"], fx, threads)
    out["verdict"] = "PASS" if ck.get("all_complete") and all(ck.values()) and all(
        c["met"] for c in out["controls"].values()) else "FAIL"
    return out


def fit_sequence(fits, backend):
    """True when the fits are the backend's classes only, the classifiers seeded step1, step2 in
    turn and the regressor with its seed, once per iteration each."""
    c, r = GBDT[backend["estimator"]]
    rs, it = backend["random_state"], backend["iterations"]
    return ({f["class"] for f in fits} == {c, r}
            and [f["random_state"] for f in fits if f["class"] == c] == [rs["step1"], rs["step2"]] * it
            and [f["random_state"] for f in fits if f["class"] == r] == [rs["regressor"]] * it)


def fixture_controls(runs, drivers, omni, flux, fx, threads):
    """Refusals that must fire, each before training: a wrong seed, a wrong backend, a wrong LightGBM
    thread count; and a child launch inside the no-launch window (find_library's ldconfig and loky's
    physical-core query on Linux; loky's sysctl elsewhere)."""
    import copy
    controls = {}

    def refused_before_training(name, spec, backend, threads_n, want):
        rec = FitRecorder(backend, threads_n)
        prod = fx / f"FX-control-{name}.root"
        res = {"expect": want}
        try:
            execute(spec, drivers[spec["driver"]], {"omnifile": str(omni), "mcfile": flux, "out": str(prod)}, rec)
            res.update(outcome="completed", met=False)
        except BackendRefusal as exc:
            res.update(outcome="refused", error=str(exc), met=want in str(exc) and rec.fits == [])
        except BaseException as exc:  # noqa: BLE001
            res.update(outcome=type(exc).__name__, error=str(exc), met=False)
        res["fits"] = rec.fits
        controls[name] = res

    l1 = runs["runs"]["L1"]
    bad_seed = copy.deepcopy(l1["backend"])
    bad_seed["random_state"]["step1"] = 7
    refused_before_training("wrong_seed", l1, bad_seed, threads["lgbm_num_threads"], "random_state=1")
    l0 = runs["runs"]["L0"]
    refused_before_training("wrong_backend", l0, runs["runs"]["X0"]["backend"], threads["lgbm_num_threads"],
                            "LGBMClassifier.fit called; run expects exact")
    refused_before_training("wrong_lgbm_threads", l0, l0["backend"], threads["lgbm_num_threads"] + 1,
                            "would train on")
    controls["launch_window"] = launch_controls()
    return controls


def launch_controls():
    """Inside a fresh LaunchSpy: the calls that launched children before must be refused here."""
    import ctypes.util
    from joblib.externals.loky.backend import context as loky_context
    probes = [("loky_physical_cores", lambda: loky_context._count_physical_cores_linux()
               if sys.platform.startswith("linux") else loky_context._count_physical_cores_darwin())]
    if sys.platform.startswith("linux"):
        probes.insert(0, ("find_library_c", lambda: ctypes.util.find_library("c")))
    res = {"platform": sys.platform, "probes": {}}
    for name, probe in probes:
        with LaunchSpy() as spy:
            try:
                probe()
                outcome = "returned"
            except LaunchRefusal:
                outcome = "refused"
            except BaseException as exc:  # noqa: BLE001 - loky swallows some refusals; the spy's record decides
                outcome = f"{type(exc).__name__}: {exc}"
        res["probes"][name] = {"outcome": outcome, "launches": spy.calls}
    res["met"] = all(p["launches"] for p in res["probes"].values())
    return res


def job_controls(rundir):
    """The two controls the job script runs before this process (``launch/xr_job.sbatch``): the real
    allocation checked against another kind's caps must be refused, and a guarded child that
    reaches ``ldconfig`` (Linux; ``sysctl`` elsewhere) must be refused by the OI-136 guard."""
    ctl = rundir / "controls"
    res = {}
    for name, want_rc, want_text in (("jobcheck_other_kind", "3", "allocation outside the frozen caps"),
                                     ("guard_refuses_launch", None, "[oi136 launch]")):
        rc_p, err_p = ctl / f"{name}.rc", ctl / f"{name}.err"
        if not (rc_p.is_file() and err_p.is_file()):
            res[name] = {"met": False, "why": f"no record in {ctl}"}
            continue
        rc, err = rc_p.read_text().strip(), err_p.read_text()
        met = (rc == want_rc if want_rc else rc not in ("", "0")) and want_text in err
        if name == "guard_refuses_launch":
            target = "ldconfig" if sys.platform.startswith("linux") else "sysctl"
            met = met and target in err
        res[name] = {"met": met, "rc": rc, "stderr_tail": err[-600:]}
    return res


def preflight(a, runs, kind, identity, inputs, env, receipt_path, rundir, drivers, extra, t0):
    """Everything a run does before its first fit on the production inputs, the fixture stage and
    the controls, then a preflight receipt; no driver ``main`` on the production inputs."""
    receipt = {"schema": "xr-preflight-receipt/2", "run": a.run, "attempt": a.attempt, "kind": "preflight",
               "not_a_result": "preflight only: its fixture products are synthetic; it cannot satisfy any comparison",
               "admission": {"path": str(Path(a.admission).resolve()), "sha256": sha256_file(a.admission)},
               "preflight_of": runs["runs"][a.run]["preflight_of"], "started_utc": utc(), "status": "running",
               "identity": identity, "inputs_start": inputs, "environment": env, "fits": []}
    alloc = rundir / "scontrol-job.txt"
    if alloc.is_file():
        receipt["allocation_record"] = {"path": str(alloc), "sha256": sha256_file(alloc), "line": alloc.read_text()}

    def write(**upd):
        receipt.update(upd)
        tmp = receipt_path.with_name(receipt_path.name + ".tmp")
        tmp.write_text(json.dumps(receipt, indent=1, sort_keys=True, default=str) + "\n")
        os.replace(tmp, receipt_path)

    write()
    status, code, error = "preflight-pass", 0, None
    spy = LaunchSpy()
    try:
        with spy:
            receipt["environment_checked"] = check_environment(runs["environment"])
            receipt["threads"] = thread_plan(kind)
            receipt["identity"] = gx.recheck(REPO, identity)
            for key, spec in runs["inputs"].items():
                st = stat_record(spec["path"])
                if any(st[k] != inputs[key][k] for k in ("size", "mtime_ns", "ino")):
                    raise gx.ProvenanceRefusal(f"input {key} changed during the preflight")
            write()
            receipt["fixture"] = fixture_stage(runs, drivers, extra, rundir, receipt["threads"])
            receipt["identity"] = gx.recheck(REPO, receipt["identity"])
        receipt["controls"] = job_controls(rundir)
        require_no_launch(spy)
        if receipt["fixture"]["verdict"] != "PASS":
            raise BackendRefusal(f"fixture stage {receipt['fixture']['verdict']}: checks {receipt['fixture']['checks']}, "
                                 f"controls {[k for k, c in receipt['fixture']['controls'].items() if not c['met']]}")
        if not all(c["met"] for c in receipt["controls"].values()):
            raise BackendRefusal(f"job controls not met: {[k for k, c in receipt['controls'].items() if not c['met']]}")
    except BackendRefusal as exc:
        status, code, error = "preflight-fail", EXIT_BACKEND, str(exc)
    except gx.ProvenanceRefusal as exc:
        status, code, error = "preflight-fail", gx.REFUSAL_EXIT, str(exc)
    except BaseException as exc:  # noqa: BLE001 - recorded, then reported by exit status
        status, code, error = "preflight-fail", 1, f"{type(exc).__name__}: {exc}"
    write(status=status, error=error, exit_code=code, launches=spy.calls, ended_utc=utc(),
          wall_s=time.perf_counter() - t0)
    print(f"[XR] {status}" + (f": {error}" if error else ""), file=sys.stderr)
    return code


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--attempt", required=True, type=int)
    ap.add_argument("--admission", required=True)
    ap.add_argument("--require-provenance", action="store_true")
    a = ap.parse_args(argv)
    t0 = time.perf_counter()
    try:
        adm = json.loads(Path(a.admission).read_text())
        if adm.get("status") != "ADMITTED":
            raise gx.ProvenanceRefusal(f"admission status is {adm.get('status')!r}, not ADMITTED")
        if Path(adm["checkout"]).resolve() != REPO:
            raise gx.ProvenanceRefusal(f"admission names checkout {adm['checkout']}, this is {REPO}")
        runs_bytes = (REPO / RUNS_REL).read_bytes()
        refs_bytes = (REPO / REFS_REL).read_bytes()
        if gx.sha256_hex(runs_bytes) != adm["runs_sha256"] or gx.sha256_hex(refs_bytes) != adm["references_sha256"]:
            raise gx.ProvenanceRefusal("runs.json or references.json differs from the admitted digest")
        runs, refs = json.loads(runs_bytes), json.loads(refs_bytes)
        if adm["outroot"] != runs["outroot"]:
            raise gx.ProvenanceRefusal(f"admission outroot {adm['outroot']} is not the frozen {runs['outroot']}")
        if a.run not in runs["runs"]:
            raise gx.ProvenanceRefusal(f"unknown run {a.run!r}")
        run = runs["runs"][a.run]
        kind = runs["kinds"][run["kind"]]
        if not 1 <= a.attempt <= kind["max_attempts_total"]:
            raise gx.ProvenanceRefusal(f"attempt {a.attempt} outside 1..{kind['max_attempts_total']}")
        expect = gx.load_expectations(None)
        expect.update(adm["expect"][a.run])
        helper, drivers, extra, records = load_code(run, expect, runs)
        identity = gx.finalize(REPO, records, expect, a.require_provenance)
        if Path.cwd().resolve() != REPO / "2d-unfolding":
            raise gx.ProvenanceRefusal(f"working directory is {Path.cwd()}, not {REPO / '2d-unfolding'}")
        forbid = [str(Path(spec["path"]).parent) for spec in runs["inputs"].values()]
        rundir = check_out_path(os.path.join(adm["outroot"], a.run, f"a{a.attempt}"), REPO, refs, forbid)
        if not rundir.is_dir():
            raise gx.ProvenanceRefusal(f"run directory {rundir} does not exist (the submit script creates it)")
        if run["kind"] == "preflight":
            out = None
            receipt_path = check_out_path(str(rundir / "preflight-receipt.json"), REPO, refs, forbid)
            gx.reserve_output(str(receipt_path))
        else:
            out = check_out_path(str(rundir / f"XR-{a.run}.root"), REPO, refs, forbid)
            receipt_path = check_out_path(str(rundir / "receipt.json"), REPO, refs, forbid)
            gx.reserve_output(str(receipt_path))
            gx.reserve_output(str(out))
        inputs = {}
        for key, spec in runs["inputs"].items():
            if expect["inputs"].get(key) != spec["sha256"]:
                raise gx.ProvenanceRefusal(f"admitted digest for {key} differs from runs.json")
            st = stat_record(spec["path"])
            digest = sha256_file(spec["path"])
            if digest != spec["sha256"] or st["size"] != spec["size"]:
                raise gx.ProvenanceRefusal(f"input {key} {spec['path']} has sha256 {digest}, size {st['size']}")
            inputs[key] = dict(st, sha256=digest)
    except gx.ProvenanceRefusal as exc:
        print(f"[REFUSED] {exc}", file=sys.stderr)
        return gx.REFUSAL_EXIT

    env = gx.environment_record()
    env.update(slurm={k: os.environ.get(k) for k in ("SLURM_JOB_ID", "SLURM_JOB_QOS", "SLURM_CPUS_PER_TASK",
                                                      "SLURM_MEM_PER_NODE", "SLURMD_NODENAME")},
               cwd=str(Path.cwd()), uname=list(os.uname()),
               affinity_cpus=len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None)
    if run["kind"] == "preflight":
        return preflight(a, runs, kind, identity, inputs, env, receipt_path, rundir, drivers, extra, t0)
    driver = drivers[run["driver"]]
    subst = {"omnifile": runs["inputs"]["omnifile"]["path"], "mcfile": runs["inputs"]["mcfile"]["path"], "out": str(out)}
    receipt = {"schema": "xr-receipt/2", "run": a.run, "attempt": a.attempt, "kind": run["kind"],
               "admission": {"path": str(Path(a.admission).resolve()), "sha256": sha256_file(a.admission)},
               "driver": run["driver"], "driver_argv": [tok.format(**subst) for tok in run["argv"]],
               "backend_expected": run["backend"], "started_utc": utc(), "status": "running", "identity": identity,
               "inputs_start": inputs, "environment": env}

    def write(**upd):
        receipt.update(upd)
        tmp = receipt_path.with_name(receipt_path.name + ".tmp")
        tmp.write_text(json.dumps(receipt, indent=1, sort_keys=True, default=str) + "\n")
        os.replace(tmp, receipt_path)

    write()
    rec = None
    status, code, error = "complete", 0, None
    spy = LaunchSpy()
    try:
        with spy:
            receipt["environment_checked"] = check_environment(runs["environment"])
            receipt["threads"] = thread_plan(kind)
            write()
            rec = FitRecorder(run["backend"], receipt["threads"]["lgbm_num_threads"])
            _, counts = execute(run, driver, subst, rec)
            identity = gx.recheck(REPO, identity)
            inputs_end = {}
            for key, spec in runs["inputs"].items():
                st = stat_record(spec["path"])
                if any(st[k] != inputs[key][k] for k in ("size", "mtime_ns", "ino")) or sha256_file(spec["path"]) != spec["sha256"]:
                    raise gx.ProvenanceRefusal(f"input {key} changed during the run")
                inputs_end[key] = st
            output = read_output(out, refs)
            output.update(path=str(out), sha256=sha256_file(out), bytes=os.path.getsize(out))
        require_no_launch(spy)
        write(fits=rec.fits, predicts=rec.predicts, fit_counts=counts, inputs_end=inputs_end, output=output,
              identity=identity)
    except BackendRefusal as exc:
        status, code, error = "backend-refused", EXIT_BACKEND, str(exc)
    except gx.ProvenanceRefusal as exc:
        status, code, error = "refused-late", gx.REFUSAL_EXIT, str(exc)
    except SystemExit as exc:
        status, code, error = "driver-exit", exc.code if isinstance(exc.code, int) else 1, repr(exc)
    except BaseException as exc:  # noqa: BLE001 - recorded, then reported by exit status
        status, code, error = "error", 1, f"{type(exc).__name__}: {exc}"
    write(status=status, error=error, exit_code=code, fits=rec.fits if rec else [],
          predicts=rec.predicts if rec else None, launches=spy.calls, ended_utc=utc(),
          wall_s=time.perf_counter() - t0)
    if error:
        print(f"[XR] {status}: {error}", file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
