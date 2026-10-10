#!/usr/bin/env python3
"""XR wrapper: run one frozen central-reproduction run (X0, X0p, X1, L0, L1) under strict provenance.

    xr_run.py --run X0 --attempt 1 --admission ADMISSION.json [--require-provenance]

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
5. both inputs are hashed and must equal the frozen digests.

During the run, every ``fit`` of the four GBDT classes is recorded with its class and
``random_state``. A fit of a class the run does not expect, or a wrong ``random_state``, stops the
run before training (exit 6). After it: the fit counts, the inputs (re-hashed), the output's
normalization parameters and reported-cell set are checked against the frozen references, and the
output's sha256 is recorded.

Exit: 0 complete; 3 provenance or path refusal; 6 backend, normalization or cell refusal; 1 other.
"""

import argparse
import datetime
import hashlib
import json
import os
import sys
import time
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


class BackendRefusal(RuntimeError):
    """The run did not execute the backend, seeds, normalization or cells it is frozen to."""


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


def load_code(run, expect):
    records = [gx.file_record(__file__, _SELF_BYTES, REPO),
               gx.bootstrap_record(sys.modules["n2"], REPO), gx.bootstrap_record(gx, REPO)]
    helper, rec = gx.load_verified("omnifold", REPO / HELPER_REL, REPO, expect["modules"].get(HELPER_REL))
    if rec["sha256"] != HELPER_SHA256:
        raise gx.ProvenanceRefusal(f"{HELPER_REL} has sha256 {rec['sha256']}; XR pins {HELPER_SHA256}")
    records.append(rec)
    name = "xr_driver_" + Path(run["driver"]).name.split(".")[0]
    driver, rec = gx.load_verified(name, REPO / run["driver"], REPO, expect["modules"].get(run["driver"]))
    if rec["sha256"] != run["driver_digest"]:
        raise gx.ProvenanceRefusal(f"{run['driver']} has sha256 {rec['sha256']}; the run pins {run['driver_digest']}")
    records.append(rec)
    return helper, driver, records


def physical_cores():
    """The node's physical-core count without starting a child process, and how it was read.

    LightGBM's default ``n_jobs`` asks joblib/loky for the physical-core count, and loky runs
    ``lscpu --parse=core`` (Linux) or ``sysctl -n hw.physicalcpu`` (macOS) in a child process,
    which the OI-136 guard refuses (neither is a leaf tool). The same number is read here from
    ``/proc/cpuinfo`` (unique physical id / core id pairs, as ``lscpu``'s unique core column) or
    from ``sysctlbyname`` through ctypes, and seeded into loky's own cache, so LightGBM's thread
    count is what it would be unguarded. No estimator setting changes.
    """
    if sys.platform == "linux":
        pairs, phys, core = set(), None, None
        with open("/proc/cpuinfo") as fh:
            for line in fh:
                k, _, v = line.partition(":")
                k = k.strip()
                if k == "physical id":
                    phys = v.strip()
                elif k == "core id":
                    core = v.strip()
                elif not k and core is not None:
                    pairs.add((phys, core))
                    phys = core = None
        if core is not None:
            pairs.add((phys, core))
        return len(pairs), "/proc/cpuinfo unique (physical id, core id)"
    if sys.platform == "darwin":
        import ctypes
        import ctypes.util
        libc = ctypes.CDLL(ctypes.util.find_library("c"))
        n = ctypes.c_int(0)
        size = ctypes.c_size_t(ctypes.sizeof(n))
        if libc.sysctlbyname(b"hw.physicalcpu", ctypes.byref(n), ctypes.byref(size), None, ctypes.c_size_t(0)):
            raise BackendRefusal("sysctlbyname(hw.physicalcpu) failed")
        return n.value, "sysctlbyname hw.physicalcpu"
    raise BackendRefusal(f"no child-free physical-core count for platform {sys.platform}")


def seed_loky_cache():
    from joblib.externals.loky.backend import context as loky_context
    import joblib
    n, source = physical_cores()
    if n < 1:
        raise BackendRefusal(f"physical-core count {n} from {source}")
    loky_context.physical_cores_cache = n
    return {"physical_cores": n, "source": source,
            "joblib_cpu_count_physical": joblib.cpu_count(only_physical_cores=True),
            "joblib_cpu_count_logical": joblib.cpu_count()}


class FitRecorder:
    """Wrap ``fit`` of the four GBDT classes; refuse an unexpected class or seed before training."""

    def __init__(self, backend):
        self.backend = backend
        self.fits = []
        self.want = dict(zip(GBDT[backend["estimator"]], ("classifier", "regressor")))

    def expected_seed(self, cls_name, n_classifier_fits):
        rs = self.backend["random_state"]
        if self.want[cls_name] == "regressor":
            return rs["regressor"]
        return rs["step1"] if n_classifier_fits % 2 == 0 else rs["step2"]

    def install(self):
        import sklearn.ensemble as ske
        import lightgbm
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
                self.fits.append({"class": _name, "random_state": seed, "n_rows": int(len(a[0])) if a else None})
                return _orig(est, *a, **k)
            fit.__xr_wrapped__ = orig
            cls.fit = fit

    def verify_counts(self):
        it = self.backend["iterations"]
        n_c = sum(1 for f in self.fits if self.want[f["class"]] == "classifier")
        n_r = sum(1 for f in self.fits if self.want[f["class"]] == "regressor")
        if n_c != 2 * it or n_r not in (0, it):
            raise BackendRefusal(f"{n_c} classifier and {n_r} regressor fits; expected {2 * it} and {it} (or 0)")
        return {"classifier_fits": n_c, "regressor_fits": n_r}


def read_output(path, refs):
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
    x = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(h.GetNbinsY())] for i in range(h.GetNbinsX())])
    rc = f.Get("runConfig")
    run_config = rc.GetTitle() if rc else None
    f.Close()
    cells = [int(i * 16 + j) for i, j in np.argwhere(x > 0)]
    want = refs["references"]["E_C"]
    bad = [n for n in PARAMS if params[n] != want["params"][n]]
    if bad:
        raise BackendRefusal(f"normalization differs from the frozen reference in {bad}: {params}")
    if cells != want["reported_globalid"]:
        raise BackendRefusal(f"reported cells differ from the frozen 205: {len(cells)} cells")
    return {"params": params, "n_reported": len(cells), "runConfig": run_config}


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
        if a.run not in runs["runs"]:
            raise gx.ProvenanceRefusal(f"unknown run {a.run!r}")
        run = runs["runs"][a.run]
        kind = runs["kinds"][run["kind"]]
        if not 1 <= a.attempt <= kind["max_attempts_total"]:
            raise gx.ProvenanceRefusal(f"attempt {a.attempt} outside 1..{kind['max_attempts_total']}")
        expect = gx.load_expectations(None)
        expect.update(adm["expect"][a.run])
        helper, driver, records = load_code(run, expect)
        identity = gx.finalize(REPO, records, expect, a.require_provenance)
        if Path.cwd().resolve() != REPO / "2d-unfolding":
            raise gx.ProvenanceRefusal(f"working directory is {Path.cwd()}, not {REPO / '2d-unfolding'}")
        forbid = [str(Path(spec["path"]).parent) for spec in runs["inputs"].values()]
        rundir = check_out_path(os.path.join(adm["outroot"], a.run, f"a{a.attempt}"), REPO, refs, forbid)
        if not rundir.is_dir():
            raise gx.ProvenanceRefusal(f"run directory {rundir} does not exist (the submit script creates it)")
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

    subst = {"omnifile": runs["inputs"]["omnifile"]["path"], "mcfile": runs["inputs"]["mcfile"]["path"], "out": str(out)}
    driver_argv = [tok.format(**subst) for tok in run["argv"]]
    env = gx.environment_record()
    env.update(slurm={k: os.environ.get(k) for k in ("SLURM_JOB_ID", "SLURM_JOB_QOS", "SLURM_CPUS_PER_TASK",
                                                      "SLURM_MEM_PER_NODE", "SLURMD_NODENAME")},
               cwd=str(Path.cwd()), uname=list(os.uname()),
               affinity_cpus=len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None)
    receipt = {"schema": "xr-receipt/1", "run": a.run, "attempt": a.attempt, "kind": run["kind"],
               "admission": {"path": str(Path(a.admission).resolve()), "sha256": sha256_file(a.admission)},
               "driver": run["driver"], "driver_argv": driver_argv, "backend_expected": run["backend"],
               "started_utc": utc(), "status": "running", "identity": identity, "inputs_start": inputs,
               "environment": env}

    def write(**upd):
        receipt.update(upd)
        tmp = receipt_path.with_name(receipt_path.name + ".tmp")
        tmp.write_text(json.dumps(receipt, indent=1, sort_keys=True, default=str) + "\n")
        os.replace(tmp, receipt_path)

    write()
    rec = FitRecorder(run["backend"])
    status, code, error = "complete", 0, None
    try:
        receipt["cpu_count"] = seed_loky_cache()
        rec.install()
        sys.argv = [str(REPO / run["driver"]), *driver_argv]
        rc = driver.main()
        if rc not in (None, 0):
            raise RuntimeError(f"driver main() returned {rc!r}")
        identity = gx.recheck(REPO, identity)
        counts = rec.verify_counts()
        inputs_end = {}
        for key, spec in runs["inputs"].items():
            st = stat_record(spec["path"])
            if any(st[k] != inputs[key][k] for k in ("size", "mtime_ns", "ino")) or sha256_file(spec["path"]) != spec["sha256"]:
                raise gx.ProvenanceRefusal(f"input {key} changed during the run")
            inputs_end[key] = st
        output = read_output(out, refs)
        output.update(path=str(out), sha256=sha256_file(out), bytes=os.path.getsize(out))
        write(fits=rec.fits, fit_counts=counts, inputs_end=inputs_end, output=output, identity=identity)
    except BackendRefusal as exc:
        status, code, error = "backend-refused", EXIT_BACKEND, str(exc)
    except gx.ProvenanceRefusal as exc:
        status, code, error = "refused-late", gx.REFUSAL_EXIT, str(exc)
    except SystemExit as exc:
        status, code, error = "driver-exit", exc.code if isinstance(exc.code, int) else 1, repr(exc)
    except BaseException as exc:  # noqa: BLE001 - recorded, then reported by exit status
        status, code, error = "error", 1, f"{type(exc).__name__}: {exc}"
    write(status=status, error=error, exit_code=code, fits=rec.fits, ended_utc=utc(),
          wall_s=time.perf_counter() - t0)
    if error:
        print(f"[XR] {status}: {error}", file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
