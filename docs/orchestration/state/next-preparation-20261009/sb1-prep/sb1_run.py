#!/usr/bin/env python3
"""SB1 benchmark wrapper: run the pinned 2D driver (or only its loaders) with or without prototype 1.

    sb1_run.py unfold  --arm {all,selective} --receipt R [options] -- <driver argv>
    sb1_run.py loaders --arm {all,selective} --receipt R --omnifile F [--universe B:I]
                       [--trees T[,T...]] [--negative-control {omit,extra}:BRANCH] [options]

``--arm all`` is production: every branch active, the pinned loaders unchanged. ``--arm selective``
is prototype 1 (``branch_select.py``): each loader's branch set is derived from its own accesses and
only those branches are active while it runs. Both arms run through the same hooks, which time each
phase and record the sha256 (dtype, shape and bytes) of every array each loader returns and of the
histogram it fills, so the two arms differ only in branch activation.

``unfold`` runs the driver's own ``main()`` with ``<driver argv>``; nothing in the driver or the
OmniFold helper is edited. The helper's ``omnifold`` and seven driver functions are wrapped in
memory, in both arms, to time them. ``loaders`` runs the four loaders with the arguments ``main()``
passes them and trains nothing. ``--compare-digests REF`` compares each loader's digests with an
``--arm all`` receipt as soon as the loader returns and stops (exit 4) before training on the first
difference.

Provenance (``2d-unfolding/uq/coverage_fixed_truth/n2/execution.py``, called, not copied). This file,
``branch_select.py``, the driver and the helper are executed from hashed bytes of this checkout
before any input is read; the driver must also equal ``DRIVER_SHA256``. Registering the helper as
``sys.modules["omnifold"]`` before ``main()`` runs is what makes the driver's ``from omnifold
import ...`` use this checkout's file instead of the one under the hardcoded
``/pscratch/.../MINERvA-OmniFold`` it inserts at ``sys.path[0]`` (OI-136).
``--require-provenance`` refuses unless the run is under ``nd-unfolding/mnv_guarded_run.py`` on this
checkout with every executed file at HEAD and stated by ``--expect``, every input digest stated and
matched by an ``--input-hashes`` record whose size, mtime and inode equal the file's at start and
at end, and the receipt and output paths new.

Exit status: 0 done; 3 provenance or input refusal; 4 an input array differs from the reference;
5 the branch selection was refused; 1 anything else. A receipt is written on every path after the
provenance check.
"""

import argparse
import datetime
import inspect
import json
import os
import resource
import sys
import time
from pathlib import Path

_SELF_BYTES = Path(__file__).read_bytes()

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
N2_PARENT = REPO / "2d-unfolding" / "uq" / "coverage_fixed_truth"
sys.path.insert(0, str(N2_PARENT))

from n2 import execution as gx  # noqa: E402

DRIVER_REL = "2d-unfolding/unfold_2d_omnifold_unbinned.py"
HELPER_REL = "unbinned_unfolding/python/omnifold.py"
#: The unmodified loaders SB1 compares against (driver blob e19aeb6d). Enforced on every run. The
#: helper's digest (``HELPER_SHA256``, unchanged since 5ac9706a) is enforced through ``--expect``,
#: which the admission manifest states and strict mode requires.
DRIVER_SHA256 = "3cc5adc7306b3043c2fd147602d866b90162644523b64060462aa4d934766933"
HELPER_SHA256 = "e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a"
CODE = (("branch_select", HERE / "branch_select.py"),
        ("unfold_2d_omnifold_unbinned", REPO / DRIVER_REL),
        ("omnifold", REPO / HELPER_REL))
LOADERS = ("fill_data_reco_2d", "fill_bkg_reco_2d", "collect_signal_arrays_2d",
           "collect_truth_denom_arrays")
TIMED = ("build_measured_training_2d", "compute_efficiency_2d", "compute_omnifold_completeness_2d",
         "extract_cross_section_2d", "project_xsec_1d")
TREE_OF = {"data": "fill_data_reco_2d", "mc_background": "fill_bkg_reco_2d",
           "mc_signal_reco": "collect_signal_arrays_2d", "mc_truth_denom": "collect_truth_denom_arrays"}
SLURM_ENV = ("SLURM_JOB_ID", "SLURM_ARRAY_JOB_ID", "SLURM_ARRAY_TASK_ID", "SLURM_JOB_QOS",
             "SLURM_JOB_PARTITION", "SLURMD_NODENAME", "SLURM_CPUS_PER_TASK", "SLURM_CPUS_ON_NODE",
             "SLURM_MEM_PER_NODE", "SLURM_MEM_PER_CPU")
OMP_ENV = ("OMP_PROC_BIND", "OMP_PLACES", "OMP_WAIT_POLICY", "GOMP_SPINCOUNT")
EXIT_MISMATCH, EXIT_SELECTION = 4, 5

bs = u2d = ofh = None


class DigestMismatch(RuntimeError):
    """A loader returned different bytes from the reference receipt."""


def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def proc_io():
    """``/proc/self/io`` counters (Linux), else None."""
    try:
        with open("/proc/self/io") as fh:
            return {k: int(v) for k, v in (line.split(":") for line in fh)}
    except OSError:
        return None


def maxrss():
    """Peak RSS of this process so far, in bytes (``ru_maxrss`` is KiB on Linux, bytes on macOS)."""
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(r) if sys.platform == "darwin" else int(r) * 1024


class Timeline:
    """Start/end of every hooked call, with the I/O counters and peak RSS at each boundary."""

    def __init__(self):
        self.t0 = time.perf_counter()
        self.events = []

    def mark(self, name):
        ev = {"name": name, "start_s": time.perf_counter() - self.t0, "io_start": proc_io()}
        self.events.append(ev)
        return ev

    def close(self, ev):
        ev.update(end_s=time.perf_counter() - self.t0, io_end=proc_io(), maxrss_end_bytes=maxrss())

    def wrap(self, name, func):
        def timed(*args, **kwargs):
            ev = self.mark(name)
            try:
                return func(*args, **kwargs)
            finally:
                self.close(ev)
        timed.__sb1_wrapped__ = func
        return timed


class Receipt:
    """The run record, written atomically at every checkpoint and on every exit path."""

    def __init__(self, path, base):
        self.path = Path(path)
        self.data = dict(base)

    def write(self, **update):
        self.data.update(update)
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps(self.data, indent=1, sort_keys=True, default=str) + "\n")
        os.replace(tmp, self.path)


def load_code(expectations):
    """Execute this file's repository code from verified bytes; return the executed-file records."""
    global bs, u2d, ofh
    records = [gx.file_record(__file__, _SELF_BYTES, REPO),
               gx.bootstrap_record(sys.modules["n2"], REPO), gx.bootstrap_record(gx, REPO)]
    loaded = {}
    for name, path in CODE:
        try:
            rel = path.resolve().relative_to(REPO).as_posix()
        except ValueError:
            raise gx.ProvenanceRefusal(f"{name}: {path} resolves outside the admitted checkout "
                                       f"{REPO}") from None
        loaded[name], rec = gx.load_verified(name, path, REPO, expectations["modules"].get(rel))
        records.append(rec)
    by_rel = {r["relpath"]: r["sha256"] for r in records}
    if by_rel.get(DRIVER_REL) != DRIVER_SHA256:
        raise gx.ProvenanceRefusal(f"{DRIVER_REL} has sha256 {by_rel.get(DRIVER_REL)}; SB1 "
                                   f"compares the pinned loaders {DRIVER_SHA256}")
    bs, u2d = loaded["branch_select"], loaded["unfold_2d_omnifold_unbinned"]
    ofh = loaded["omnifold"].OmniFold_helper_functions
    return records


def stat_record(path):
    st = os.stat(path)
    return {"path": str(Path(path).resolve()), "size": st.st_size, "mtime_ns": st.st_mtime_ns,
            "ino": st.st_ino}


def check_inputs(inputs, expectations, hashes_path, strict):
    """Stat every input; with a hash record, require its digest and the same size/mtime/inode."""
    hashes = json.loads(Path(hashes_path).read_text())["files"] if hashes_path else {}
    out = {}
    for key, path in inputs.items():
        rec = stat_record(path)
        want = expectations["inputs"].get(key)
        seen = hashes.get(rec["path"])
        if strict and (want is None or seen is None):
            raise gx.ProvenanceRefusal(f"strict provenance needs a stated digest and a hash record "
                                       f"for input {key} ({rec['path']})")
        if seen is not None:
            same = {k: seen.get(k) == rec[k] for k in ("size", "mtime_ns", "ino")}
            if not all(same.values()):
                raise gx.ProvenanceRefusal(f"input {key} differs from its hash record: {same}")
            if want is not None and seen.get("sha256") != want:
                raise gx.ProvenanceRefusal(f"input {key} was hashed as {seen.get('sha256')}, "
                                           f"expected {want}")
        rec.update(key=key, sha256_stated=want,
                   sha256_hashed=seen.get("sha256") if seen else None)
        out[key] = rec
    return out


def driver_inputs(argv):
    """The input files and output a driver argv names; refuses modes that are not SB1's."""
    ap = argparse.ArgumentParser(add_help=False)
    for flag in ("--omnifile", "--mcfile", "--universe", "--out", "--bkg-mode"):
        ap.add_argument(flag)
    ap.add_argument("--flux-universe-file", default="baseline_flux/flux_integral_universes_MEFHC.root")
    ap.add_argument("--closure", action="store_true")
    ap.add_argument("--closure-alt-universe")
    a, _ = ap.parse_known_args(argv)
    if a.closure or a.closure_alt_universe:
        raise gx.ProvenanceRefusal("closure modes are not part of SB1")
    if not (a.omnifile and a.mcfile and a.out):
        raise gx.ProvenanceRefusal("SB1 states --omnifile, --mcfile and --out explicitly")
    inputs = {"omnifile": a.omnifile, "mcfile": a.mcfile}
    if a.universe and a.universe.partition(":")[0] == "Flux":
        inputs["flux_universe_file"] = a.flux_universe_file
    return inputs, a.out


def reference_digests(path, argv_key):
    ref = json.loads(Path(path).read_text())
    if ref.get("status") != "complete" or ref.get("arm") != "all":
        raise gx.ProvenanceRefusal(f"reference {path} is not a complete --arm all receipt")
    if ref.get("comparison_key") != argv_key:
        raise gx.ProvenanceRefusal(f"reference {path} ran {ref.get('comparison_key')}, "
                                   f"not {argv_key}")
    return {r["tree"]: r for r in ref["loaders"]}


def install_hooks(arm, timeline, receipt, reference, control):
    records = []

    def hook(name):
        orig = getattr(u2d, name)
        hist_arg = {"fill_data_reco_2d": "h_data_2d", "fill_bkg_reco_2d": "h_bkg_2d"}.get(name)

        def loader(*args, **kwargs):
            tree, rest = args[0], args[1:]
            settings = bs.bound_settings(orig, rest, kwargs)
            ev = timeline.mark(f"load:{name}")
            try:
                if arm == "selective":
                    kw = dict(kwargs)
                    if control and control["tree"] == tree.GetName():
                        kw[control["kind"]] = (control["branch"],)
                    result, rec = bs.call_selective(orig, tree, *rest, **kw)
                else:
                    result, rec = bs.call_all(orig, tree, *rest, **kwargs)
            finally:
                timeline.close(ev)
            ev = timeline.mark(f"digest:{name}")
            hist = (inspect.signature(orig).bind(*args, **kwargs).arguments.get(hist_arg)
                    if hist_arg else None)
            rec.update(bs.result_digests(name, result, hist), tree=tree.GetName(),
                       entries=int(tree.GetEntries()), settings=settings)
            timeline.close(ev)
            records.append(rec)
            receipt.write(loaders=records, phases=timeline.events)
            if reference is not None:
                want = reference.get(tree.GetName())
                if want is None or want["digests"] != rec["digests"] or \
                        want["settings"] != rec["settings"]:
                    diff = sorted(k for k in rec["digests"]
                                  if want is None or want["digests"].get(k) != rec["digests"][k])
                    raise DigestMismatch(f"{name} on {tree.GetName()}: differs from the reference "
                                         f"in {diff or 'settings'}")
            return result
        loader.__sb1_wrapped__ = orig
        setattr(u2d, name, loader)

    for name in LOADERS:
        hook(name)
    for name in TIMED:
        setattr(u2d, name, timeline.wrap(name, getattr(u2d, name)))
    ofh.omnifold = timeline.wrap("omnifold", ofh.__dict__["omnifold"])
    return records


def run_loaders(args, timeline):
    """The four loaders with ``main()``'s arguments (driver 1306-1440), on one open file."""
    ROOT = u2d.ROOT
    f_in = ROOT.TFile.Open(args.omnifile, "READ")
    if not f_in or f_in.IsZombie():
        raise RuntimeError(f"cannot open {args.omnifile}")
    _, _, pot_scale = u2d.get_pot_scales(f_in)
    pt_lo, pt_hi = u2d.PT_EDGES[0], u2d.PT_EDGES[-1]
    pz_lo, pz_hi = u2d.PZ_EDGES[0], u2d.PZ_EDGES[-1]
    ub = None
    if args.universe:
        band, _, idx = args.universe.partition(":")
        ub = (band, int(idx))
    for tree_name in args.trees:
        t = f_in.Get(tree_name)
        if tree_name == "data":
            h = u2d.make_th2d("hDataReco2D", "Data reco", u2d.PT_EDGES, u2d.PZ_EDGES)
            u2d.fill_data_reco_2d(t, h, pt_lo, pt_hi, pz_lo, pz_hi, verbose=False)
        elif tree_name == "mc_background":
            h = u2d.make_th2d("hBkgReco2D", "Background reco (POT-scaled)", u2d.PT_EDGES,
                              u2d.PZ_EDGES)
            u2d.fill_bkg_reco_2d(t, h, pot_scale, pt_lo=pt_lo, pt_hi=pt_hi, pz_lo=pz_lo,
                                 pz_hi=pz_hi, verbose=False, universe_branch=ub)
        elif tree_name == "mc_signal_reco":
            u2d.collect_signal_arrays_2d(t, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale,
                                         use_weights=True, verbose=False, universe_branch=ub,
                                         alt_universe_branch=None)
        else:
            u2d.collect_truth_denom_arrays(t, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale,
                                           use_weights=True, verbose=False, universe_branch=ub)
    f_in.Close()


def parse(argv):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["unfold", "loaders"])
    ap.add_argument("--arm", required=True, choices=["all", "selective"])
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--label", default="")
    ap.add_argument("--expect", metavar="JSON")
    ap.add_argument("--require-provenance", action="store_true")
    ap.add_argument("--input-hashes", metavar="JSON",
                    help="hash-job record {files: {abspath: {sha256, size, mtime_ns, ino}}}")
    ap.add_argument("--compare-digests", metavar="RECEIPT")
    ap.add_argument("--omnifile", help="loaders mode")
    ap.add_argument("--universe", help="loaders mode, BAND:IDX")
    ap.add_argument("--trees", default="data,mc_background,mc_signal_reco,mc_truth_denom",
                    help="loaders mode, comma-separated")
    ap.add_argument("--negative-control", metavar="{omit,extra}:BRANCH",
                    help="loaders mode, --arm selective, one tree: must be refused (exit 5)")
    argv = list(argv)
    split = argv.index("--") if "--" in argv else len(argv)
    a = ap.parse_args(argv[:split])
    rest = argv[split + 1:]
    if a.mode == "unfold":
        if split == len(argv) or not rest:
            ap.error("unfold needs `-- <driver argv>`")
        a.driver_argv = rest
    else:
        if split != len(argv) or not a.omnifile:
            ap.error("loaders takes --omnifile and no `--` argv")
        a.trees = [t for t in a.trees.split(",") if t]
        if not a.trees or any(t not in TREE_OF for t in a.trees):
            ap.error(f"--trees must name trees from {sorted(TREE_OF)}")
        a.driver_argv = None
    a.control = None
    if a.negative_control:
        kind, _, branch = a.negative_control.partition(":")
        if a.mode != "loaders" or a.arm != "selective" or len(a.trees) != 1 or \
                kind not in ("omit", "extra") or not branch:
            ap.error("--negative-control needs loaders mode, --arm selective, one tree and "
                     "omit:BRANCH or extra:BRANCH")
        a.control = {"kind": kind, "branch": branch, "tree": a.trees[0]}
    return a


def comparison_key(a):
    """What must be equal for two receipts' loader digests to be comparable."""
    if a.mode == "unfold":
        argv, skip = [], False
        for tok in a.driver_argv:
            if skip:
                skip = False
                continue
            if tok == "--out":
                skip = True
                continue
            if not tok.startswith("--out="):
                argv.append(tok)
        return {"mode": "unfold", "driver_argv_without_out": argv}
    return {"mode": "loaders", "omnifile": str(Path(a.omnifile).resolve()),
            "universe": a.universe, "trees": a.trees}


def main(argv=None):
    a = parse(sys.argv[1:] if argv is None else argv)
    started = utc()
    timeline = Timeline()
    try:
        expectations = gx.load_expectations(a.expect)
        identity = gx.finalize(REPO, load_code(expectations), expectations, a.require_provenance)
        if a.mode == "unfold":
            inputs, out = driver_inputs(a.driver_argv)
        else:
            inputs, out = {"omnifile": a.omnifile}, None
        input_start = check_inputs(inputs, expectations, a.input_hashes, a.require_provenance)
        key = comparison_key(a)
        reference = reference_digests(a.compare_digests, key) if a.compare_digests else None
        if a.require_provenance:
            gx.reserve_output(a.receipt)
            if out is not None:
                gx.reserve_output(out)
    except gx.ProvenanceRefusal as exc:
        print(f"[REFUSED] {exc}", file=sys.stderr)
        return gx.REFUSAL_EXIT

    env = gx.environment_record()
    env.update(slurm={k: os.environ.get(k) for k in SLURM_ENV},
               omp={k: os.environ.get(k) for k in OMP_ENV},
               affinity_cpus=len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity")
               else None, os_cpu_count=os.cpu_count(), uname=list(os.uname()))
    receipt = Receipt(a.receipt, {
        "schema": "sb1-receipt/1", "mode": a.mode, "arm": a.arm, "label": a.label,
        "argv": list(sys.argv), "driver_argv": a.driver_argv, "comparison_key": key,
        "compare_digests": a.compare_digests, "negative_control": a.control,
        "started_utc": started, "status": "running", "identity": identity,
        "inputs_start": input_start, "environment": env, "loaders": [], "phases": []})
    receipt.write()
    records = install_hooks(a.arm, timeline, receipt, reference, a.control)
    status, code, error = "complete", 0, None
    try:
        if a.mode == "unfold":
            sys.argv = [str(REPO / DRIVER_REL), *a.driver_argv]
            ev = timeline.mark("driver:main")
            try:
                u2d.main()
            finally:
                timeline.close(ev)
        else:
            run_loaders(a, timeline)
        identity = gx.recheck(REPO, identity)
        input_end = check_inputs(inputs, expectations, a.input_hashes, a.require_provenance)
    except DigestMismatch as exc:
        status, code, error = "input-mismatch", EXIT_MISMATCH, str(exc)
    except bs.SelectionError as exc:
        status, code, error = "selection-refused", EXIT_SELECTION, f"{type(exc).__name__}: {exc}"
    except gx.ProvenanceRefusal as exc:
        status, code, error = "refused-late", gx.REFUSAL_EXIT, str(exc)
    except SystemExit as exc:
        status, code, error = "driver-exit", exc.code if isinstance(exc.code, int) else 1, repr(exc)
    except BaseException as exc:                      # noqa: BLE001 - recorded, then re-raised
        status, code, error = "error", 1, f"{type(exc).__name__}: {exc}"
        receipt.write(status=status, error=error, ended_utc=utc(), loaders=records,
                      phases=timeline.events, wall_s=time.perf_counter() - timeline.t0,
                      maxrss_bytes=maxrss(), io_end=proc_io())
        raise
    output = None
    if status == "complete" and out is not None:
        output = gx.input_record(out, None, True)
    receipt.write(status=status, error=error, ended_utc=utc(), identity=identity,
                  inputs_end=input_end if status == "complete" else None, output=output,
                  loaders=records, phases=timeline.events,
                  wall_s=time.perf_counter() - timeline.t0, maxrss_bytes=maxrss(),
                  io_end=proc_io(), exit_code=code)
    if error:
        print(f"[SB1] {status}: {error}", file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
